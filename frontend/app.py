"""Streamlit viewer: step through frames and compare naive vs context instructions.

Reads results/<run>/records.jsonl (and judged.jsonl if present). The frontend
never calls the models; it only renders what the backend produced, so it can be
opened on any machine that has the results directory.
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path

import pandas as pd
import streamlit as st_ui
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = REPO_ROOT / "results"
DIMENSIONS = ["safety", "actionability", "spatial_accuracy", "conciseness", "hallucination"]

st_ui.set_page_config(page_title="Low-vision navigation: naive vs context", layout="wide")

st_ui.markdown(
    """
    <style>
      .stApp { font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif; }
      h1, h2, h3 { font-weight: 600; letter-spacing: -0.01em; }
      .instr { font-size: 1.15rem; line-height: 1.5; padding: 0.9rem 1.1rem;
               border-left: 4px solid #2F5D62; background: #F2F6F5; border-radius: 0 6px 6px 0; }
      .instr.naive { border-left-color: #9A6B4E; background: #F8F3EE; }
      .cues { font-family: ui-monospace, Menlo, monospace; font-size: 0.85rem;
              color: #3B3B3B; white-space: pre-wrap; }
      .score-pill { display:inline-block; padding: 0.15rem 0.55rem; margin: 0 0.25rem 0.25rem 0;
                    border-radius: 999px; background: #E8EEEE; font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- data
@st_ui.cache_data(show_spinner=False)
def load_run(run_dir: str, judged_name: str) -> tuple[list[dict], bool]:
    """Rows from the chosen judged file if present, else the unjudged records."""
    d = Path(run_dir)
    judged = d / judged_name
    src = judged if judged.exists() else d / "records.jsonl"
    with src.open() as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    return rows, judged.exists()


def judged_files(*run_dirs: Path) -> list[str]:
    """Judged filenames present in all given run dirs, e.g. judged.jsonl, judged_v2_every4.jsonl."""
    common: set[str] | None = None
    for d in run_dirs:
        names = {p.name for p in d.glob("judged*.jsonl")}
        common = names if common is None else common & names
    return sorted(common or [])


def available_runs() -> list[str]:
    if not RESULTS_ROOT.exists():
        return []
    return sorted(p.name for p in RESULTS_ROOT.iterdir() if (p / "records.jsonl").exists())


def means(rows: list[dict]) -> dict[str, float | None]:
    out = {}
    for dim in DIMENSIONS:
        vals = [r["scores"][dim] for r in rows if r.get("scores", {}).get(dim) is not None]
        out[dim] = round(st.fmean(vals), 2) if vals else None
    return out


def resolve_frame(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


# ------------------------------------------------------------------------ sidebar
runs = available_runs()
st_ui.sidebar.header("Runs")
if not runs:
    st_ui.info(
        "No runs found. Generate some first:\n\n"
        "`make run-naive FRAMES=data/<walk>` and `make run-context FRAMES=data/<walk>`\n\n"
        "Then reload this page."
    )
    st_ui.stop()

default_a = next((r for r in runs if r.endswith("_naive")), runs[0])
default_b = next(
    (r for r in runs if r.endswith("_context_v2_nomem")),
    next((r for r in runs if r.endswith("_context")), runs[-1]),
)
run_a = st_ui.sidebar.selectbox("Baseline (naive)", runs, index=runs.index(default_a))
run_b = st_ui.sidebar.selectbox("Treatment (context)", runs, index=runs.index(default_b))
show_prompt_context = st_ui.sidebar.checkbox("Show cues and memory", value=True)
judged_options = judged_files(RESULTS_ROOT / run_a, RESULTS_ROOT / run_b) or ["judged.jsonl"]
default_judged = next((n for n in judged_options if "v2" in n), judged_options[0])
judged_name = st_ui.sidebar.selectbox(
    "Judge file", judged_options, index=judged_options.index(default_judged),
    help="judged.jsonl: judge v1, all frames. judged_v2_every4.jsonl: judge v2, every 4th frame.",
)

rows_a, judged_a = load_run(str(RESULTS_ROOT / run_a), judged_name)
rows_b, judged_b = load_run(str(RESULTS_ROOT / run_b), judged_name)
by_id_a = {r["frame_id"]: r for r in rows_a}
by_id_b = {r["frame_id"]: r for r in rows_b}
frame_ids = sorted(set(by_id_a) & set(by_id_b))

# --------------------------------------------------------------------------- head
st_ui.title("Does engineered context make VLM guidance safer for low-vision walking?")
st_ui.caption(
    f"Comparing **{run_a}** against **{run_b}** on {len(frame_ids)} shared frames. "
    "Instructions are what the assistant would speak into the user's earpiece."
)

# ------------------------------------------------------------------------ summary
if judged_a and judged_b:
    ma, mb = means(rows_a), means(rows_b)
    df = pd.DataFrame(
        {"naive": [ma[d] for d in DIMENSIONS], "context": [mb[d] for d in DIMENSIONS]},
        index=[d.replace("_", " ") for d in DIMENSIONS],
    )
    c1, c2 = st_ui.columns([3, 2])
    with c1:
        st_ui.subheader("Rubric means (1–5, higher is better)")
        st_ui.bar_chart(df, height=260)
    with c2:
        st_ui.subheader("Latency and length")
        la = [r["latency_s"] for r in rows_a if r.get("latency_s") is not None]
        lb = [r["latency_s"] for r in rows_b if r.get("latency_s") is not None]
        wa = [len(r["instruction"].split()) for r in rows_a]
        wb = [len(r["instruction"].split()) for r in rows_b]
        st_ui.dataframe(
            pd.DataFrame(
                {
                    "naive": [round(st.median(la), 2) if la else None, round(st.fmean(wa), 1)],
                    "context": [round(st.median(lb), 2) if lb else None, round(st.fmean(wb), 1)],
                },
                index=["median latency (s)", "mean words per instruction"],
            ),
            use_container_width=True,
        )
        suffix = judged_name.removeprefix("judged").removesuffix(".jsonl")
        report = RESULTS_ROOT / run_b / f"report{suffix}.md"
        if report.exists():
            with st_ui.expander("Full paired report"):
                st_ui.markdown(report.read_text())
else:
    st_ui.warning(
        "One or both runs are not judged yet, so only instructions are shown. "
        "Run `make judge RUN=results/<run>` on each."
    )

st_ui.divider()

# ------------------------------------------------------------------- frame viewer
if not frame_ids:
    st_ui.error("The two runs share no frame ids. Choose runs generated from the same frames.")
    st_ui.stop()

if "idx" not in st_ui.session_state:
    st_ui.session_state.idx = 0
nav1, nav2, nav3 = st_ui.columns([1, 6, 1])
with nav1:
    if st_ui.button("Previous", use_container_width=True):
        st_ui.session_state.idx = max(st_ui.session_state.idx - 1, 0)
with nav3:
    if st_ui.button("Next", use_container_width=True):
        st_ui.session_state.idx = min(st_ui.session_state.idx + 1, len(frame_ids) - 1)
with nav2:
    st_ui.session_state.idx = st_ui.slider(
        "Frame", 0, len(frame_ids) - 1, st_ui.session_state.idx, label_visibility="collapsed"
    )

fid = frame_ids[st_ui.session_state.idx]
ra, rb = by_id_a[fid], by_id_b[fid]

img_col, txt_col = st_ui.columns([1.1, 1.4])
with img_col:
    fp = resolve_frame(rb["frame_path"])
    if fp.exists():
        st_ui.image(Image.open(fp), caption=f"Frame {fid}", use_container_width=True)
    else:
        st_ui.error(f"Frame image not found: {fp}")
    if show_prompt_context and rb.get("cues"):
        st_ui.markdown("**Sensor cues fed to the context condition**")
        st_ui.markdown(f"<div class='cues'>{rb['cues']}</div>", unsafe_allow_html=True)
    if show_prompt_context and rb.get("memory"):
        with st_ui.expander("Scene memory at this frame"):
            st_ui.markdown(f"<div class='cues'>{rb['memory']}</div>", unsafe_allow_html=True)


def render_instruction(rec: dict, label: str, css: str) -> None:
    st_ui.markdown(f"**{label}**")
    st_ui.markdown(f"<div class='instr {css}'>{rec['instruction']}</div>", unsafe_allow_html=True)
    meta = f"{rec.get('latency_s', '–')} s"
    if rec.get("completion_tokens") is not None:
        meta += f", {rec['completion_tokens']} tokens"
    st_ui.caption(meta)
    if rec.get("scores"):
        pills = "".join(
            f"<span class='score-pill'>{d.replace('_', ' ')} {rec['scores'][d] or '–'}</span>"
            for d in DIMENSIONS
        )
        st_ui.markdown(pills, unsafe_allow_html=True)
        if rec.get("judge_rationale"):
            st_ui.caption(rec["judge_rationale"])


with txt_col:
    render_instruction(ra, "Naive (single frame, generic prompt)", "naive")
    st_ui.write("")
    render_instruction(rb, "Context (cues + memory + BLV system prompt)", "")
