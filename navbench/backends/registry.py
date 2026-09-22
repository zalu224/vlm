"""Build a backend from a configs/models.yaml entry. Cloud backends import lazily and fail
fast, naming the missing environment variable, so a run never dies mid-way."""

from __future__ import annotations

import os


def build_backend(entry: dict, sampling: dict, server: dict | None = None):
    kind = entry.get("backend")
    common = {
        "temperature": sampling.get("temperature", 1.0),
        "top_p": sampling.get("top_p", 1.0),
        "max_tokens": sampling.get("max_tokens", 400),
        "image_max_side": sampling.get("image_max_side", 1024),
    }
    if kind == "mock":
        from .mock import MockBackend

        return MockBackend()
    env = entry.get("env")
    if env and not os.environ.get(env):
        raise OSError(
            f"{entry.get('served', kind)} needs {env} in the environment (export {env}=...)"
        )
    if kind == "mlx":
        from .mlx import MlxServerBackend

        return MlxServerBackend(
            (server or {}).get("base_url", "http://localhost:8080/v1"), entry["served"], **common
        )
    if kind == "openai":
        from .openai_backend import OpenAIBackend

        return OpenAIBackend(entry["served"], **common)
    if kind == "anthropic":
        from .anthropic_backend import AnthropicBackend

        return AnthropicBackend(entry["served"], **common)
    if kind == "gemini":
        from .gemini_backend import GeminiBackend

        return GeminiBackend(entry["served"], **common)
    raise ValueError(
        f"model {entry.get('served')} is marked unavailable or has no backend ({kind})"
    )
