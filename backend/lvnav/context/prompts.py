"""Prompt templates for the naive and context conditions.

Prompt versions are explicit so that results can be tied to the exact wording used.
When you change a prompt, bump the version key and record the change in
backend/README.md under "Prompt versions".
"""

from __future__ import annotations

from dataclasses import dataclass

NAIVE_SYSTEM = "You are a helpful assistant."

NAIVE_USER = (
    "This image is from a camera worn by a blind person who is walking. Tell them what to do next."
)

BLV_SYSTEM_V1 = """You are a sighted guide speaking into the earpiece of a person who is blind or has low vision while they walk. Your only job is to keep them safe and moving toward open space.

Rules:
1. Reply with at most two short sentences. The person hears you, they do not read you.
2. Lead with the most safety-critical fact (a hazard within a few steps), then the action.
3. Use body-relative directions the person can act on: "on your left", "directly ahead", "two steps ahead", "at knee height". Never use colours or visual detail they cannot use.
4. Only mention what is relevant to the next few seconds of walking. Do not describe the scene.
5. If the way ahead is clear, say so briefly and confirm the direction.
6. If you are unsure, say what you are unsure about rather than guessing.
7. Do not repeat the last instruction unless the situation has not changed."""

CONTEXT_USER_V1 = """Current frame is attached.
{cues_block}{memory_block}
Give the next instruction now."""

CUES_BLOCK_V1 = """
Sensor cues for this frame (from a depth estimator and object detector; treat as strong but not perfect evidence):
{cues}
"""

MEMORY_BLOCK_V1 = """
Scene memory:
{memory}
"""


@dataclass(frozen=True)
class Prompt:
    system: str
    user: str
    version: str


def build_naive_prompt() -> Prompt:
    return Prompt(system=NAIVE_SYSTEM, user=NAIVE_USER, version="naive-v1")


def build_context_prompt(
    cues_text: str | None = None,
    memory_text: str | None = None,
    version: str = "v1",
    label: str = "context",
) -> Prompt:
    """Build the guidance prompt with whichever context components are supplied.

    Passing only cues, only memory, or both gives the three non-naive conditions.
    The BLV system prompt is constant across all of them, so any measured difference
    is attributable to the context components rather than to the instruction style.
    """
    if version != "v1":
        raise ValueError(f"Unknown context prompt version: {version}")
    if cues_text is None and memory_text is None:
        raise ValueError("build_context_prompt needs at least one of cues_text or memory_text")
    return Prompt(
        system=BLV_SYSTEM_V1,
        user=CONTEXT_USER_V1.format(
            cues_block="" if cues_text is None else CUES_BLOCK_V1.format(cues=cues_text),
            memory_block="" if memory_text is None else MEMORY_BLOCK_V1.format(memory=memory_text),
        ),
        version=f"{label}-{version}",
    )
