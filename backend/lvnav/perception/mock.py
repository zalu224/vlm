"""Deterministic stand-ins for the perception models (tests and dry runs)."""

from __future__ import annotations

import hashlib

import numpy as np
from PIL import Image

from .cues import Detection


def _seed_from_image(image: Image.Image) -> int:
    digest = hashlib.md5(image.tobytes()[:4096]).hexdigest()
    return int(digest[:8], 16)


class MockDepth:
    """Synthesises a depth map with a near obstacle whose position depends on the image bytes."""

    def __call__(self, image: Image.Image) -> np.ndarray:
        rng = np.random.default_rng(_seed_from_image(image))
        w, h = image.size
        depth = np.linspace(0.2, 0.5, h)[:, None].repeat(w, axis=1)
        cx = int(rng.integers(0, w))
        x1, x2 = max(cx - w // 10, 0), min(cx + w // 10, w)
        depth[h // 2 :, x1:x2] = 0.85
        return depth.astype(np.float32)


class MockDetector:
    def __call__(self, image: Image.Image) -> list[Detection]:
        rng = np.random.default_rng(_seed_from_image(image) + 1)
        w, h = image.size
        labels = ["person", "pole", "bicycle", "trash can"]
        dets = []
        for _ in range(int(rng.integers(0, 3))):
            cx = float(rng.uniform(0.1, 0.9) * w)
            bw, bh = w * 0.12, h * 0.35
            dets.append(
                Detection(
                    label=str(rng.choice(labels)),
                    confidence=float(rng.uniform(0.35, 0.95)),
                    box=(cx - bw / 2, h * 0.45, cx + bw / 2, h * 0.45 + bh),
                )
            )
        return dets
