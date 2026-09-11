# Materials and Data Collection Guide

Everything needed to run the study, and exactly how to capture it. Work through this in order; the dataset is the only part nobody can do for you, and it is the part that determines whether the results mean anything.

Budget: **one afternoon** for capture, **30 minutes** for annotation.

---

## 1. Equipment

| Item | Requirement | Notes |
|---|---|---|
| Camera | Any phone from the last five years | Shoot at default resolution; do not use portrait mode or any depth/blur effect |
| Computer | Apple Silicon Mac, 16 GB or more | See `docs/HARDWARE.md` for the memory budget |
| Objects | ~20 household items | Section 2 — this is the important choice |
| Surface | A pantry shelf, cupboard, fridge shelf, or bookshelf | One or two locations is enough |
| Lighting | Whatever you already have | You will deliberately vary it; no equipment needed |
| Tape measure or a known reference | Optional | Only to keep your distance buckets honest |

No wearable hardware, microphone, or speaker is required. Everything is measured from photographs.

## 2. Choosing the objects

**This is the single most important decision in the study.** A collection of obviously different objects makes every method score near-perfectly and measures nothing. The objects must be hard to tell apart.

Aim for roughly 20 items in three groups:

**Group A — confusable pairs (10–12 items, the core of the study).** Items that share a brand, shape, and color scheme and differ only in a printed word:
- Two or three varieties of the same canned soup or beans
- Two cereals or crackers from the same brand line
- Four to six spice jars from the same rack — identical jars, different labels
- Two similar bottles (olive oil / vinegar, two sauces from one brand)

**Group B — same shape, different color (4–5 items).** Containers of the same form in clearly different packaging. These test whether color adds anything once visual matching is already working.

**Group C — controls (3–4 items).** Obviously distinct objects: a cereal box, a milk carton, a dish soap bottle. If accuracy on these is not near-perfect, something is broken in the setup rather than interesting about the method.

Record your list in `data/shelf/ITEMS.md` as you go, noting which group each item belongs to. You will need that grouping to interpret the results.

### Naming

Give each item a lowercase id with underscores. The id becomes its folder name and the prefix of every photograph of it:

```
cinnamon              smoked_paprika        chicken_noodle_soup
tomato_soup           honey_nut_cereal      olive_oil
```

Keep ids distinguishable at a glance. `soup_1` and `soup_2` will cost you time during annotation.

## 3. Reference photographs

Two or three per item, roughly 40–60 photographs in total. Ten minutes of work.

- Object alone against a plain background (a countertop or a sheet of paper).
- Object fills most of the frame, label facing the camera and readable.
- Even lighting, no flash, no shadow across the label.
- Vary the angle slightly between shots: straight on, then rotated maybe 20–30 degrees. Averaging two or three views is what makes matching survive the angle the object happens to sit at on the shelf.

Save them as:

```
data/shelf/catalog/<item_id>/ref01.jpg
data/shelf/catalog/<item_id>/ref02.jpg
```

## 4. Shelf photographs

Roughly 200 photographs. Two to three hours including setup, less if you work quickly.

**Arrangement.** Place 6–12 items on the shelf at once, always including several confusable ones together. Rearrange between rounds so position does not become an accidental clue — if the cinnamon is always on the left, the study measures memorization of your shelf rather than recognition of the object.

**Vary these three things systematically**, since they are what the results are reported against:

| Variable | Levels | How |
|---|---|---|
| Distance | ~0.5 m, ~1.0 m, ~1.5 m | Step back; pace it out, precision is not required |
| Lighting | Bright, normal, dim | Daylight, room lights, room lights with curtains drawn |
| Angle | Straight on, from the left, from the right | Roughly 30 degrees off-center |

You do not need every combination. Cover each level of each variable a reasonable number of times.

**Also capture some harder cases** — roughly 20% of the set:
- An item partly hidden behind another
- An item turned so the label is at an angle
- Two confusable items sitting directly next to each other
- A shelf crowded with more items than usual

**Hold the camera at chest height**, roughly where a body-worn camera would sit. Do not center the target object in the frame; that is a cue a real system would not have.

### Filenames matter

Name each photograph after the item being *requested* in it:

```
cinnamon__d1_bright_01.jpg
cinnamon__d3_dim_04.jpg
tomato_soup__d2_angled_02.jpg
smoked_paprika__d1_occluded_01.jpg
```

The part before the double underscore is the target; everything after it is for your own reference and is ignored by the code. This convention lets the tooling fill in the target automatically, cutting annotation from two decisions per image to one. `d1/d2/d3` for distance and a lighting word are worth recording — you will want them when you break results down.

Each photograph is one trial, so aim for **at least five per item** as the requested target. Items that appear in the background without being requested still act as distractors, which is useful.

## 5. Folder layout

