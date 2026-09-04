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
