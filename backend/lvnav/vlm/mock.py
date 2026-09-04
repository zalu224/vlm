"""Deterministic mock backend for tests, CI and dry runs without a model server."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from .base import VLMResponse

_INSTRUCTIONS = [
    "Path ahead is clear. Keep walking straight.",
    "Slow down. A person is directly ahead about two steps away; step to your left.",
    "Pole on your right at arm's length. Stay centre and continue.",
    "Stop. Obstacle at knee height directly ahead; move one step right, then continue.",
]


class MockBackend:
    name = "mock"

    def __init__(self, latency_s: float = 0.01) -> None:
        self.latency_s = latency_s

    def generate(
        self,
        system: str,
        user: str,
        image: Path | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> VLMResponse:
        time.sleep(self.latency_s)
        # Judge requests ask for JSON; instruction requests get a canned instruction.
        if "Return ONLY a JSON object" in user:
            seed = int(hashlib.md5(user.encode()).hexdigest()[:8], 16)
            base = 2 + (seed % 3)
            scores = {
                "safety": min(base + 1, 5),
                "actionability": base,
                "spatial_accuracy": max(base - 1, 1),
                "conciseness": 4 if len(re.findall(r"\w+", user)) < 400 else 3,
                "hallucination": base,
            }
            text = json.dumps({"scores": scores, "rationale": "Mock judge output."})
        else:
            key = (str(image) if image else "") + user[:64]
            idx = int(hashlib.md5(key.encode()).hexdigest()[:8], 16) % len(_INSTRUCTIONS)
            text = _INSTRUCTIONS[idx]
        return VLMResponse(
            text=text,
            latency_s=self.latency_s,
            prompt_tokens=len(user.split()) + len(system.split()),
            completion_tokens=len(text.split()),
        )
