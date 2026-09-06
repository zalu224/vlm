# Context-Engineered VLM Guidance for Low-Vision Navigation

A one-week, laptop-scale research study of whether **structured spatial context** (rolling scene memory + explicit obstacle and free-space cues) improves the navigation instructions a vision-language model (VLM) gives to a person who is blind or has low vision (pBLV), compared with naive single-frame prompting.

Everything runs locally on an Apple Silicon Mac with 18 GB of unified memory. No cloud APIs, no GPU cluster, no fine-tuning.

---

## Research question

> Given egocentric walking video, does injecting engineered context into the VLM prompt produce instructions that are safer, more actionable, and more spatially accurate than single-frame prompting, and at what latency cost?

Two conditions are compared on identical frames:

| Condition | What the VLM sees |
|---|---|
| **Naive** (baseline) | The current frame + a generic "help a blind user" prompt |
| **Context** (ours) | The current frame + a BLV-specific system prompt + free-space/obstacle cues from a depth estimator and open-vocabulary detector + a rolling summary of the last *N* frames and the last instruction given |

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

## Hardware feasibility (18 GB Apple Silicon)

| Component | Model | Approx. memory | Runs on |
|---|---|---|---|
| VLM | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | ~5–6 GB | MLX (Metal) |
| VLM (lighter) | `mlx-community/Qwen2.5-VL-3B-Instruct-4bit` | ~2.5–3 GB | MLX (Metal) |
| Depth | `depth-anything/Depth-Anything-V2-Small-hf` | ~0.3 GB | PyTorch MPS |
| Detector | `yolov8s-worldv2.pt` (YOLO-World) | ~0.3 GB | PyTorch MPS |
| Runtime overhead | Python, PyTorch, MLX, Streamlit | ~2–3 GB | — |
| **Total** | | **~9–11 GB** | leaves ~7 GB headroom |

Expected throughput on an M3 Pro-class chip: 3–8 s per frame for the 7B model, 1–3 s for the 3B model. At 1 fps sampling, a 5-minute walk (300 frames) evaluates in well under an hour per condition. Details and fallbacks: `docs/HARDWARE.md`.

## Quick start

```bash
# 1. Clone and set up the backend (Python 3.11+ recommended)
git clone <your-fork-url> lvnav && cd lvnav
make setup                       # creates .venv, installs backend + frontend deps

# 2. Start the local VLM server (separate terminal; downloads ~3–6 GB on first run)
make serve-vlm                   # mlx_vlm.server on http://localhost:8080

# 3. Put an egocentric walking video in data/ and extract frames at 1 fps
make frames VIDEO=data/walk01.mp4 OUT=data/walk01

# 4. Run both conditions on the same frames
make run-naive   FRAMES=data/walk01
make run-context FRAMES=data/walk01

# 4b. The best context arm (prompt v2, no last-instruction echo)
make run-context-v2 FRAMES=data/walk01

# 5. Score with the LLM judge and build the comparison report
make judge-v2 RUN=results/walk01_context_v2_nomem
make judge-v2 RUN=results/walk01_naive CUES_FROM=results/walk01_context_v2_nomem
make report-v2 A=results/walk01_naive B=results/walk01_context_v2_nomem
# (judge v1 on all frames: make judge RUN=... ; make report A=... B=...)

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
│   ├── PROPOSAL.md        ← 2-page research proposal (hand to the professor)
│   ├── LITERATURE.md      ← annotated bibliography
│   ├── RUBRIC.md          ← BLV evaluation rubric + judge prompt rationale
│   ├── HARDWARE.md        ← memory budget, model choices, fallbacks
│   └── WEEK_PLAN.md       ← day-by-day schedule with deliverables
├── backend/
│   ├── README.md          ← backend-specific setup, CLI reference, extension points
│   ├── pyproject.toml
│   ├── configs/default.yaml
│   ├── lvnav/             ← the Python package (perception, context, vlm, eval)
│   ├── scripts/           ← thin wrappers (serve_vlm.sh)
│   └── tests/             ← pytest suite, runs with the mock backend
├── frontend/
│   ├── README.md          ← viewer-specific notes
│   ├── requirements.txt
│   └── app.py             ← Streamlit results viewer for the presentation
├── data/                  ← videos and extracted frames (git-ignored except samples/)
└── results/               ← run outputs: records.jsonl, judged.jsonl, report.md
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

`judged.jsonl` adds a `scores` object with the five rubric dimensions (1–5), a `judge_rationale` string, the verbatim `judge_raw` output and `judge_version`. Judge-v2 subset files are named `judged_v2_every<N>.jsonl`. `report.md` contains paired per-dimension means, latency statistics and the ten largest score deltas for qualitative inspection.

## Status and roadmap

- [x] Backend pipeline, mock backend, unit tests
- [x] Streamlit viewer
- [x] Egocentric walking footage: two CC-BY POV walks, 580 frames (`docs/DATA.md`); self-recorded corridor / sidewalk / crossing walks still to add
- [x] Four arms run on all 580 frames: naive, context-v1, context-v1-nomem, context-v2-nomem
- [x] Judged with judge v1 (all frames) and judge v2 (every 4th frame); paired reports
- [ ] Human spot-check of 74 frames (`results/manual_sheet_suwon.csv`) and judge–human agreement
- [x] Results table below; full analysis in `docs/RESULTS.md`; day-by-day log in `docs/PROGRESS.md`

### Results

Judge v2, every 4th frame of both walks, paired per frame, n = 144. Δ is context-v2-nomem minus naive; 95 % confidence intervals in `docs/RESULTS.md`.

| Dimension | Naive | Context (v2, no echo) | Δ |
|---|---|---|---|
| Safety | 1.76 | 2.37 | +0.60 |
| Actionability | 2.95 | 3.61 | +0.66 |
| Spatial accuracy | 2.45 | 2.97 | +0.53 |
| Conciseness | 2.57 | 3.86 | +1.28 |
| Hallucination (↑ = fewer) | 2.60 | 4.09 | +1.48 |
| Median VLM latency (s), all frames | 4.9 | 4.7 | −0.2 |
| Words per instruction | 65 | 9 | |

Two things the week turned up that were not in the proposal: the pre-registered context prompt collapsed into one repeated sentence because the rolling memory echoed the model's own last instruction (removing that one line fixes it), and the 7B model used as judge produced halo-effect scores until the judge prompt demanded a reason before each score. Both are documented in `docs/RESULTS.md`.

## Changelog

- **v0.2.0** (2026-09-06) — First full results. Free-space cue now scored on an approach band (ground plane excluded). Context prompt v2 and `include_last_instruction: false` ablation configs. Judge v2 (per-dimension reasons), `--judge-version`, `--every`, `--judged-name`; `judged.jsonl` gains `judge_raw` and `judge_version`; reports gain repetition and computed-conciseness rows. Blinded `manual-sheet` and `agreement` commands. Docs: `PROGRESS.md`, `DATA.md`, `RESULTS.md`.
- **v0.1.0** — Initial scaffold: backend package, mock-tested pipeline, judge, report generator, Streamlit viewer, documentation set.

## License

MIT. See `LICENSE`.
