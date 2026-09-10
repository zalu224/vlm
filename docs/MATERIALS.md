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
