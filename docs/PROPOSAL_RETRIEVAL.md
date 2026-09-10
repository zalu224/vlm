# Research Proposal

## Finding and Verifying Specific Objects for Blind and Low-Vision Users

**Field:** Human-centered AI, accessibility, computer vision
**Setting:** Household objects photographed on domestic shelves
**Deliverables:** Reproducible codebase, measured results on three research questions, written report, live demonstration

---

## 1. Summary

Wayfinding technology can bring a blind shopper to the right aisle. It cannot bring them to the right jar. That final stretch — the *last meter* — is where assistive vision currently fails: a system can announce "there is a jar here" without being able to say whether it is the cinnamon or the paprika sitting beside it.

This study builds a system for that problem and measures how well it works. Given a request for a specific object, it finds the object among visually similar neighbors, then verifies that the object the user actually reached for is the right one. It also asks how small the underlying model can be before the system stops working — a question that decides whether such a system can run on a wearable device rather than in the cloud.

## 2. Background

This study builds directly on Ruan et al. (2026), a wearable system for helping blind and low-vision users locate and retrieve products in stores. Their pipeline has three stages: find the product using open-vocabulary object detection combined with visual and color matching; guide the user's hand toward it using audio and spoken description; and verify that the object reached is the correct one, correcting the user when it is not. They report detection near-perfect at close range, spoken guidance up to 94.4% accurate, and verification above 86% in their best configuration.

We replicate the **finding** and **verification** stages on household objects photographed on domestic shelves. The guidance stage is not replicated: it requires a user in motion and cannot be measured from photographs.

Using a home setting rather than a store is a deliberate simplification, and it costs less than it might appear. The visual problem is the same one — a shelf of packaged goods where several items share a brand, a shape, and a color scheme, and differ only in a printed word. A domestic pantry supplies that difficulty directly, while removing the logistics of photographing in a shop. What it does not supply is scale, unfamiliar packaging, and the visual noise of a retail aisle, and the write-up says so.

Two extensions distinguish this study from a straight replication. First, the finding stage is broken into an ablation, so the contribution of each matching signal is measured rather than assumed. Second, the whole pipeline is run at two model sizes, to locate which stage fails first under compute constraints.

## 3. Research questions

### RQ1 — Does visual matching actually help find a specific object?

An object detector proposes "there is a box here" but has no notion of *which* box was requested. Two matching signals are added on top: similarity between the candidate and reference photographs of the target, and similarity of color distribution.

- **Measured by:** how often the correct object is ranked first, compared across three settings — detection alone, detection plus visual matching, and detection plus visual matching plus color.
- **Expected:** detection alone performs near chance whenever several similar containers are visible, since it has no way to prefer one. Visual matching produces a large improvement. Color adds a small further gain, concentrated on items of identical shape in differently colored packaging — precisely the same-brand, different-variety case that is hardest.

### RQ2 — Can a VLM reliably tell the user they have the wrong object?

After the system points a user toward an object, it must confirm what they actually picked up. The two possible errors are not equally serious: telling someone "yes, that is your medication" when it is not is far worse than saying "I am not sure."

- **Measured by:** verification accuracy, and separately the **false-confirmation rate** — how often the model approves an incorrect object. Both are measured on correct objects and on deliberately confusable ones.
- **Expected:** overall accuracy will appear acceptable while false confirmations remain too high for deployment, because agreement is a model's default behavior. Reporting a single accuracy figure would hide this, which is why the two are separated.

### RQ3 — How small can the model be, and which stage breaks first?

An assistive device is worn, so the model should ideally run on the device. We repeat both stages with a smaller model.

- **Measured by:** the change in ranking accuracy, verification accuracy, false-confirmation rate, and response time when moving from the larger model to the smaller one.
- **Expected:** finding degrades gently, because the spatial work is done by the detector rather than by the model. Verification degrades sharply, because it requires reading small printed labels. If confirmed, this identifies fine-grained visual discrimination — not spatial reasoning — as the real bottleneck for wearable assistive vision, which is a concrete finding for anyone designing such a device.

## 4. Method

**Objects.** Roughly 20 household objects in three groups, chosen to be genuinely difficult rather than conveniently distinct:

