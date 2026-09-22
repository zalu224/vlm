"""The committed question file: one row per (task, image[, variant]) with its answer."""

from __future__ import annotations

import json
from pathlib import Path

from . import prompts

PROMPTS = {
    "counting": prompts.COUNTING,
    "spatial": prompts.SPATIAL,
    "commonsense": prompts.COMMONSENSE,
}
ANSWER_TYPES = {
    "counting": "int",
    "spatial": "choice",
    "commonsense": "yesno",
    "navigation": "free",
}
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "questions" / "questions.jsonl"


def load_questions(path: Path | None = None) -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in Path(path or DEFAULT_PATH).read_text().splitlines()
        if line.strip()
    ]
    out: dict[str, dict] = {}
    for r in rows:
        if r["qid"] in out:
            raise ValueError(f"duplicate qid {r['qid']}")
        out[r["qid"]] = r
    return out


def validate_questions(
    questions: dict[str, dict], known_images: set[str] | None = None
) -> list[str]:
    problems = []
    for qid, q in questions.items():
        task = q.get("task")
        if task not in ANSWER_TYPES:
            problems.append(f"{qid}: unknown task {task!r}")
            continue
        if q.get("answer_type") != ANSWER_TYPES[task]:
            problems.append(f"{qid}: answer_type should be {ANSWER_TYPES[task]}")
        if q.get("tier") not in ("paper", "ext"):
            problems.append(f"{qid}: tier must be paper|ext")
        if known_images is not None and q.get("image") not in known_images:
            problems.append(f"{qid}: image {q.get('image')!r} missing from the manifest")
        a, at = q.get("answer"), q.get("answer_type")
        if at == "int" and not isinstance(a, int):
            problems.append(f"{qid}: answer must be an int")
        if at == "yesno" and a not in ("yes", "no"):
            problems.append(f"{qid}: answer must be yes|no")
        if at == "choice" and (not q.get("choices") or a not in q["choices"]):
            problems.append(f"{qid}: answer must be one of choices")
        if at == "free" and not q.get("gold"):
            problems.append(f"{qid}: navigation rows need a gold description")
        if not q.get("verified"):
            problems.append(f"{qid}: not verified by eye")
    return problems


def build_prompt(q: dict) -> tuple[str | None, str]:
    """(system, user) for a question row."""
    if q["task"] == "navigation":
        return prompts.NAVIGATION_SYSTEM, q.get("query") or prompts.NAVIGATION_QUERIES[0]
    return None, PROMPTS[q["task"]]
