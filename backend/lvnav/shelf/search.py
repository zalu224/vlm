"""Phase 1: rank detected candidates against a requested catalogue item.

Runs every ablation arm in a single pass over the images, because the expensive
part (embedding each crop) is shared by all arms.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm

from .catalog import Catalog
from .detect import crop
from .matcher import (
    Candidate,
    SearchVariant,
    color_histogram,
    cosine,
    hardest_distractor,
    histogram_similarity,
    rank_candidates,
    top_k_hit,
)


def load_jsonl(path: Path) -> list[dict]:
    with Path(path).open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _target_similarity(crop_emb: np.ndarray, item, text_weight: float) -> float:
    """Blend similarity to the reference photos with similarity to the item's name.

    Reference photos dominate: a user asking for 'the cinnamon' has a specific jar in
    mind, and text similarity alone cannot separate two spice jars of the same brand.
    Text is kept at a low weight so the system still degrades sensibly for an item
    whose references are poor.
    """
    img_sim = cosine(crop_emb, item.embedding) if item.embedding is not None else 0.0
    txt_sim = cosine(crop_emb, item.text_embedding) if item.text_embedding is not None else 0.0
    return (1.0 - text_weight) * img_sim + text_weight * txt_sim


def run_search(
    trials: list[dict],
    detections_path: Path,
    catalog: Catalog,
    embedder,
    out_path: Path,
    text_weight: float = 0.25,
    variants: list[SearchVariant] | None = None,
) -> Path:
    """For each trial, rank candidates under every variant and record the outcome.

    A trial is `{"image": ..., "target": <item_id>, "gt_box": <box_id or -1>}`.
    `gt_box == -1` means no detected box contains the target, which is a detector
    recall failure and is reported separately from ranking failures.
    """
    variants = variants or SearchVariant.all()
    dets_by_image = {d["image"]: d for d in load_jsonl(detections_path)}
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as fh:
        for trial in tqdm(trials, desc="search", unit="trial"):
            rec = dets_by_image.get(trial["image"])
            if rec is None:
                raise KeyError(f"No detections cached for {trial['image']}; run shelf detect first")
            item = catalog[trial["target"]]
            boxes = rec["boxes"]

            t0 = time.perf_counter()
            with Image.open(trial["image"]) as im:
                im = im.convert("RGB")
                crops = [crop(im, b["box"]) for b in boxes]
            embs = embedder.embed_images(crops) if crops else np.zeros((0, 1), dtype=np.float32)
            hists = [color_histogram(c) for c in crops]
            for c in crops:
                c.close()

            candidates = [
                Candidate(
                    box_id=b["box_id"],
                    box=tuple(b["box"]),
                    det_conf=b["conf"],
                    embed_sim=_target_similarity(embs[i], item, text_weight),
                    color_sim=(
                        histogram_similarity(hists[i], item.histogram)
                        if item.histogram is not None
                        else 0.0
                    ),
                )
                for i, b in enumerate(boxes)
            ]
            elapsed = time.perf_counter() - t0

            row: dict = {
                "image": trial["image"],
                "target": trial["target"],
                "target_name": item.name,
                "gt_box": trial["gt_box"],
                "n_candidates": len(candidates),
                "detector_recall": trial["gt_box"] >= 0,
                "latency_s": round(elapsed, 3),
                "variants": {},
            }
            for v in variants:
                ranked = rank_candidates(candidates, v)
                pred = ranked[0] if ranked else None
                row["variants"][v.value] = {
                    "pred_box": None if pred is None else pred.box_id,
                    "pred_score": None if pred is None else pred.score,
                    "top1": top_k_hit(ranked, trial["gt_box"], 1) if ranked else False,
                    "top3": top_k_hit(ranked, trial["gt_box"], 3) if ranked else False,
                    "ranking": [c.box_id for c in ranked[:5]],
                }
                if v is SearchVariant.EMBED_COLOR:
                    hd = hardest_distractor(ranked, trial["gt_box"])
                    row["hard_distractor_box"] = None if hd is None else hd.box_id
            fh.write(json.dumps(row) + "\n")
    return out_path
