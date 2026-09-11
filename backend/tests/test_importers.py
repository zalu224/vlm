"""Importers for public datasets and auto-annotation from known ground-truth boxes."""

import json

import numpy as np
from PIL import Image

from lvnav.shelf.annotate import MISSED, fill_gt_from_boxes, iou
from lvnav.shelf.importers import import_grocery_store, slug


def test_slug_makes_item_ids():
    assert slug("Arla-Standard-Milk") == "arla_standard_milk"
    assert (
        slug("God-Morgon Orange/Red-Grapefruit Juice") == "god_morgon_orange_red_grapefruit_juice"
    )


def test_iou_basic():
    assert iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0
    assert iou([0, 0, 10, 10], [5, 0, 15, 10]) == 1 / 3
    assert iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0.0


def test_fill_gt_from_boxes_matches_best_iou_or_marks_missed(tmp_path):
    dets = tmp_path / "detections.jsonl"
    dets.write_text(
        json.dumps(
            {
                "image": "a.jpg",
                "size": [100, 100],
                "boxes": [
                    {"box_id": 0, "label": "box", "conf": 0.9, "box": [0, 0, 50, 50]},
                    {"box_id": 1, "label": "box", "conf": 0.8, "box": [50, 50, 100, 100]},
                ],
            }
        )
        + "\n"
        + json.dumps(
            {
                "image": "b.jpg",
                "size": [100, 100],
                "boxes": [{"box_id": 0, "label": "box", "conf": 0.9, "box": [0, 0, 20, 20]}],
            }
        )
        + "\n"
    )
    trials = [
        {"image": "a.jpg", "target": "x", "gt_box": None, "n_boxes": 2},
        {"image": "b.jpg", "target": "y", "gt_box": None, "n_boxes": 1},
    ]
    gt = {"a.jpg": [48, 52, 100, 100], "b.jpg": [60, 60, 100, 100]}
    filled = fill_gt_from_boxes(trials, dets, gt, min_iou=0.5)
    assert filled[0]["gt_box"] == 1 and filled[0]["gt_iou"] > 0.8
    assert filled[1]["gt_box"] == MISSED


def _fake_grocery_src(root):
    """Minimal Grocery Store Dataset layout: 3 packaged classes in one coarse group + 1 fruit."""
    rows = [
        "Class Name (str),Class ID (int),Coarse Class Name (str),Coarse Class ID (int),Iconic Image Path (str),Product Description Path (str)"
    ]
    specs = [
        ("Arla-Standard-Milk", 0, "Milk", 0, "Packages"),
        ("Arla-Sour-Milk", 1, "Milk", 0, "Packages"),
        ("Garant-Standard-Milk", 2, "Milk", 0, "Packages"),
        ("Royal-Gala", 3, "Apple", 1, "Fruit"),
    ]
    rng = np.random.default_rng(0)
    train_lines, test_lines = [], []
    for name, cid, coarse, ccid, top in specs:
        icon = root / "dataset/iconic-images-and-descriptions" / top / coarse / name
        icon.mkdir(parents=True)
        Image.new("RGB", (198, 198), tuple(int(v) for v in rng.integers(0, 255, 3))).save(
            icon / f"{name}_Iconic.jpg"
        )
        rows.append(
            f"{name},{cid},{coarse},{ccid},/iconic-images-and-descriptions/{top}/{coarse}/{name}/{name}_Iconic.jpg,/x.txt"
        )
        for split, lines, n in (("train", train_lines, 4), ("test", test_lines, 3)):
            d = root / "dataset" / split / top / coarse / name
            d.mkdir(parents=True)
            for i in range(n):
                Image.fromarray(rng.integers(0, 255, (348, 348, 3), dtype=np.uint8)).save(
                    d / f"{name}_{i:03d}.jpg"
                )
                lines.append(f"{split}/{top}/{coarse}/{name}/{name}_{i:03d}.jpg, {cid}, {ccid}")
    (root / "dataset/classes.csv").write_text("\n".join(rows) + "\n")
    (root / "dataset/train.txt").write_text("\n".join(train_lines) + "\n")
    (root / "dataset/test.txt").write_text("\n".join(test_lines) + "\n")


