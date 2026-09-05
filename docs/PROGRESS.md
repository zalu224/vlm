# Progress Log

Running record of what has been done, decided, and blocked. Newest entry at the bottom of each day. Numbers that end up in the write-up are copied here first so they have a provenance trail.

Conventions: one entry per milestone; decisions get a **Decision:** line with the reason; anything that needs Aaron's action is under **Needs Aaron**.

---

## Day 1 — 2026-09-05 (Fri): environment, data, plan

### State on arrival
- Scaffold v0.1.0 arrived as `lvnav.zip` with its own single-commit git history. Nothing had been run: no venv, no models, no footage.
- Machine: Apple M3 Pro, 18 GB unified memory, macOS 26.4.1. Python 3.11 and 3.13, uv, ffmpeg, Ollama present. No torch/mlx/transformers installed.
- Disk was the surprise: only 19 GB free before setup, 16 GB after installing the stack. Model download (5.65 GB) fits; raw video must stay short and be deleted after frame extraction.

### Done
- **Repo flattened.** `lvnav/` contents and `.git` moved to `/Users/aaronlu/vlmproj`; duplicate top-level `PROPOSAL.md`/`README.md` (byte-identical to `docs/PROPOSAL.md` and `README.md`) and the zip deleted. `vlmproj` is now the project repo (it sits inside a larger git repo rooted at `~`; that outer repo just sees this as an untracked nested repo).
- **Environment.** `uv venv --python 3.11 .venv`; installed `backend[dev,perception]`, `frontend/requirements.txt`, `mlx-vlm 0.6.17`, `huggingface_hub`, `datasets`, `yt-dlp`. Versions: torch 2.14.0 (MPS available), transformers 5.16.1, ultralytics 8.4.141.
- **Tests + lint pass** on the mock backend: 9 passed, ruff clean.
- **Server route check.** `mlx_vlm.server` exposes `/v1/models` and `/health`, so the client's startup health check works unchanged. CLI flags `--model` and `--port` match the Makefile.
- **Papers verified.** All four core arXiv IDs in `docs/LITERATURE.md` resolve to real papers with the stated titles (2510.00766, 2603.15624, 2606.04111, 2503.12844). Summaries in `docs/LITERATURE.md` are accurate.
- **7B model download started** in the background (`logs/download_7b.log`), 5.65 GB.
- **Public footage.** Two CC-BY POV walking videos downloading at ≤1080p video-only (`logs/dl_*.log`); provenance in `docs/DATA.md`.

### Decisions
- **Decision:** data = Aaron's own recordings + public bootstrap. Public data lets the full pipeline run today; the indoor corridor walk only comes from Aaron's recording (no CC indoor POV footage found).
- **Decision:** judge = local Qwen2.5-VL, same as generator, per the proposal's no-external-API constraint. Self-preference risk is bounded by the Day-5 human spot-check.
- **Decision:** start with the 7B model, per `docs/HARDWARE.md` decision rule; drop to 3B only if median latency > 8 s or memory pressure.
- **Decision:** GuideDog (HF `kjunh/GuideDog`) is **gated**, needs an HF login and terms acceptance. It is static images with no frame ordering, so it cannot exercise rolling memory. Plan: use its gold split (2,106 human-verified image + guidance pairs) as a *secondary* static-image check once access is granted; primary evaluation stays on video frames.

### Needs Aaron
- [ ] Record 3 walks at chest height, 2–4 min each, 1080p, phone in landscape: (1) indoor corridor, (2) sidewalk with pedestrians, (3) a street crossing. Drop them in `data/raw/`. No faces need to be kept; frames are extracted at 1 fps and the raw video can be deleted.
- [ ] Optional: `hf auth login` in the venv and accept the GuideDog terms at https://huggingface.co/datasets/kjunh/GuideDog to enable the static-image check.

### Open questions / risks
- YouTube walking tours are shot at head height with a stabilised camera and mostly look ahead at the sidewalk; that is close to but not identical to a chest-mounted BLV wearable. Note this in the write-up's limitations.
- Dataset licence: both videos are "Creative Commons Attribution (reuse allowed)". Attribution goes in `docs/DATA.md` and the write-up.

### Day 1, later: perception calibrated, VLM live, first runs launched

- **Frames extracted** at 1 fps, ≤1024 px long side: `data/suwon` 295 frames, `data/london` 285 frames (580 total, ≥300 target met). Raw video kept in `data/raw/` for now (207 MB).
- **Mock pipeline on real frames** (`--limit 10`, both conditions, judge, report): passes. Day-1 artefact done.
- **Root-cause fix:** YOLO-World needed the `clip` package; see `docs/HARDWARE.md`. Pinned in `pyproject.toml`.
- **Perception timing on MPS:** first call ~5 s (kernel warm-up), then **0.12–0.15 s per frame** for depth + detector together.
- **Free-space bug found and fixed.** With the scaffold's rule (90th-percentile closeness over the whole lower half) every zone read *blocked* on 5 of 6 frames, including open road. Depth heatmaps showed why: the ground at the user's feet is the closest surface in every egocentric frame and dominates the percentile. Measured closeness on clear sidewalk: 0.2–0.4 through 80 % of the height, spiking to 0.9+ only in the bottom 10 %. **Decision:** score an *approach band* (rows 50–80 %) instead, thresholds blocked ≥ 0.80, partly ≥ 0.55. Validated on a 12-frame contact sheet spanning both walks: open street → clear, shopper at arm's length on the left → left blocked, bike rack near right → right blocked, plaza with people at ~5–10 m → partly blocked. Three new unit tests with a ground-ramp fixture that matches the measured profile.
- **VLM server:** `mlx_vlm.server` with Qwen2.5-VL-7B-Instruct-4bit on :8080. `/v1/models` present. One frame + naive prompt: 12.6 s cold, **5.0 s warm** (448 prompt tokens, 80 completion). Well under the 8 s decision threshold, so 7B stays.
- **Naive baseline already shows the expected failure mode:** verbose third-person paragraphs ("The person wearing the camera should proceed cautiously... listen for any sounds...") that hit the 80-token cap mid-sentence. Mean 72 words per instruction on the first 29 frames, median latency 4.97 s.
- **Launched** (background, `logs/run_naive.log` then `logs/run_chain.log`): naive on both walks → context on both walks → judge all four (naive judged with `--cues-from` the matching context run) → two reports. Estimated 3–4 h total. Cue code at commit after this entry.
- Disk after all downloads: 8.8 GB free.
- **Judge pre-check** (one naive record, live 7B, cues borrowed from the smoke context run): returns well-formed JSON, parses to all five scores. 17 s while sharing the GPU with the naive run; expect ~8–10 s standalone, so the four judge passes are ~3 h. Observation: it scored a 72-word, mid-sentence-truncated paragraph **3/5 on conciseness**, which is lenient. Watch this dimension in the Day-5 human agreement check.
- **Viewer pre-check:** `streamlit run frontend/app.py` serves (HTTP 200) on the smoke results.

### Notes for the write-up
- London frames carry a burned-in timecode overlay (top-left); the VLM may read it. Mention as a data artefact.
- Judge and generator share one server; perception (torch/MPS) and the VLM (MLX/Metal) share the GPU during context runs, so context latency includes some contention. Report perception time separately from VLM time (both are in `records.jsonl`: `latency_s` is VLM only).