| Group | Count | Purpose |
|---|---|---|
| Confusable pairs — same brand, different variety; identical spice jars differing only by label | 10–12 | The core of the study; where detection alone must fail |
| Same shape, different packaging color | 4–5 | Isolates what color contributes once visual matching works |
| Clearly distinct controls | 3–4 | If these are not near-perfect, the setup is broken rather than the method interesting |

A collection of obviously different objects would let every method score near-perfectly and would measure nothing. The difficulty of the object set is a design decision, not an accident of what was in the cupboard.

**Images.** Roughly 200 photographs on domestic shelves, varied systematically by distance (approximately 0.5, 1.0 and 1.5 meters, following the original study's distance analysis), lighting (bright, normal, dim), and viewing angle. About a fifth are deliberately harder: an object partly hidden, a label turned away, two confusable items side by side, an unusually crowded shelf. Objects are not centered in frame, since a real system would not have that cue. Two or three reference photographs of each object are taken separately against a plain background.

Full capture protocol, naming convention, and validation steps: `docs/MATERIALS.md`.

**Procedure.**
1. An open-vocabulary detector proposes candidate regions in each photograph. Detection runs once and is reused by every later stage, so the ablation arms are compared on identical candidates.
2. Each candidate is scored against the requested object by visual similarity and color similarity, and the candidates are ranked.
3. A person marks which candidate is correct, or marks that the detector missed the object entirely. This is the only manual step in the study, and takes roughly 30 minutes for the full set.
4. The model is shown the correct object and asked to verify it, then shown the highest-ranked *incorrect* candidate and asked again.

## 5. Evaluation

**Detection failures are separated from ranking failures.** If no proposed candidate contains the target, that is a failure of the detector, not of the matching stage. Both are reported: ranking accuracy among objects the detector found, and end-to-end accuracy over all trials. A single combined figure would obscure which component needs work.

**Wrong candidates are chosen adversarially.** The incorrect object used in verification is whichever candidate the system itself ranked highest among the wrong ones — the object a user would most plausibly reach for by mistake. This is a harder and more realistic test than a randomly selected distractor, and it costs no extra annotation because the ranking already exists.

**The model may decline to answer.** The verification prompt offers three responses — yes, no, and unsure — so a model that cannot read a label has somewhere to go besides guessing. The rate of unsure responses is reported alongside accuracy, since a system that admits uncertainty is more useful than one that guesses confidently.

## 6. Limitations

- **No blind or low-vision participants.** This study measures system behavior on photographs, not usefulness to a user. Participant studies require ethical approval and are the necessary next step.
- **Not comparable to the original numbers.** Different objects, different models, and a home rather than a store mean this replicates the *structure* of the prior findings, not their values. The published figures should not be treated as a target.
- **Reference photographs are clean.** Reference images are frontal and well lit while shelf crops are neither. That gap is a limitation of the setup, not a result about matching.
- **Sample size.** With roughly 200 trials, differences of a few percentage points between ablation arms are not meaningful and will be reported as such.
- **Static images.** Photographs remove motion blur, camera shake, and the timing pressure of a real reach. Results are an upper bound on live performance.
- **Domestic rather than retail.** A home pantry reproduces the visual difficulty of the original problem but not its scale or the unfamiliarity of store packaging. Findings should be read as applying to known objects in a familiar space.

## 7. Plan

| Phase | Work | Output |
|---|---|---|
| 1 | Select objects; photograph references and shelf images; validate the dataset | Dataset |
| 2 | Run detection; mark ground truth | Annotated trials |
| 3 | Run matching across all three ablation arms | Finding results (RQ1) |
| 4 | Run verification at the larger model size | Verification results (RQ2) |
| 5 | Repeat both stages with the smaller model | Model-size comparison (RQ3) |
| 6 | Analysis, written report, demonstration | Final deliverables |

Phases 1–4 are self-contained and produce a complete result on their own; phase 5 strengthens it. Materials and capture protocol are in `docs/MATERIALS.md`; implementation commands and the detailed schedule are in `docs/LASTSHELF.md`.

## 8. Future work

- Participant studies with blind and low-vision users, measuring retrieval success and time rather than ranking accuracy.
- Adding the audio guidance stage from the original system, and comparing non-speech sound against spoken direction.
- Live camera input, to measure the loss from motion blur and reaching in real time.
- Extending the object set beyond packaged goods to unlabeled objects, where visual matching has no printed text to rely on.
- Training a small model on the larger model's verification outputs, to recover accuracy at wearable scale.
