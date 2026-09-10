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
    detections_path: Path, targets: list[str] | None, out_path: Path, default_target: str | None
) -> Path:
    """One trial per shelf image. `target` is pre-filled if a per-image mapping is
    supplied (a `targets.json` of {image_stem: item_id}), otherwise left for the
    annotator."""
    rows = []
    mapping = {}
    if targets:
        mapping = {Path(k).stem: v for k, v in json.loads(Path(targets[0]).read_text()).items()}
    for rec in load_jsonl(detections_path):
        stem = Path(rec["image"]).stem
        rows.append(
            {
                "image": rec["image"],
                "target": mapping.get(stem, default_target),
                "gt_box": None,
                "n_boxes": len(rec["boxes"]),
            }
        )
    return write_trials(rows, out_path)


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


def load_ready_trials(trials_path: Path) -> list[dict]:
    """Only trials with both a target and a ground-truth decision are evaluated."""
    rows = load_jsonl(trials_path)
    ready = [r for r in rows if r.get("gt_box") is not None and r.get("target")]
    if not ready:
        raise ValueError(f"No annotated trials in {trials_path}. Run `lvnav shelf annotate` first.")
    return ready
