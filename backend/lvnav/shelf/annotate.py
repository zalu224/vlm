"""Ground-truth trials: which detected box holds the requested item.

Annotation is the only human bottleneck in this study, so the flow is built to be
fast rather than general: the detector proposes boxes, and the annotator types the
number of the correct one (or `m` if the detector missed it entirely). At roughly
five seconds per image that is under half an hour for 200 trials.

Two ways in:
* `lvnav shelf trials --auto` builds a template with `gt_box: null` for every image.
* `lvnav shelf annotate` fills those in, either in the terminal or, more comfortably,
  in the Streamlit annotator (`frontend/pages/1_Shelf_annotator.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from .dataset import target_from_filename
from .search import load_jsonl

MISSED = -1


def write_trials(rows: list[dict], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return path


def build_template(
    detections_path: Path,
    targets: list[str] | None,
    out_path: Path,
    default_target: str | None,
    from_filename: bool = False,
) -> Path:
    """One trial per shelf image, with the requested target pre-filled where possible.

    Three ways to supply the target, in priority order: parsed from the filename
    (`cinnamon__d1_03.jpg`), looked up in a `targets.json` of {image_stem: item_id},
    or a single `default_target` for every image. Pre-filling matters: it is the
    difference between annotating one field per image and two.
    """
    rows = []
    mapping = {}
    if targets:
        mapping = {Path(k).stem: v for k, v in json.loads(Path(targets[0]).read_text()).items()}
    unresolved = 0
    for rec in load_jsonl(detections_path):
        path = Path(rec["image"])
        target = None
        if from_filename:
            target = target_from_filename(path)
        target = target or mapping.get(path.stem) or default_target
        if target is None:
            unresolved += 1
        rows.append(
            {
                "image": rec["image"],
                "target": target,
                "gt_box": None,
                "n_boxes": len(rec["boxes"]),
            }
        )
    write_trials(rows, out_path)
    if unresolved:
        print(
            f"  note: {unresolved}/{len(rows)} trials have no target yet; "
            "the annotator will ask for each one"
        )
    return Path(out_path)


def render_boxes(image_path: Path, boxes: list[dict], out_path: Path | None = None) -> Image.Image:
    """Draw numbered boxes so the annotator (or a reader of the paper) can see what
    the detector proposed."""
    im = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(im)
    w = max(int(min(im.size) * 0.004), 2)
    for b in boxes:
        x1, y1, x2, y2 = b["box"]
        draw.rectangle([x1, y1, x2, y2], outline=(255, 200, 0), width=w)
        tag = str(b["box_id"])
        draw.rectangle([x1, y1 - 22, x1 + 12 + 10 * len(tag), y1], fill=(255, 200, 0))
        draw.text((x1 + 5, y1 - 19), tag, fill=(0, 0, 0))
    if out_path:
        im.save(out_path, quality=90)
    return im


def annotate_cli(trials_path: Path, detections_path: Path, catalog_ids: list[str]) -> Path:
    """Terminal annotation loop. Writes after every entry so it is safe to stop."""
    trials = load_jsonl(trials_path)
    dets = {d["image"]: d for d in load_jsonl(detections_path)}
    preview_dir = Path(trials_path).parent / "annotate_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"{len(trials)} trials. For each image, open the preview, then type the box number.\n"
        "  <n>  box n holds the target   |   m  detector missed it   |   s  skip   |   q  quit\n"
    )
    for i, t in enumerate(trials):
        if t.get("gt_box") is not None:
            continue
        rec = dets[t["image"]]
        preview = preview_dir / (Path(t["image"]).stem + "_boxes.jpg")
        render_boxes(Path(t["image"]), rec["boxes"], preview)

        target = t.get("target")
        if not target:
            target = input(f"[{i + 1}/{len(trials)}] target item id: ").strip()
            if target not in catalog_ids:
                print(f"  ! {target!r} is not in the catalogue; known: {sorted(catalog_ids)[:8]}")
                continue
            t["target"] = target

        ans = input(f"[{i + 1}/{len(trials)}] {preview.name} target={target} box? ").strip().lower()
        if ans == "q":
            break
        if ans == "s":
            continue
        t["gt_box"] = MISSED if ans == "m" else int(ans)
        write_trials(trials, trials_path)

    done = sum(1 for t in trials if t.get("gt_box") is not None)
    write_trials(trials, trials_path)
    print(f"Annotated {done}/{len(trials)} trials -> {trials_path}")
    return Path(trials_path)


def iou(a, b) -> float:
    """Intersection over union of two xyxy boxes."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter = max(0.0, min(ax2, bx2) - max(ax1, bx1)) * max(0.0, min(ay2, by2) - max(ay1, by1))
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / union if union > 0 else 0.0


def _containment(gt, box) -> tuple[float, float]:
    """(share of the detected box inside gt, share of gt covered by the box)."""
    gx1, gy1, gx2, gy2 = gt
    x1, y1, x2, y2 = box
    inter = max(0.0, min(x2, gx2) - max(x1, gx1)) * max(0.0, min(y2, gy2) - max(y1, gy1))
    barea = (x2 - x1) * (y2 - y1)
    garea = (gx2 - gx1) * (gy2 - gy1)
    return (inter / barea if barea else 0.0), (inter / garea if garea else 0.0)


def fill_gt_from_boxes(
    trials: list[dict],
    detections_path: Path,
    gt_boxes: dict[str, list[float]],
    min_iou: float = 0.5,
    match: str = "iou",
    min_inside: float = 0.8,
    min_cover: float = 0.15,
) -> list[dict]:
    """Auto-annotate trials whose ground-truth box is already known (public datasets).

    Mirrors what the human annotator does: pick the detected box that best overlaps the
    true box; if none qualifies, the detector missed the target.

    `match="iou"` (real shelves, tight ground-truth facings): best IoU, threshold `min_iou`.
    `match="contain"` (composite shelves, where the ground truth is the whole tile and the
    detector rightly boxes only the product inside it): a box qualifies when at least
    `min_inside` of it lies inside the tile and it covers at least `min_cover` of the tile
    (composite products cover a median third of their tile; a sliver does not count);
    the box covering most of the tile wins. The rule used and the score are stored on the
    trial (`gt_match`, `gt_iou`) so borderline matches can be audited.
    """
    dets = {d["image"]: d for d in load_jsonl(detections_path)}
    out = []
    for t in trials:
        t = dict(t)
        gt = gt_boxes.get(t["image"])
        rec = dets.get(t["image"])
        if gt is None or rec is None:
            out.append(t)
            continue
        best, best_score = None, 0.0
        for b in rec["boxes"]:
            if match == "contain":
                inside, cover = _containment(gt, b["box"])
                score = cover if (inside >= min_inside and cover >= min_cover) else 0.0
            else:
                v = iou(gt, b["box"])
                score = v if v >= min_iou else 0.0
            if score > best_score:
                best, best_score = b["box_id"], score
        t["gt_box"] = best if best is not None else MISSED
        t["gt_iou"] = round(best_score, 3)
        t["gt_match"] = match
        out.append(t)
    return out


def load_ready_trials(trials_path: Path) -> list[dict]:
    """Only trials with both a target and a ground-truth decision are evaluated."""
    rows = load_jsonl(trials_path)
    ready = [r for r in rows if r.get("gt_box") is not None and r.get("target")]
    if not ready:
        raise ValueError(f"No annotated trials in {trials_path}. Run `lvnav shelf annotate` first.")
    return ready
