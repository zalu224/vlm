"""Click-to-annotate ground truth for the Last-Shelf study.

The detector has already proposed numbered boxes; this page shows them over the
image and you press the matching button. That is the whole job: one click per
image, roughly 20 minutes for 200 trials. Saves after every click, so it is safe
to close the tab and come back.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MISSED = -1

st.set_page_config(page_title="Shelf annotator", layout="wide")
st.markdown(
    """
    <style>
      .stApp { font-family: "Iowan Old Style", Georgia, serif; }
      div[data-testid="stHorizontalBlock"] button { font-variant-numeric: tabular-nums; }
      .target { font-size: 1.6rem; font-weight: 600; letter-spacing: -0.01em; }
      .prog { color: #5A5A5A; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

BOX_COLOR = (255, 196, 0)
HIT_COLOR = (60, 220, 130)


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def write_jsonl(rows: list[dict], p: Path) -> None:
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def draw(image_path: Path, boxes: list[dict], highlight: int | None) -> Image.Image:
    im = Image.open(image_path).convert("RGB")
    d = ImageDraw.Draw(im)
    w = max(int(min(im.size) * 0.004), 2)
    for b in boxes:
        x1, y1, x2, y2 = b["box"]
        on = highlight == b["box_id"]
        d.rectangle(
            [x1, y1, x2, y2],
            outline=HIT_COLOR if on else BOX_COLOR,
            width=w * (2 if on else 1),
        )
        tag = str(b["box_id"])
        d.rectangle(
            [x1, max(y1 - 26, 0), x1 + 16 + 11 * len(tag), max(y1, 26)],
            fill=HIT_COLOR if on else BOX_COLOR,
        )
        d.text((x1 + 6, max(y1 - 22, 4)), tag, fill=(0, 0, 0))
    return im


results_dir = Path(
    st.sidebar.text_input("Results directory", value=str(REPO_ROOT / "results" / "shelf"))
)
trials_path = results_dir / "trials.jsonl"
det_path = results_dir / "detections.jsonl"
catalog_path = results_dir / "catalog.json"

if not trials_path.exists() or not det_path.exists():
    st.title("Shelf annotator")
    st.info(
        "Nothing to annotate yet. From the repository root:\n\n"
        "```\nlvnav shelf index  --catalog data/shelf/catalog\n"
        "lvnav shelf detect --images  data/shelf/images\n"
        "lvnav shelf trials --default-target <item_id>\n```\n\n"
        "Then reload this page."
    )
    st.stop()

trials = read_jsonl(trials_path)
dets = {d["image"]: d for d in read_jsonl(det_path)}
item_ids = (
    [r["item_id"] for r in json.loads(catalog_path.read_text())] if catalog_path.exists() else []
)

done = sum(1 for t in trials if t.get("gt_box") is not None)
st.sidebar.metric("Annotated", f"{done} / {len(trials)}")
only_todo = st.sidebar.checkbox("Skip finished trials", value=True)

todo = [i for i, t in enumerate(trials) if t.get("gt_box") is None]
order = todo if only_todo else list(range(len(trials)))
if not order:
    st.title("Shelf annotator")
    st.success(f"All {len(trials)} trials annotated. Next: `lvnav shelf search`.")
    st.stop()

if "pos" not in st.session_state or st.session_state.pos >= len(order):
    st.session_state.pos = 0
idx = order[st.session_state.pos]
trial = trials[idx]
rec = dets[trial["image"]]
boxes = rec["boxes"]


def save_and_advance(value: int | None, target: str | None = None) -> None:
    if target:
        trials[idx]["target"] = target
    trials[idx]["gt_box"] = value
    write_jsonl(trials, trials_path)
    st.session_state.pos = min(st.session_state.pos + 1, len(order) - 1)


left, right = st.columns([2, 1])
with left:
    st.image(
        draw(Path(trial["image"]), boxes, trial.get("gt_box")),
        use_container_width=True,
        caption=Path(trial["image"]).name,
    )

with right:
    st.markdown(
        f"<div class='prog'>{st.session_state.pos + 1} of {len(order)} to do</div>",
        unsafe_allow_html=True,
    )
    target = trial.get("target")
    if not target and item_ids:
        target = st.selectbox("Which item is being asked for?", item_ids)
    st.markdown(
        f"<div class='target'>{(target or '?').replace('_', ' ')}</div>", unsafe_allow_html=True
    )
    st.write("Which numbered box holds it?")

    per_row = 5
    for start in range(0, len(boxes), per_row):
        cols = st.columns(per_row)
        for col, b in zip(cols, boxes[start : start + per_row], strict=False):
            with col:
                label, key = str(b["box_id"]), f"b{idx}_{b['box_id']}"
                if st.button(label, key=key, use_container_width=True):
                    save_and_advance(b["box_id"], target)
                    st.rerun()

    st.write("")
    if st.button("Detector missed it", use_container_width=True):
        save_and_advance(MISSED, target)
        st.rerun()

    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("Back", use_container_width=True):
            st.session_state.pos = max(st.session_state.pos - 1, 0)
            st.rerun()
    with nav2:
        if st.button("Skip", use_container_width=True):
            st.session_state.pos = min(st.session_state.pos + 1, len(order) - 1)
            st.rerun()

    if trial.get("gt_box") is not None:
        current = "detector missed it" if trial["gt_box"] == MISSED else f"box {trial['gt_box']}"
        st.caption(f"Currently recorded: {current}")
