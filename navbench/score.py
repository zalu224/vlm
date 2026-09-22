"""Accuracy, mean and variance per question, task and scene, as in the paper."""

from __future__ import annotations

import statistics as st
from collections import defaultdict


def _acc(rows: list[dict], answer) -> float:
    return round(sum(1 for r in rows if r["parsed"] == answer) / len(rows), 3) if rows else 0.0


def score_rows(rows: list[dict], questions: dict[str, dict]) -> dict:
    by_qid: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_qid[r["qid"]].append(r)
    out_q, task_rows = {}, defaultdict(list)
    for qid, rs in by_qid.items():
        q = questions[qid]
        entry = {
            "task": q["task"],
            "scene": q.get("scene"),
            "answer": q["answer"],
            "n": len(rs),
            "accuracy": _acc(rs, q["answer"]),
            "parse_fail": sum(1 for r in rs if r["parsed"] is None),
        }
        if q["answer_type"] == "int":
            vals = [r["parsed"] for r in rs if isinstance(r["parsed"], int)]
            entry["mean"] = round(st.fmean(vals), 3) if vals else None
            entry["variance"] = round(st.pvariance(vals), 3) if len(vals) > 1 else 0.0
        out_q[qid] = entry
        task_rows[q["task"]].append((rs, q["answer"]))
    by_task = {}
    for task, items in task_rows.items():
        n = sum(len(rs) for rs, _ in items)
        correct = sum(1 for rs, a in items for r in rs if r["parsed"] == a)
        by_task[task] = {
            "n": n,
            "accuracy": round(correct / n, 3) if n else 0.0,
            "questions": len(items),
        }
    return {"by_qid": out_q, "by_task": by_task}


def score_all(runs_root, questions: dict[str, dict]) -> dict:
    """Every runs/<model>/<task>.jsonl with a scored answer type -> {model: score_rows(...)}."""
    import json
    from pathlib import Path

    out = {}
    for model_dir in sorted(p for p in Path(runs_root).iterdir() if p.is_dir()):
        rows = []
        for task in ("counting", "spatial", "commonsense"):
            f = model_dir / f"{task}.jsonl"
            if f.exists():
                rows += [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
        rows = [r for r in rows if r["qid"] in questions]
        if rows:
            out[model_dir.name] = score_rows(rows, questions)
    return out
