# Datasets

Three datasets sit side by side under `data/`. They are never mixed: each has its own `catalog/`, `images/` and `results/<dataset>/`, and each result table names its dataset.

| dataset | folder | what it is | ground truth | licence |
|---|---|---|---|---|
| Home shelf | `data/shelf` | Aaron's own household items and shelf photos (`docs/MATERIALS.md`) | hand-annotated in the viewer | private |
| GroZi-3.2k | `data/grozi_val` | 84 real supermarket shelves, 343 products, one reference photo each | boxes shipped with the dataset, matched to detections automatically | academic use |
| Grocery Store | `data/grocery` | 31 packaged products as real in-store photos, tiled into composite shelves | exact tile position | MIT |

## Why these two public sets

Survey done 2026-09-10, looking for: reference photos per product, cluttered scenes with product-level boxes, visually confusable packaged goods, phone-quality images, a citable licence, and a size that fits a laptop.

| candidate | verdict |
|---|---|
| **GroZi-3.2k** (George & Floerkemeier 2014; OS2D copy) | **Adopted.** 3,235 product front images and 680 shelf photos from five Swiss stores, every box labelled with its product. Same structure as the home study, annotation already done. Original ETH host is gone; OS2D's Google Drive archive (0.57 GB) is live. |
| **Grocery Store Dataset** (Klasson et al. 2019) | **Adopted for the verification stage.** 5,125 in-store phone photos, 81 fine-grained classes with an iconic image each; the packaged classes are real same-brand variants (four Arla milks, four Tropicana juices, six yoghurts). No shelf scenes, so shelves are composited. MIT, 258 MB clone. |
| Holoselecta (Fuchs 2019) | Not adopted. 295 vending-machine fronts, 109 products by GTIN, CC BY 4.0, but no reference photos ship with it and the glass fronts are not shelves. Worth revisiting if a second real-scene set is needed. |
| ORBIT (Microsoft 2021) | Not adopted for now. The only set recorded by blind and low-vision people, CC BY 4.0, with clutter boxes; but the objects are personal items (keys, brushes), not label-only look-alikes, and it is tens of GB. |
| Unitail (Chen et al. 2022) | Rejected. The shelf detection set is no longer public; the OCR set is product crops for academic use only. |
| RPC (Wei et al. 2019) | Rejected. Checkout-counter scenes, not shelves; CC BY-NC-SA; 8.8 GB. |
| SKU-110K | Rejected. Boxes carry no product identity. |
| GroZi-120 (2007) | Rejected. Original host dead; only account-gated mirrors. |

## GroZi-3.2k

```bash
.venv/bin/gdown 1Fx9lvmjthe3aOqjvKc6MJpMuLF22I1Hp -O data/grozi/grozi.zip && (cd data/grozi && unzip -q grozi.zip)
lvnav shelf import grozi --src data/grozi/grozi --out data/grozi_val --subsets val
```

The archive holds `classes/grozi.csv` (8,922 boxes, normalised `lx rx ty by`, class id, a `difficult` flag, split), `classes/images/<classid>.jpg` (1,063 product fronts, median 308×395 px) and `src/3264/<imageid>.jpg` (680 shelves at 3264×2448). The two validation splits annotate the same 84 shelves for 158 "old" and 185 "new" classes; together they are the first-run scope. The importer writes up to three trial copies per shelf, one per distinct product with a non-difficult box, downscaled to 1600 px, and `gt_boxes.json` with the largest facing of that product. Products have no names, so the matcher's text branch is inert on this set (`names.json` is a constant).

What it tests well: search on real shelves with dense same-category neighbours (median 12 facings, 4 products per shelf). What it cannot test: a spoken product name (there are none), and the 7B-vs-3B reading of *English* labels, since the products are Swiss.

## Grocery Store Dataset

```bash
git clone --depth 1 https://github.com/marcusklasson/GroceryStoreDataset.git data/grocery_store_src
lvnav shelf import grocery --src data/grocery_store_src --out data/grocery --per-target 6
```

Only the 31 packaged classes are imported (fruit and vegetables are outside the study). References are up to three real in-store photos per item from the train split, not the 198 px iconic render. Trial images are **composite shelves**: six test-split photos of same-category products (milk with milk, juice with juice) tiled on a 3×2 grid at 348 px per tile, six composites per target, 186 images. The layout is synthetic and every figure and table that uses this set must say so; the product photos, the confusability and the ground truth are real.

What it tests well: verification against genuine same-brand variants, and how far a smaller model can read a 348 px label. What it cannot test: real shelf clutter, occlusion or lighting.

## Auto-annotation

For both public sets the human annotation step is replaced by `lvnav shelf trials --from-filename --gt-boxes data/<dataset>/gt_boxes.json`. It does what the annotator does: picks the detected box that best matches the known box, or marks the target as missed by the detector. Two match rules, chosen per dataset and recorded on every trial (`gt_match`, `gt_iou`):

- `--match iou` (GroZi, tight ground-truth facings): best IoU, threshold 0.5.
- `--match contain` (Grocery composites, where the ground truth is the whole tile and the detector rightly boxes only the product inside it): a box qualifies when at least 80 % of it lies inside the tile and it covers at least 15 % of the tile; the box covering most of the tile wins. With plain IoU the composites showed 18 % "recall" while the best box was fully inside the tile in nearly every case.

Detector settings that matter on these sets (`docs/HARDWARE.md` has the measurements): inference size 1280 (the ultralytics default of 640 shrinks a shelf until products are 40 px wide and halves recall), and for GroZi confidence 0.05 with up to 60 boxes, which took recall on a 40-trial sample from 45 % to 68 % at the price of ~29 candidates per shelf. The home-shelf defaults stay at conf 0.15.

## First search results (2026-09-11, no VLM involved)

Detector: YOLO-World, container vocabulary, imgsz 1280; conf 0.15 on Grocery, 0.05 on GroZi. Top-1/top-3 are over trials where the detector found the target; end-to-end top-1 charges detector misses to the system.

| dataset | trials | detector recall | candidates / image | arm | top-1 | top-3 | end-to-end top-1 |
|---|---|---|---|---|---|---|---|
| Grocery (composite) | 186 | 74.7 % | 9.3 | det | 15.1 % | 40.3 % | 11.3 % |
| | | | | + CLIP | 56.8 % | 89.2 % | 42.5 % |
| | | | | + colour | 59.7 % | 85.6 % | 44.6 % |
| GroZi-3.2k (val) | 219 | 70.3 % | 28.5 | det | 9.1 % | 21.4 % | 6.4 % |
| | | | | + CLIP | 34.4 % | 71.4 % | 24.2 % |
| | | | | + colour | 42.2 % | 79.2 % | 29.7 % |

Reading: detection alone is at chance for the number of candidates, as RQ1 expects; CLIP is the large step; colour adds a further eight points on real shelves and two on composites. The remaining ceiling is the detector (a quarter to a third of targets never get a box), which is why recall is reported first. Correction (the VLM stage) has not been run on these sets yet: `lvnav shelf correct --results results/<dataset> --label qwen7b`, then the 3B, then `shelf report`.
