# Results

Context-engineered VLM guidance for low-vision navigation: one-week ablation on egocentric video. Numbers here are copied from `results/*/report*.md` and `docs/PROGRESS.md`; the commands that produced them are in the root README. Status: **judge results final; human spot-check pending** (see §6).

## 1. Setup in one paragraph

Two Creative-Commons first-person walking videos (Suwon market street, 295 frames; London sidewalk with crossings, 285 frames; 1 fps, ≤ 1024 px) were fed to Qwen2.5-VL-7B-Instruct (4-bit, MLX, temperature 0, ≤ 80 tokens) under four conditions on identical frames. Perception: Depth Anything V2 Small (free space per left/centre/right zone from an approach band at 50–80 % of image height) and YOLO-World S with a 20-term BLV vocabulary (obstacles with zone and near/mid/far). Instructions were scored 1–5 on safety, actionability, spatial accuracy, conciseness and hallucination by the same model acting as judge, under two judge prompts (§4). All runs are reproducible from `results/<run>/config.yaml`.

| Arm | System prompt | Per-frame cues | Memory (last 3 frames' cues) | Last instruction echoed |
|---|---|---|---|---|
| naive | generic assistant | none | no | no |
| context-v1 (pre-registered) | BLV rules v1 | yes | yes | **yes** |
| context-v1-nomem | BLV rules v1 | yes | yes | no |
| context-v2-nomem | BLV rules v2: explicit cue → action rule (STOP / SLOW DOWN / CONTINUE), no example phrases, check image for hazards cues miss | yes | yes | no |

## 2. Headline: paired deltas, context-v2-nomem minus naive (judge v2, every 4th frame, both walks, n = 144)

| Dimension | naive | context-v2-nomem | mean Δ | 95 % CI | better / worse |
|---|---|---|---|---|---|
| safety | 1.76 | 2.37 | **+0.60** | +0.27 … +0.94 | 54 / 32 |
| actionability | 2.95 | 3.61 | **+0.66** | +0.42 … +0.89 | 74 / 22 |
| spatial accuracy | 2.45 | 2.97 | **+0.53** | +0.28 … +0.78 | 47 / 19 |
| conciseness | 2.57 | 3.86 | **+1.28** | +1.10 … +1.46 | 107 / 6 |
| hallucination (↑ = fewer) | 2.60 | 4.09 | **+1.48** | +1.12 … +1.83 | 87 / 18 |
| overall | 2.47 | 3.38 | **+0.91** | +0.71 … +1.11 | 108 / 27 |

Every interval excludes zero. The best context arm wins 108 of 144 paired frames.

## 3. All arms, both walks (judge v2, every 4th frame)

| Run | n | safety | action. | spatial | concise | halluc. | overall | wins / losses vs naive |
|---|---|---|---|---|---|---|---|---|
| suwon_naive | 74 | 1.60 | 2.63 | 2.15 | 2.49 | 2.51 | 2.28 | |
| suwon_context-v1 | 74 | 1.22 | 3.03 | 1.84 | 3.88 | 3.97 | 2.79 | 51 / 15 |
| suwon_context-v1-nomem | 74 | 1.51 | 2.99 | 2.22 | 3.68 | 3.97 | 2.87 | 49 / 22 |
| suwon_context-v2-nomem | 74 | **2.41** | **3.53** | **2.97** | 3.84 | **4.03** | **3.35** | **58 / 11** |
| london_naive | 72 | 1.92 | 3.27 | 2.75 | 2.65 | 2.69 | 2.65 | |
| london_context-v1 | 72 | 1.85 | 3.25 | 2.26 | 3.86 | 3.74 | 2.99 | 37 / 28 |
| london_context-v1-nomem | 72 | 1.53 | 3.66 | 2.59 | 4.00 | 4.13 | 3.18 | 42 / 18 |
| london_context-v2-nomem | 72 | **2.33** | **3.69** | **2.97** | 3.88 | **4.15** | **3.41** | **50 / 16** |

Generation statistics on all frames (no judge involved):

| Run | words / instr. | unique instr. / frames | "stop" | "slow" | "left" or "right" | hit 80-token cap |
|---|---|---|---|---|---|---|
| naive (Suwon / London) | 66 / 63 | 0.97 / 0.96 | 9 % / 16 % | 0 / 0 | 7 % / 17 % | 77 % / 48 % |
| context-v1 | 8.0 / 9.9 | **0.09 / 0.14** | 0 / 0 | 0 / 0 | 12 % / 48 % | 0 |
| context-v1-nomem | 8.6 / 8.9 | 0.62 / 0.47 | 1 % / 0 | 11 % / 8 % | 22 % / 19 % | 0 |
| context-v2-nomem | 8.5 / 9.9 | 0.40 / 0.47 | **20 % / 7 %** | 11 % / 21 % | **45 % / 69 %** | 0 |

## 4. Finding 1: the pre-registered context prompt collapsed, and the cause was the memory echo

context-v1 emitted "Two steps ahead, there's a person. Move forward." on 103 of 295 Suwon frames regardless of the scene, never said "stop" or "slow", and copied example phrases from its own system prompt ("a traffic light is at knee height"). Twelve-frame trials isolated the cause: with the last instruction removed from the rolling memory, both v1 and v2 prompts produce 11–12 unique instructions in 12 frames; with it present, both collapse (v1: 3–6; v2: 4–5). At temperature 0 the model treats its previous sentence as the answer. The rolling *cue* memory is harmless and stays on.

The v2 decision rule only works once the echo is gone: v2-with-echo is worse than v1 on every count.

## 5. Finding 2: the local judge needed fixing before it could measure anything

Judge v1 (single JSON with five scores and one rationale) had all context arms *losing* to naive, including an 8-word instruction scoring 2.0 on conciseness against a 66-word paragraph cut off mid-sentence at 2.6. Diagnosis: on 49 % of Suwon context-v1 frames all five scores were identical; the same instruction scored conciseness 1 on 76 frames and 5 on one; rationales contradicted scores ("not concise" about eight words; hallucination 5 while noting an invented object).

Judge v2 asks for a one-sentence reason *before* each score, states the dimensions are independent, and anchors conciseness on length and form only. Uniform score vectors fell to ≤ 5 % on every run, conciseness now tracks length (naive paragraphs 2.5–2.7, all context arms 3.7–4.0), and reasons match scores. Under v2 the verdict flips: every context arm beats naive. v1 numbers are kept in `results/*/judged.jsonl` and `report.md`; v2 in `judged_v2_every4.jsonl` and `report_v2_every4.md`.

Cost: v2 produces ~5× the output tokens (10–11 s per frame on a quiet machine vs ~8 s), which is why it was run on every 4th frame.

Residual v2 quirks: it sometimes scores an *omission* as hallucination ("does not mention the bus" → 3), and it over-anchors on the cues when the VLM correctly reports something the detector missed (Suwon frame 248: a person bending down in the alley, `Obstacles: none detected`, context arm penalised). Both are noted for a v3 judge prompt.

## 6. Human spot-check

Blinded sheet: `results/manual_sheet_suwon.csv`, 74 rows (37 naive + 37 context-v2-nomem, every 8th Suwon frame, shuffled, condition hidden). _Judge–human Spearman ρ per dimension, for both judges, to be added after scoring (`lvnav agreement`, see `docs/RUBRIC.md`)._

## 7. Latency (H3)

_Quiet-machine re-measurement on 50 identical Suwon frames, naive vs context-v2-nomem: see the table appended below once the run completes. Full-run medians (all frames, GPU shared at times): naive 4.9 s, context arms 4.1–4.8 s; perception adds 0.12–0.15 s per frame on MPS after warm-up._

## 8. Failure catalogue (largest regressions of context-v2-nomem under naive, judge v2)

| Class | Frames | What happened | Implication |
|---|---|---|---|
| **Detector miss + cue anchoring** | london 44 (bollard at near range, right), london 84 (pole), suwon 212 (crosswalk, pedestrian signal) | The object is in the vocabulary but was not detected; the context arm followed the cues ("Continue, person far ahead on the left") and ignored the visible hazard; naive mentioned it. | The v2 prompt's "check the image for hazards the cues miss" is not enough; the detector's recall on thin vertical objects (bollards, poles, signal posts) is the weak link. Candidates: lower `detector_conf` for those classes, or a second cue source (edge/vertical-structure detector). |
| **Scene semantics the cues cannot carry** | suwon 212, london 136 (traffic signals), suwon 264 (alley exit) | Crossing decisions depend on signal state and road layout; cues encode only free space and obstacles. Naive sometimes read the signal (and got it wrong: called a green figure red on suwon 212). | Add a crossing/signal cue or leave crossings out of scope; do not trust either arm at crossings. |
| **Judge over-anchoring on cues** | suwon 248, london 148 | The context arm reported something true that the detector did not list; the judge scored it as unsupported. | Judge v3: "supported by the image *or* the cues" must be applied literally; human spot-check bounds this. |
| **Naive verbosity scored as content** | london 168 and others | Naive gave a tourist-style paragraph ("you will soon reach Trafalgar Square") that scored moderately; context gave a correct "slow down, keep left". | Length bias is reduced in judge v2 but not gone. |

## 9. Hypotheses

- **H1 (quality): supported in direction, not in detail.** The best context arm is better on all five dimensions with CIs excluding zero. But the predicted "largest gain on spatial accuracy" is wrong: spatial is the *smallest* gain (+0.53); hallucination (+1.48) and conciseness (+1.28) are the largest.
- **H2 (hallucination): supported.** Naive invents white canes, tactile paving, crosswalks and signals; the context arms rarely mention anything not in the frame or cues.
- **H3 (latency): supported, provisionally.** Context arms are no slower than naive at the VLM (shorter outputs outweigh ~700 extra prompt tokens); perception adds ~3 %. Final numbers in §7.
- **Unplanned finding:** prompt-level context helps only if the temporal memory does not include the model's own previous output; and a 7B open model used as judge needs per-dimension reasoning before it produces usable scores.

## 10. Limitations

- Judge and generator are the same 7B model; self-preference is bounded only by the pending human spot-check.
- Public walking-tour footage is head-height and stabilised; a chest-mounted wearable would be lower and shakier. London frames carry a burned-in timecode overlay. Self-recorded corridor / sidewalk / crossing walks are still to be added.
- No pBLV participants; the rubric is a proxy.
- Full-run latencies were partly measured under memory pressure from other applications; the quiet-machine subset in §7 is the number to cite.
- Judge v2 was run on every 4th frame (144 paired frames), not all 580, for cost.
