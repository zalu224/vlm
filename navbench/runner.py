"""nav run: every question of a task, `repeats` times, through one backend.

Output: runs/<model>/<task>.jsonl, one row per (qid, repeat). Resume-safe: existing
(qid, repeat) pairs are skipped, so a run can be stopped and continued, and `repeats` can be
raised later without redoing work. Seeds are the repeat index so the row is reproducible on
servers that honour a seed and simply varied on those that do not.
"""

from __future__ import annotations

import json
from pathlib import Path

from tqdm import tqdm

from .parse import parse_answer
from .questions import build_prompt


def _existing(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    done = set()
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            done.add((r["qid"], r["repeat"]))
    return done


def run_task(
    questions: dict[str, dict],
    task: str,
    backend,
    run_dir: Path,
    data_root: Path,
    *,
    repeats: int,
    model_name: str,
    tier: str | None = None,
    limit: int | None = None,
) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / f"{task}.jsonl"
    done = _existing(out)
    qs = [
        q for q in questions.values() if q["task"] == task and (tier is None or q["tier"] == tier)
    ]
    if limit:
        qs = qs[:limit]
    todo = [(q, k) for q in qs for k in range(repeats) if (q["qid"], k) not in done]
    with out.open("a") as fh:
        for q, k in tqdm(todo, desc=f"{model_name}/{task}", unit="call"):
            system, user = build_prompt(q)
            image = Path(data_root) / "images" / f"{q['image']}.jpg"
            reply = backend.generate(system, user, image, seed=k)
            parsed = (
                reply.text
                if q["answer_type"] == "free"
                else parse_answer(reply.text, q["answer_type"], q.get("choices"))
            )
            fh.write(
                json.dumps(
                    {
                        "model": model_name,
                        "task": task,
                        "qid": q["qid"],
                        "repeat": k,
                        "image": q["image"],
                        "system": system,
                        "prompt": user,
                        "output": reply.text,
                        "parsed": parsed,
                        "answer": q.get("answer"),
                        "correct": None if q["answer_type"] == "free" else parsed == q["answer"],
                        "latency_s": round(reply.latency_s, 3),
                        "prompt_tokens": reply.prompt_tokens,
                        "completion_tokens": reply.completion_tokens,
                    }
                )
                + "\n"
            )
            fh.flush()
    return out
