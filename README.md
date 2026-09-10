# Finding and Verifying Objects for Blind and Low-Vision Users

**Active study.** Can open-vocabulary detection plus a small vision-language model find a specific household object among visually similar neighbours, and reliably tell the user when they have reached the wrong one?

Everything runs locally from a set of photographs taken at home. No cloud APIs, no fine-tuning, no wearable hardware.

| Document | What it is |
|---|---|
| `docs/PROPOSAL_RETRIEVAL.md` | The research proposal: questions, method, evaluation, limitations |
| `docs/MATERIALS.md` | What to buy, photograph, and check before running anything |
| `docs/LASTSHELF.md` | Implementation guide and schedule |
| `docs/HARDWARE.md` | Memory budget and model choices |

## Start here

```bash
make setup                    # one-time environment setup
make serve-vlm                # local model server, second terminal
make shelf-check              # validate your dataset before anything else
```

Then follow `docs/MATERIALS.md` section 8 for the run sequence. The next section explains what each stage does.

A second study on context engineering for walking guidance is **parked**, not abandoned: its code, tests and proposal remain in the repository and can be picked up later. See *Parked work* below.

---

# The Study

A compressed replication of the search and correction phases of Ruan et al. (arXiv 2601.12486), a wearable system for helping pBLV locate and retrieve products. The paper solves the **last meter**: wayfinding gets you to the aisle, not to the right jar. Their pipeline is YOLO-World detection plus embedding and colour-histogram matching to find the product, spatialized audio and VLM speech to guide the hand, and a VLM check that verifies the item actually reached.

This version keeps **search** and **correction**, drops navigation and sonification (they need a moving user), and measures everything on ~200 still shelf photographs of household items.

**What it measures**

- *Search*, as a three-arm ablation: detection only → + CLIP similarity → + colour histogram. Detector recall is reported separately so a detector miss is never charged to the matcher.
- *Correction*: the VLM verifies a crop against the requested item. Positives are the ground-truth crop; negatives are the highest-ranked wrong candidate — the item a user would plausibly grab by mistake. **False confirmations** (saying yes to the wrong item) are counted on their own, because that error is far more harmful than an unnecessary "no".
- Both phases across model sizes (3B vs 7B), to find which one breaks first as the model shrinks.

**Pipeline**

```
data/shelf/catalog/<item>/ref*.jpg ──► shelf index   ──► catalog.json  (CLIP + histograms)
data/shelf/images/*.jpg            ──► shelf detect  ──► detections.jsonl  (run once, reused)
                                       shelf trials  ──► trials.jsonl   (template)
                                       annotator     ──► trials.jsonl   (one click per image)
                                       shelf search  ──► search.jsonl   (all 3 arms, one pass)
                                       shelf correct ──► correction_<model>.jsonl
                                       shelf report  ──► report.md + summary.json
```

```bash
make serve-vlm                                   # terminal 2
make shelf-check                                 # validate the dataset first
make shelf-index
make shelf-detect
make shelf-trials                                # targets read from filenames
make viewer                                      # "Shelf annotator" page: one click per image
make shelf-search
make shelf-correct LABEL=qwen7b
make shelf-correct LABEL=qwen3b MODEL=mlx-community/Qwen2.5-VL-3B-Instruct-4bit
make shelf-report
```

`make shelf-check` runs first for a reason: it catches missing reference photos, misnamed files and thin per-item coverage in seconds, which is much cheaper than discovering them after annotation. Object selection and the capture protocol are in `docs/MATERIALS.md`; design and caveats in `docs/LASTSHELF.md`.


## Hardware feasibility

| Component | Model | Approx. memory | Runs on |
|---|---|---|---|
| VLM | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | ~5–6 GB | MLX (Metal) |
| VLM (lighter) | `mlx-community/Qwen2.5-VL-3B-Instruct-4bit` | ~2.5–3 GB | MLX (Metal) |
| Detector | `yolov8s-worldv2.pt` (YOLO-World) | ~0.3 GB | PyTorch MPS |
| Matcher | `openai/clip-vit-base-patch32` | ~0.2 GB | PyTorch MPS |
| Depth (parked study only) | `depth-anything/Depth-Anything-V2-Small-hf` | ~0.3 GB | PyTorch MPS |
| Runtime overhead | Python, PyTorch, MLX, Streamlit | ~2–3 GB | — |
| **Total** | | **~9–11 GB** | leaves ~7 GB headroom |

Only one model is resident at a time in practice: detection finishes before verification starts. Expect roughly 3–8 s per verification call on the 7B model and 1–3 s on the 3B, so ~400 verification calls take well under an hour. Details and fallbacks: `docs/HARDWARE.md`.

---

# Parked work: Context Engineering for Walking Guidance

Not part of the active study. Kept intact — code, tests, proposal (`docs/PROPOSAL_CONTEXT.md`) and schedule (`docs/WEEK_PLAN.md`) — as the natural follow-on once object retrieval is finished.

