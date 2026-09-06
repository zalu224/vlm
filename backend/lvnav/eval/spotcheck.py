"""Human spot-check tooling: a blinded scoring sheet and judge–human agreement.

The sheet interleaves frames from several runs in a shuffled order and hides which
run each row came from; the key file maps rows back. Cues shown on every row come
from whichever run has them (the context run), so the human scores both conditions
on the same evidence the judge saw.
"""

from __future__ import annotations

import csv
import random
import statistics as st
from pathlib import Path

from ..pipeline import read_jsonl
from .rubric import DIMENSIONS

SHEET_COLUMNS = ["item", "frame_id", "frame_path", "cues", "instruction", *DIMENSIONS, "notes"]


def write_blinded_sheet(
    runs: list[Path], out: Path, every: int = 8, seed: int = 0
) -> tuple[Path, Path]:
    """Write `<out>` (blinded sheet) and `<out stem>_key.csv`. Returns both paths."""
    runs = [Path(r) for r in runs]
    per_run = {r.name: read_jsonl(r / "records.jsonl")[::every] for r in runs}
    cues_by_frame: dict[str, str] = {}
    for rows in per_run.values():
        for rec in rows:
            if rec.get("cues"):
                cues_by_frame.setdefault(rec["frame_id"], rec["cues"])

    items = [(name, rec) for name, rows in per_run.items() for rec in rows]
    random.Random(seed).shuffle(items)

    out = Path(out)
    key_path = out.with_name(out.stem + "_key.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh, key_path.open("w", newline="") as kh:
        w = csv.DictWriter(fh, fieldnames=SHEET_COLUMNS)
        k = csv.DictWriter(kh, fieldnames=["item", "run", "frame_id"])
        w.writeheader()
        k.writeheader()
        for i, (name, rec) in enumerate(items, 1):
            item = f"{i:03d}"
            w.writerow(
                {
                    "item": item,
                    "frame_id": rec["frame_id"],
                    "frame_path": rec["frame_path"],
                    "cues": rec.get("cues") or cues_by_frame.get(rec["frame_id"], ""),
                    "instruction": rec["instruction"],
                    **dict.fromkeys(DIMENSIONS, ""),
                    "notes": "",
                }
            )
            k.writerow({"item": item, "run": name, "frame_id": rec["frame_id"]})
    return out, key_path


def _ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    return ranks


def spearman(a: list[float], b: list[float]) -> float | None:
    """Spearman rank correlation with average ranks for ties; None if undefined."""
    if len(a) != len(b) or len(a) < 3:
        return None
    ra, rb = _ranks(a), _ranks(b)
    if st.pvariance(ra) == 0 or st.pvariance(rb) == 0:
        return None
    return round(st.correlation(ra, rb), 3)


def agreement(
    sheet: Path, key: Path, results_root: Path, judged_name: str = "judged.jsonl"
) -> dict:
    """Judge–human agreement per dimension over the rows the human has scored.

    Returns {dimension: {"n": int, "rho": float | None, "mean_human": float,
    "mean_judge": float, "exact": float}} plus an "overall" entry on per-row means.
    """
    human = {r["item"]: r for r in csv.DictReader(Path(sheet).open())}
    key_rows = list(csv.DictReader(Path(key).open()))
    judged_cache: dict[str, dict[str, dict]] = {}
    pairs: dict[str, list[tuple[float, float]]] = {d: [] for d in DIMENSIONS}
    overall: list[tuple[float, float]] = []
    for k in key_rows:
        h = human.get(k["item"])
        if not h or not all(h.get(d, "").strip() for d in DIMENSIONS):
            continue
        run = k["run"]
        if run not in judged_cache:
            judged_cache[run] = {
                r["frame_id"]: r for r in read_jsonl(Path(results_root) / run / judged_name)
            }
        j = judged_cache[run].get(k["frame_id"])
        if not j or None in j["scores"].values():
            continue
        hs = {d: float(h[d]) for d in DIMENSIONS}
        for d in DIMENSIONS:
            pairs[d].append((hs[d], float(j["scores"][d])))
        overall.append((st.fmean(hs.values()), st.fmean(j["scores"].values())))

    def summary(ps: list[tuple[float, float]]) -> dict:
        if not ps:
            return {"n": 0, "rho": None, "mean_human": None, "mean_judge": None, "exact": None}
        a, b = [p[0] for p in ps], [p[1] for p in ps]
        return {
            "n": len(ps),
            "rho": spearman(a, b),
            "mean_human": round(st.fmean(a), 2),
            "mean_judge": round(st.fmean(b), 2),
            "exact": round(sum(x == y for x, y in ps) / len(ps), 2),
        }

    out = {d: summary(pairs[d]) for d in DIMENSIONS}
    out["overall"] = summary(overall)
    return out
