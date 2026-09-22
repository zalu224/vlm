"""Anthropic Messages API. Zero-arg client resolves ANTHROPIC_API_KEY; tests inject a fake.

Only `temperature` is sent (current Claude models reject temperature and top_p together).
A `refusal` stop reason is recorded as an empty output with the stop reason in `raw`, so it
counts as a parse failure in scoring instead of crashing the run.
"""

from __future__ import annotations

import time
from pathlib import Path

from .base import Reply, encode_jpeg


class AnthropicBackend:
    name = "anthropic"

    def __init__(self, model, *, temperature=1.0, top_p=1.0, max_tokens=400, image_max_side=1024):
        self.model, self.temperature = model, temperature
        self.max_tokens, self.image_max_side = max_tokens, image_max_side
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic()
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def generate(self, system, user, image, *, seed=None) -> Reply:
        content: list[dict] = []
        if image is not None:
            b64, mt = encode_jpeg(Path(image), self.image_max_side)
            content.append(
                {"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}}
            )
        content.append({"type": "text", "text": user})
        kw = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": content}],
        )
        if system:
            kw["system"] = system
        t0 = time.perf_counter()
        resp = self.client.messages.create(**kw)
        latency = time.perf_counter() - t0
        stop = getattr(resp, "stop_reason", None)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        u = getattr(resp, "usage", None)
        return Reply(
            text,
            latency,
            getattr(u, "input_tokens", None),
            getattr(u, "output_tokens", None),
            {"stop_reason": stop},
        )
