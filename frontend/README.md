# Frontend: results viewer

A single-file Streamlit app for stepping through frames and comparing the naive and context conditions side by side. It is the artefact you open during the presentation.

Repo-wide conventions and the result-file schema it depends on are in the root `README.md`. This file covers only the viewer.

## Run

```bash
# from the repository root, after `make setup`
make viewer            # or: .venv/bin/streamlit run frontend/app.py
```

The app scans `results/` for any directory containing `records.jsonl`. If `judged.jsonl` exists it also shows rubric scores and the summary chart; if `report.md` exists it is embedded in an expander.

## What it shows

1. **Header summary** (only when both runs are judged): a bar chart of the five rubric means and a small table of median latency and instruction length.
2. **Frame stepper**: Previous / Next buttons and a slider over the frames both runs share.
3. **Left column**: the frame image, the sensor cues the context condition received, and the rolling scene memory.
4. **Right column**: both instructions rendered as spoken-guidance blocks, with latency, token count, per-dimension score pills and the judge's one-line rationale.

## Design notes

- The two conditions use two restrained accent colours (teal for context, clay for naive) so they are distinguishable at a glance from the back of a room; everything else is neutral.
- Instructions are set large because they are the whole point; cues and memory are monospace and small because they are evidence, not the result.
- No model is ever loaded here. The viewer is safe to open while a run is still in progress (files are read on each rerun; use the sidebar to switch runs).

## Changing the viewer

- If the backend adds a field to `records.jsonl` / `judged.jsonl`, add its rendering here and document it in the root README's *Output schema* section.
- Keep the app dependency-light (`streamlit`, `pandas`, `pillow`). Do not import `lvnav` from the frontend; the viewer must work with results copied from another machine.
- Frame paths in the JSONL are relative to the repository root; `resolve_frame()` handles that. If you move `data/`, re-run the pipeline rather than patching paths.
