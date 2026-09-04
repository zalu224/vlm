# Research Proposal

## Context-Engineered Vision-Language Guidance for Low-Vision Navigation: A One-Week Ablation on Egocentric Video

**Track:** Low-vision assistive technology (human-centered AI, multimodal interaction)
**Duration:** 7 days
**Compute:** One Apple Silicon laptop (18 GB unified memory), no external APIs
**Deliverables:** Reproducible codebase, paired results on ≥ 300 egocentric frames, 2-page write-up, live demo

---

### 1. Motivation

Vision-language models (VLMs) can already describe a street scene fluently. Whether that fluency translates into guidance a blind pedestrian can act on within the next two seconds is a different question. Recent evaluations of frontier VLMs on navigation assistance for people who are blind or have low vision (pBLV) identify three recurring failures: unreliable spatial reasoning (left/right and distance errors), verbose or descriptive output that is not actionable when spoken, and weak alignment with what a blind user actually needs to hear. The same literature notes that most benchmarks use static images and explicitly calls for frame-by-frame evaluation on egocentric video from wearable devices.

Independently, robotics work on aerial navigation has shown that VLM reasoning becomes far more reliable when it is fed structured context from cheap perception modules (open-vocabulary grounding, geometric cues) rather than asked to infer everything from pixels. This proposal tests whether the same principle — *context engineering rather than model scaling* — closes the gap for assistive guidance.

### 2. Research question and hypotheses

**RQ.** On egocentric walking video, does injecting engineered context into a VLM's prompt produce navigation instructions that are safer, more actionable and more spatially accurate than naive single-frame prompting, and at what latency cost?

- **H1 (quality).** The context condition scores higher on safety, actionability and spatial accuracy, with the largest gain on spatial accuracy, because explicit zone/proximity cues remove the model's need to estimate geometry from a single monocular frame.
- **H2 (hallucination).** The context condition mentions fewer unsupported objects, because the prompt anchors it to detector output and instructs it to flag uncertainty.
- **H3 (cost).** Context adds under 40 % latency at 1 fps on the target hardware, dominated by perception rather than the longer prompt.

### 3. Method

**Conditions.** Both conditions use the same locally served VLM (Qwen2.5-VL-7B-Instruct, 4-bit, via MLX) at temperature 0 on identical frames sampled at 1 fps.

| | Naive | Context |
|---|---|---|
| System prompt | generic assistant | BLV guide rules: ≤ 2 spoken sentences, hazard first, body-relative directions, no scene description, state uncertainty |
| Per-frame input | image | image + free-space per zone (L/C/R) from Depth Anything V2 + obstacles with proximity from YOLO-World |
| Temporal input | none | rolling memory of the last 3 frames' cues and the last instruction given |

**Perception.** Depth Anything V2 (Small) yields relative depth; the lower half of the frame is split into three zones and each is labelled clear / partly blocked / blocked from its 90th-percentile closeness. YOLO-World with a 20-term BLV vocabulary (person, pole, stairs, curb, …) provides obstacles; each is assigned a zone and a near/mid/far bucket from the median depth inside its box. The fusion logic is model-free and unit-tested.

**Evaluation.** Every instruction is scored 1–5 on five dimensions (safety, actionability, spatial accuracy, conciseness, hallucination) by an LLM judge that sees the frame, the perception cues and the instruction but *not* the generating prompt, so both conditions are judged on identical evidence. A stratified sample of 40 frames is scored by hand to estimate judge–human agreement (Spearman ρ per dimension). We report paired per-frame deltas, win/loss counts, and the ten largest improvements and regressions for qualitative analysis.

**Data.** Egocentric walking footage at chest or head height, covering at least one indoor corridor, one sidewalk with pedestrians, and one street crossing. Self-recorded footage is sufficient for the ablation; public egocentric BLV datasets will be used if access is confirmed on Day 1 (see `docs/WEEK_PLAN.md`).

### 4. Expected contribution

1. A controlled, reproducible measurement of how much *prompt-level* context helps a mid-sized open VLM on BLV guidance — a number the current literature does not report.
2. An open pipeline that runs entirely on a laptop, lowering the barrier for follow-up studies with pBLV participants.
3. A failure-case catalogue (largest regressions) that points to which cue types matter most, informing what a wearable prototype should actually sense.

### 5. Limitations and ethics

No pBLV participants are involved in this one-week phase; the judge is a proxy and the human spot-check bounds its reliability. Footage is self-recorded in public spaces without identifiable faces retained. The system is a research probe, not an assistive device, and is not to be used for real navigation.

### 6. Extension paths (beyond one week)

- Replace the LLM judge with pBLV participant ratings (IRB required).
- Stream from a phone camera to test real-time behaviour with speech output.
- Fine-tune a 3B VLM on judged context-condition outputs (distillation) to recover latency.
- Port the same context-engineering harness to the drone track: swap depth/detector cues for SLAM pose and obstacle map summaries feeding a diffusion planner.
