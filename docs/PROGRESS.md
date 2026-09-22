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
- [ ] `export ANTHROPIC_API_KEY=...` (judge and Claude runs), `OPENAI_API_KEY`, `GEMINI_API_KEY` for the paper's cloud models. Keys are read from the environment only; nothing is written to the repo.
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
