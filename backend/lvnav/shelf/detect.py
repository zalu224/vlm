"""Phase 0: run open-vocabulary detection over every shelf image once and cache it.

Detection is the slowest reusable step, so it is separated from search: the search
ablations and the annotator all read the same `detections.jsonl`, which means the
detector runs once for the whole study.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from ..perception.cues import Detection

# Container nouns, not item names. The detector's job is to propose "there is a jar
# here"; deciding *which* jar is the matcher's job, exactly as in the paper.
CONTAINER_VOCABULARY = [
    "box",
    "can",
    "jar",
    "bottle",
    "carton",
    "bag",
    "tube",
    "packet",
    "container",
    "cup",
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def list_images(images_dir: Path) -> list[Path]:
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    return sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def detect_shelves(
    images_dir: Path,
    detector,
    out_path: Path,
    min_area_frac: float = 0.002,
    max_boxes: int = 30,
) -> Path:
    """Write one JSON line per image: {"image": ..., "size": [w, h], "boxes": [...]}.

    Tiny boxes are dropped: below ~0.2% of frame area a crop carries too few pixels
    for CLIP or a VLM to read a label, so keeping them only inflates the candidate
    set and hurts top-1.
    """
    images = list_images(images_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as fh:
        for path in tqdm(images, desc="detect", unit="img"):
            with Image.open(path) as im:
                im = im.convert("RGB")
                w, h = im.size
                dets: list[Detection] = detector(im)
            kept = []
            for d in dets:
                x1, y1, x2, y2 = d.box
                if (x2 - x1) * (y2 - y1) < min_area_frac * w * h:
                    continue
                kept.append(
                    {
                        "label": d.label,
                        "conf": round(float(d.confidence), 4),
                        "box": [round(float(v), 2) for v in d.box],
                    }
                )
            kept.sort(key=lambda b: -b["conf"])
            kept = kept[:max_boxes]
            for i, b in enumerate(kept):
                b["box_id"] = i
            fh.write(json.dumps({"image": str(path), "size": [w, h], "boxes": kept}) + "\n")
    return out_path


def crop(
    image: Image.Image, box: list[float] | tuple[float, ...], pad: float = 0.04
) -> Image.Image:
    """Crop with a small margin so labels are not clipped at the box edge."""
    w, h = image.size
    x1, y1, x2, y2 = box
    dx, dy = (x2 - x1) * pad, (y2 - y1) * pad
    return image.crop((max(x1 - dx, 0), max(y1 - dy, 0), min(x2 + dx, w), min(y2 + dy, h)))