```
data/shelf/
├── ITEMS.md                        your item list, with group labels
├── catalog/
│   ├── cinnamon/ref01.jpg  ref02.jpg
│   ├── smoked_paprika/ref01.jpg  ref02.jpg
│   └── ...                         ~20 folders
└── images/
    ├── cinnamon__d1_bright_01.jpg
    ├── tomato_soup__d2_angled_02.jpg
    └── ...                         ~200 photographs
```

## 6. Check the dataset before running anything

```bash
make shelf-check
```

This validates the whole dataset in seconds and reports two kinds of problem. **Errors** block the study: an item folder with no reference photos, filenames that do not follow the convention, a photograph naming an item that has no catalogue folder. **Warnings** do not block it but belong in the write-up: thin coverage of some item, images below 640 px, fewer items than the proposal targets.

Fix the errors, rerun until it is clean, and only then move on. Everything after this point is automated.

## 7. Software setup

```bash
make setup          # one-time: creates .venv and installs everything
make serve-vlm      # leave running in a second terminal
```

Models download automatically on first use (roughly 6 GB total, once). The detector and CLIP come down when first called; the VLM downloads when the server starts.

## 8. Running the study

```bash
make shelf-check                     # dataset validation (section 6)
make shelf-index                     # reference photos -> embeddings        seconds
make shelf-detect                    # detection over all images             2-5 min
make shelf-trials                    # annotation template                   seconds
make viewer                          # annotate: one click per image         20-30 min
make shelf-search                    # all three matching arms               3-8 min
make shelf-correct LABEL=qwen7b      # verification, larger model            15-40 min
make shelf-correct LABEL=qwen3b MODEL=mlx-community/Qwen2.5-VL-3B-Instruct-4bit
make shelf-report                    # results tables + summary.json
```

Add `BACKEND=mock` to any of these to rehearse the whole sequence in seconds without models, which is worth doing once before you have a dataset.

## 9. Annotation

Open the **Shelf annotator** page in the viewer sidebar. For each photograph it draws the detector's numbered boxes and shows the requested item; press the number of the box holding that item, or **Detector missed it** if none of them do.

- One click per image. Progress saves after every click, so you can stop and resume.
- Marking a miss is not a failure of your annotation — it is the measurement of detector recall, and it is reported separately from ranking accuracy.
- Do not agonize over near-ties. If two boxes both cover the item, pick the tighter one.

## 10. Checklist

**Before capture**
- [ ] ~20 items chosen, with at least 10 in confusable pairs
- [ ] Item ids written down in `ITEMS.md`, lowercase with underscores
- [ ] Camera set to standard mode, portrait/depth effects off

**Capture**
- [ ] 2–3 reference photos per item, label readable
- [ ] ~200 shelf photos covering three distances, three lighting levels, three angles
- [ ] ~20% harder cases: occlusion, rotation, adjacent confusables, clutter
- [ ] Every file named `<item_id>__<details>.jpg`
- [ ] At least five photos per item as the requested target

**Before running**
- [ ] `make shelf-check` reports no errors
- [ ] `make serve-vlm` running in a second terminal
- [ ] `BACKEND=mock` rehearsal completed once

**After running**
- [ ] `report.md` reviewed, including the failure cases at the bottom
- [ ] Warnings from `shelf-check` noted in the write-up as limitations

---

## 11. This project's items (catalogued 2026-09-10)

The seven items photographed so far are organised as the tooling expects: `data/shelf/catalog/<item_id>/ref01.jpg` (front), `ref02.jpg` (left), `ref03.jpg` (right), downscaled to 1600 px with the phone's orientation applied; the untouched originals are in `data/shelf/originals/`. Prompt-facing names are in `catalog/names.json`, the grouping in `data/shelf/ITEMS.md`.

| item_id | what it is | container | group |
|---|---|---|---|
| `cinnamon` | McCormick ground cinnamon, red cap | jar | B |
| `paprika` | Gold Emblem paprika, black cap, orange label | jar | B |
| `oregano` | Good & Gather oregano leaves, black cap, green label | jar | B |
| `olive_oil` | extra virgin olive oil, green glass, 250 ml | bottle | B |
| `balsamic_vinegar` | Napoleon organic balsamic vinegar, gold cap, 500 ml | bottle | B |
| `frosted_flakes` | Kroger Frosted Flakes, giant size | box | C |
| `fruit_snacks` | Welch's mixed fruit fruit snacks | box | C |

### What the models already say about them

Both models were run on the 21 reference photos before any shelf photo exists, to check the catalogue and to see how hard the set is.

**Detection (YOLO-World, container vocabulary, conf 0.15).** The main item was boxed in all 21 photos. Spice jars come back as `cup` or `bottle`, boxes as `box`, bottles as `bottle`; the label does not matter, only that a box encloses the item, which it does every time. A few photos also pick up small background objects on the counter (the blue box behind the cinnamon, appliances), which is what shelf photos will look like too. Boxed images: `docs/figures/catalog_boxes/`, contact sheet `docs/figures/catalog_boxes_sheet.jpg`.