A study of whether **structured spatial context** (rolling scene memory + explicit obstacle and free-space cues) improves the navigation instructions a vision-language model (VLM) gives to a person who is blind or has low vision (pBLV), compared with naive single-frame prompting.

Everything runs locally. No cloud APIs, no fine-tuning.

---

## Research question

> Given egocentric walking video, does injecting engineered context into the VLM prompt produce instructions that are safer, more actionable, and more spatially accurate than single-frame prompting, and at what latency cost?

Four conditions run on identical frames, isolating the two context components so each one's contribution is attributable:

| Condition (`--mode`) | Frame | Sensor cues | Rolling memory |
|---|---|---|---|
| `naive` (baseline) | yes | — | — |
| `cues` | yes | yes | — |
| `memory` | yes | — | yes |
| `context` | yes | yes | yes |

Every non-naive condition shares the same BLV guide rules (≤ 2 spoken sentences, hazard first, body-relative directions, state uncertainty), so measured differences are attributable to the context rather than to instruction style.

Instructions are scored on a five-dimension BLV rubric (safety, actionability, spatial accuracy, conciseness, hallucination) by an LLM-as-judge and spot-checked by hand. See `docs/RUBRIC.md`.

## Why this matters

Recent evaluations of frontier VLMs on pBLV navigation find that the main failure modes are unreliable spatial reasoning, verbose or biased output, and poor alignment with what a blind user needs to hear. Most published work evaluates on static images; the literature explicitly calls for frame-by-frame evaluation on egocentric video from wearable devices. This project targets exactly that gap with a controlled, reproducible ablation. Full annotated bibliography: `docs/LITERATURE.md`.

## System overview

```
 egocentric video ──► frame extractor (1 fps)
                            │
                            ▼
              ┌──────────────────────────┐
              │  perception (optional)   │
              │  • Depth Anything V2 (S) │──► free-space per zone (L/C/R)
              │  • YOLO-World (S)        │──► obstacles + proximity bucket
              └──────────────────────────┘
                            │  spatial cues (text)
                            ▼
              ┌──────────────────────────┐
              │  context builder         │
              │  • BLV system prompt     │
              │  • rolling memory (N)    │
              │  • last instruction      │
              └──────────────────────────┘
                            │  prompt + image
                            ▼
              ┌──────────────────────────┐
              │  VLM  (Qwen2.5-VL 4-bit) │   served locally via mlx-vlm
              └──────────────────────────┘
                            │  instruction (≤ 2 sentences)
                            ▼
              results/<run>/records.jsonl ──► judge ──► report ──► Streamlit viewer
```

### Running the parked study

```bash
# 1. Clone and set up the backend (Python 3.11+ recommended)
git clone <your-fork-url> lvnav && cd lvnav
make setup                       # creates .venv, installs backend + frontend deps

# 2. Start the local VLM server (separate terminal; downloads ~3–6 GB on first run)
make serve-vlm                   # mlx_vlm.server on http://localhost:8080

# 3. Put an egocentric walking video in data/ and extract frames at 1 fps
make frames VIDEO=data/walk01.mp4 OUT=data/walk01

# 4. Run the conditions on the same frames
make run-all FRAMES=data/walk01          # naive, cues, memory, context
#   or individually: make run-naive / run-cues / run-memory / run-context

# 5. Score with the LLM judge and build the comparison report
make judge   RUN=results/walk01_naive
make judge   RUN=results/walk01_context
make report  A=results/walk01_naive B=results/walk01_context

# 6. Open the viewer for the presentation
make viewer
```

To smoke-test the pipeline without any models (CI mode), use `--backend mock` on every command; see `backend/README.md`.


## Repository layout

```
lvnav/
├── README.md              ← this file: repo-wide conventions and workflow
├── Makefile               ← one-line entry points for every stage
├── docs/
│   ├── PROPOSAL_RETRIEVAL.md ← active study proposal
│   ├── MATERIALS.md          ← equipment, object choice, capture protocol, checklists
│   ├── PROPOSAL_CONTEXT.md   ← parked study proposal
│   ├── LITERATURE.md      ← annotated bibliography
│   ├── RUBRIC.md          ← BLV evaluation rubric + judge prompt rationale
│   ├── HARDWARE.md        ← memory budget, model choices, fallbacks
│   ├── WEEK_PLAN.md       ← day-by-day schedule for study A
│   └── LASTSHELF.md       ← study B: design, commands, 2–3 day schedule
├── backend/
│   ├── README.md          ← backend-specific setup, CLI reference, extension points
│   ├── pyproject.toml
│   ├── configs/default.yaml
│   ├── lvnav/             ← the Python package (perception, context, vlm, eval, shelf)
│   ├── scripts/           ← thin wrappers (serve_vlm.sh)
│   └── tests/             ← pytest suite, runs with the mock backend
├── frontend/
│   ├── README.md          ← viewer-specific notes
│   ├── requirements.txt
│   ├── app.py             ← Streamlit results viewer for study A
│   └── pages/
│       └── 1_Shelf_annotator.py  ← click-to-annotate ground truth for study B
├── data/                  ← videos, frames, shelf images (git-ignored except samples/)
└── results/               ← run outputs; results/shelf/ for study B
```

