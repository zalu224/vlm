"""Build the figures and data tables for docs/paper from results/.

Usage (from the repo root, with the venv active):
    python backend/scripts/make_paper.py [--results results] [--out docs/paper]

Reads records.jsonl / judged*.jsonl for the eight study runs plus the two latency
runs, writes:
    docs/paper/data/*.csv, summary.json      per-frame scores and aggregates
    docs/paper/figures/*.png                 charts and annotated frame panels
    docs/paper/reports/*.md                  copies of the paired reports
Everything is deterministic given results/, so the paper can be rebuilt.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import statistics as st
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lvnav.eval.metrics import conciseness_auto  # noqa: E402
from lvnav.eval.rubric import DIMENSIONS  # noqa: E402

DIMS = list(DIMENSIONS)
DIM_LABEL = {
    "safety": "Safety",
    "actionability": "Actionability",
    "spatial_accuracy": "Spatial accuracy",
    "conciseness": "Conciseness",
    "hallucination": "Hallucination\n(higher = fewer)",
}
WALKS = ["suwon", "london"]
ARMS = ["naive", "context", "context_v1_nomem", "context_v2_nomem"]
ARM_LABEL = {
    "naive": "naive",
    "context": "context-v1",
    "context_v1_nomem": "context-v1, no echo",
    "context_v2_nomem": "context-v2, no echo",
}
# Reference categorical palette, slots 1-4 in fixed order (validated, see dataviz skill).
ARM_COLOR = {
    "naive": "#2a78d6",
    "context": "#eb6834",
    "context_v1_nomem": "#1baf7a",
    "context_v2_nomem": "#eda100",
}
INK, INK2, MUTED, GRID, BASE, SURFACE = (
    "#0b0b0b",
    "#52514e",
    "#898781",
    "#e1e0d9",
    "#c3c2b7",
    "#fcfcfb",
)
V2_NAME = "judged_v2_every4.jsonl"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.edgecolor": BASE,
        "axes.labelcolor": INK2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "savefig.dpi": 180,
    }
)


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.open() if line.strip()]


def complete(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("scores") and None not in r["scores"].values()]


def overall(r: dict) -> float:
    return st.fmean(r["scores"].values())


def ci95(xs: list[float]) -> tuple[float, float, float]:
    m = st.fmean(xs)
    se = st.stdev(xs) / len(xs) ** 0.5 if len(xs) > 1 else 0.0
    return m, m - 1.96 * se, m + 1.96 * se


# ------------------------------------------------------------------------------ data
def load_all(results: Path) -> dict:
    d: dict = {"records": {}, "v1": {}, "v2": {}}
    for w in WALKS:
        for a in ARMS:
            run = results / f"{w}_{a}"
            d["records"][(w, a)] = read_jsonl(run / "records.jsonl")
            d["v1"][(w, a)] = read_jsonl(run / "judged.jsonl")
            d["v2"][(w, a)] = read_jsonl(run / V2_NAME)
    for name in ("latency_naive", "latency_v2_nomem"):
        p = results / name / "records.jsonl"
        d["records"][("latency", name)] = read_jsonl(p) if p.exists() else []
    return d


def export_data(d: dict, out: Path) -> dict:
    data = out / "data"
    data.mkdir(parents=True, exist_ok=True)
    for judge in ("v1", "v2"):
        with (data / f"scores_judge_{judge}.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["walk", "arm", "frame_id", *DIMS, "instruction", "cues", "judge_rationale"])
            for (walk, arm), rows in d[judge].items():
                for r in rows:
                    w.writerow(
                        [walk, ARM_LABEL[arm], r["frame_id"]]
                        + [r["scores"].get(k) for k in DIMS]
                        + [r["instruction"], r.get("cues") or "", r.get("judge_rationale", "")]
                    )
    summary: dict = {"arms": {}, "paired_v2_nomem_minus_naive": {}, "latency": {}}
    gen_rows = []
    for (walk, arm), rows in d["records"].items():
        if walk == "latency":
            continue
        ins = [r["instruction"] for r in rows]
        low = [i.lower() for i in ins]
        cnt = Counter(ins)
        v1 = complete(d["v1"][(walk, arm)])
        v2 = complete(d["v2"][(walk, arm)])
        entry = {
            "n_frames": len(rows),
            "median_vlm_latency_s": round(st.median(r["latency_s"] for r in rows), 2),
            "mean_words": round(st.fmean(len(i.split()) for i in ins), 1),
            "unique_ratio": round(len(cnt) / len(rows), 3),
            "top_share": round(cnt.most_common(1)[0][1] / len(rows), 3),
            "stop_rate": round(sum("stop" in i for i in low) / len(rows), 3),
            "slow_rate": round(sum("slow" in i for i in low) / len(rows), 3),
            "side_rate": round(sum(("left" in i or "right" in i) for i in low) / len(rows), 3),
            "cap_hit_rate": round(
                sum(r.get("completion_tokens") == 80 for r in rows) / len(rows), 3
            ),
            "conciseness_auto": round(st.fmean(conciseness_auto(i) for i in ins), 2),
            "judge_v1": {k: round(st.fmean(r["scores"][k] for r in v1), 2) for k in DIMS},
            "judge_v2": {k: round(st.fmean(r["scores"][k] for r in v2), 2) for k in DIMS},
            "judge_v1_n": len(v1),
            "judge_v2_n": len(v2),
            "judge_v1_uniform_share": round(
                sum(len(set(r["scores"].values())) == 1 for r in v1) / len(v1), 3
            ),
            "judge_v2_uniform_share": round(
                sum(len(set(r["scores"].values())) == 1 for r in v2) / len(v2), 3
            ),
        }
        entry["judge_v1"]["overall"] = round(st.fmean(entry["judge_v1"][k] for k in DIMS), 2)
        entry["judge_v2"]["overall"] = round(st.fmean(entry["judge_v2"][k] for k in DIMS), 2)
        summary["arms"][f"{walk}_{arm}"] = entry
        gen_rows.append(
            [walk, ARM_LABEL[arm]]
            + [
                entry[k]
                for k in (
                    "n_frames",
                    "median_vlm_latency_s",
                    "mean_words",
                    "unique_ratio",
                    "top_share",
                    "stop_rate",
                    "slow_rate",
                    "side_rate",
                    "cap_hit_rate",
                    "conciseness_auto",
                )
            ]
        )
    with (data / "generation_stats.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "walk",
                "arm",
                "n_frames",
                "median_vlm_latency_s",
                "mean_words",
                "unique_ratio",
                "top_share",
                "stop_rate",
                "slow_rate",
                "side_rate",
                "cap_hit_rate",
                "conciseness_auto",
            ]
        )
        w.writerows(gen_rows)
    # paired deltas, pooled, judge v2
    for k in DIMS + ["overall"]:
        deltas = []
        for w in WALKS:
            nav = {r["frame_id"]: r for r in complete(d["v2"][(w, "naive")])}
            for r in complete(d["v2"][(w, "context_v2_nomem")]):
                a = nav.get(r["frame_id"])
                if not a:
                    continue
                deltas.append(
                    overall(r) - overall(a) if k == "overall" else r["scores"][k] - a["scores"][k]
                )
        m, lo, hi = ci95(deltas)
        summary["paired_v2_nomem_minus_naive"][k] = {
            "n": len(deltas),
            "mean": round(m, 3),
            "ci95": [round(lo, 3), round(hi, 3)],
            "better": sum(x > 0 for x in deltas),
            "worse": sum(x < 0 for x in deltas),
        }
    for name in ("latency_naive", "latency_v2_nomem"):
        rows = d["records"][("latency", name)]
        if rows:
            lat = sorted(r["latency_s"] for r in rows)
            summary["latency"][name] = {
                "n": len(rows),
                "median_s": round(st.median(lat), 2),
                "p90_s": round(lat[int(0.9 * (len(lat) - 1))], 2),
                "prompt_tokens": round(st.fmean(r["prompt_tokens"] for r in rows)),
                "completion_tokens": round(st.fmean(r["completion_tokens"] for r in rows)),
            }
    (data / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def copy_reports(results: Path, out: Path) -> None:
    rep = out / "reports"
    rep.mkdir(parents=True, exist_ok=True)
    for w in WALKS:
        for a in ARMS[1:]:
            for name in ("report.md", "report_v2_every4.md"):
                src = results / f"{w}_{a}" / name
                if src.exists():
                    shutil.copy(src, rep / f"{w}_{a}_{name}")


# --------------------------------------------------------------------------- figures
def fig_dumbbell(summary: dict, out: Path) -> None:
    """Fig 2: naive -> context-v2-nomem per dimension, pooled judge v2."""
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    pooled = {}
    for k in DIMS:
        a = [summary["arms"][f"{w}_naive"]["judge_v2"][k] for w in WALKS]
        b = [summary["arms"][f"{w}_context_v2_nomem"]["judge_v2"][k] for w in WALKS]
        pooled[k] = (st.fmean(a), st.fmean(b))
    ys = list(range(len(DIMS)))[::-1]
    for y, k in zip(ys, DIMS, strict=True):
        a, b = pooled[k]
        ax.plot([a, b], [y, y], color=GRID, linewidth=2, zorder=1)
        ax.scatter(
            [a], [y], s=70, color=ARM_COLOR["naive"], zorder=3, edgecolor=SURFACE, linewidth=1.5
        )
        ax.scatter(
            [b],
            [y],
            s=70,
            color=ARM_COLOR["context_v2_nomem"],
            zorder=3,
            edgecolor=SURFACE,
            linewidth=1.5,
        )
        ax.text(a - 0.08, y, f"{a:.2f}", ha="right", va="center", color=INK2, fontsize=9)
        ax.text(
            b + 0.08,
            y,
            f"{b:.2f}",
            ha="left",
            va="center",
            color=INK,
            fontsize=9,
            fontweight="semibold",
        )
    ax.set_yticks(ys)
    ax.set_yticklabels([DIM_LABEL[k].replace("\n", " ") for k in DIMS], color=INK)
    ax.set_xlim(1, 5)
    ax.set_xlabel("Mean judge-v2 score (1–5), both walks, every 4th frame")
    ax.grid(axis="y", visible=False)
    ax.scatter([], [], color=ARM_COLOR["naive"], s=50, label="naive")
    ax.scatter([], [], color=ARM_COLOR["context_v2_nomem"], s=50, label="context-v2, no echo")
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    ax.set_title("Context engineering moves every dimension up", loc="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(out / "fig2_dumbbell_naive_vs_v2.png")
    plt.close(fig)


def fig_deltas(summary: dict, out: Path) -> None:
    """Fig 3: paired per-frame delta with 95 % CI, pooled."""
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    keys = DIMS + ["overall"]
    ys = list(range(len(keys)))[::-1]
    for y, k in zip(ys, keys, strict=True):
        e = summary["paired_v2_nomem_minus_naive"][k]
        lo, hi = e["ci95"]
        col = INK if k == "overall" else ARM_COLOR["context_v2_nomem"]
        ax.plot([lo, hi], [y, y], color=col, linewidth=2, solid_capstyle="round", zorder=2)
        ax.scatter([e["mean"]], [y], s=60, color=col, zorder=3, edgecolor=SURFACE, linewidth=1.5)
        ax.text(
            hi + 0.05,
            y,
            f"+{e['mean']:.2f}  ({e['better']} better / {e['worse']} worse)",
            va="center",
            ha="left",
            color=INK2,
            fontsize=8.5,
        )
    ax.axvline(0, color=BASE, linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(
        [DIM_LABEL[k].replace("\n", " ") if k in DIM_LABEL else "Overall" for k in keys], color=INK
    )
    ax.set_xlim(-0.3, 3.3)
    ax.set_xlabel("Paired difference, context-v2-no-echo minus naive (judge v2, n = 144), 95 % CI")
    ax.grid(axis="y", visible=False)
    ax.set_title("Every interval clears zero", loc="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(out / "fig3_paired_deltas_ci.png")
    plt.close(fig)


def fig_arms(summary: dict, out: Path) -> None:
    """Fig 4: all four arms per dimension, one panel per walk (judge v2)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    width = 0.19
    for ax, w in zip(axes, WALKS, strict=True):
        for i, a in enumerate(ARMS):
            vals = [summary["arms"][f"{w}_{a}"]["judge_v2"][k] for k in DIMS]
            xs = [x + (i - 1.5) * (width + 0.01) for x in range(len(DIMS))]
            ax.bar(xs, vals, width=width, color=ARM_COLOR[a], label=ARM_LABEL[a], zorder=2)
            if a in ("naive", "context_v2_nomem"):
                for x, v in zip(xs, vals, strict=True):
                    ax.text(
                        x, v + 0.06, f"{v:.1f}", ha="center", va="bottom", fontsize=7.5, color=INK2
                    )
        ax.set_xticks(range(len(DIMS)))
        ax.set_xticklabels([DIM_LABEL[k] for k in DIMS], color=INK, fontsize=8.5)
        ax.set_ylim(1, 5)
        ax.grid(axis="x", visible=False)
        ax.set_title(
            f"{w.capitalize()} ({summary['arms'][f'{w}_naive']['judge_v2_n']} frames per arm)",
            loc="left",
            color=INK,
            fontsize=10,
        )
    axes[0].set_ylabel("Mean judge-v2 score (1–5)")
    axes[0].legend(loc="upper left", frameon=False, fontsize=8.5, ncol=2)
    fig.suptitle(
        "All four arms, judge v2, every 4th frame", x=0.01, ha="left", color=INK, fontsize=11
    )
    fig.tight_layout()
    fig.savefig(out / "fig4_all_arms_by_walk.png")
    plt.close(fig)


