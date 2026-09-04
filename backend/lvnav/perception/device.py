"""Torch device selection with Apple Silicon (MPS) support."""

from __future__ import annotations


def resolve_device(requested: str = "auto") -> str:
    """Return 'mps', 'cuda' or 'cpu'. Import torch lazily so the mock path stays light."""
    import torch

    if requested != "auto":
        return requested
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
