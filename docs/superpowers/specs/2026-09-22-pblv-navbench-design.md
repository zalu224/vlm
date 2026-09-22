# pBLV navigation benchmark — design

**Date:** 2026-09-22 · **Status:** approved in conversation (repo rebuilt around it; paper's models plus ours; 100 repeats; Claude Fable 5.1 as judge)

## 1. Goal

Replicate *Exploring the Use of VLMs for Navigation Assistance for People with Blindness and Low Vision* (Li et al., arXiv 2603.15624) on its released dataset (github.com/rizzojr01/vlm_navigation_eval, 145 photos), with the paper's four tasks and protocol, on the paper's models where they still exist and on our local models; then extend it with the folders the paper did not use (dim light, couch, hallway).

## 2. What the paper did

| task | scenes | prompt | answer | metric |
|---|---|---|---|---|
| Counting | 8 classroom scenes, 1–6 chairs | "Count the number of chairs in the scene." | integer | accuracy, mean, variance over 100 queries |
| Spatial reasoning | 8 cases, two chairs at different depths; cases 1–2 also flipped to test side bias | "Which chair is closer to the viewpoint?" | left/right or a colour | accuracy over 100 queries |
| Common-sense (vacant seat) | 5 office scenes: empty chair; coat on chair; coat hung on chair; laptop + backpack; laptop + backpack rearranged | "Are there any vacant seats in this image? A 'vacant seat' refers to a seating option (e.g., chair, bench, or couch) that is unoccupied by any person and does not have any personal items placed on it or on the corresponding desk, table, or surface. Answer yes or no before providing details." | yes/no | accuracy over 100 queries |
| Navigation | 13 classroom/office cases with obstacles (box, bag, paper, wet-floor sign, ball, pot, table, tissue); 3 queries × 10 executions | system prompt with six parts (purpose, vacant-seat definition, context, clear guidance, filter irrelevant detail, no hallucination); user asks to be guided to a vacant seat | free text | human ratings, three independent yes/no criteria: destination, route, obstacles; Cohen's κ 0.83 |

Models: GPT-4o, GPT-4V, Gemini-1.5-Pro, Claude-3.5-Sonnet, LLaVA-v1.6-Mistral-7B, LLaVA-OneVision-Qwen2-7B, default decoding. Resolution was reduced for some models (Appendix A.1).

## 3. Scene mapping (filenames → tasks)

| task | images |
|---|---|
| counting | `classroom_chairs_{1,2,3,3_2,4,4_2,5,6}` |
| spatial | `indoor_left_closer`, `indoor_left_closer_flipped`, `indoor_right_closer_2`, `indoor_right_closer_2_flipped`, `indoor_right_front_closer`, `outdoor_daytime_orange_yellow`, `outdoor_daytime_yellow_orange`, `outdoor_chair_orange_yellow` (colour cases; labels verified by eye, not by name order) |
| commonsense | `IMG_Cl`, `IMG_Cl_Coat`, `IMG_Cl_Coat_Hanging`, `IMG_Clf_Laptop(f)_Bag(l)`, `IMG_Clf_Laptop(l)_Bag(f)` |
| navigation (13) | `classroom_chairs_{bag,box,paper,wet,wet2}` + `IMG_Cl_Obstacle_{Ball,Box,Box2,ClAndBag,Pot,TableAndPot,TableAndPot2,Tissue}` |
| **extension** | `dim_light/*` (the office scenes in low light → commonsense), `couch/*` and `hallway/*` (benches/couches → commonsense), remaining `campus/*` (outdoor colour chairs → counting/spatial), `chairs/*` not used above (→ commonsense) |

Every label is derived from the filename and then checked by viewing the image; the check is recorded in `questions/questions.jsonl` (`verified: true` and a `notes` field). Where the filename is ambiguous the image is left out of the paper-faithful set and, if used, goes in the extension with the visual reading as the label.

## 4. Architecture

```
data/pblv_nav/            ingested copies: EXIF-corrected, ≤1600 px, manifest.jsonl (git-ignored)
questions/questions.jsonl committed. One row per (task, image[, variant]): qid, task, tier (paper|ext),
                          image, prompt, answer, answer_type (int|choice|yesno|free), choices, gold (nav: vacant seat + obstacles + route), notes
navbench/
  data.py      ingest the cloned repo; manifest
  questions.py load/validate questions; per-task prompt builders (verbatim paper prompts)
  backends/    mlx (OpenAI-compatible local server), openai, anthropic, gemini, mock — one interface: generate(system, user, image, temperature) -> text, latency, tokens
  runner.py    nav run: (model × task) → runs/<model>/<task>.jsonl, one row per (qid, repeat); resume-safe; default sampling
  parse.py     answer extraction per answer_type; parse failures kept
  score.py     accuracy / mean / variance per task and scene; per-count table; flip-bias table
  judge.py     nav judge: Claude Fable 5.1 rates each navigation output on the three criteria (image + gold + output); judged.jsonl; agreement helpers for a human spot-check
  report.py    nav report: docs/RESULTS.md tables and figures
  cli.py       nav ingest | questions | run | score | judge | report
configs/models.yaml   model roster: id, backend, served name, notes on availability
tests/                every module on the mock backend; questions file validated in CI
```

Sampling: the paper used each provider's default decoding. We use `temperature=1.0, top_p=1.0` for every model, local and cloud, so the 100 repeats measure the same thing everywhere; configurable per model. Images are sent at ≤1024 px long side to every model (the paper reduced some; the write-up states ours).

## 5. Models

| model | backend | status on this machine |
|---|---|---|
| Qwen2.5-VL-7B-Instruct 4-bit, Qwen2.5-VL-3B 4-bit, Qwen3-VL-2B 4-bit, InternVL3-2B 4-bit (ours) | mlx | cached, run now |
| LLaVA-v1.6-Mistral-7B 4-bit (paper) | mlx | on mlx-community, 4 GB, run now |
| LLaVA-OneVision-Qwen2-7B (paper) | — | no 4-bit MLX build; bf16 does not fit 18 GB / 12 GB disk. Reported as not reproducible here |
| GPT-4o (paper), GPT-4V (paper, retired → note) | openai | needs `OPENAI_API_KEY` |
| Claude-3.5-Sonnet (paper; retired → nearest available), Claude Fable 5.1 / Opus 5 (ours) | anthropic | needs `ANTHROPIC_API_KEY` |
| Gemini-1.5-Pro (paper; likely retired → nearest available) | gemini | needs `GEMINI_API_KEY` |

Cloud backends are implemented against the official SDKs and unit-tested with mocks; `nav run` fails fast with the missing variable named.

## 6. Judge

Claude Fable 5.1 (`claude-fable-5-1`) reads the image, the case's gold (which seat is vacant, obstacles and where, the sensible route) and the model output, and returns `{destination, route, obstacles}` each yes/no with a one-line reason, following the paper's three annotator questions verbatim. Thinking is left on (the model's default); `output_config.format` structured output for the JSON. A blinded human sheet of 40 outputs and κ between Aaron and the judge bound its reliability, mirroring the paper's κ. `nav judge` needs `ANTHROPIC_API_KEY`.

## 7. Compute

Fundamental tasks: 21 questions × 100 repeats = 2,100 calls per model; navigation 13 × 3 × 10 = 390. At 2–4 s per call locally: 2–3 h per 7B model, ~1 h per 2B. Five local models ≈ one night. Runs are resumable and one model is served at a time.

## 8. Outputs

`runs/<model>/<task>.jsonl`, `runs/<model>/judged.jsonl`, `reports/results.json`, `docs/RESULTS.md` with the paper's tables reproduced side by side with ours (per-count accuracy; spatial with flipped pairs; common-sense per scene; navigation three criteria), plus the extension tables.

## 9. Differences from the paper, stated up front

Local 4-bit models instead of the paper's open models in full precision; one sampling setting for all models; LLM judge instead of two human annotators (bounded by a human spot-check); LLaVA-OneVision and the retired cloud snapshots not reproducible; extension tiers are ours.
