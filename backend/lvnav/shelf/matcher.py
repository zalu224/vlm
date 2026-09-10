"""Candidate scoring and ranking.

Deliberately model-free: embeddings arrive as plain arrays, so the fusion maths
(the part that decides which jar is the cinnamon) is unit-tested without loading
CLIP. Mirrors the paper's combination of open-vocabulary detection, embedding
similarity and colour-histogram matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from PIL import Image

HIST_BINS = (8, 8, 4)  # H, S, V


class SearchVariant(StrEnum):
    """Ablation arms. Each adds one signal to the previous."""

    DETECTION = "det"  # detector confidence only (no notion of which item)
    EMBED = "embed"  # + CLIP similarity to the target
    EMBED_COLOR = "embed+color"  # + colour-histogram similarity to reference photos

    @classmethod
    def all(cls) -> list[SearchVariant]:
        return [cls.DETECTION, cls.EMBED, cls.EMBED_COLOR]


@dataclass
class Candidate:
    box_id: int
    box: tuple[float, float, float, float]
    det_conf: float
    embed_sim: float | None = None
    color_sim: float | None = None
    score: float | None = None


def color_histogram(image: Image.Image, bins: tuple[int, int, int] = HIST_BINS) -> np.ndarray:
    """Normalised HSV histogram of an image crop."""
    arr = np.asarray(image.convert("HSV"), dtype=np.float32)
    if arr.size == 0:
        return np.zeros(int(np.prod(bins)), dtype=np.float32)
    idx = np.zeros(arr.shape[:2], dtype=np.int64)
    scale = 1
    for c, nb in reversed(list(enumerate(bins))):
        q = np.clip((arr[..., c] / 256.0 * nb).astype(np.int64), 0, nb - 1)
        idx += q * scale
        scale *= nb
    hist = np.bincount(idx.ravel(), minlength=int(np.prod(bins))).astype(np.float32)
    total = hist.sum()
    return hist / total if total else hist


def histogram_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Histogram intersection in [0, 1]; 1 means identical colour distributions."""
    return float(np.minimum(a, b).sum())


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def rank_candidates(
    candidates: list[Candidate],
    variant: SearchVariant,
    w_embed: float = 1.0,
    w_color: float = 0.35,
    w_det: float = 0.1,
) -> list[Candidate]:
    """Score and sort candidates, best first.

    Detection confidence carries a small weight in every variant so that ties break
    toward crisper boxes. In the DETECTION arm it is the only signal, which is the
    point of that arm: it shows how far a detector gets with no idea which item you
    asked for.
    """
    scored: list[Candidate] = []
    for c in candidates:
        if variant is SearchVariant.DETECTION:
            score = c.det_conf
        else:
            score = w_det * c.det_conf + w_embed * (c.embed_sim or 0.0)
            if variant is SearchVariant.EMBED_COLOR:
                score += w_color * (c.color_sim or 0.0)
        scored.append(
            Candidate(c.box_id, c.box, c.det_conf, c.embed_sim, c.color_sim, round(score, 5))
        )
    scored.sort(key=lambda c: (-(c.score or 0.0), c.box_id))
    return scored


def top_k_hit(ranked: list[Candidate], gt_box_id: int, k: int) -> bool:
    return any(c.box_id == gt_box_id for c in ranked[:k])


def hardest_distractor(ranked: list[Candidate], gt_box_id: int) -> Candidate | None:
    """Highest-scoring candidate that is not the target: the natural negative case
    for the correction phase, and the one a user is most likely to reach for."""
    for c in ranked:
        if c.box_id != gt_box_id:
            return c
    return None
