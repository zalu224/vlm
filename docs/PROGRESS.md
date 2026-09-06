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

### Memory pressure during the naive run (19:10)
- macOS reported low memory and killed a background wait shell. Swap in use: 30 GB of 37 GB. The VLM server's 6 GB footprint was ~98 % *compressed* (paged out): the model weights were being swapped while other apps (Cursor helpers, two node processes, opencode, several Claude sessions, >10 GB together) held physical memory.
- Effect on data: naive latency was a flat **5.0 s median through frame 119**, then degraded to 6.2–6.7 s medians with spikes to 49 s from frame ~120 on (also the window in which I ran the perception contact sheet, the judge pre-check and the viewer alongside the server).
- **Decision:** the full 580-frame runs are used for *quality* (H1, H2) only. **H3 latency is re-measured on a 50-frame subset per condition in a quiet state** (no other GPU/memory load, other apps closed), reported separately with the machine state noted. Records keep per-frame `latency_s` either way, so the contaminated window can be shown, not hidden.
- Kept the 7B model: the pressure is external, not the pipeline's own budget (docs/HARDWARE.md decision rule assumes a quiet machine).

### Needs Aaron (added 19:15)
- [ ] While the chain runs (next ~4–5 h), closing Cursor / opencode / stray node processes will stop the model weights from being paged out. Otherwise the run still completes, just slower.

### Notes for the write-up
- London frames carry a burned-in timecode overlay (top-left); the VLM may read it. Mention as a data artefact.
- Judge and generator share one server; perception (torch/MPS) and the VLM (MLX/Metal) share the GPU during context runs, so context latency includes some contention. Report perception time separately from VLM time (both are in `records.jsonl`: `latency_s` is VLM only).

---

## Day 1, evening (still 2026-09-05): context runs done, first paired reading

### Numbers (generation only; judging still running)

| Run | n | median VLM latency | p90 | mean words | hit 80-token cap | unique instructions |
|---|---|---|---|---|---|---|
| suwon_naive | 295 | 4.93 s | 5.89 s | 66.0 | 226 (77 %) | — |
| london_naive | 285 | 4.84 s | 5.98 s | 63.3 | 137 (48 %) | — |
| suwon_context | 295 | 4.14 s | 4.29 s | 8.0 | 0 | **26** |
| london_context | 285 | 4.26 s | 4.39 s | 9.9 | 0 | **41** |

Context is *faster* than naive despite ~700 extra prompt tokens, because it emits ~8 words instead of 80 tokens; decoding dominates. (Latency caveat from the memory-pressure note still applies; these medians are consistent with the quiet-state 5.0 s baseline.)

### Reading 21 paired outputs (every ~30th frame of both walks)

**Naive (v1)** behaves as the literature predicts: third-person ("The person wearing the camera should..."), scene description, numbered lists, hallucinated aids (tactile paving, white cane) and occasional nonsense (london/000280: "choose two stations you would like to see"). But it sometimes *reads the scene* usefully: london/000130 it read a "Road Ahead Closed" sign and a diversion arrow.

**Context (v1)** is concise (2 sentences, ~8 words) and mostly spatially grounded, but shows three failure modes that v1's rules did not prevent:

1. **Mode collapse via memory feedback.** With temperature 0 and the last instruction in the prompt, the model repeats itself: "Two steps ahead, there's a person. Move forward." appears on 103/295 Suwon frames regardless of cues. Rule 7 ("do not repeat unless unchanged") was ignored.
2. **No safety verbs.** "stop" and "slow" occur in **0 %** of context instructions on both walks, even for `person (centre, near)` or all three zones blocked. Everything ends in "Move forward." The prompt asks for hazard-first but gives no decision rule linking cue → action.
3. **Prompt-example leakage and cue parroting.** Example phrases from the system prompt ("two steps ahead", "at knee height") are copied verbatim: london/000000 "a traffic light is at knee height". Cue wording is echoed with broken semantics: "The car ahead is partly blocked", "A person is partly blocked directly ahead".
4. **Cue anchoring overrides the image.** london/000130: cues say centre clear → "The road ahead is clear" while the image shows a road-closed barrier that the naive condition noticed. This is the regression class H2 needs to watch (detector vocabulary has no "barrier"/"sign" that fired here).

**Decision:** keep `context-v1` as the pre-registered condition and report it as is. Add `context-v2` (Day-4 prompt iteration per WEEK_PLAN): explicit cue → action decision rule (stop / slow / veer / continue), output format instead of example phrases, an instruction to check the image for hazards the cues miss, and memory kept but with an anti-repetition instruction that names the previous instruction as "already said". Also add a config-only ablation arm `context-v1` with `include_last_instruction: false` to test whether memory feedback alone causes the collapse. Report adds a repetition metric (unique-instruction ratio, share of the most common instruction) so this is measured, not anecdotal.

### Day-4 prompt iteration, done early (12-frame trials, every 25th frame of each walk)

| Arm | Suwon unique /12 | London unique /12 | Safety verbs | Notes |
|---|---|---|---|---|
| context-v1 (full run, same frames) | 3 | 6 | none | "Two steps ahead, there's a person. Move forward." |
| context-v1, no last-instruction echo | 12 | 11 | "move slowly", "step cautiously", "keep left" | diverse, sometimes garbled ("aheadft"); one degenerate output on frame 0 |
| context-v2, with echo | 4 | 5 | none | worse than v1; decision rule ignored |
| **context-v2, no echo** | **11** | **11** | "STOP", "slow down and keep to the left/right" | follows the decision rule; some cue parroting ("The centre is partly blocked") remains |

**Finding:** the repetition collapse is caused by feeding the model its own last instruction at temperature 0, not by the prompt wording. With the echo removed, both prompts diversify; v2's decision rule then takes effect (STOP for a bus directly ahead, slow-and-keep-to-a-side for a partly blocked centre), whereas with the echo v2 is *worse* than v1. Trial records: `results/trial_*`.

**Decision:** four arms go into the write-up: naive, context-v1 (pre-registered), context-v1-nomem (isolates the memory feedback), context-v2-nomem (Day-4 candidate). Config `backend/configs/context_v2_nomem.yaml`. Full runs + judging queued behind the current chain (`logs/run_chain2.sh`, ~2.5 h after chain 1 ends). Rolling *cue* memory (last 3 frames) stays on in every context arm; only the echoed instruction is removed.
