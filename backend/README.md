# Backend: `lvnav` package

The Python package that does all the work: frame extraction, perception, context construction, VLM calls, judging and reporting. Repo-wide conventions, the research framing and the result-file contract live in the root `README.md`; this file covers the package and its CLI.

## Install

```bash
# From the repository root (creates .venv, installs backend + frontend)
make setup

# Or manually
python3 -m venv .venv && source .venv/bin/activate
pip install -e "backend[dev]"            # core + tests
pip install -e "backend[perception]"     # torch, transformers, ultralytics (needed for context mode)
pip install mlx-vlm                      # macOS only: serves the VLM
```

Python 3.11+. On Apple Silicon, `torch` wheels from PyPI include MPS support; no extra index is needed.

## Package layout

```
lvnav/
├── cli.py               lvnav <subcommand>  (extract-frames | run | judge | report | manual-sheet)
├── config.py            typed config, loaded from configs/default.yaml, saved per run
├── pipeline.py          frame → (perception) → prompt → VLM → records.jsonl
├── data/frames.py       video sampling and frame listing
├── perception/
│   ├── cues.py          model-free fusion: zones, proximity buckets, SpatialCues.to_text()
│   ├── depth.py         Depth Anything V2 wrapper (transformers, MPS)
│   ├── detector.py      YOLO-World wrapper (ultralytics, MPS)
│   ├── device.py        auto → mps | cuda | cpu
│   └── mock.py          deterministic stand-ins for tests / dry runs
├── context/
│   ├── memory.py        RollingMemory (last N cue summaries + last instruction)
│   └── prompts.py       versioned prompt templates for naive and context conditions
├── vlm/
│   ├── base.py          VLMBackend protocol, VLMResponse
│   ├── openai_compat.py OpenAI-compatible HTTP client (mlx_vlm.server, Ollama, LM Studio)
│   └── mock.py          canned instructions + canned judge JSON
└── eval/
    ├── rubric.py        five dimensions + judge prompt generated from them
    ├── judge.py         records.jsonl → judged.jsonl
    └── metrics.py       summaries, paired deltas, report.md
```

## CLI reference

All commands accept `--config <yaml>` and, where a model is involved, `--backend http|mock`, `--model`, `--base-url`.

```bash
lvnav extract-frames --video data/walk01.mp4 --out data/walk01 --fps 1 [--max-side 1024]
lvnav run   --frames data/walk01 --mode naive   [--limit 20] [--run-name walk01_naive]
lvnav run   --frames data/walk01 --mode cues     # sensor cues, no history
lvnav run   --frames data/walk01 --mode memory   # history, no sensor cues
lvnav run   --frames data/walk01 --mode context  # both
lvnav judge --run results/walk01_context
lvnav judge --run results/walk01_naive --cues-from results/walk01_context
lvnav report --a results/walk01_naive --b results/walk01_context [--out report.md]
lvnav manual-sheet --run results/walk01_context --every 8
```

`--backend mock` replaces both the VLM and the perception models with deterministic fakes. The full pipeline, judge and report run in seconds this way; it is what CI uses.

## Shelf study CLI

```bash
lvnav shelf index    --catalog data/shelf/catalog          # → results/shelf/catalog.json
lvnav shelf detect   --images  data/shelf/images [--conf 0.15] [--max-boxes 30]
lvnav shelf trials   --default-target cinnamon             # or --targets targets.json
lvnav shelf annotate                                       # terminal; the viewer page is faster
lvnav shelf search   [--text-weight 0.25]                  # all three arms in one pass
lvnav shelf correct  --label qwen7b [--model <id>] [--limit N]
lvnav shelf report                                         # → results/shelf/report.md
lvnav shelf summary                                        # → results/shelf/summary.json
```

Every shelf subcommand takes `--results` (default `results/shelf`) and `--backend http|mock`.

### Shelf output schema

`detections.jsonl` — one line per image: `{image, size: [w,h], boxes: [{box_id, label, conf, box: [x1,y1,x2,y2]}]}`. Boxes are sorted by confidence and `box_id` is the index into that sorted list, so ids are stable across every later stage.

`trials.jsonl` — `{image, target: <item_id>, gt_box: <box_id | -1 | null>, n_boxes}`. `-1` means the detector missed the item entirely; `null` means not yet annotated and is skipped by `search`.

`search.jsonl` — per trial: `{image, target, target_name, gt_box, n_candidates, detector_recall, latency_s, hard_distractor_box, variants: {<arm>: {pred_box, pred_score, top1, top3, ranking}}}`.