## Repository conventions (repo-wide)

These rules apply across the whole repository. Changes that affect only one half live in that half's README.

- **Documentation ownership.** `README.md` (root) owns anything that spans backend and frontend: the research framing, data layout, Makefile targets, result file schemas. `backend/README.md` owns the Python package and CLI. `frontend/README.md` owns the Streamlit viewer. Update the existing file; do not create parallel READMEs.
- **Result schema is a contract.** `records.jsonl` and `judged.jsonl` are produced by the backend and consumed by the frontend. Their fields are documented in `backend/README.md` under *Output schema*; a change there requires a matching change in `frontend/app.py` and a note in this README's changelog.
- **Reproducibility.** Every run writes its resolved config into `results/<run>/config.yaml`. Model identifiers, prompt versions and sampling settings are never hard-coded outside `backend/configs/`.
- **Fix root causes.** If a dependency, model download or MPS kernel fails, fix the environment or the configuration rather than adding a workaround in code. Document the fix in `docs/HARDWARE.md` so it does not recur.
- **No hidden hardware assumptions.** Code must degrade gracefully: perception modules are optional, the VLM is behind an HTTP interface, and every stage runs with `--backend mock` for testing.
- **Style.** Python 3.11+, type hints, `ruff` for lint/format (config in `backend/pyproject.toml`). Commit messages: `<area>: <imperative summary>` where area ∈ {backend, frontend, docs, repo}.

## Output schema (summary)

Each line of `results/<run>/records.jsonl` is one frame:

```json
{"run": "walk01_context", "mode": "context", "frame_id": "000042", "frame_path": "data/walk01/000042.jpg",
 "cues": "Free space: left=near-blocked, centre=clear, right=partly blocked. Obstacles: person (centre, near), pole (right, mid).",
 "memory": "Prev 3 frames: ... Last instruction: ...",
 "instruction": "Slow down. A person is directly ahead about two steps away; stay left.",
 "latency_s": 4.21, "prompt_tokens": 1180, "completion_tokens": 27}
```

For study B, `results/shelf/` holds `catalog.json`, `detections.jsonl`, `trials.jsonl`, `search.jsonl`, `correction_<model>.jsonl`, `report.md` and `summary.json`; their fields are documented in `backend/README.md`.

`judged.jsonl` adds a `scores` object with the five rubric dimensions (1–5) and a `judge_rationale` string. `report.md` contains paired per-dimension means, latency statistics and the ten largest score deltas for qualitative inspection.

## Status and roadmap

**Parked — walking guidance**

- [x] Backend pipeline, mock backend, unit tests
- [x] Streamlit viewer
- [ ] Collect egocentric walking footage (see `docs/WEEK_PLAN.md`, Day 1)
- [ ] Run all four conditions on ≥ 300 frames
- [ ] Human spot-check of 40 frames against the judge

**Active — object retrieval**

- [x] Catalogue, detection, search ablation, correction, report, annotator
- [ ] Choose ~20 confusable household objects (`docs/MATERIALS.md` section 2)
- [ ] Photograph references and ~200 shelf images; `make shelf-check` clean
- [ ] Annotate trials
- [ ] Run search and correction at 7B and 3B
- [ ] Fill in the results tables below

### Results

_To be filled after the evaluation runs._

| Dimension | Naive | Cues | Memory | Context |
|---|---|---|---|---|
| Safety | | | | |
| Actionability | | | | |
| Spatial accuracy | | | | |
| Conciseness | | | | |
| Hallucination (↑ = fewer) | | | | |
| Median latency (s) | | | | |

#### Object retrieval

| Metric | Detection only | + CLIP | + colour |
|---|---|---|---|
| Top-1 (target found) | | | |
| End-to-end Top-1 | | | |

| Model | Correction accuracy | False confirms | Median latency |
|---|---|---|---|
| Qwen2.5-VL-7B | | | |
| Qwen2.5-VL-3B | | | |

## Changelog

- **v0.4.0** — Refocused the repository on the object-retrieval study. Added `docs/MATERIALS.md` (equipment, object selection, capture protocol, checklists), `lvnav shelf check` for dataset validation, and filename-derived targets so annotation is one decision per image. The context-engineering study is parked with its code and proposal intact.
- **v0.3.0** — Split the proposal into two standalone studies (`PROPOSAL_CONTEXT.md`, `PROPOSAL_RETRIEVAL.md`). Study A now runs four conditions (`naive`, `cues`, `memory`, `context`) so the two context components can be attributed separately.
- **v0.2.0** — Added study B (Last-Shelf): catalogue indexing, cached open-vocabulary detection, three-arm search ablation, VLM correction with hard negatives and false-confirm accounting, report generator, and a click-to-annotate Streamlit page.
- **v0.1.0** — Initial scaffold: backend package, mock-tested pipeline, judge, report generator, Streamlit viewer, documentation set.

## License

MIT. See `LICENSE`.
