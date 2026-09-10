# Last-Shelf: fast technical evaluation of item retrieval

A compressed replication of the **search** and **correction** phases of Ruan et al., *A Multimodal Assistive System for Product Localization and Retrieval for People who are Blind or have Low Vision* (arXiv 2601.12486). Sonification and human trials are deliberately out of scope: everything here is measured on a fixed set of roughly 200 shelf photographs, so the whole study runs offline on one laptop.

## What the original does, and what this keeps

| Paper phase | Original | Here |
|---|---|---|
| Product search | YOLO-World detection + embedding similarity + colour-histogram matching | Kept, and split into three ablation arms so each signal's contribution is measured |
| Product navigation | Spatialized sonification + VLM verbal guidance | **Dropped.** Requires a moving user; not measurable on still images |
| Product correction | VLM verifies the reached item, gives corrective feedback | Kept, with positives and hard negatives, and a false-confirmation rate |

The paper reports detection near-perfect at close range, VLM navigation up to 94.4%, and correction above 86% under their best configuration. Those numbers came from their hardware, their models and a store setting; nothing here is directly comparable to them. What this study produces is the *shape* of the same result on household items with a small local VLM.

## The question this version answers

> On household shelves, how far can the model be shrunk before the retrieval loop stops working — and which phase breaks first?

Working hypothesis: search degrades gracefully, because the geometry comes from the detector and CLIP does the discrimination, while **correction degrades sharply**, because verifying "is this cinnamon or smoked paprika" needs label-reading at a resolution small VLMs handle poorly. If that holds, the finding is that the last-meter bottleneck is fine-grained visual discrimination rather than spatial reasoning, which is directly relevant to whether a wearable can run on-device.

## Study design

**Items.** ~20 household items, chosen adversarially: at least three same-brand different-flavour pairs (two soup cans, two cereal boxes), a spice rack where jars differ only by label, and a few visually distinctive items as controls. Adversarial pairs are the point; a pantry of obviously different objects makes every method look good.

**Images.** ~200 shelf photographs: vary distance (roughly 0.5 / 1.0 / 1.5 m to mirror the paper's distance analysis), lighting (daylight, overhead, dim), angle, and occlusion. Phone camera is fine. One requested target per image gives 200 trials.

**Catalogue.** Two or three reference photos per item, item filling the frame. Averaging reference views is what makes matching robust to shelf pose.

**Ablation arms.**

| Arm | Signals | What it tells you |
|---|---|---|
| `det` | detector confidence only | How far detection alone gets with no idea which item was requested — the floor |
| `embed` | + CLIP similarity to reference photos and item name | The main contribution of visual matching |
| `embed+color` | + HSV histogram intersection | Whether colour still adds anything on top of CLIP |

**Correction cases.** Generated automatically from the annotation, so they cost nothing extra:
- *Positive* — the ground-truth crop. Expected verdict: yes.
- *Negative* — the highest-ranked wrong candidate, i.e. the item a user would most plausibly grab by mistake. Expected verdict: no.

**Metrics.**
- Detector recall (was the target enclosed by any proposed box) — reported separately, so detector misses are never charged to the matcher.
- Top-1 and top-3 per arm, plus end-to-end top-1 over all trials.
- Correction accuracy, confirm rate on positives, **false-confirm rate on negatives**, unsure rate, parse-error count, median latency.
- The two error types are not symmetric: confirming the wrong item to a blind user is much worse than an unnecessary "no", so false confirms are reported on their own and the prompt offers an explicit `unsure` option.

## Running it

```bash
# 0. One-time: local VLM server in a second terminal
make serve-vlm                                      # Qwen2.5-VL-7B-Instruct-4bit

# 1. Reference catalogue -> embeddings + histograms  (seconds)
lvnav shelf index  --catalog data/shelf/catalog

# 2. Detection over every shelf image, cached once   (~2-5 min for 200 images)
lvnav shelf detect --images  data/shelf/images

# 3. Annotation template, then click through it      (~20-30 min, the only manual step)
lvnav shelf trials --default-target cinnamon        # or --targets targets.json
make viewer                                          # open "Shelf annotator" in the sidebar
#   ...or in the terminal:  lvnav shelf annotate

# 4. Search, all three arms in one pass              (~3-8 min)
lvnav shelf search

# 5. Correction, once per model you want to compare  (~15-40 min each)
lvnav shelf correct --label qwen7b
lvnav shelf correct --label qwen3b --model mlx-community/Qwen2.5-VL-3B-Instruct-4bit

# 6. Report + machine-readable metrics
lvnav shelf report
lvnav shelf summary
```

Add `--backend mock` to any command to exercise the pipeline with no models at all.

## Two-to-three day schedule

| Day | Work | Output |
|---|---|---|
| **1 (morning)** | Pick 20 items, shoot 2–3 reference photos each, shoot ~200 shelf images across distances and lighting | `data/shelf/` populated |
| **1 (afternoon)** | `index`, `detect`, `trials`, then annotate in the viewer | `trials.jsonl` complete |
| **2 (morning)** | `search`, read the three-arm table, inspect ranking failures; tune `--text-weight` or detector `--conf` **once** and rerun if detector recall is under ~85% | `search.jsonl`, first numbers |
| **2 (afternoon)** | `correct` with 7B, then 3B | two `correction_*.jsonl` |
| **3** | `report`, `summary`, write up, assemble figures from the failure cases | `report.md` + write-up |

## Reporting honestly

- State plainly that this is not a reproduction of the paper's numbers: different items, different hardware, different models, no user study.
- Report detector recall before ranking accuracy. A top-1 number computed only over found targets looks much better than the end-to-end number, and both belong in the table.
- The catalogue reference photos are clean and frontal while shelf crops are not; that gap is a limitation, not a result.
- With ~200 trials, a difference of a few percentage points between arms is noise. Say so rather than ranking arms that are within a couple of points of each other.
