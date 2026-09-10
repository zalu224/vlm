"""Phase 3: the VLM verifies whether the crop in front of the user is the target.

This is the safety-relevant module. Two error types are not symmetric: telling a
blind user "yes, that's it" when it is not (a false confirmation) is far worse than
an unnecessary "no", so the prompt asks for an explicit uncertainty option and the
report breaks the two out separately.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from .catalog import Catalog
from .detect import crop
from .search import load_jsonl

CORRECTION_SYSTEM = (
    "You verify grocery and household items for a person who is blind. You look at a "
    "close-up photo of one item they are holding or reaching for, and you say whether "
    "it is the item they asked for. Confirming the wrong item is the worst thing you "
    "can do, so say no or unsure whenever the label does not clearly match."
)

CORRECTION_USER = """The person asked for: {target_name}

The attached photo is the item they are reaching for. Decide whether it is that item.

Answer with ONLY a JSON object, no other text:
{{"verdict": "yes" | "no" | "unsure", "identified_as": "<what the item actually appears to be, or empty>", "spoken": "<one short sentence you would say aloud>"}}

Rules:
- "yes" only if the label or packaging clearly identifies it as the requested item.
- "no" if it is clearly a different item; put your best guess in identified_as.
- "unsure" if the photo is too blurry, cropped or small to read the label.
"""

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
VALID_VERDICTS = {"yes", "no", "unsure"}


def parse_correction(text: str) -> dict:
    """Extract the verdict object; unparseable output becomes an explicit error row."""
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError(f"No JSON in correction output: {text[:200]!r}")
    data = json.loads(m.group(0))
    verdict = str(data.get("verdict", "")).strip().lower()
    return {
        "verdict": verdict if verdict in VALID_VERDICTS else None,
        "identified_as": str(data.get("identified_as", "")).strip(),
        "spoken": str(data.get("spoken", "")).strip(),
    }


def _cases_for(row: dict) -> list[tuple[str, int]]:
    """Positive case = the ground-truth crop. Negative case = the hardest distractor,
    i.e. the box the search stage ranked highest among the wrong ones."""
    cases: list[tuple[str, int]] = []
    if row["gt_box"] >= 0:
        cases.append(("positive", row["gt_box"]))
    hd = row.get("hard_distractor_box")
    if hd is not None and hd != row["gt_box"]:
        cases.append(("negative", int(hd)))
    return cases


def run_correction(
    search_path: Path,
    detections_path: Path,
    catalog: Catalog,
    backend,
    out_path: Path,
    model_label: str = "vlm",
    limit: int | None = None,
) -> Path:
    """Score every positive and hard-negative case with the VLM."""
    rows = load_jsonl(search_path)
    if limit:
        rows = rows[:limit]
    dets_by_image = {d["image"]: d for d in load_jsonl(detections_path)}
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = out_path.parent / "crops"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as fh:
        for row in tqdm(rows, desc=f"correct[{model_label}]", unit="trial"):
            boxes = {b["box_id"]: b for b in dets_by_image[row["image"]]["boxes"]}
            item = catalog[row["target"]]
            for case, box_id in _cases_for(row):
                box = boxes.get(box_id)
                if box is None:
                    continue
                crop_path = tmp_dir / f"{Path(row['image']).stem}_{box_id}.jpg"
                if not crop_path.exists():
                    with Image.open(row["image"]) as im:
                        crop(im.convert("RGB"), box["box"]).save(crop_path, quality=92)

                user = CORRECTION_USER.format(target_name=item.name)
                resp = backend.generate(CORRECTION_SYSTEM, user, image=crop_path)
                try:
                    parsed = parse_correction(resp.text)
                    error = None
                except (ValueError, json.JSONDecodeError) as exc:
                    parsed = {"verdict": None, "identified_as": "", "spoken": ""}
                    error = str(exc)

                expected = "yes" if case == "positive" else "no"
                fh.write(
                    json.dumps(
                        {
                            "model": model_label,
                            "image": row["image"],
                            "target": row["target"],
                            "target_name": item.name,
                            "case": case,
                            "box_id": box_id,
                            "crop_path": str(crop_path),
                            "expected": expected,
                            **parsed,
                            "correct": parsed["verdict"] == expected,
                            "false_confirm": case == "negative" and parsed["verdict"] == "yes",
                            "latency_s": round(resp.latency_s, 3),
                            "parse_error": error,
                            "raw": resp.text[:400],
                        }
                    )
                    + "\n"
                )
                fh.flush()
    return out_path
