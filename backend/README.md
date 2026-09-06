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
lvnav run   --frames data/walk01 --mode context [--limit 20]
lvnav judge --run results/walk01_context
lvnav judge --run results/walk01_naive --cues-from results/walk01_context
lvnav report --a results/walk01_naive --b results/walk01_context [--out report.md]
lvnav manual-sheet --run results/walk01_context --every 8
```

`--backend mock` replaces both the VLM and the perception models with deterministic fakes. The full pipeline, judge and report run in seconds this way; it is what CI uses.

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
| `naive-v1` | Generic assistant system prompt; "tell them what to do next". |
| `context-v1` | BLV guide rules (≤ 2 spoken sentences, hazard first, body-relative, no scene description, state uncertainty, don't repeat) + sensor cues + rolling memory. |
| `context-v2` | Day-4 iteration after reading v1 outputs (see `docs/PROGRESS.md`). Adds an explicit cue → action decision rule (STOP / SLOW DOWN / CONTINUE), removes example phrases that v1 copied verbatim, tells the model to check the image for hazards the cues miss, and reframes memory as "what you already said". Config: `configs/context_v2.yaml`. |
| `context-v1` + `include_last_instruction: false` | Ablation arm, same prompt as v1 with the last instruction dropped from memory. Config: `configs/context_v1_nomem.yaml`. |

To iterate: add `BLV_SYSTEM_V2` / `CONTEXT_USER_V2` in `context/prompts.py`, extend `build_context_prompt`, set `context.prompt_version: v2` in a copied config, and add a row here. Never edit a version in place after a run has used it.

## Extending

- **New cue source** (e.g. optical flow for "approaching" objects): add a callable returning something `fuse()` can consume, or extend `SpatialCues` with a new field and its `to_text()` line. Add a unit test in `tests/test_cues.py`.
- **New backend** (e.g. a cloud API for a sanity comparison): implement `VLMBackend.generate` in `vlm/`, register it in `build_backend`.
- **New judge**: `eval/judge.py` takes any `VLMBackend`; a text-only judge just ignores the image argument.
- **New condition**: add a `Mode` literal and branch in `pipeline.run_pipeline`; keep the record schema unchanged.

## Testing and lint

```bash
make test     # pytest with mock backend, < 1 s
make lint     # ruff check + format check
```

Tests cover cue fusion, memory windowing, prompt versioning, judge-output parsing, and the full naive→context→judge→report path. Model wrappers (`depth.py`, `detector.py`, `openai_compat.py`) are exercised only in real runs; keep them thin.

## Troubleshooting

See the root-cause log in `docs/HARDWARE.md`. When you fix an environment issue, add it there rather than working around it in code.
