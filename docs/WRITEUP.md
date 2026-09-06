# Context-Engineered VLM Guidance for Low-Vision Navigation: A One-Week Ablation on Egocentric Video

Aaron Lu · September 2026 · code and results: `lvnav` repository (`docs/RESULTS.md` for full tables)

## Abstract

Vision-language models describe street scenes fluently but give blind and low-vision (BLV) pedestrians guidance that is verbose, spatially unreliable and sometimes invented. We test whether *prompt-level context engineering* rather than model scaling closes that gap. On 580 egocentric walking frames from two public first-person videos, a locally served Qwen2.5-VL-7B (4-bit) was prompted under four conditions: a naive single-frame prompt, and three "context" prompts that inject free-space and obstacle cues from a monocular depth estimator and an open-vocabulary detector, a rolling memory of recent cues, and BLV-specific speaking rules. Judged on a five-dimension BLV rubric, the best context condition beats naive on every dimension (paired Δ overall +0.91 on a 1–5 scale, 95 % CI +0.71 to +1.11, n = 144; hallucination +1.48, conciseness +1.28, actionability +0.66, safety +0.60, spatial accuracy +0.53) at identical VLM latency (4.78 vs 4.79 s per frame) plus 3 % for perception. Two unplanned findings matter as much as the headline: the pre-registered context prompt collapsed into one repeated sentence because the rolling memory echoed the model's own previous instruction, and the same 7B model used as a judge produced halo-effect scores until the judge prompt required a reason before each score. Everything runs on an 18 GB laptop with no cloud APIs.

## 1. Motivation

Recent evaluations of frontier VLMs for BLV navigation assistance (Li et al., 2026) name three recurring failures: unreliable spatial reasoning, verbose or biased output, and poor alignment with what a blind user needs to hear. Kim et al. (2025/26) show that generic VLM judges miss BLV-specific utility and call for frame-by-frame evaluation on egocentric video. In aerial robotics, AgenticDiffusion (Batool et al., 2026) shows VLM reasoning becomes reliable when fed structured context from cheap perception modules. This study transfers that principle to assistive guidance and measures it.

## 2. Method

**Data.** Two Creative-Commons first-person walking videos (Suwon market street, 295 frames; London sidewalk with crossings, 285 frames), sampled at 1 fps, ≤ 1024 px. Head-height, stabilised footage; a chest-mounted wearable would be lower and shakier.

**Perception.** Depth Anything V2 Small gives relative depth; each of three vertical zones is labelled clear / partly blocked / blocked from the 90th-percentile closeness in an *approach band* (rows 50–80 % of the frame). The band matters: the ground at the user's feet is the closest surface in every egocentric frame, and a rule over the whole lower half marked every zone blocked. YOLO-World S with a 20-term BLV vocabulary supplies obstacles with zone and near/mid/far bucket. Fusion is model-free and unit-tested. 0.12–0.15 s per frame on Apple MPS.

**Conditions** (same model, temperature 0, ≤ 80 tokens, identical frames):

| Arm | Prompt | Cues | Cue memory (3 frames) | Own last instruction in prompt |
|---|---|---|---|---|
| naive | generic assistant | – | – | – |
| context-v1 (pre-registered) | BLV rules: ≤ 2 sentences, hazard first, body-relative, no description, state uncertainty | ✓ | ✓ | ✓ |
| context-v1-nomem | same | ✓ | ✓ | – |
| context-v2-nomem | adds an explicit cue → action rule (STOP / SLOW DOWN / CONTINUE), removes example phrases, asks the model to check the image for hazards the cues miss | ✓ | ✓ | – |

**Evaluation.** Every instruction is scored 1–5 on safety, actionability, spatial accuracy, conciseness and hallucination by the same Qwen model, which sees the frame, the cues and the instruction but not the generating prompt. Judge v1 returns five scores and one rationale; judge v2 requires a one-sentence reason before each score, states that dimensions are independent, and anchors conciseness on length and form. v1 was run on all frames, v2 on every 4th frame. A blinded 74-row human spot-check sheet exists for judge–human agreement (pending).

## 3. Results

**Headline (judge v2, paired per frame, both walks, n = 144, context-v2-nomem − naive).** Safety +0.60 [+0.27, +0.94]; actionability +0.66 [+0.42, +0.89]; spatial accuracy +0.53 [+0.28, +0.78]; conciseness +1.28 [+1.10, +1.46]; hallucination +1.48 [+1.12, +1.83]; overall +0.91 [+0.71, +1.11]. The context arm wins 108 of 144 frames, loses 27. Mean length 9 words vs 65; 77 % of naive Suwon outputs were cut off by the token cap.

**Latency (H3).** Same 50 frames, quiet machine: naive 4.78 s median (448 prompt / 79 completion tokens), context 4.79 s (999 / 13). The longer prompt costs what the shorter answer saves. Perception adds ~3 %. Bound of < 40 % overhead holds.

**Finding 1: the memory echo.** context-v1 produced "Two steps ahead, there's a person. Move forward." on 103 of 295 Suwon frames, never said "stop" or "slow", and copied example phrases from its own system prompt. Removing the single line that echoed the previous instruction raised unique instructions per frame from 0.09 to 0.62 with the same prompt, and only then did the v2 decision rule take effect ("stop" in 20 % of Suwon frames, side-relative directions in 45–69 %). With the echo present, v2 was worse than v1.

**Finding 2: the judge.** Under judge v1 every context arm *lost* to naive, with an 8-word instruction scoring lower on conciseness than a truncated 66-word paragraph. Half of the context-v1 frames had five identical scores and rationales contradicted the numbers. Judge v2 removed the halo (uniform score vectors ≤ 5 %), made conciseness track length, and reversed the verdict. This reproduces, on a 7B open model, the evaluator failure Kim et al. describe, and shows a cheap prompt-level fix.

**Hypotheses.** H1 (quality) holds in direction on all five dimensions, but its sub-claim that spatial accuracy would gain most is wrong: it gains least. H2 (fewer hallucinations) holds and is the largest effect. H3 (latency) holds.

## 4. Failure catalogue

Largest regressions of the best arm fall into three classes. (1) *Detector miss plus cue anchoring*: a bollard, a pole and a signal post were in the vocabulary but undetected; the context arm followed the cues and ignored the visible hazard while naive mentioned it. (2) *Scene semantics cues cannot carry*: crossing decisions depend on signal state, which neither arm handles (naive called a green pedestrian signal red). (3) *Judge over-anchoring*: the context arm correctly reported a person the detector missed and was penalised for contradicting the cues. Class 1 says what a wearable should sense next: thin vertical structures. Class 3 is bounded by the human spot-check.

## 5. Limitations and next steps

Generator and judge are the same model; public footage is not wearable footage; no pBLV participants; judge v2 ran on a quarter of the frames. Next: complete the human agreement study; add self-recorded corridor, sidewalk and crossing walks; a judge v3 that scores omissions and unsupported mentions separately; a second cue source for thin vertical obstacles; then, with participants, replace the LLM judge with pBLV ratings.

## References

Batool et al. AgenticDiffusion. arXiv 2606.04111. · Kim et al. Are Large Vision-Language Models Ready to Guide Blind and Low-Vision Individuals? arXiv 2510.00766. · Li et al. Exploring the Use of VLMs for Navigation Assistance for pBLV. arXiv 2603.15624. · GuideDog. arXiv 2503.12844. · Depth Anything V2; YOLO-World; Qwen2.5-VL; MLX.
