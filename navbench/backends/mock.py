"""Deterministic mock: picks a canned answer by hashing prompt and seed."""

from __future__ import annotations

import hashlib
import time

from .base import Reply

DEFAULT_ANSWERS = {
    "count": ["There are 2 chairs.", "3", "I count 4 chairs in the scene."],
    "closer": [
        "The chair on the left is closer.",
        "The right chair is closer to the viewpoint.",
    ],
    "vacant": [
        "Yes. The chair by the table is empty.",
        "No, both chairs have items on them.",
    ],
    "guide": [
        "Walk forward about three steps; the empty chair is on your right. A box is on the floor to your left."
    ],
}


class MockBackend:
    name = "mock"

    def __init__(self, answers: dict[str, list[str]] | None = None, latency_s: float = 0.0) -> None:
        self.answers = answers or DEFAULT_ANSWERS
        self.latency_s = latency_s

    def generate(self, system, user, image, *, seed=None) -> Reply:
        low = user.lower()
        key = next((k for k in self.answers if k in low), None) or next(iter(self.answers))
        opts = self.answers[key]
        h = int(hashlib.md5(f"{user}|{seed}".encode()).hexdigest()[:8], 16)
        if self.latency_s:
            time.sleep(self.latency_s)
        return Reply(opts[h % len(opts)], self.latency_s, len(user.split()), 8)
