"""Metrics and the markdown report for the shelf study."""

from __future__ import annotations

import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

from .matcher import SearchVariant
from .search import load_jsonl


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.1f}%" if d else "–"


def search_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    recall = sum(1 for r in rows if r["detector_recall"])
    out = {
        "n_trials": n,
        "detector_recall": recall,
        "detector_recall_pct": _pct(recall, n),
        "mean_candidates": round(st.fmean([r["n_candidates"] for r in rows]), 1) if n else None,
        "median_latency_s": round(st.median([r["latency_s"] for r in rows]), 3) if n else None,
        "variants": {},
    }
    # Ranking accuracy is computed over trials the detector actually found, so that a
    # detector miss is not silently blamed on the matcher.
    found = [r for r in rows if r["detector_recall"]]
    for v in SearchVariant.all():
        key = v.value
        present = [r for r in found if key in r["variants"]]
        t1 = sum(1 for r in present if r["variants"][key]["top1"])
        t3 = sum(1 for r in present if r["variants"][key]["top3"])
        out["variants"][key] = {
            "n": len(present),
            "top1": t1,
            "top1_pct": _pct(t1, len(present)),
            "top3": t3,
            "top3_pct": _pct(t3, len(present)),
            "end_to_end_top1_pct": _pct(t1, n),
        }
    return out


def correction_metrics(rows: list[dict]) -> dict:
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    out: dict[str, dict] = {}
    for model, rs in by_model.items():
        pos = [r for r in rs if r["case"] == "positive"]
        neg = [r for r in rs if r["case"] == "negative"]
        correct = sum(1 for r in rs if r["correct"])
        false_confirms = sum(1 for r in rs if r["false_confirm"])
        unsure = sum(1 for r in rs if r["verdict"] == "unsure")
        parse_err = sum(1 for r in rs if r.get("parse_error"))
        out[model] = {
            "n": len(rs),
            "accuracy_pct": _pct(correct, len(rs)),
            "positive_n": len(pos),
            "confirm_rate_pct": _pct(sum(1 for r in pos if r["verdict"] == "yes"), len(pos)),
            "negative_n": len(neg),
            "false_confirm_n": false_confirms,
            "false_confirm_pct": _pct(false_confirms, len(neg)),
            "unsure_pct": _pct(unsure, len(rs)),
            "parse_error_n": parse_err,
            "median_latency_s": (round(st.median([r["latency_s"] for r in rs]), 3) if rs else None),
            "top_confusions": Counter(
                r["identified_as"].lower()
                for r in rs
                if r["case"] == "positive" and r["verdict"] == "no" and r["identified_as"]
            ).most_common(5),
        }
    return out


def write_report(search_path: Path, correction_paths: list[Path], out_path: Path) -> Path:
    srows = load_jsonl(search_path)
    sm = search_metrics(srows)
    crows: list[dict] = []
    for p in correction_paths:
        crows.extend(load_jsonl(p))
    cm = correction_metrics(crows) if crows else {}

    L: list[str] = [
        "# Last-Shelf: technical evaluation",
        "",
        f"Trials: **{sm['n_trials']}**. Detector recall (target enclosed by some box): "
        f"**{sm['detector_recall_pct']}** ({sm['detector_recall']}/{sm['n_trials']}). "
        f"Mean candidates per image: {sm['mean_candidates']}. "
        f"Median search latency: {sm['median_latency_s']} s.",
        "",
        "## Phase 1 — search (ablation)",
        "",
        "Ranking accuracy is over trials where the detector found the target, so detector"
        " misses are not charged to the matcher. End-to-end is over all trials.",
        "",
        "| Variant | n | Top-1 | Top-3 | End-to-end Top-1 |",
        "|---|---|---|---|---|",
    ]
    labels = {
        "det": "Detection only",
        "embed": "+ CLIP embedding",
        "embed+color": "+ colour histogram",
    }
    for key, m in sm["variants"].items():
        L.append(
            f"| {labels.get(key, key)} | {m['n']} | {m['top1_pct']} | {m['top3_pct']} "
            f"| {m['end_to_end_top1_pct']} |"
        )

    if cm:
        L += [
            "",
            "## Phase 3 — correction (VLM verification)",
            "",
            "Positives are the ground-truth crop; negatives are the highest-ranked wrong"
            " candidate, i.e. the item a user would most plausibly reach for by mistake."
            " **False confirm** — saying yes to a wrong item — is the safety-critical error.",
            "",
            "| Model | n | Accuracy | Confirm rate (pos) | False confirm (neg) | Unsure | Parse errors | Median latency |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for model, m in cm.items():
            L.append(
                f"| {model} | {m['n']} | {m['accuracy_pct']} | {m['confirm_rate_pct']} "
                f"| {m['false_confirm_pct']} ({m['false_confirm_n']}/{m['negative_n']}) "
                f"| {m['unsure_pct']} | {m['parse_error_n']} | {m['median_latency_s']} s |"
            )
        for model, m in cm.items():
            if m["top_confusions"]:
                L += ["", f"**{model} — most common misidentifications of the correct item**", ""]
                L += [f"- {name}: {count}" for name, count in m["top_confusions"]]

    L += [
        "",
        "## Failure cases worth showing",
        "",
    ]
    misses = [r for r in srows if not r["detector_recall"]][:5]
    if misses:
        L.append("Detector misses (no proposed box contains the target):")
        L += [f"- `{Path(r['image']).name}` — target {r['target_name']}" for r in misses]
    ranking_fails = [
        r
        for r in srows
        if r["detector_recall"] and not r["variants"].get("embed+color", {}).get("top1")
    ][:5]
    if ranking_fails:
        L += ["", "Ranking failures (found but not ranked first):"]
        L += [
            f"- `{Path(r['image']).name}` — target {r['target_name']}, "
            f"gt box {r['gt_box']}, predicted {r['variants']['embed+color']['pred_box']}"
            for r in ranking_fails
        ]

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L))
    return out_path
