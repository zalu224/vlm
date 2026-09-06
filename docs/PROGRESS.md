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

---

## Day 1, night (23:10): first judged results — and the judge is the problem

### Judge v1 results (Qwen2.5-VL-7B, same model as generator)

| | Suwon naive | Suwon context-v1 | London naive | London context-v1 |
|---|---|---|---|---|
| safety | 2.75 | 1.42 | 3.15 | 2.27 |
| actionability | 3.24 | 2.14 | 3.89 | 2.87 |
| spatial accuracy | 2.74 | 1.69 | 3.13 | 2.36 |
| conciseness | 2.61 | **2.01** | 2.93 | **2.54** |
| hallucination | 4.52 | 3.09 | 4.86 | 4.12 |
| overall | 3.17 | 2.07 | 3.59 | 2.83 |
| B better / worse / tied | | 69 / 176 / 39 | | 69 / 156 / 60 |
| unique instructions / frames | 0.97 | 0.09 | 0.97 | 0.14 |
| parse errors | 0 | 11 | 0 | 0 |

Taken at face value: the pre-registered context-v1 **loses on every dimension**. Safety and hallucination losses are plausible (the collapsed "Two steps ahead, there's a person. Move forward." is wrong on most frames). But an 8-word instruction scoring **lower on conciseness** than a 66-word paragraph cut off mid-sentence cannot be right.

### Judge diagnosis
- **Halo effect.** On 49 % of Suwon context frames all five scores are identical (13 % naive). The same instruction on 103 frames got conciseness 1 on 76 of them, 3 on 14, 5 on 1. The judge forms one opinion and writes it into every box.
- **Rationale–score mismatch.** Rationales say "the instruction is not concise" about eight words, and naive gets hallucination 5 while the rationale notes "a person in traditional attire, which is not visible in the image".
- **Length bias.** Naive paragraphs sit at a uniform 3/3/3/3/5.
- Raw judge text was not saved, so the 11 parse errors cannot be inspected; fixed (`judge_raw` field, schema note in backend README).

This is exactly the failure the VL-Guide paper (2510.00766) reports for generic VLM judges on BLV tasks, reproduced on a 7B open model. It is a result in itself for the write-up.

### Decisions
- **Judge v2** (`judge.version: v2`, `eval/rubric.py`): a one-sentence *reason before each score*, an explicit statement that dimensions are independent, and length-based anchors for conciseness. Parser accepts both shapes. `lvnav judge --every 8 --judge-version v2` scores a stratified subset so v1 and v2 can be compared cheaply and the same frames feed the human spot-check.
- **Computed conciseness** (`conciseness_auto`, model-free, rubric scale) added to every report as an objective anchor for that dimension.
- Next: re-judge every 8th frame of `suwon_naive` and `suwon_context` with v2; if uniform-vector rate stays > 30 % or conciseness still tracks correctness, the local judge is the bottleneck and the Claude-judge option goes back to Aaron with this evidence.
- Judge v1 numbers stay in the repo and the write-up as the pre-registered evaluator; v2 is reported as the corrected one, with judge–human agreement for both.

### Judge v2 first look (23:40; 16 Suwon context frames, every 8th, before the job was killed by memory pressure)

| | v1 | v2 |
|---|---|---|
| uniform score vectors | 16/16 | **0/16** |
| conciseness mean (8-word instruction) | 1.27 | **3.94** |
| safety mean | 1.13 | 1.00 |
| hallucination mean | 2.07 | 3.44 |
| judge latency (GPU shared with chain2) | ~8 s | ~42 s |

Reasons now match scores ("directs the pedestrian into the path of a person" → safety 1; "concise, one sentence" → conciseness 4). The halo is gone and the safety verdict on the collapsed v1 instruction is still 1, which is the correct outcome. **v2 is the evaluator for the write-up; v1 stays reported as the pre-registered one.**

Cost: ~5× v1 output tokens. Plan: judge v2 on **every 4th frame** of all eight runs (4 arms × 2 walks ≈ 580 calls, ~3 h quiet) after chain2; the every-8th subset of that is the human spot-check set. Do not run anything else on the GPU meanwhile: swap hit 16.5/17.4 GB and macOS killed the first v2 job at frame 16.

---

## Day 2 — 2026-09-06 (Sat), 00:45: all four arms generated

Generation-only statistics (no judge involved). `uniq` = unique instructions / frames; `top` = share of the most common instruction; verb columns = share of instructions containing the word; `concA` = computed conciseness (1–5).

