"""OpenAI Chat Completions (GPT-4o and successors). Client is built lazily; tests inject a fake."""

from __future__ import annotations

import time
from pathlib import Path

from .base import Reply, encode_jpeg


class OpenAIBackend:
    name = "openai"

    def __init__(self, model, *, temperature=1.0, top_p=1.0, max_tokens=400, image_max_side=1024):
        self.model, self.temperature, self.top_p = model, temperature, top_p
        self.max_tokens, self.image_max_side = max_tokens, image_max_side
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def generate(self, system, user, image, *, seed=None) -> Reply:
        content: list[dict] = []
        if image is not None:
            b64, mt = encode_jpeg(Path(image), self.image_max_side)
            content.append({"type": "image_url", "image_url": {"url": f"data:{mt};base64,{b64}"}})
        content.append({"type": "text", "text": user})
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": content}
        ]
        kw = dict(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )
        if seed is not None:
            kw["seed"] = seed
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(**kw)
        u = getattr(resp, "usage", None)
        return Reply(
            (resp.choices[0].message.content or "").strip(),
            time.perf_counter() - t0,
            getattr(u, "prompt_tokens", None),
            getattr(u, "completion_tokens", None),
        )
