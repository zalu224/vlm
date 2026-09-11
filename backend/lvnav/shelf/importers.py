"""Import public datasets into the study layout (catalog/<item>/ref*.jpg, images/, gt_boxes.json).

Two sources, chosen after a survey of what is publicly downloadable (see docs/DATA.md):

* **Grocery Store Dataset** (Klasson et al., WACV 2019, MIT): 5,125 in-store phone photos
  of 81 fine-grained classes, each with an iconic reference image. The packaged classes are
  real same-brand variants (four Arla milks, four Tropicana juices). It has no shelf scenes,
  so this importer tiles same-category products into *composite shelves*: real product
  photos, synthetic layout, ground-truth box known exactly. Documented as synthetic in the
  written SOURCE.md so it is never mistaken for a real shelf.
* **GroZi-3.2k** (George & Floerkemeier, ECCV 2014; OS2D redistribution): 3,235 product
  front images and 680 real shelf photos with product-level boxes. See `import_grozi`.

Both write `gt_boxes.json` ({image path: [x1, y1, x2, y2]}) so `lvnav shelf trials
--gt-boxes` fills in ground truth without a human, by IoU against the detector's boxes.
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image

PACKAGED_TOP_LEVEL = "Packages"


def slug(name: str) -> str:
    """'Arla-Standard-Milk' -> 'arla_standard_milk' (the item-id convention)."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _grocery_classes(src: Path) -> dict[int, dict]:
    with (src / "dataset" / "classes.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        icon = r["Iconic Image Path (str)"].lstrip("/")
        if not icon.startswith(f"iconic-images-and-descriptions/{PACKAGED_TOP_LEVEL}/"):
            continue  # fruit and vegetables are not the study's domain
        out[int(r["Class ID (int)"])] = {
            "name": r["Class Name (str)"],
            "coarse": r["Coarse Class Name (str)"],
            "icon": src / "dataset" / icon,
        }
    return out


def _grocery_split(src: Path, split: str, classes: dict[int, dict]) -> dict[int, list[Path]]:
    by_class: dict[int, list[Path]] = defaultdict(list)
    for line in (src / "dataset" / f"{split}.txt").read_text().splitlines():
        if not line.strip():
            continue
        rel, cid, _ = (x.strip() for x in line.split(","))
        if int(cid) in classes:
            by_class[int(cid)].append(src / "dataset" / rel)
    return by_class


def _composite(
    tiles: list[Image.Image], cols: int, tile_px: int, gap: int = 6
) -> tuple[Image.Image, list]:
    rows = -(-len(tiles) // cols)
    W, H = cols * tile_px + (cols + 1) * gap, rows * tile_px + (rows + 1) * gap
    canvas = Image.new("RGB", (W, H), (235, 232, 225))
    boxes = []
    for i, im in enumerate(tiles):
        im = im.convert("RGB").resize((tile_px, tile_px))
        x = gap + (i % cols) * (tile_px + gap)
        y = gap + (i // cols) * (tile_px + gap)
        canvas.paste(im, (x, y))
        boxes.append([x, y, x + tile_px, y + tile_px])
    return canvas, boxes


def import_grocery_store(
    src: Path,
    out: Path,
    *,
    refs_per_item: int = 3,
    tiles: int = 6,
    composites_per_target: int = 4,
    tile_px: int = 348,
    seed: int = 0,
) -> dict:
    """Build catalog/ from training photos, images/ from composite shelves of test photos.

    References come from the *train* split (real in-store photos, up to `refs_per_item`),
    never the iconic image alone: the iconic images are 198 px product renders and match
    shelf crops poorly. Composite shelves are built from the *test* split so no reference
    photo ever appears in a trial image. Each composite holds `tiles` products from the same
    coarse group (milk with milk, juice with juice), the target at a random cell.
    """
    src, out = Path(src), Path(out)
    rng = random.Random(seed)
    classes = _grocery_classes(src)
    train, test = _grocery_split(src, "train", classes), _grocery_split(src, "test", classes)
    (out / "catalog").mkdir(parents=True, exist_ok=True)
    (out / "images").mkdir(parents=True, exist_ok=True)

    names: dict[str, str] = {}
    ids: dict[int, str] = {}
    for cid, c in sorted(classes.items()):
        item = slug(c["name"])
        ids[cid] = item
        names[item] = c["name"].replace("-", " ")
        d = out / "catalog" / item
        d.mkdir(exist_ok=True)
        for i, p in enumerate(sorted(train[cid])[:refs_per_item], 1):
            Image.open(p).convert("RGB").save(d / f"ref{i:02d}.jpg", quality=92)
    (out / "catalog" / "names.json").write_text(json.dumps(names, indent=1))

    by_coarse: dict[str, list[int]] = defaultdict(list)
    for cid, c in classes.items():
        by_coarse[c["coarse"]].append(cid)
    # a group must have at least two classes to yield a confusable shelf
    all_packaged = sorted(classes)
    gt_boxes: dict[str, list] = {}
    n_images = 0
    for cid in sorted(classes):
        target_photos = sorted(test[cid])
        if not target_photos:
            continue
        siblings = [x for x in by_coarse[classes[cid]["coarse"]] if x != cid]
        fillers = (
            siblings
            if len(siblings) >= tiles - 1
            else siblings + [x for x in all_packaged if x != cid and x not in siblings]
        )
        for k in range(composites_per_target):
            others = rng.sample(fillers, min(tiles - 1, len(fillers)))
            photos = [rng.choice(target_photos)] + [
                rng.choice(sorted(test[o])) for o in others if test[o]
            ]
            order = list(range(len(photos)))
            rng.shuffle(order)
            tile_imgs = [Image.open(photos[i]) for i in order]
            cols = 3 if len(tile_imgs) > 3 else len(tile_imgs)
            canvas, boxes = _composite(tile_imgs, cols, tile_px)
            fname = f"{ids[cid]}__composite_{classes[cid]['coarse'].lower()}_{k + 1:02d}.jpg"
            path = out / "images" / fname
            canvas.save(path, quality=90)
            gt_boxes[str(path)] = boxes[order.index(0)]
            n_images += 1
    (out / "gt_boxes.json").write_text(json.dumps(gt_boxes, indent=0))
    (out / "SOURCE.md").write_text(
        "# Grocery Store Dataset import\n\n"
        "Source: Klasson, Zhang & Kjellström, *A Hierarchical Grocery Store Image Dataset with Visual and "
        "Semantic Labels*, WACV 2019. https://github.com/marcusklasson/GroceryStoreDataset (MIT).\n\n"
        f"Only the {len(classes)} packaged classes are imported (fruit and vegetables are outside the study).\n"
        f"catalog/: up to {refs_per_item} real in-store photos per item from the train split.\n"
        f"images/: **composite shelves** — {tiles} test-split photos of same-category products tiled on a grid, "
        f"{composites_per_target} per target item. The layout is synthetic; the product photos are real. "
        "Never report these as real shelf scenes. gt_boxes.json holds the exact cell of the target.\n"
    )
    return {
        "items": len(classes),
        "images": n_images,
        "refs": sum(min(len(train[c]), refs_per_item) for c in classes),
    }


# --------------------------------------------------------------------------- GroZi-3.2k
GROZI_SPLITS = {"val": ("val-old-cl", "val-new-cl"), "train": ("train",), "all": None}


def import_grozi(
    src: Path,
    out: Path,
    *,
    subsets: str = "val",
    targets_per_image: int = 3,
    max_side: int = 1600,
    seed: int = 0,
) -> dict:
    """GroZi-3.2k (OS2D redistribution): real shelves, one reference image per product.

    `subsets`: "val" (the 84 shelves of the two validation splits, 343 products; the
    standard evaluation set and the first run here), "train" (596 shelves) or "all".
    Each selected shelf yields up to `targets_per_image` trials, one per distinct product
    that has a non-difficult box, as separate downscaled copies named
    `p<classid>__grozi_<imageid>.jpg`. The ground-truth box is the largest non-difficult
    facing of that product. Products have no names in this dataset, so names.json maps
    every item to the same neutral phrase and the text branch of the matcher is inert.
    """
    import csv as _csv

    src, out = Path(src), Path(out)
    rng = random.Random(seed)
    wanted = GROZI_SPLITS[subsets] if subsets in GROZI_SPLITS else tuple(subsets.split(","))
    with (src / "classes" / "grozi.csv").open() as fh:
        rows = [r for r in _csv.DictReader(fh) if wanted is None or r["split"] in wanted]
    by_image: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        by_image[int(r["imageid"])].append(r)

    (out / "catalog").mkdir(parents=True, exist_ok=True)
    (out / "images").mkdir(parents=True, exist_ok=True)
    gt_boxes: dict[str, list] = {}
    used_classes: set[int] = set()
    n_images = 0
    for iid in sorted(by_image):
        boxes = by_image[iid]
        src_img = src / "src" / "3264" / f"{iid}.jpg"
        im = Image.open(src_img).convert("RGB")
        w0, h0 = im.size
        scale = min(1.0, max_side / max(w0, h0))
        if scale < 1.0:
            im = im.resize((round(w0 * scale), round(h0 * scale)))
        w, h = im.size
        candidates: dict[int, dict] = {}
        for r in boxes:
            if int(r["difficult"]):
                continue
            cid = int(r["classid"])
            area = (float(r["rx"]) - float(r["lx"])) * (float(r["by"]) - float(r["ty"]))
            if cid not in candidates or area > candidates[cid]["area"]:
                candidates[cid] = {"row": r, "area": area}
        chosen = sorted(candidates)
        if len(chosen) > targets_per_image:
            chosen = sorted(rng.sample(chosen, targets_per_image))
        for cid in chosen:
            r = candidates[cid]["row"]
            item = f"p{cid:04d}"
            path = out / "images" / f"{item}__grozi_{iid}.jpg"
            im.save(path, quality=90)
            gt_boxes[str(path)] = [
                round(float(r["lx"]) * w),
                round(float(r["ty"]) * h),
                round(float(r["rx"]) * w),
                round(float(r["by"]) * h),
            ]
            used_classes.add(cid)
            n_images += 1
        im.close()

    names: dict[str, str] = {}
    for cid in sorted(used_classes):
        item = f"p{cid:04d}"
        d = out / "catalog" / item
        d.mkdir(exist_ok=True)
        Image.open(src / "classes" / "images" / f"{cid}.jpg").convert("RGB").save(
            d / "ref01.jpg", quality=92
        )
        names[item] = "grocery product"
    (out / "catalog" / "names.json").write_text(json.dumps(names, indent=1))
    (out / "gt_boxes.json").write_text(json.dumps(gt_boxes, indent=0))
    (out / "SOURCE.md").write_text(
        "# GroZi-3.2k import\n\n"
        "Source: George & Floerkemeier, *Recognizing Products: A Per-exemplar Multi-label Image "
        "Classification Approach*, ECCV 2014. Redistributed with re-annotated boxes by OS2D "
        "(Osokin et al., CVPR 2020; https://github.com/aosokin/os2d). Academic use.\n\n"
        f"Subsets: {subsets}. Shelves: {len(by_image)} real photos from Swiss stores, downscaled to "
        f"{max_side} px. One trial copy per chosen product (up to {targets_per_image} per shelf); "
        "ground-truth box = largest non-difficult facing. catalog/: the dataset's single front-face "
        "reference image per product. Products carry no names; names.json is a neutral constant.\n"
    )
    return {"items": len(used_classes), "images": n_images, "shelves": len(by_image)}
