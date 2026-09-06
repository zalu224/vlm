"""BLV navigation-instruction rubric and the judge prompt built from it.

Dimensions are scored 1–5. Higher is always better, including `hallucination`
(5 = nothing invented). Rationale for each dimension lives in docs/RUBRIC.md.
"""

from __future__ import annotations

DIMENSIONS: dict[str, str] = {
    "safety": (
        "Does the instruction surface the most safety-critical hazard within the next few steps "
        "first, and would following it keep the person safe?"
    ),
    "actionability": (
        "Can a blind person act on it immediately? Body-relative directions, a clear verb, "
        "no ambiguity about what to do."
    ),
    "spatial_accuracy": (
        "Are the stated positions and distances of objects consistent with the image and the "
        "sensor cues (left/centre/right, near/mid/far)?"
    ),
    "conciseness": (
        "Is it as short as it can be for spoken delivery (ideally one or two short sentences) "
        "with no scene description or filler?"
    ),
    "hallucination": (
        "Does it avoid mentioning objects, hazards or directions that are not supported by the "
        "image or cues? 5 = nothing invented, 1 = mostly invented."
    ),
}

JUDGE_SYSTEM = (
    "You are an accessibility researcher who evaluates spoken navigation instructions for people "
    "who are blind or have low vision. You are strict, consistent, and you score only what is "
    "in front of you."
)

JUDGE_USER = """Evaluate one navigation instruction generated for a blind pedestrian.

The image is attached. Independent sensor cues for the same frame (from a depth estimator and object detector) are:
{cues}

Instruction to evaluate:
\"\"\"{instruction}\"\"\"

Score each dimension from 1 (poor) to 5 (excellent):
{dimension_block}

Return ONLY a JSON object with this exact shape and no other text:
{{"scores": {{"safety": <1-5>, "actionability": <1-5>, "spatial_accuracy": <1-5>, "conciseness": <1-5>, "hallucination": <1-5>}}, "rationale": "<one or two sentences>"}}"""


def dimension_block() -> str:
    return "\n".join(f"- {k}: {v}" for k, v in DIMENSIONS.items())


def build_judge_prompt(instruction: str, cues: str | None) -> tuple[str, str]:
    user = JUDGE_USER.format(
        cues=cues or "(no sensor cues were computed for this frame)",
        instruction=instruction,
        dimension_block=dimension_block(),
    )
    return JUDGE_SYSTEM, user


# ---------------------------------------------------------------------------- v2
# v1 (above) produced halo-effect scoring with Qwen2.5-VL-7B: on ~50 % of context frames
# all five dimensions were identical, an 8-word instruction was scored 1/5 on conciseness,
# and rationales contradicted the numbers. v2 forces a one-line reason *before* each score,
# states that dimensions are independent, and gives length-based anchors for conciseness so
# that dimension cannot absorb the judge's overall opinion. Both versions are kept so results
# can be tied to the exact judge prompt (`judge_version` in config).

JUDGE_SYSTEM_V2 = (
    "You are an accessibility researcher who evaluates spoken navigation instructions for people "
    "who are blind or have low vision. You score five INDEPENDENT dimensions. A bad instruction "
    "can still be concise; a safe instruction can still be spatially wrong. Never let your overall "
    "opinion leak from one dimension into another. Write the reason first, then the score."
)

JUDGE_USER_V2 = """Evaluate one navigation instruction generated for a blind pedestrian.

The image is attached. Independent sensor cues for the same frame (from a depth estimator and object detector) are:
{cues}

Instruction to evaluate:
\"\"\"{instruction}\"\"\"

Score each dimension from 1 to 5. Scoring anchors:
- safety: 5 = names the most safety-critical hazard within a few steps first and the action keeps the person safe; 3 = safe action but a relevant near hazard is unmentioned; 1 = directs the person into a hazard or ignores an imminent one.
- actionability: 5 = a concrete verb plus a body-relative direction (left / right / ahead / stop); 3 = a verb but vague direction; 1 = description only, or asks the person to look or read.
- spatial_accuracy: 5 = every stated side and distance matches the image and cues; 3 = one error; 1 = wrong side or wrong distance for the main object. If nothing spatial is stated, score 3.
- conciseness: judge LENGTH AND FORM ONLY, ignoring whether it is correct. 5 = at most two short sentences, no scene description; 4 = two sentences with a little extra; 3 = three sentences or some description; 2 = a paragraph; 1 = a long paragraph, a list, or cut off mid-sentence.
- hallucination: list the objects, hazards and directions the instruction mentions; 5 = all are supported by the image or cues; 3 = one unsupported; 1 = most are unsupported.

Return ONLY a JSON object with this exact shape and no other text:
{{"safety": {{"reason": "<one sentence>", "score": <1-5>}}, "actionability": {{"reason": "<one sentence>", "score": <1-5>}}, "spatial_accuracy": {{"reason": "<one sentence>", "score": <1-5>}}, "conciseness": {{"reason": "<one sentence>", "score": <1-5>}}, "hallucination": {{"reason": "<one sentence>", "score": <1-5>}}}}"""


def build_judge_prompt_v2(instruction: str, cues: str | None) -> tuple[str, str]:
    user = JUDGE_USER_V2.format(
        cues=cues or "(no sensor cues were computed for this frame)", instruction=instruction
    )
    return JUDGE_SYSTEM_V2, user


JUDGE_VERSIONS = {"v1": build_judge_prompt, "v2": build_judge_prompt_v2}
