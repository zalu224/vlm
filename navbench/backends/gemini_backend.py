"""Google Gemini via google-genai. Client built lazily from GEMINI_API_KEY; tests inject a fake."""

from __future__ import annotations

import time
from pathlib import Path

from .base import Reply, encode_jpeg


class GeminiBackend:
    name = "gemini"

    def __init__(self, model, *, temperature=1.0, top_p=1.0, max_tokens=400, image_max_side=1024):
        self.model, self.temperature, self.top_p = model, temperature, top_p
        self.max_tokens, self.image_max_side = max_tokens, image_max_side
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client()
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def generate(self, system, user, image, *, seed=None) -> Reply:
        import base64

        parts: list = []
        if image is not None:
            b64, mt = encode_jpeg(Path(image), self.image_max_side)
            parts.append({"inline_data": {"mime_type": mt, "data": base64.b64decode(b64)}})
        parts.append(user)
        config = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_tokens,
        }
        if system:
            config["system_instruction"] = system
        if seed is not None:
            config["seed"] = seed
        t0 = time.perf_counter()
        resp = self.client.models.generate_content(model=self.model, contents=parts, config=config)
        u = getattr(resp, "usage_metadata", None)
        return Reply(
            (getattr(resp, "text", "") or "").strip(),
            time.perf_counter() - t0,
            getattr(u, "prompt_token_count", None),
            getattr(u, "candidates_token_count", None),
        )
