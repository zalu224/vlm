# Research Proposal — Study A

## Context Engineering for Vision-Language Guidance in Low-Vision Navigation

**Field:** Human-centered AI, accessibility, computer vision
**Companion study:** `docs/PROPOSAL_RETRIEVAL.md` (object finding and verification), which shares this codebase but is independent of this proposal.

---

## 1. Summary

A person who is blind or has low vision, walking down a sidewalk, needs to hear one thing: *what to do in the next two seconds*. Vision-language models (VLMs) are very good at describing what a camera sees and quite bad at this. They produce fluent paragraphs when the situation calls for four words, they confuse left with right, and they mention objects that are not there.

The usual response to these failures is to reach for a larger model. This study tests a different response: **keep the model the same and improve what it is told**. Alongside each camera frame we supply measurements a small, cheap perception module can produce — where obstacles are, how far away they are, which direction is walkable — plus a short record of what was just said. We call this *context engineering*.

The study measures whether this improves the spoken instructions, and separates the contribution of the measurements from the contribution of the memory.

## 2. Background

Recent evaluations of leading VLMs on navigation assistance for blind and low-vision users report three recurring failures: unreliable spatial reasoning, output too long or descriptive to be useful when spoken aloud, and poor alignment with what a blind user actually needs to hear. The same work notes that most benchmarks use isolated still images, and calls for evaluation on continuous video from body-worn cameras.

Work in aerial robotics points toward a remedy. There, VLM reasoning becomes markedly more reliable when the model is given structured information from small perception modules rather than being asked to infer everything from raw pixels. Whether that transfers to assistive guidance is an open question, and it is the question this study answers.

## 3. Research questions

### RQ1 — Does structured context improve spoken guidance?

We compare instructions generated from a plain prompt against instructions generated from a prompt containing obstacle positions, distances, walkable directions, and recent history. The model, the frames, and the settings are identical; only the prompt differs.

- **Measured by:** five qualities of each instruction, scored 1–5 — safety, actionability, spatial accuracy, brevity, and freedom from invented detail.
- **Expected:** the largest gain appears in spatial accuracy, because explicit measurements remove the model's need to estimate geometry from a single image. Instructions should also get shorter, which matters when they are heard rather than read.

### RQ2 — Which part of the context is doing the work?

Structured context has two distinct components — measurements of the current frame, and memory of the preceding seconds — and they may not contribute equally. We run four conditions on the same frames:

| Condition | Camera frame | Sensor measurements | Recent history |
|---|---|---|---|
| Plain | yes | — | — |
| Measurements only | yes | yes | — |
| Memory only | yes | — | yes |
| Full context | yes | yes | yes |

- **Measured by:** the same five qualities, compared across all four conditions.
- **Expected:** measurements drive most of the gain in spatial accuracy. Memory contributes something different — fewer repeated instructions and better handling of an obstacle that is approaching rather than merely present. If memory adds nothing, that is a useful negative result, since it is the cheaper component to drop.

### RQ3 — What does context cost, and does the benefit survive a smaller model?

Guidance is only useful if it arrives in time, and an assistive device should ideally run the model on the device itself.

- **Measured by:** response time per frame in every condition, split between perception and the model; instruction length; and whether the ranking of conditions is preserved when the same experiment is repeated with a smaller model.
- **Expected:** context adds moderate time, dominated by perception rather than by the longer prompt. The smaller model benefits *more* from context than the larger one, because it has less capacity to infer geometry unaided — if so, context engineering is most valuable exactly where compute is most limited.

## 4. Method

**Materials.** Video from a body-worn camera covering an indoor corridor, a sidewalk with pedestrians, and a street crossing. Frames are sampled once per second, giving roughly 300 frames.

**Perception.** A monocular depth estimator produces relative distances; the lower half of each frame is divided into left, center and right, and each is labeled clear, partly blocked, or blocked. An open-vocabulary detector identifies obstacles relevant to a pedestrian — people, poles, stairs, curbs, vehicles — and each is assigned a direction and a near/medium/far distance. These become a short line of text supplied with the frame.

**Memory.** A rolling record of the last three frames and the most recent instruction given.

**Guidance rules.** Every non-plain condition shares one set of instructions to the model: at most two short sentences, most urgent hazard first, body-relative directions, no scene description, state uncertainty rather than guessing, and do not repeat yourself. Holding these constant across conditions means any measured difference is attributable to the context itself and not to a change in style.

## 5. Evaluation

Each instruction is scored on the five qualities by an automated evaluator that sees the camera frame and the sensor measurements but **not** the prompt that produced the instruction. This matters: an evaluator shown the prompt could reward a condition simply for echoing what it was given. In the plain condition the evaluator is supplied with the same measurements, so it judges every condition against identical evidence.

Because the evaluator is itself a model, a person independently scores a sample of roughly 40 frames, drawn from all conditions and presented in shuffled order so the scorer cannot tell them apart. We report agreement between human and automated scores for each quality, and flag any quality where agreement is weak rather than quietly reporting it as reliable.

Results are reported as per-frame paired comparisons — how often each condition beats the plain baseline on the same frame — alongside averages, plus the largest improvements and the largest regressions for qualitative inspection.

## 6. Limitations

- **No blind or low-vision participants.** This study measures system behavior, not usefulness. Participant studies require ethical approval and are the necessary next step.
- **Automated scoring is a proxy.** The human validation sample bounds how far to trust it; it does not replace it. Using the same model family to generate and to score also risks self-preference, which is a further reason the human sample matters.
- **Sample size.** With roughly 300 frames, differences of a few percentage points are not meaningful and will be reported as such.
- **Sampling rate.** One frame per second is not real-time. Timing measurements indicate feasibility; they do not demonstrate it.
- **Not a usable device.** This is a research probe and must not be relied on for real navigation.

## 7. Plan

| Phase | Work | Output |
|---|---|---|
| 1 | Record walking footage; extract frames | Dataset |
| 2 | Run perception; check measurement quality by inspection | Verified sensor cues |
| 3 | Run all four conditions on identical frames | Instruction sets |
| 4 | Automated scoring; human validation sample | Scores and agreement statistics |
| 5 | Repeat with a smaller model | Model-size comparison (RQ3) |
| 6 | Analysis, written report, demonstration | Final deliverables |

Implementation commands and a day-by-day schedule are in `docs/WEEK_PLAN.md`.

## 8. Future work

- Participant studies with blind and low-vision users, replacing automated scoring with real judgments.
- Live camera input with spoken output, to test behavior under genuine timing pressure.
- Adding a non-speech audio channel and comparing it against spoken guidance.
- Training a small model on the outputs of a larger one under full context, to recover speed without losing quality.
- Applying the same approach to the group's drone work, where a planner would receive measured obstacle information in place of detector output.
