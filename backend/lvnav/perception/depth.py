"""Monocular relative depth via Depth Anything V2 (Small) through Hugging Face transformers."""

from __future__ import annotations

import numpy as np
from PIL import Image

from .device import resolve_device


class DepthEstimator:
    """Returns a normalised closeness map in [0, 1] where 1 = closest to the camera.

    Depth Anything predicts relative inverse depth (larger = closer). We min-max
    normalise per frame; absolute scale is not needed for zone-level free-space
    reasoning. Model weights (~100 MB) download on first use.
    """

    def __init__(self, model_id: str, device: str = "auto") -> None:
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation

        self.device = resolve_device(device)
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_id).to(self.device).eval()
        self._torch = torch

    def __call__(self, image: Image.Image) -> np.ndarray:
        torch = self._torch
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            pred = self.model(**inputs).predicted_depth  # (1, H', W')
        pred = torch.nn.functional.interpolate(
            pred.unsqueeze(1), size=image.size[::-1], mode="bicubic", align_corners=False
        ).squeeze()
        arr = pred.float().cpu().numpy()
        lo, hi = float(arr.min()), float(arr.max())
        return (arr - lo) / (hi - lo + 1e-6)
