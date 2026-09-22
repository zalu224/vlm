"""OpenAI-compatible chat endpoint (mlx_vlm.server locally; any compatible server)."""

from __future__ import annotations

import time
from pathlib import Path

import requests

from .base import Reply, encode_jpeg


class MlxServerBackend:
    name = "mlx"

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: int = 400,
        image_max_side: int = 1024,
        timeout_s: int = 180,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature, self.top_p = temperature, top_p
        self.max_tokens, self.image_max_side, self.timeout_s = max_tokens, image_max_side, timeout_s
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Authorization": "Bearer local"}
        )

    def health(self) -> bool:
        try:
            return self.session.get(f"{self.base_url}/models", timeout=5).ok
        except requests.RequestException:
            return False

    def generate(self, system, user, image, *, seed=None) -> Reply:
        content: list[dict] = []
        if image is not None:
            b64, mt = encode_jpeg(Path(image), self.image_max_side)
            content.append({"type": "image_url", "image_url": {"url": f"data:{mt};base64,{b64}"}})
        content.append({"type": "text", "text": user})
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": content}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        if seed is not None:
            payload["seed"] = seed
        t0 = time.perf_counter()
        r = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, timeout=self.timeout_s
        )
        latency = time.perf_counter() - t0
        if not r.ok:
            raise RuntimeError(f"server error {r.status_code}: {getattr(r, 'text', '')[:300]}")
        data = r.json()
        usage = data.get("usage") or {}
        return Reply(
            data["choices"][0]["message"]["content"].strip(),
            latency,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            data,
        )
