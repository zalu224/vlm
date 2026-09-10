"""CLIP image/text embeddings, with a deterministic mock for tests and dry runs."""

from __future__ import annotations

import hashlib

import numpy as np
from PIL import Image

DEFAULT_CLIP = "openai/clip-vit-base-patch32"


class ClipEmbedder:
    """Wraps a CLIP checkpoint. ViT-B/32 is ~150 MB and runs comfortably on MPS."""

    def __init__(self, model_id: str = DEFAULT_CLIP, device: str = "auto") -> None:
        import torch
        from transformers import CLIPModel, CLIPProcessor

        from ..perception.device import resolve_device

        self.device = resolve_device(device)
        self.model = CLIPModel.from_pretrained(model_id).to(self.device).eval()
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self._torch = torch

    def embed_images(self, images: list[Image.Image]) -> np.ndarray:
        torch = self._torch
        if not images:
            return np.zeros((0, self.model.config.projection_dim), dtype=np.float32)
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            feats = self.model.get_image_features(**inputs)
        return feats.float().cpu().numpy()

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        torch = self._torch
        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True).to(
            self.device
        )
        with torch.no_grad():
            feats = self.model.get_text_features(**inputs)
        return feats.float().cpu().numpy()


class MockEmbedder:
    """Content-hashed pseudo-embeddings: deterministic, and identical inputs match."""

    dim = 64

    def _vec(self, key: bytes) -> np.ndarray:
        seed = int(hashlib.md5(key).hexdigest()[:8], 16)
        return np.random.default_rng(seed).normal(size=self.dim).astype(np.float32)

    def embed_images(self, images: list[Image.Image]) -> np.ndarray:
        if not images:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([self._vec(im.convert("RGB").tobytes()[:2048]) for im in images])

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([self._vec(t.encode()) for t in texts])


def build_embedder(model_id: str = DEFAULT_CLIP, device: str = "auto", use_mock: bool = False):
    return MockEmbedder() if use_mock else ClipEmbedder(model_id, device)
