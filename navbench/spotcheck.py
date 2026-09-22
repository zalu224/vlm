"""Human spot-check of the LLM judge: a blinded sheet and Cohen's kappa per criterion.

The paper reports kappa 0.83 between two human annotators. Here one human (Aaron) rates a
random subset of judged outputs without seeing the model name or the judge's ratings; kappa
between the human and the judge bounds the judge as a proxy.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

CRITERIA = ("destination", "route", "obstacles")


def cohens_kappa(a: list, b: list) -> float | None:
    if len(a) != len(b) or not a:
        return None
    n = len(a)
    po = sum(1 for x, y in zip(a, b, strict=True) if x == y) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1.0 else round((po - pe) / (1 - pe), 3)


def write_sheet(judged_path: Path, questions: dict, out: Path, *, n: int = 40, seed: int = 0):
    rows = [json.loads(line) for line in Path(judged_path).read_text().splitlines() if line.strip()]
    rng = random.Random(seed)
    picked = rng.sample(rows, min(n, len(rows)))
    out = Path(out)
    key = out.with_name(out.stem + "_key.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh, key.open("w", newline="") as kh:
        w = csv.DictWriter(
            fh, fieldnames=["item", "image", "gold", "prompt", "output", *CRITERIA, "notes"]
        )
        k = csv.DictWriter(kh, fieldnames=["item", "model", "qid", "repeat"])
        w.writeheader()
        k.writeheader()
        for i, r in enumerate(picked, 1):
            item = f"{i:03d}"
            w.writerow(
                {
                    "item": item,
                    "image": r["image"],
                    "gold": questions[r["qid"]]["gold"],
                    "prompt": r["prompt"],
                    "output": r["output"],
                    **dict.fromkeys(CRITERIA, ""),
                    "notes": "",
                }
            )
            k.writerow({"item": item, "model": r["model"], "qid": r["qid"], "repeat": r["repeat"]})
    return out, key


def agreement(sheet: Path, key: Path, judged_path: Path) -> dict:
    human = {r["item"]: r for r in csv.DictReader(Path(sheet).open())}
    keys = list(csv.DictReader(Path(key).open()))
    judged = {}
    for line in Path(judged_path).read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            judged[(r["model"], r["qid"], int(r["repeat"]))] = r
    out = {}
    for c in CRITERIA:
        h, j = [], []
        for k in keys:
            row = human.get(k["item"])
            jr = judged.get((k["model"], k["qid"], int(k["repeat"])))
            if not row or not row.get(c, "").strip() or not jr or jr["ratings"].get(c) is None:
                continue
            h.append(row[c].strip().lower() == "yes")
            j.append(bool(jr["ratings"][c]))
        out[c] = {
            "n": len(h),
            "agreement": round(sum(x == y for x, y in zip(h, j, strict=True)) / len(h), 3)
            if h
            else None,
            "kappa": cohens_kappa(h, j),
        }
    return out