| Run | n | median VLM s | words | uniq | top | stop | slow | left/right | concA |
|---|---|---|---|---|---|---|---|---|---|
| suwon_naive | 295 | 4.93 | 66.0 | 0.97 | 0.01 | 0.09 | 0.00 | 0.07 | 1.23 |
| suwon_context (v1) | 295 | 4.14 | 8.0 | 0.09 | 0.35 | 0.00 | 0.00 | 0.12 | 5.00 |
| suwon_context_v1_nomem | 295 | 4.18 | 8.6 | 0.62 | 0.08 | 0.01 | 0.11 | 0.22 | 4.84 |
| suwon_context_v2_nomem | 295 | 4.66 | 8.5 | 0.40 | 0.08 | **0.20** | 0.11 | **0.45** | 4.93 |
| london_naive | 285 | 4.84 | 63.3 | 0.96 | 0.01 | 0.16 | 0.00 | 0.17 | 1.61 |
| london_context (v1) | 285 | 4.26 | 9.9 | 0.14 | 0.17 | 0.00 | 0.00 | 0.48 | 5.00 |
| london_context_v1_nomem | 285 | 4.16 | 8.9 | 0.47 | 0.06 | 0.00 | 0.08 | 0.19 | 4.99 |
| london_context_v2_nomem | 285 | 4.75 | 9.9 | 0.47 | 0.06 | 0.07 | **0.21** | **0.69** | 4.89 |

Reading: removing the echo lifts unique-instruction ratio from ~0.1 to ~0.5 at the same length; the v2 decision rule then adds the safety verbs (Suwon: "stop" in 20 % of frames vs 0 % for v1) and side-relative directions (45–69 % vs 12–48 %). The most common v2-nomem outputs are exactly the rule's three branches ("STOP. There's a person directly ahead." ×25; "The centre is partly blocked. Slow down and keep to the right." ×14; "Continue. There's a person ahead and to the right." ×13), which is the intended behaviour at temperature 0, not collapse. Residual cue parroting ("The centre is partly blocked") is the next prompt-iteration target, not for this week.

Latency: all context arms 4.1–4.8 s median vs 4.9 s naive; H3 (< 40 % overhead) holds with margin on VLM time alone, and perception adds ~0.15 s. Still to be re-measured on a quiet machine.

### 03:15: judge v1 on all four arms (pre-registered evaluator, full frames)

| Run | safety | action. | spatial | concise | halluc. | overall | uniform vectors | wins / losses vs naive |
|---|---|---|---|---|---|---|---|---|
| suwon_naive | 2.75 | 3.24 | 2.74 | 2.61 | 4.52 | 3.17 | 0.13 | |
| suwon_context (v1) | 1.42 | 2.14 | 1.69 | 2.01 | 3.08 | 2.07 | 0.49 | 69 / 176 |
| suwon_context_v1_nomem | 2.00 | 2.62 | 2.17 | 2.35 | 3.62 | 2.55 | 0.32 | 101 / 139 |
| suwon_context_v2_nomem | 2.99 | 3.54 | 3.03 | 3.11 | 3.56 | **3.25** | 0.14 | **142 / 85** |
| london_naive | 3.15 | 3.89 | 3.13 | 2.93 | 4.86 | 3.59 | 0.04 | |
| london_context (v1) | 2.27 | 2.87 | 2.36 | 2.54 | 4.12 | 2.83 | 0.08 | 69 / 156 |
| london_context_v1_nomem | 2.08 | 2.90 | 2.32 | 2.59 | 4.17 | 2.81 | 0.11 | 67 / 159 |
| london_context_v2_nomem | 3.05 | 3.78 | 3.06 | 3.21 | 4.26 | 3.47 | 0.02 | 110 / 102 |

Even under the biased v1 judge, **v2-nomem beats naive on Suwon** (142 wins vs 85 losses) and is level on London (110 vs 102). The v1-judge conciseness column still tracks correctness rather than length (v2-nomem 3.1 vs naive 2.6–2.9 for 8 vs 65 words), so per-dimension claims wait for judge v2 (chain3 started 03:13). Hallucination under v1 is the one dimension where every context arm trails naive; check whether v2 keeps that, since v1 gave naive paragraphs a reflexive 5.

### 04:10: judge v2, Suwon, every 4th frame (74 frames per arm)

| Run | safety | action. | spatial | concise | halluc. | overall | uniform | wins / losses vs naive |
|---|---|---|---|---|---|---|---|---|
| suwon_naive | 1.60 | 2.63 | 2.15 | 2.49 | 2.51 | 2.28 | 0.10 | |
| suwon_context (v1) | 1.22 | 3.03 | 1.84 | 3.88 | 3.97 | 2.79 | 0.00 | 51 / 15 |
| suwon_context_v1_nomem | 1.51 | 2.99 | 2.22 | 3.68 | 3.97 | 2.87 | 0.01 | 49 / 22 |
| suwon_context_v2_nomem | **2.41** | **3.53** | **2.97** | 3.84 | **4.03** | **3.35** | 0.05 | **58 / 11** |

Δ (v2-nomem − naive): safety +0.81, actionability +0.90, spatial +0.82, conciseness +1.35, hallucination +1.52. Judge latency 10–11 s (machine quiet overnight). 1 parse failure in 296.

