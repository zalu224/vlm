"""One interface for every model backend."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image


@dataclass
class Reply:
    text: str
    latency_s: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    raw: dict | None = None


class Backend(Protocol):
    name: str

    def generate(
        self, system: str | None, user: str, image: Path | None, *, seed: int | None = None
    ) -> Reply: ...


def encode_jpeg(path: Path, max_side: int) -> tuple[str, str]:
    """(base64 JPEG, media type) with the long side capped at `max_side`."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
