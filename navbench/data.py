"""Ingest the dataset repo (github.com/rizzojr01/vlm_navigation_eval) into data/pblv_nav.

The phone photos carry EXIF orientation 6 (stored landscape, displayed portrait). Every model
must see the photo the way a person sees it, so orientation is applied once here and the
copies are saved upright, downscaled to `max_side`, with a manifest of what came from where.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def image_id(src_root: Path, path: Path) -> str:
    """'<folder>/<stem>' relative to the repo's data/ folder, e.g. 'campus/classroom_chairs_1'."""
    rel = path.relative_to(src_root / "data")
    return f"{rel.parent.as_posix()}/{rel.stem}"


def ingest(src_root: Path, out: Path, *, max_side: int = 1600) -> Path:
    src_root, out = Path(src_root), Path(out)
    files = sorted(
        p
        for p in (src_root / "data").rglob("*")
        if p.suffix.lower() in IMAGE_EXTS and ".ipynb_checkpoints" not in p.parts
    )
    rows = []
    for p in files:
        iid = image_id(src_root, p)
        dest = out / "images" / f"{iid}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((max_side, max_side))
            w, h = im.size
            if not dest.exists():
                im.save(dest, quality=92)
        rows.append(
            {
                "image_id": iid,
                "folder": p.parent.name,
                "path": dest.relative_to(out).as_posix(),
                "width": w,
                "height": h,
                "source": str(p),
            }
        )
    manifest = out / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return manifest
