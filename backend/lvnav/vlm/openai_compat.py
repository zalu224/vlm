"""Client for any OpenAI-compatible chat endpoint (mlx_vlm.server, Ollama, LM Studio).

Images are sent as base64 data URLs in the standard multimodal message format.
The frame is downscaled to `image_max_side` before encoding to keep the number of
vision tokens (and therefore latency and memory) bounded.
"""

from __future__ import annotations

import base64
import io
import time
from pathlib import Path

import requests
from PIL import Image

from .base import VLMResponse


def _encode_image(path: Path, max_side: int) -> str:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


class OpenAICompatBackend:
    name = "http"

    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 80,
        timeout_s: int = 120,
        image_max_side: int = 768,
        api_key: str = "local",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.image_max_side = image_max_side
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        )

    def health(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/models", timeout=5)
            return r.ok
        except requests.RequestException:
            return False

    def generate(
        self,
        system: str,
        user: str,
        image: Path | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> VLMResponse:
        content: list[dict] = [{"type": "text", "text": user}]
        if image is not None:
            content.insert(
                0,
                {
                    "type": "image_url",
                    "image_url": {"url": _encode_image(Path(image), self.image_max_side)},
                },
            )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": content},
            ],
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
            "stream": False,
        }
        t0 = time.perf_counter()
        r = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, timeout=self.timeout_s
        )
        latency = time.perf_counter() - t0
        if not r.ok:
            raise RuntimeError(f"VLM server error {r.status_code}: {r.text[:400]}")
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage") or {}
        return VLMResponse(
            text=text,
            latency_s=latency,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            raw=data,
        )
