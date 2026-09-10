# Research Proposal

## Vision-Language Models for Low-Vision Assistance: Finding Objects and Guiding Movement

**Field:** Human-centered AI, accessibility, computer vision
**Format:** Two studies, run in sequence
**Deliverables:** Reproducible codebase, measured results on both studies, written report, live demonstration

---

## 1. Summary

People who are blind or have low vision (pBLV) face two everyday problems that current technology handles poorly:

1. **Finding a specific object.** Existing aids can announce "there is a jar" but not "that is *your* cinnamon, not the paprika next to it."
2. **Moving safely through space.** Existing aids describe a scene fluently but rarely say the one thing a person needs to hear in the next two seconds.

Vision-language models (VLMs) are strong at describing images and weak at both of these tasks. This proposal tests a specific idea for closing that gap: rather than using a larger model, **give a smaller model better-structured information** — object locations from a detector, distances from a depth estimator, and a memory of what was just said. We call this *context engineering*.

We run two studies. **Study 1** is object retrieval on shelves, evaluated on still photographs. **Study 2** is walking guidance, evaluated on video from a body-worn camera. Study 1 is faster and comes first.

## 2. Background

Recent evaluations of leading VLMs on navigation assistance for pBLV report three recurring failures: unreliable spatial reasoning (confusing left and right, misjudging distance), output that is too long or descriptive to be useful when spoken aloud, and poor alignment with what a blind user actually needs. The same work notes that most benchmarks use isolated still images and calls for evaluation on continuous video from wearable devices.

Separately, work on aerial robotics has shown that VLM reasoning becomes markedly more reliable when the model is fed structured information from small, cheap perception modules instead of being asked to infer everything from raw pixels. Our studies test whether the same principle holds for assistive technology.

Study 1 builds directly on Ruan et al. (2026), a wearable system for helping pBLV locate products in stores. Their pipeline combines open-vocabulary object detection with visual matching to find an item, then uses a VLM to confirm the user reached the right one. We replicate the finding and verification stages on household objects, and extend their work by testing how far the model can be reduced before the system stops working.

## 3. Research questions

Each question below states what is being asked, what will be measured, and what we expect to find.

### RQ1 — Does visual matching actually help find a specific object?

An object detector can propose "there is a box here" but has no notion of *which* box was requested. We add two matching signals on top of detection: similarity between the image and reference photos of the target, and similarity of color distribution.

- **Measured by:** how often the correct object is ranked first (top-1 accuracy), compared across three settings — detection alone, detection plus visual matching, and detection plus visual matching plus color.
- **Expected:** detection alone performs near chance when several similar containers are visible; visual matching produces a large improvement; color adds a small further gain, mainly on same-shape items in different packaging.

### RQ2 — Can a VLM reliably tell the user they have the wrong object?

After the system points a user toward an object, it must verify what they actually reached for. This is the safety-critical step: telling someone "yes, that is your medication" when it is not is far worse than saying "I am not sure."

- **Measured by:** verification accuracy, and separately the **false-confirmation rate** — how often the model approves the wrong object. Both are measured on correct objects and on deliberately confusable ones.
- **Expected:** overall accuracy will look acceptable while false confirmations remain too high for deployment, because confirming is the model's default behavior.

### RQ3 — How small can the model be before the system breaks, and which part breaks first?

Assistive devices are worn, so the model should be small enough to run on the device itself. We compare a larger and a smaller VLM across both tasks.

- **Measured by:** the change in accuracy and response time for each stage when moving from the larger to the smaller model.
- **Expected:** finding objects degrades gently, because the spatial work is done by the detector rather than the VLM. Verification degrades sharply, because it requires reading small printed labels. If confirmed, this identifies fine-grained visual discrimination — not spatial reasoning — as the real bottleneck for wearable assistive vision.

### RQ4 — Does structured context improve spoken walking guidance?

For walking, we compare two ways of prompting the same model on the same video frames: a plain request to describe what to do, versus a prompt containing explicit obstacle positions, distances, walkable space, and a short memory of the last few seconds.

- **Measured by:** five qualities of each spoken instruction, scored 1–5: safety, actionability, spatial accuracy, brevity, and freedom from invented details. Also response time.
- **Expected:** the largest gain is in spatial accuracy, since explicit measurements remove the model's need to estimate geometry from a single image. Instructions should also become shorter, which matters because they are heard rather than read.

## 4. Study 1 — Finding and verifying household objects

**Materials.** Roughly 20 household objects, chosen to be genuinely difficult: several same-brand items in different varieties (two soup cans, two cereal boxes), a spice rack whose jars differ only by their labels, and a few clearly distinct items as controls. Approximately 200 photographs of these objects on shelves, varied by distance, lighting, viewing angle, and partial blocking. Two or three reference photographs per object.

**Procedure.**
1. An object detector proposes candidate regions in each photograph.
2. Each candidate is scored against the requested object using visual similarity and color.
3. A human marks which candidate is correct, giving ground truth. This is the only manual step.
4. The VLM is shown the correct object and asked to verify it, then shown the most convincing wrong candidate and asked again.

**What this design gets right.** Detection failures are reported separately from ranking failures, so a missed object is never blamed on the matching stage. The wrong candidates used for verification are the ones the system itself ranked highest, which is what a user would most plausibly reach for by mistake — a harder and more realistic test than a randomly chosen object.

## 5. Study 2 — Walking guidance

**Materials.** Video from a body-worn camera covering an indoor corridor, a sidewalk with pedestrians, and a street crossing. Frames are sampled once per second.

**Procedure.** Each frame is processed twice by the same model: once with a plain prompt, once with a prompt containing measured obstacle positions, walkable space, and recent history. Both instructions are then scored on the five qualities in RQ4 by an automated evaluator that sees the image and the measurements but not the prompts, so neither condition is favored.

**Validation.** Because the automated evaluator is itself a model, a person independently scores a sample of about 40 frames. We report the agreement between human and automated scores for each quality and flag any quality where agreement is weak.

## 6. Limitations

- **No pBLV participants.** Neither study involves blind or low-vision participants, so we measure system behavior, not usefulness. Participant studies require ethical approval and are the natural next step.
- **Automated scoring is a proxy.** The human validation sample bounds how much confidence to place in it, but does not replace it.
- **Sample size.** With roughly 200 trials per study, differences of a few percentage points are not meaningful and will be reported as such.
- **Not comparable to published numbers.** Different objects, models, and settings mean our results replicate the *structure* of prior findings, not their exact values.
- **Not a usable device.** These are research probes and must not be relied on for real navigation.

## 7. Plan

| Phase | Work | Output |
|---|---|---|
| 1 | Collect objects, reference photographs, and shelf images | Study 1 dataset |
| 2 | Run detection, mark ground truth, run matching | Study 1 finding results (RQ1) |
| 3 | Run verification at both model sizes | Study 1 verification results (RQ2, RQ3) |
| 4 | Record walking video; run both prompting conditions | Study 2 outputs |
| 5 | Automated scoring and human validation | Study 2 results (RQ4) |
| 6 | Analysis, written report, demonstration | Final deliverables |

Study 1 (phases 1–3) is self-contained and produces publishable results on its own.

## 8. Future work

- Participant studies with pBLV users, replacing automated scoring with real judgments.
- Adding the audio guidance channel from the original system, and comparing speech against non-speech sound.
- Live camera input with spoken output, to test behavior under real timing pressure.
- Training a small model on the outputs of the larger one, to recover speed without losing accuracy.
- Applying the same context-engineering approach to the group's drone work, where measured obstacle information would be supplied to a planner in place of detector output.