`correction_<label>.jsonl` — per case: `{model, image, target_name, case: positive|negative, box_id, crop_path, expected, verdict, identified_as, spoken, correct, false_confirm, latency_s, parse_error, raw}`.

### Design notes

- **Detection runs once.** All three search arms and the annotator read the same cached `detections.jsonl`. Re-running `detect` invalidates `box_id`s, so re-annotate if you change detector settings.
- **The matcher is model-free.** `matcher.py` takes plain arrays, so ranking behaviour is unit-tested without loading CLIP. Add new signals there and give them a test.
- **Negatives are free.** The hardest distractor comes out of the search ranking, so correction gets balanced positive/negative cases with no extra annotation.
- **Two error types, reported separately.** A false confirmation is the harmful failure; the prompt offers `unsure` so the model has somewhere to go besides guessing.

## The VLM server

The backend talks to any OpenAI-compatible chat endpoint. On the Mac:

```bash
make serve-vlm                                   # default: Qwen2.5-VL-7B-Instruct-4bit on :8080
make serve-vlm VLM_MODEL=mlx-community/Qwen2.5-VL-3B-Instruct-4bit
```

`vlm.base_url` in the config must end in `/v1`. The client checks `GET /v1/models` on startup and fails fast with a clear message if nothing is listening. Ollama (`ollama run qwen2.5vl:7b`, base URL `http://localhost:11434/v1`) also works but is slower than MLX on Apple Silicon.

## Output schema

`results/<run>/records.jsonl`, one object per frame:

| Field | Type | Notes |
|---|---|---|
| `run`, `mode` | str | `mode` ∈ {naive, context} |
| `frame_id`, `frame_path` | str | path relative to repo root |
| `prompt_version` | str | e.g. `naive-v1`, `context-v1` |
| `cues` | str \| null | text summary fed to the VLM (context only) |
| `cues_struct` | obj \| null | `{free_space: {zone: label}, obstacles: [...]}` |
| `memory` | str \| null | rolling memory text at this frame (context only) |
| `instruction` | str | model output |
| `latency_s` | float | wall-clock for the VLM call only |
| `prompt_tokens`, `completion_tokens` | int \| null | from the server's `usage` if provided |

`judged.jsonl` = the same rows plus `scores` (`{dimension: 1–5 | null}`), `judge_rationale`, `judge_latency_s`. `config.yaml` is the fully resolved config used for the run. Changing any of these fields is a contract change: update `frontend/app.py` and the root README.

## Prompt versions

| Version | Change |
|---|---|
| `correction-v1` | Shelf verification: yes/no/unsure verdict as JSON, with an explicit instruction that confirming a wrong item is the worst outcome. In `shelf/correction.py`. |
| `naive-v1` | Generic assistant system prompt; "tell them what to do next". |
| `cues-v1` / `memory-v1` | The same BLV guide rules with only one context component supplied, isolating each one's contribution. |
| `context-v1` | BLV guide rules (≤ 2 spoken sentences, hazard first, body-relative, no scene description, state uncertainty, don't repeat) + sensor cues + rolling memory. |

To iterate: add `BLV_SYSTEM_V2` / `CONTEXT_USER_V2` in `context/prompts.py`, extend `build_context_prompt`, set `context.prompt_version: v2` in a copied config, and add a row here. Never edit a version in place after a run has used it.

## Extending

- **New cue source** (e.g. optical flow for "approaching" objects): add a callable returning something `fuse()` can consume, or extend `SpatialCues` with a new field and its `to_text()` line. Add a unit test in `tests/test_cues.py`.
- **New backend** (e.g. a cloud API for a sanity comparison): implement `VLMBackend.generate` in `vlm/`, register it in `build_backend`.
- **New judge**: `eval/judge.py` takes any `VLMBackend`; a text-only judge just ignores the image argument.
- **New condition**: add a `Mode` literal and add it to `USES_CUES` / `USES_MEMORY` in `pipeline.py`; keep the record schema unchanged. `cues`/`memory` modes exist to attribute the two context components separately, so preserve that separation when adding more.

## Testing and lint

```bash
make test     # pytest with mock backend, < 1 s
make lint     # ruff check + format check
```

Tests cover cue fusion, memory windowing, prompt versioning, judge-output parsing, the full naive→context→judge→report path, and for the shelf study: histogram maths, each ablation arm's ranking behaviour, verdict parsing, catalogue round-tripping, and the full index→detect→trials→search→correct→report path. Model wrappers (`depth.py`, `detector.py`, `openai_compat.py`) are exercised only in real runs; keep them thin.

## Troubleshooting

See the root-cause log in `docs/HARDWARE.md`. When you fix an environment issue, add it there rather than working around it in code.