def test_import_grocery_store_builds_catalog_and_composite_shelves(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    _fake_grocery_src(src)
    stats = import_grocery_store(
        src, out, refs_per_item=2, tiles=3, composites_per_target=2, seed=0
    )
    # only packaged classes become items; fruit is excluded
    items = sorted(p.name for p in (out / "catalog").iterdir() if p.is_dir())
    assert items == ["arla_sour_milk", "arla_standard_milk", "garant_standard_milk"]
    assert len(list((out / "catalog/arla_standard_milk").glob("ref*.jpg"))) == 2
    # composite shelves: every file names its target, gt_boxes.json has a box per image
    images = sorted((out / "images").glob("*.jpg"))
    assert len(images) == 3 * 2 and all("__" in p.stem for p in images)
    gt = json.loads((out / "gt_boxes.json").read_text())
    assert len(gt) == len(images)
    w, h = Image.open(images[0]).size
    x1, y1, x2, y2 = gt[str(images[0])]
    assert 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h
    assert stats["items"] == 3 and stats["images"] == 6
    assert (out / "SOURCE.md").exists()


def _fake_grozi_src(root):
    """OS2D GroZi-3.2k layout: classes/grozi.csv (normalised boxes), classes/images/<cid>.jpg,
    src/3264/<imageid>.jpg. Two shelf images: image 0 in train, image 1 in val-new-cl."""
    rng = np.random.default_rng(1)
    (root / "classes/images").mkdir(parents=True)
    (root / "src/3264").mkdir(parents=True)
    for cid in range(4):
        Image.fromarray(rng.integers(0, 255, (120, 90, 3), dtype=np.uint8)).save(
            root / f"classes/images/{cid}.jpg"
        )
    for iid in range(2):
        Image.fromarray(rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)).save(
            root / f"src/3264/{iid}.jpg"
        )
    rows = [
        "gtbboxid,classid,imageid,lx,rx,ty,by,difficult,split",
        "0,0,0,0.10,0.30,0.10,0.50,0,train",
        "1,1,0,0.40,0.60,0.10,0.50,0,train",
        "2,2,1,0.05,0.25,0.20,0.60,0,val-new-cl",
        "3,2,1,0.30,0.50,0.20,0.60,1,val-new-cl",  # second facing, difficult
        "4,3,1,0.60,0.90,0.20,0.70,0,val-old-cl",
    ]
    (root / "classes/grozi.csv").write_text("\n".join(rows) + "\n")


def test_import_grozi_val_split_builds_catalog_images_and_gt(tmp_path):
    from lvnav.shelf.importers import import_grozi

    src, out = tmp_path / "grozi", tmp_path / "out"
    _fake_grozi_src(src)
    stats = import_grozi(src, out, subsets="val", targets_per_image=5, max_side=320, seed=0)
    items = sorted(p.name for p in (out / "catalog").iterdir() if p.is_dir())
    assert items == ["p0002", "p0003"]  # only classes boxed in val images
    assert (out / "catalog/p0002/ref01.jpg").exists()
    images = sorted((out / "images").glob("*.jpg"))
    assert [p.name for p in images] == ["p0002__grozi_1.jpg", "p0003__grozi_1.jpg"]
    w, h = Image.open(images[0]).size
    assert max(w, h) == 320  # downscaled copy
    gt = json.loads((out / "gt_boxes.json").read_text())
    x1, y1, x2, y2 = gt[str(images[0])]
    # class 2's non-difficult facing is lx=0.05..0.25, ty=0.20..0.60 of a 320x240 image
    assert (x1, y1, x2, y2) == (16, 48, 80, 144)
    assert stats == {"items": 2, "images": 2, "shelves": 1}
    assert "GroZi-3.2k" in (out / "SOURCE.md").read_text()
