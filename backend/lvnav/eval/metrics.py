"""Aggregate judged runs into a paired comparison report."""

from __future__ import annotations

import re
import statistics as st
from collections import Counter
from pathlib import Path

from ..pipeline import read_jsonl
from .rubric import DIMENSIONS


def _mean(xs: list[float]) -> float | None:
    return round(st.fmean(xs), 3) if xs else None


_SENTENCE_RE = re.compile(r"[.!?]+(?:\s|$)")


def conciseness_auto(instruction: str) -> int:
    """Model-free conciseness score on the rubric's 1-5 scale, from length and form only.

    5 = at most two sentences and at most 20 words; 4 = at most two sentences and at most
    30 words; 3 = at most three sentences and at most 45 words; 2 = up to 70 words;
    1 = longer, a list, or cut off mid-sentence. Used alongside the judged score so the
    dimension has an objective anchor.
    """
    text = instruction.strip()
    words = len(text.split())
    sentences = max(len(_SENTENCE_RE.findall(text)), 1)
    truncated = not text.endswith((".", "!", "?", '"'))
    is_list = bool(re.search(r"(^|\n)\s*(\d+\.|[-*•])\s", text))
    if truncated or is_list or words > 70:
        return 1
    if words > 45 or sentences > 3:
        return 2
    if words > 30 or sentences > 2:
        return 3
    if words > 20:
        return 4
    return 5


def summarise(judged: list[dict]) -> dict:
    out: dict = {"n": len(judged), "dimensions": {}, "latency_s": {}, "words": {}}
    for dim in DIMENSIONS:
        vals = [r["scores"][dim] for r in judged if r.get("scores", {}).get(dim) is not None]
        out["dimensions"][dim] = {"mean": _mean(vals), "n": len(vals)}
    lat = [r["latency_s"] for r in judged if r.get("latency_s") is not None]
    if lat:
        out["latency_s"] = {
            "median": round(st.median(lat), 3),
            "p90": round(sorted(lat)[int(0.9 * (len(lat) - 1))], 3),
            "mean": _mean(lat),
        }
    words = [len(r["instruction"].split()) for r in judged]
    out["words"] = {"mean": _mean(words), "max": max(words) if words else None}
    out["conciseness_auto"] = _mean([conciseness_auto(r["instruction"]) for r in judged])
    # Repetition: a condition that keeps emitting the same sentence regardless of the
    # scene has collapsed, even if each individual instruction scores well.
    counts = Counter(r["instruction"].strip() for r in judged)
    top, top_n = counts.most_common(1)[0] if counts else ("", 0)
    out["repetition"] = {
        "unique": len(counts),
        "unique_ratio": round(len(counts) / len(judged), 3) if judged else None,
        "top": top,
        "top_share": round(top_n / len(judged), 3) if judged else None,
    }
    out["overall"] = _mean([v["mean"] for v in out["dimensions"].values() if v["mean"] is not None])
    return out


def paired_deltas(a: list[dict], b: list[dict]) -> list[dict]:
    """Per-frame (b − a) overall score deltas for frames present in both runs."""
    by_id = {r["frame_id"]: r for r in a}
    rows = []
    for rb in b:
        ra = by_id.get(rb["frame_id"])
        if not ra:
            continue
        sa = [v for v in ra["scores"].values() if v is not None]
        sb = [v for v in rb["scores"].values() if v is not None]
        if not sa or not sb:
            continue
        rows.append(
            {
                "frame_id": rb["frame_id"],
                "delta": round(st.fmean(sb) - st.fmean(sa), 3),
                "a_instruction": ra["instruction"],
                "b_instruction": rb["instruction"],
                "cues": rb.get("cues") or ra.get("cues"),
            }
        )
    return rows


def write_report(run_a: Path, run_b: Path, out_path: Path | None = None) -> Path:
    run_a, run_b = Path(run_a), Path(run_b)
    a = read_jsonl(run_a / "judged.jsonl")
    b = read_jsonl(run_b / "judged.jsonl")
    sa, sb = summarise(a), summarise(b)
    deltas = paired_deltas(a, b)
    wins = sum(d["delta"] > 0 for d in deltas)
    losses = sum(d["delta"] < 0 for d in deltas)
    ties = len(deltas) - wins - losses

    lines = [
        f"# Paired comparison: `{run_a.name}` (A) vs `{run_b.name}` (B)",
        "",
        f"Frames judged: A = {sa['n']}, B = {sb['n']}, paired = {len(deltas)}.",
        f"B better on {wins} frames, worse on {losses}, tied on {ties}.",
        "",
        "## Rubric means (1–5, higher is better)",
        "",
        "| Dimension | A | B | Δ (B−A) |",
        "|---|---|---|---|",
    ]
    for dim in DIMENSIONS:
        ma, mb = sa["dimensions"][dim]["mean"], sb["dimensions"][dim]["mean"]
        d = round(mb - ma, 3) if ma is not None and mb is not None else None
        lines.append(f"| {dim.replace('_', ' ')} | {ma} | {mb} | {d} |")
    oa, ob = sa["overall"], sb["overall"]
    lines.append(
        f"| **overall** | **{oa}** | **{ob}** | **{round(ob - oa, 3) if oa and ob else None}** |"
    )

    lines += [
        "",
        "## Latency and length",
        "",
        "| Metric | A | B |",
        "|---|---|---|",
        f"| median latency (s) | {sa['latency_s'].get('median')} | {sb['latency_s'].get('median')} |",
        f"| p90 latency (s) | {sa['latency_s'].get('p90')} | {sb['latency_s'].get('p90')} |",
        f"| mean words / instruction | {sa['words']['mean']} | {sb['words']['mean']} |",
        f"| conciseness, computed (1–5) | {sa['conciseness_auto']} | {sb['conciseness_auto']} |",
        f"| unique instructions / frames | {sa['repetition']['unique_ratio']} | {sb['repetition']['unique_ratio']} |",
        f"| share of most common instruction | {sa['repetition']['top_share']} | {sb['repetition']['top_share']} |",
        "",
        f'Most common A: "{sa["repetition"]["top"]}"  ',
        f'Most common B: "{sb["repetition"]["top"]}"',
        "",
        "## Largest improvements (B over A)",
        "",
    ]
    for d in sorted(deltas, key=lambda x: -x["delta"])[:10]:
        lines += [
            f"**Frame {d['frame_id']}** (Δ {d['delta']:+.2f})",
            f"- cues: {d['cues']}",
            f"- A: {d['a_instruction']}",
            f"- B: {d['b_instruction']}",
            "",
        ]
    lines += ["## Largest regressions (B under A)", ""]
    for d in sorted(deltas, key=lambda x: x["delta"])[:5]:
        lines += [
            f"**Frame {d['frame_id']}** (Δ {d['delta']:+.2f})",
            f"- cues: {d['cues']}",
            f"- A: {d['a_instruction']}",
            f"- B: {d['b_instruction']}",
            "",
        ]

    out_path = out_path or (run_b / "report.md")
    out_path.write_text("\n".join(lines))
    return out_path
