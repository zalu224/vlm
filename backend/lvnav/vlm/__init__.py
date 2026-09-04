"""VLM backends behind a single interface."""

from __future__ import annotations

from .base import VLMBackend, VLMResponse
from .mock import MockBackend
from .openai_compat import OpenAICompatBackend


def build_backend(kind: str, cfg, model_override: str | None = None) -> VLMBackend:
    """Factory used by the CLI. `cfg` is a VLMConfig."""
    if kind == "mock":
        return MockBackend()
    if kind == "http":
        backend = OpenAICompatBackend(
            base_url=cfg.base_url,
            model=model_override or cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            timeout_s=cfg.timeout_s,
            image_max_side=cfg.image_max_side,
        )
        if not backend.health():
            raise ConnectionError(
                f"No VLM server responding at {cfg.base_url}. "
                "Start one with `make serve-vlm` (macOS) or pass --backend mock."
            )
        return backend
    raise ValueError(f"Unknown backend: {kind}")


__all__ = ["VLMBackend", "VLMResponse", "MockBackend", "OpenAICompatBackend", "build_backend"]
