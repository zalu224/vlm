"""Dataset conventions and validation for the home study.

The study lives or dies on the dataset, and the failure modes are boring: an item
photographed only at one distance, a catalogue folder with no reference photos, 200
images that all turn out to be of four objects. Those are cheap to detect before
any model runs and expensive to discover afterwards, so `check()` runs first.

Filename convention
-------------------
    <item_id>__<free text>.jpg        e.g. cinnamon__d1_bright_03.jpg

The part before the double underscore is the requested target for that image. This
removes the need to type a target for every trial: `lvnav shelf trials
--from-filename` reads it directly, leaving only the box choice to annotate.
Metadata after the separator is free-form and ignored by the code, so use it to
record distance and lighting for your own analysis.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from .detect import list_images

SEPARATOR = "__"
ITEM_ID_RE = re.compile(r"^[a-z0-9_]+$")

# Study targets from the proposal. Warnings, not errors: a smaller pilot is valid,
# it just needs to be reported as a pilot.
MIN_ITEMS = 15
MIN_IMAGES = 150
MIN_IMAGES_PER_ITEM = 5
MIN_REFS_PER_ITEM = 2
MIN_RESOLUTION = 640


def target_from_filename(path: Path) -> str | None:
    """Extract the requested item id from a filename, or None if unconventional."""
    stem = Path(path).stem
    if SEPARATOR not in stem:
        return None
    return stem.split(SEPARATOR, 1)[0].strip().lower() or None


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        lines = ["Dataset check", "=" * 13, ""]
        for k, v in self.stats.items():
            lines.append(f"  {k:.<34} {v}")
        if self.errors:
            lines += ["", "ERRORS (fix before running the study):"]
            lines += [f"  - {e}" for e in self.errors]
        if self.warnings:
            lines += ["", "Warnings (study will run; note them in the write-up):"]
            lines += [f"  - {w}" for w in self.warnings]
        if not self.errors and not self.warnings:
            lines += ["", "  Dataset looks good. Next: lvnav shelf index"]
        elif not self.errors:
            lines += ["", "  No blocking problems. Next: lvnav shelf index"]
        return "\n".join(lines)


def check(catalog_dir: Path, images_dir: Path, strict_names: bool = True) -> CheckResult:
    """Validate a home dataset before any model runs."""
    res = CheckResult()
    catalog_dir, images_dir = Path(catalog_dir), Path(images_dir)

    if not catalog_dir.is_dir():
        res.errors.append(f"Catalogue directory missing: {catalog_dir}")
        return res
    if not images_dir.is_dir():
        res.errors.append(f"Images directory missing: {images_dir}")
        return res

    # --- catalogue -----------------------------------------------------------
    item_dirs = sorted(p for p in catalog_dir.iterdir() if p.is_dir())
    items: dict[str, int] = {}
    for d in item_dirs:
        refs = [p for p in d.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        items[d.name] = len(refs)
        if not refs:
            res.errors.append(f"Catalogue item '{d.name}' has no reference photos")
        elif len(refs) < MIN_REFS_PER_ITEM:
            res.warnings.append(
                f"Item '{d.name}' has {len(refs)} reference photo; "
                f"{MIN_REFS_PER_ITEM}+ makes matching robust to shelf pose"
            )
        if strict_names and not ITEM_ID_RE.match(d.name):
            res.errors.append(
                f"Item id '{d.name}' must be lowercase letters, digits and underscores only"
            )

    if not items:
        res.errors.append(f"No catalogue items found under {catalog_dir}")
        return res
    if len(items) < MIN_ITEMS:
        res.warnings.append(
            f"{len(items)} items; the proposal targets {MIN_ITEMS}+. Fewer is a valid pilot, "
            "but say so in the write-up"
        )

    # --- images --------------------------------------------------------------
    images = list_images(images_dir)
    if not images:
        res.errors.append(f"No images found under {images_dir}")
        return res

    unnamed, unknown, small = [], [], []
    per_item: Counter[str] = Counter()
    for p in images:
        tgt = target_from_filename(p)
        if tgt is None:
            unnamed.append(p.name)
            continue
        if tgt not in items:
            unknown.append(f"{p.name} -> '{tgt}'")
            continue
        per_item[tgt] += 1
        try:
            with Image.open(p) as im:
                if min(im.size) < MIN_RESOLUTION:
                    small.append(f"{p.name} ({im.size[0]}x{im.size[1]})")
        except OSError:
            res.errors.append(f"Unreadable image: {p.name}")

    if unnamed:
        res.errors.append(
            f"{len(unnamed)} image(s) do not follow <item_id>__<anything>.jpg, "
            f"e.g. {unnamed[0]}. Rename them or use --default-target instead of --from-filename"
        )
    if unknown:
        res.errors.append(
            f"{len(unknown)} image(s) name an item with no catalogue folder, e.g. {unknown[0]}"
        )
    if small:
        res.warnings.append(
            f"{len(small)} image(s) below {MIN_RESOLUTION}px on the short side, e.g. {small[0]}; "
            "small crops are hard to read labels from"
        )
    if len(images) < MIN_IMAGES:
        res.warnings.append(f"{len(images)} images; the proposal targets {MIN_IMAGES}+")

    thin = [i for i in items if per_item[i] < MIN_IMAGES_PER_ITEM]
    if thin:
        res.warnings.append(
            f"{len(thin)} item(s) appear as the target in fewer than {MIN_IMAGES_PER_ITEM} "
            f"images, e.g. {sorted(thin)[:3]}; per-item accuracy will be noisy for them"
        )
    never = [i for i in items if per_item[i] == 0]
    if never:
        res.warnings.append(
            f"{len(never)} catalogue item(s) are never requested: {sorted(never)[:5]}. "
            "They still act as distractors, which is fine, but they are not being tested"
        )

    res.stats = {
        "catalogue items": len(items),
        "reference photos": sum(items.values()),
        "shelf images": len(images),
        "images with a valid target": sum(per_item.values()),
        "items requested at least once": len([i for i in items if per_item[i]]),
        "median images per requested item": (
            sorted(per_item.values())[len(per_item) // 2] if per_item else 0
        ),
    }
    return res