**Identification (Qwen2.5-VL-7B, 1024 px, ~7 s each).** Asked for brand, product and size from the front photo, it read all seven correctly, down to "2.37 oz" and "66 club size pouches". Output in `results/shelf/catalog_vlm_id.json`. With a whole clean reference photo the verification stage is easy; the study's question is what happens with a shelf crop.

**Confusability (CLIP ViT-B/32 on the reference photos, cosine; 1.00 = identical).**

| | balsamic | cinnamon | flakes | snacks | olive oil | oregano | paprika |
|---|---|---|---|---|---|---|---|
| balsamic_vinegar | 1.00 | 0.69 | 0.53 | 0.61 | **0.89** | 0.63 | 0.68 |
| cinnamon | | 1.00 | 0.67 | 0.69 | 0.68 | 0.73 | **0.80** |
| frosted_flakes | | | 1.00 | 0.74 | 0.53 | 0.58 | 0.62 |
| fruit_snacks | | | | 1.00 | 0.60 | 0.60 | 0.67 |
| olive_oil | | | | | 1.00 | 0.64 | 0.70 |
| oregano | | | | | | 1.00 | 0.77 |
| paprika | | | | | | | 1.00 |

Colour histograms give the same picture (olive oil vs balsamic 0.89; the three jars 0.73 to 0.79). Only one pair is hard for the matcher: the two dark bottles. The three spice jars are moderately alike in shape and not at all in colour, and the two boxes are distinct from everything.

### What this means for the study

The set as it stands is **all Group B and C**: same-shape-different-colour items plus controls. Group A, the confusable pairs the proposal calls "the core of the study", is empty. Section 2 warns about exactly this: with these seven, detection plus CLIP will score near-perfectly, colour will look decisive, and the verification stage will rarely be tested on a plausible wrong item. The results would be real but would not answer RQ1 or RQ2.

Two ways forward, in order of preference.

**Option 1, add same-line siblings (recommended, one shopping trip).** Each current item already anchors a brand line; buying its neighbours gives Group A pairs that differ only by the printed word:

| anchor already owned | add (same brand, same container) | new item_id |
|---|---|---|
| McCormick cinnamon (red cap) | McCormick ground nutmeg, ground ginger, or allspice | `nutmeg`, `ginger` |
| Good & Gather oregano (green label) | Good & Gather basil, thyme, or parsley | `basil`, `thyme` |
| Gold Emblem paprika (orange label) | Gold Emblem chili powder or cumin | `chili_powder`, `cumin` |
| Napoleon balsamic (dark bottle) | Napoleon red wine vinegar, or any second dark-glass vinegar/oil | `red_wine_vinegar` |
| Kroger Frosted Flakes | Kroger Corn Flakes or Frosted Flakes regular size | `corn_flakes` |
| Welch's mixed fruit snacks | Welch's Berries 'n Cherries or Island Fruits | `fruit_snacks_berry` |

That is six to eight additions for a 13 to 15 item set with at least five confusable pairs, which meets the proposal's minimum. Photograph each new item the same way: three reference photos, ids in lowercase with underscores, then `make shelf-check`.

**Option 2, run a pilot with the seven now.** Valid, and a good rehearsal of the whole pipeline, but report it as a pilot: `make shelf-check` will warn that 7 is below the 15-item target, and the write-up must say that RQ1 is only tested on one hard pair (oil vs vinegar) and three moderate ones (the jars).

### Shelf photographs for seven items

The protocol in section 4 scales down cleanly. The tooling needs every item requested in at least five photos; aim for ten so per-item numbers are not noise.

- **70 photographs** (10 per item as the requested target), 4 to 7 items on the shelf at once, always with a confusable partner next to the target: the two bottles together, at least two jars together.
- Cover the grid: 3 distances × 3 lighting levels means each combination appears about 8 times across the set. Angles and the 20 % harder cases (occlusion, label turned, crowded) as in section 4.
- Rearrange between rounds. With only seven items it is very easy for position to become the cue.
- Chest height, target not centred.

Filenames use the real ids, so the tooling fills in the target itself:

```
olive_oil__d1_bright_01.jpg      balsamic_vinegar__d2_dim_03.jpg
paprika__d3_normal_02.jpg        cinnamon__d1_occluded_01.jpg
frosted_flakes__d2_angled_01.jpg fruit_snacks__d1_crowded_02.jpg
```

Drop them in `data/shelf/images/`, then:

```bash
make shelf-check            # must report no errors; the 7-item warning is expected for a pilot
make shelf-detect           # cached once, reused by every later stage
make shelf-trials           # targets come from the filenames
make viewer                 # Shelf annotator: one click per photo, ~6 minutes for 70
make shelf-search
make shelf-correct LABEL=qwen7b
make shelf-correct LABEL=qwen3b MODEL=mlx-community/Qwen2.5-VL-3B-Instruct-4bit
make shelf-report
```

`shelf-index` is already done for these seven (`results/shelf/catalog.json`); rerun it after adding items.
