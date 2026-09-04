"""Backend interface shared by the real HTTP client and the mock."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class VLMResponse:
    text: str
    latency_s: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    raw: dict | None = None


class VLMBackend(Protocol):
    name: str

    def generate(
        self,
        system: str,
        user: str,
        image: Path | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> VLMResponse: ...