def fig_generation(summary: dict, out: Path) -> None:
    """Fig 5: generation statistics (no judge) - repetition and safety verbs per arm."""
    metrics = [
        ("unique_ratio", "Unique instructions / frames"),
        ("stop_rate", 'Share saying "stop"'),
        ("side_rate", 'Share with "left" or "right"'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    for ax, (key, title) in zip(axes, metrics, strict=True):
        for j, w in enumerate(WALKS):
            for i, a in enumerate(ARMS):
                v = summary["arms"][f"{w}_{a}"][key]
                x = j * (len(ARMS) + 1) + i
                ax.bar(
                    x,
                    v,
                    width=0.8,
                    color=ARM_COLOR[a],
                    zorder=2,
                    label=ARM_LABEL[a] if j == 0 else None,
                )
                ax.text(x, v + 0.015, f"{v:.2f}", ha="center", va="bottom", fontsize=7, color=INK2)
        ax.set_xticks([1.5, len(ARMS) + 2.5])
        ax.set_xticklabels([w.capitalize() for w in WALKS], color=INK)
        ax.set_ylim(0, 1.08)
        ax.grid(axis="x", visible=False)
        ax.set_title(title, loc="left", color=INK, fontsize=10)
    handles, labels = axes[0].get_legend_handles_labels()
    axes[1].legend(handles, labels, loc="upper left", frameon=False, fontsize=7.5)
    fig.suptitle(
        "What the four arms actually say (all 580 frames, no judge involved)",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out / "fig5_generation_stats.png")
    plt.close(fig)


def fig_judges(summary: dict, out: Path) -> None:
    """Fig 6: judge v1 vs v2 - uniform score vectors and conciseness by arm (Suwon + London pooled)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    x = list(range(len(ARMS)))
    # panel A: share of frames where all five scores are identical
    for i, (judge, col) in enumerate(
        (
            ("judge_v1_uniform_share", ARM_COLOR["naive"]),
            ("judge_v2_uniform_share", ARM_COLOR["context"]),
        )
    ):
        vals = [st.fmean(summary["arms"][f"{w}_{a}"][judge] for w in WALKS) for a in ARMS]
        xs = [v + (i - 0.5) * 0.36 for v in x]
        axes[0].bar(
            xs, vals, width=0.34, color=col, zorder=2, label="judge v1" if i == 0 else "judge v2"
        )
        for xx, v in zip(xs, vals, strict=True):
            axes[0].text(
                xx, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, color=INK2
            )
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(
        [ARM_LABEL[a].replace(", ", ",\n") for a in ARMS], fontsize=8, color=INK
    )
    axes[0].set_ylim(0, 0.6)
    axes[0].set_ylabel("Share of frames with five identical scores")
    axes[0].set_title(
        "Halo effect: v1 gives one number five times", loc="left", color=INK, fontsize=10
    )
    axes[0].legend(frameon=False, fontsize=8.5)
    axes[0].grid(axis="x", visible=False)
    # panel B: conciseness by judge vs mean words
    for i, (judge, col, label) in enumerate(
        (
            ("judge_v1", ARM_COLOR["naive"], "judge v1"),
            ("judge_v2", ARM_COLOR["context"], "judge v2"),
        )
    ):
        vals = [
            st.fmean(summary["arms"][f"{w}_{a}"][judge]["conciseness"] for w in WALKS) for a in ARMS
        ]
        xs = [v + (i - 0.5) * 0.36 for v in x]
        axes[1].bar(xs, vals, width=0.34, color=col, zorder=2, label=label)
        for xx, v in zip(xs, vals, strict=True):
            axes[1].text(
                xx, v + 0.05, f"{v:.1f}", ha="center", va="bottom", fontsize=7.5, color=INK2
            )
    words = [st.fmean(summary["arms"][f"{w}_{a}"]["mean_words"] for w in WALKS) for a in ARMS]
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(
        [
            f"{ARM_LABEL[a]}\n({wd:.0f} words)".replace(", ", ",\n")
            for a, wd in zip(ARMS, words, strict=True)
        ],
        fontsize=8,
        color=INK,
    )
    axes[1].set_ylim(1, 5)
    axes[1].set_ylabel("Mean conciseness score (1–5)")
    axes[1].set_title("Only v2 scores conciseness by length", loc="left", color=INK, fontsize=10)
    axes[1].legend(frameon=False, fontsize=8.5, loc="upper left")
    axes[1].grid(axis="x", visible=False)
    fig.suptitle(
        "The same 7B model as judge, before and after the judge-prompt fix",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out / "fig6_judge_v1_vs_v2.png")
    plt.close(fig)


# ------------------------------------------------------------------ image panels
def _font(size: int):
    for name in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, width_px):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= width_px:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fig_examples(d: dict, results: Path, out: Path, repo: Path) -> None:
    """Fig 7 (wins) and Fig 8 (failure classes): frame + cues + naive vs context-v2 instructions + judge-v2 scores."""
    wins = []
    for w in WALKS:  # two largest paired improvements per walk, judged v2, distinct instructions
        nav = {r["frame_id"]: r for r in complete(d["v2"][(w, "naive")])}
        cands = [
            (overall(r) - overall(nav[r["frame_id"]]), r)
            for r in complete(d["v2"][(w, "context_v2_nomem")])
            if r["frame_id"] in nav
        ]
        seen: set[str] = set()
        for _delta, r in sorted(cands, key=lambda t: -t[0]):
            if r["instruction"] in seen:
                continue
            seen.add(r["instruction"])
            wins.append((w, r["frame_id"]))
            if len(seen) == 2:
                break
    fails = [("suwon", "000248"), ("suwon", "000212"), ("london", "000044")]
    captions = {
        (
            "suwon",
            "000248",
        ): "Judge over-anchoring: the detector missed the crouching person; context saw them; judge penalised the contradiction with the cues.",
        (
            "suwon",
            "000212",
        ): "Scene semantics: green pedestrian signal. Naive called it red; context never mentioned the crossing.",
        (
            "london",
            "000044",
        ): "Detector miss + cue anchoring: bollard at near range undetected; context followed the cues, naive mentioned it.",
    }
    for name, frames in (("fig7_examples_wins", wins), ("fig8_failure_classes", fails)):
        _panel(d, results, repo, frames, captions, out / f"{name}.png")


def _panel(d, results, repo, frames, captions, path):
    W, IMG_W, PAD = 1180, 480, 14
    f_t, f_b, f_s = _font(17), _font(15), _font(13)
    tiles = []
    for w, fid in frames:
        img = Image.open(repo / f"data/{w}/{fid}.jpg").convert("RGB")
        img = img.resize((IMG_W, int(img.height * IMG_W / img.width)))
        v2 = {r["frame_id"]: r for r in d["v2"][(w, "context_v2_nomem")]}
        nv = {r["frame_id"]: r for r in d["v2"][(w, "naive")]}
        recs_n = {r["frame_id"]: r for r in d["records"][(w, "naive")]}
        recs_c = {r["frame_id"]: r for r in d["records"][(w, "context_v2_nomem")]}
        cues = recs_c[fid]["cues"]
        naive_txt = recs_n[fid]["instruction"].replace("\n", " ")
        ctx_txt = recs_c[fid]["instruction"]

        def sc(r):
            return (
                "  ".join(f"{k[:4]} {r['scores'][k]}" for k in DIMS)
                if r and None not in r["scores"].values()
                else "(not in judged subset)"
            )

        text_w = W - IMG_W - 3 * PAD
        canvas = Image.new("RGB", (W, 10), SURFACE)
        dr = ImageDraw.Draw(canvas)
        blocks = [
            (f"{w}/{fid}", f_t, INK),
            ("Cues: " + cues, f_s, INK2),
            ("Naive: " + (naive_txt[:260] + ("…" if len(naive_txt) > 260 else "")), f_b, INK),
            ("   judge v2: " + sc(nv.get(fid)), f_s, MUTED),
            ("Context-v2, no echo: " + ctx_txt, f_b, INK),
            ("   judge v2: " + sc(v2.get(fid)), f_s, MUTED),
        ]
        if (w, fid) in captions:
            blocks.append(("Why it matters: " + captions[(w, fid)], f_s, INK2))
        lines = []
        for txt, font, col in blocks:
            for ln in _wrap(dr, txt, font, text_w):
                lines.append((ln, font, col))
            lines.append(("", f_s, col))
        text_h = sum(font.size + 5 for _, font, _ in lines)
        h = max(img.height, text_h) + 2 * PAD
        tile = Image.new("RGB", (W, h), SURFACE)
        tile.paste(img, (PAD, PAD))
        dr = ImageDraw.Draw(tile)
        y = PAD
        for ln, font, col in lines:
            dr.text((IMG_W + 2 * PAD, y), ln, font=font, fill=col)
            y += font.size + 5
        dr.line([(0, h - 1), (W, h - 1)], fill=GRID, width=1)
        tiles.append(tile)
    total = sum(t.height for t in tiles)
    sheet = Image.new("RGB", (W, total), SURFACE)
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height
    sheet.save(path, quality=88)


def fig_cues(repo: Path, out: Path) -> None:
    """Fig 1: frame | depth closeness map with the approach band | cue text (needs the perception models)."""
    try:
        import numpy as np

        from lvnav.config import load_config
        from lvnav.perception import build_perception
    except Exception as exc:  # noqa: BLE001
        print(f"skip fig1 (perception unavailable): {exc}")
        return
    cfg = load_config(repo / "backend/configs/default.yaml")
    p = build_perception(cfg.perception)
    frames = [("suwon", "000120"), ("suwon", "000200"), ("london", "000070")]
    f_s = _font(14)
    tiles = []
    for w, fid in frames:
        img = Image.open(repo / f"data/{w}/{fid}.jpg").convert("RGB")
        depth = p.depth(img)
        cues = p(img)
        small = img.resize((512, 288))
        heat = (
            Image.fromarray((np.clip(depth, 0, 1) * 255).astype(np.uint8))
            .convert("RGB")
            .resize((512, 288))
        )
        dr = ImageDraw.Draw(heat)
        dr.rectangle([0, 144, 511, 230], outline=ARM_COLOR["context_v2_nomem"], width=3)
        dr.text(
            (6, 148), "approach band (rows 50–80 %)", font=f_s, fill=ARM_COLOR["context_v2_nomem"]
        )
        for x in (170, 341):
            dr.line([(x, 144), (x, 230)], fill=ARM_COLOR["context_v2_nomem"], width=2)
        tile = Image.new("RGB", (1180, 288 + 62), SURFACE)
        tile.paste(small, (14, 8))
        tile.paste(heat, (540, 8))
        dr = ImageDraw.Draw(tile)
        lines = _wrap(dr, f"{w}/{fid}   |   {cues.to_text()}", f_s, 1150)
        for i, ln in enumerate(lines):
            dr.text((14, 302 + i * 19), ln, font=f_s, fill=INK)
        tiles.append(tile)
    sheet = Image.new("RGB", (1180, sum(t.height for t in tiles)), SURFACE)
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height
    sheet.save(out / "fig1_perception_cues.png", quality=88)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--results", type=Path, default=Path("results"))
    ap.add_argument("--out", type=Path, default=Path("docs/paper"))
    ap.add_argument("--skip-perception", action="store_true", help="skip fig1 (needs torch models)")
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[2]
    d = load_all(args.results)
    summary = export_data(d, args.out)
    copy_reports(args.results, args.out)
    figs = args.out / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    fig_dumbbell(summary, figs)
    fig_deltas(summary, figs)
    fig_arms(summary, figs)
    fig_generation(summary, figs)
    fig_judges(summary, figs)
    fig_examples(d, args.results, figs, repo)
    if not args.skip_perception:
        fig_cues(repo, figs)
    print(
        f"wrote {args.out}/data, {args.out}/reports and {sorted(p.name for p in figs.glob('*.png'))}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
