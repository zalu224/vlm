# Progress log

Newest entries at the bottom. Decisions carry a **Decision:** line; things only Aaron can do are under **Needs Aaron**.

## 2026-09-15 — pivot to the navigation benchmark

- Aaron asked to replace the data with github.com/rizzojr01/vlm_navigation_eval and replicate that research. The repo is a dataset only: 145 photos in five folders, no code, questions or labels; its README matches Li et al. 2026 (arXiv 2603.15624), so the benchmark questions had to be authored here from the filenames and checked by eye.
- The shelf study's final results (7B verification on GroZi-3.2k and Grocery Store) were recorded before archiving: false-confirmation rates of 30 % by name, 47 % by reference photo on composites, 90 % by reference photo on real shelves. The 3B runs never completed (the run script stalled on a download signal).
- **Decision (Aaron):** archive the shelf study and rebuild main; run the paper's models plus ours; 100 repeats as in the paper; Claude Fable 5.1 as the judge for the navigation task.
- Archive: branch `shelf-archive`, tag `shelf-v0.4.1`; data moved to `~/lvnav-archive-local/shelf-study` (1.1 GB, including Aaron's own catalogue photos).

## 2026-09-22 — navbench built

- Design spec: `docs/superpowers/specs/2026-09-22-pblv-navbench-design.md`. Paper details recovered from the full text: exact prompts for the three fundamental tasks, the six components of the navigation system prompt (text not printed in the paper; ours is a stated reconstruction), the three annotator criteria, resolution settings, and the reported numbers (GPT-4o 94/100/80 % on counting/spatial/common-sense; LLaVA-Mistral 44/62/22 %).
- Package `navbench` from scratch: ingest (EXIF orientation 6 applied, 1600 px), prompts, question loader/validator, backends (local OpenAI-compatible server, OpenAI, Anthropic, Gemini, mock), resumable runner, parser, scorer, judge, report, CLI. 19 tests, all on mocks and fake clients; CI runs `nav questions --check`.
- **Labels.** 34 paper-tier scenes mapped from filenames and verified on contact sheets: counting `classroom_chairs_{1..6}` (8 scenes), spatial 5 indoor + 3 outdoor colour pairs (cases 1 and 2 mirrored, as the paper says), common-sense the five office scenes, navigation the 13 obstacle cases (5 classroom + 8 office) × 3 queries. One filename trap recorded: `outdoor_chair_orange_yellow` has the **yellow** chair nearer despite the name order. Extension tier: 5 counts and 16 vacant-seat scenes (dim light, couches, hallway benches) where the answer is unambiguous.
- **Models.** Local now: Qwen2.5-VL 7B/3B, Qwen3-VL 2B, InternVL3 2B, LLaVA-v1.6-Mistral-7B (4-bit MLX). Not reproducible here: LLaVA-OneVision-Qwen2-7B (no 4-bit build; bf16 does not fit). Cloud: GPT-4o, GPT-4V (retired → gpt-4-turbo), Claude 3.5 Sonnet (nearest available), Gemini 1.5 Pro (nearest available), plus Claude Opus 5; all gated on keys.
- **Sampling:** temperature 1.0, top-p 1.0 for every model, images at 1024 px, stated as a difference from the paper's "default decoding".

### Needs Aaron
- [ ] `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` if we want the paper's *cloud models* run here. Keys are read from the environment only; nothing is written to the repo. **The judge no longer needs a key** (see 2026-09-22, in-session judging).
- [ ] After the judge runs: rate the blinded spot-check sheet (40 outputs) so judge–human agreement can be reported next to the paper's κ = 0.83.

## 2026-09-22 — first full model: Qwen2.5-VL-7B (5 h 15 min for all tasks)

| task | ours (7B, 4-bit, T=1.0) | GPT-4o (paper) | LLaVA-1.6-Mistral-7B (paper) |
|---|---|---|---|
| counting (8 scenes × 100) | 78 % | 94 % | 44 % |
| spatial (8 cases × 100) | 94 % | 100 % | 62 % |
| common-sense vacant seat (5 × 100) | 47 % | 80 % | 22 % |

- Counting fails on one scene: the five-chair layout is read as six on 82 % of repeats; 1, 2 → 100 %, 3 → 82 %, 4 → 86 %, 6 → 86 %. The paper's Claude-3.5 and Gemini collapse on the 3-chair scene (0 % and 7 %); ours does not.
- Spatial: no side bias. Case 1 and its mirror 98 / 99 %, case 2 and its mirror 99 / 97 %. The only weak case is the chair pulled out in front (67 %), where the model sometimes reasons about the far chair.
- Common sense: the empty chair is called vacant 98 % of the time, but a coat laid on the chair still gets "yes" 81 % of the time, a coat hung on it 92 %, and the laptop-plus-backpack scenes about 75 %. The model answers the object question, not the definition: exactly the failure the paper reports for open models, at a higher level.
- Parse failures: 0 of 2,520. Median latency 5.7 s (counting), 6.9 s (spatial), 6.7 s (common sense), 8.1 s (navigation, 390 outputs awaiting the judge).
- The chain moved on to Qwen2.5-VL-3B at 08:40.

## 2026-09-22 — Qwen2.5-VL-3B (3 h 05 min)

| task | 3B | 7B |
|---|---|---|
| counting | 68 % | 78 % |
| spatial | 58 % | 94 % |
| common-sense vacant seat | 49 % | 47 % |

- **The paper's side-bias finding reproduces at 3B.** Case 1 (left chair nearer) 73 %, its mirror (right nearer) 34 %; case 2 (right nearer) 36 %, its mirror (left nearer) 79 %. The 3B answers "left" most of the time whatever the picture; the 7B is within two points across each mirrored pair. This is the reason the paper flipped cases 1 and 2, and the mirrored pairs are what exposes it.
- Counting degrades on the harder layouts (3 chairs 41 %, 6 chairs 61 %) while 1 and 2 stay above 94 %.
- Common sense is flat between sizes (49 % vs 47 %): both models say "yes" to an occupied chair; size does not fix the definition problem.
- Parse failures: 98 of 2,520 for the 3B (mostly answers with no number or no yes/no), 38 for the 7B, all counted as wrong.

## 2026-09-22 — judging moved in-session, no API key

- **Decision (Aaron):** "don't need for anthropic key just use our subscription for output judging with opus model, or choose the best model for the vision task." This supersedes the earlier choice of Claude Fable 5.1 over the API.
- Judging now runs as Claude Opus 5 inside the Claude Code session. Opus 5 is the vision-capable model on the subscription, and rating genuinely is a vision task: the rater has to look at the photograph to know which seat is free and what is on the floor. The three annotator questions are unchanged.
- Two new subcommands. `nav judge-export` writes one rating task per navigation **case** — the photograph, that case's gold, and every model's outputs for it — and `nav judge-import` merges the verdicts into `runs/judged.jsonl` in exactly the schema the API judge produced. `nav report`, `nav sheet` and `nav agreement` are untouched.
- **Blinding is kept.** Outputs are grouped by case, never by model, and each carries only `rating_id = sha1(model|qid|repeat)[:12]`. The model names live in `index.json`, which the rater does not open. This matches the paper's annotators, who did not know the source of an output. Grouping by case also means each photograph is read once and all of its outputs are judged against that single reading.
- The three annotator questions were factored into one constant (`CRITERIA_BLOCK` in `judge.py`) so both judging paths ask exactly the same thing. The API path stays implemented and tested as the alternative when a key exists.
- Exported 1,170 outputs across the 13 cases (3 models finished × 390 each). Rated by 13 parallel raters, one per case, each viewing its own photograph.

## 2026-09-22 — navigation judged: 1,170 outputs, three local models

All 13 cases rated, 90 outputs each (3 models × 3 queries × 10 executions). Every rating file validated against its task file: 1,170 verdicts, ids matching exactly, no malformed values.

| model | destination | route | obstacles | all three |
|---|---|---|---|---|
| Qwen2.5-VL-7B | 90 % | 48 % | 30 % | 17 % |
| Qwen3-VL-2B | 90 % | 37 % | 15 % | 7 % |
| Qwen2.5-VL-3B | 66 % | 17 % | 25 % | 5 % |
| GPT-4o (paper) | 81 % | 92 % | 84 % | – |
| Claude-3.5-Sonnet (paper) | 85 % | 87 % | 82 % | – |
| Gemini-1.5-Pro (paper) | 30 % | 13 % | 64 % | – |

- **The gap between local and cloud models is not in finding the seat, it is in describing how to reach it.** Our 7B beats the paper's GPT-4o on destination (90 % vs 81 %) and loses badly on route (48 % vs 92 %) and obstacles (30 % vs 84 %). Picking the vacant chair out of a photograph is the part small models already do; turning it into directions a person could follow without sight is the part they do not.
- Obstacles is the worst criterion for every local model. The typical failure is a route described as if the floor were clear: the wet-floor sign, the boxes or the paper are simply not mentioned. This is the criterion that matters most for safety, and it is the one that collapses.
- Per-case spread is wide. The tissue case reaches 87 % / 53 % / 32 %; the backpack-on-chair case (nav_1) falls to 32 % / 14 % / 5 %, because the models direct the user to the occupied chair. Case nav_9 (chair and bag) splits destination at 53 %.
- Qwen3-VL-2B is the clearest case of a model that sees well and guides badly: joint-best on destination (90 %) at a fifth of the 7B's size, but last on obstacles (15 %).
- One output contains stray Chinese tokens mid-sentence ("Watch out for the 万事瞩目 macdonald"), a 7B decoding failure that the judge marked down on route and obstacles rather than destination.
- `reports/spotcheck.csv` written: 40 blinded outputs for Aaron, with the key held separately in `reports/spotcheck_key.csv`.

### Needs Aaron
- [ ] Fill the `destination`, `route`, `obstacles` columns in `reports/spotcheck.csv` (yes/no), then `nav agreement` reports Cohen's κ against the judge, beside the paper's κ = 0.83.

## 2026-09-22 — the chain's last two models both failed; both now fixed

The overnight chain reported "ALL DONE" having produced nothing for either remaining model. Two unrelated faults, neither of which the script noticed as fatal.

**InternVL3-2B: the MLX server cannot serve it at all.** Every request returned 500 with `RuntimeError: There is no Stream(gpu, 2) in current thread.`, raised from `mx.async_eval` on the prompt cache in `mlx_vlm/generate/ar.py`. The server generates inside `asyncio.to_thread`, so the cache ends up holding a GPU stream belonging to another thread. The Qwen models survive this; InternVL3 does not, on the first call. `--max-num-seqs 1` does not help, so it is not continuous batching.

The same weights generate correctly when loaded and called on one thread, which is the fix: a new `mlx-direct` backend (`navbench/backends/mlx_direct.py`) loads the model in-process and generates without any HTTP server. Same constructor arguments and same `Reply` as the server backend, so the runner is untouched; `configs/models.yaml` selects it for `internvl3-2b` alone, with the reason recorded next to the entry. Verified end to end: 6.0 s per call, plausible answers. One real difference from the server path is that `image_max_side` is not applied — mlx_vlm resizes with the model's own processor — and that is stated rather than hidden.

**LLaVA-v1.6-Mistral-7B: the readiness window was shorter than the download.** The server was still fetching 4.26 GB of weights when the 600 s readiness loop gave up; the chain then declared "server failed to start", and its final `pkill` killed the download mid-file. `logs/run_remaining_models.sh` fetches the weights to completion first (`hf download`, a no-op once cached) and only then starts the server, with a 30 min window for the load itself.

- **Watch the disk.** 4.8 GB free with 2.8 GB of LLaVA weights still to fetch. It fits, with roughly 2 GB to spare, but there is no room for a second 7B model after this.
- `nav report` now prints an **incomplete-runs** line naming any model with fewer answers than the protocol calls for, with the shortfall per task. Without it a model part-way through its run shows an accuracy indistinguishable from a finished one; InternVL3-2B at 16 of 800 counting answers was displayed as a flat percentage.
- Qwen3-VL-2B's extension tier did complete; its common-sense figure is 41 %, not the 36 % reported from a partial file earlier today.