- **The v1 verdict flips under v2.** v1 had every context arm losing to naive; v2 has every context arm winning. The difference is the halo: v1 wrote its overall dislike of the collapsed instruction into conciseness and hallucination.
- **Naive hallucinates more than v1 said** (2.51 vs 4.52): v2 catches invented white canes, tactile paving, crosswalks, stop signs that the naive prompt elicits. H2 holds under v2.
- **H1 nuance:** the largest gains are on hallucination and conciseness, not spatial accuracy as predicted (spatial +0.82 is mid-pack). Report as is.
- **Judge v2 quirk to note:** it sometimes scores an *omission* as hallucination ("does not mention the bus" → hallucination 3). Dimension definition should say unsupported mentions only; v3 candidate, not this week.
- Pre-registered context-v1 wins on v2 too (51/15) but only via conciseness and hallucination; its safety (1.22) is *below* naive because "Move forward" into a near person is scored 1. Honest result: the v1 prompt made things shorter, not safer; the echo removal plus decision rule made them safer.

### 04:40: human spot-check sheet ready

- `results/manual_sheet_suwon.csv`: 74 rows (37 naive + 37 context-v2-nomem, every 8th Suwon frame, shuffled, condition hidden). Key: `results/manual_sheet_suwon_key.csv`. Every row has a judge-v2 score (every-8th ⊂ every-4th) and a judge-v1 score.
- New commands: `lvnav manual-sheet --runs ...` (blinded, shuffled) and `lvnav agreement --sheet ... --key ... --judged-name ...` (Spearman ρ per dimension). Protocol in `docs/RUBRIC.md`.

### Needs Aaron (added 04:40)
- [ ] Score `results/manual_sheet_suwon.csv` (open each `frame_path`, fill the five 1–5 columns, don't open the key). ~74 rows, maybe 45–60 min. Then run the two `lvnav agreement` commands from `docs/RUBRIC.md`.

### 05:05: judge v2 complete on both walks; all three chains finished

**London, judge v2, every 4th frame (72 per arm)**

| Run | safety | action. | spatial | concise | halluc. | overall | wins / losses vs naive |
|---|---|---|---|---|---|---|---|
| london_naive | 1.92 | 3.27 | 2.75 | 2.65 | 2.69 | 2.65 | |
| london_context (v1) | 1.85 | 3.25 | 2.26 | 3.86 | 3.74 | 2.99 | 37 / 28 |
| london_context_v1_nomem | 1.53 | 3.66 | 2.59 | 4.00 | 4.13 | 3.18 | 42 / 18 |
| london_context_v2_nomem | **2.33** | **3.69** | **2.97** | 3.88 | **4.15** | **3.41** | **50 / 16** |

**Pooled, both walks, paired per frame: context-v2-nomem − naive (judge v2, n = 144)**

| Dimension | mean Δ | 95 % CI | better / worse |
|---|---|---|---|
| safety | +0.60 | +0.27 … +0.94 | 54 / 32 |
| actionability | +0.66 | +0.42 … +0.89 | 74 / 22 |
| spatial accuracy | +0.53 | +0.28 … +0.78 | 47 / 19 |
| conciseness | +1.28 | +1.10 … +1.46 | 107 / 6 |
| hallucination | +1.48 | +1.12 … +1.83 | 87 / 18 |
| overall | +0.91 | +0.71 … +1.11 | 108 / 27 |

Every CI excludes zero. Ordering of gains: hallucination > conciseness > actionability > safety > spatial. **H1 holds in direction, but its sub-claim (largest gain on spatial accuracy) does not**: spatial is the *smallest* gain. **H2 holds** (hallucination +1.48, the largest). H3 pending the quiet-machine run started 05:05.

Judge-v2 parse failures: 4 of 592 (0.7 %). Uniform score vectors ≤ 5 % on every run (v1: up to 49 %).

### 05:20: failure catalogue (frames inspected) and docs/RESULTS.md drafted

Viewed the top regressions of context-v2-nomem under naive:
- **suwon/000248** — a person bending down mid-alley; detector said `none detected`; the context arm still said "There's a person bending down a few steps ahead" (correct, from the image); judge v2 penalised it for contradicting the cues. → *judge over-anchoring*, not a system failure.
- **suwon/000212** — zebra crossing, pedestrian signal is **green**; naive said it was red and told the user to wait; context said "person ahead on your right" and never mentioned the crossing. Judge preferred naive. → *scene semantics cues cannot carry* + judge error.
- **london/000044** — bollard at near range just right of centre, not detected (bollard is in the vocabulary); context said "Continue. There's a person far ahead on the left"; naive mentioned the bollard. → *detector miss + cue anchoring*, the genuine failure class.

`docs/RESULTS.md` written with all tables, the two findings (memory echo; judge halo), hypotheses verdicts, failure catalogue and limitations. Latency section awaits the quiet-machine run (started 05:05). Disk is back to 16 GB free (external cleanup).
