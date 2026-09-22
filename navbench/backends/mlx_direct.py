"""MLX in-process: load the model here and generate on this thread, with no HTTP server.

Why this exists. `mlx_vlm.server` runs generation inside `asyncio.to_thread`, and for some
architectures the prompt cache ends up holding a GPU stream that belongs to a different thread;
the first call then dies with `RuntimeError: There is no Stream(gpu, 2) in current thread.`
InternVL3-2B hits this on every request while the Qwen models do not, so the server path cannot
run it at all. The same weights generate correctly when loaded and called on one thread, which is
what this backend does. It is otherwise a drop-in for `MlxServerBackend`: same constructor
arguments, same `Reply`, so `nav run` and the runner are unchanged.

The cost is that the model is held in this process, so one model runs at a time — which is
already how the benchmark is organised.
"""

from __future__ import annotations

import time

from .base import Reply


class MlxDirectBackend:
    name = "mlx-direct"

    def __init__(
        self,
        model: str,
        *,
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: int = 400,
        image_max_side: int = 1024,
        **_ignored,
    ) -> None:
        self.model_id = model
        self.temperature, self.top_p = temperature, top_p
        self.max_tokens, self.image_max_side = max_tokens, image_max_side
        self._model = None
        self._processor = None

    def _ensure_loaded(self):
        """Load once, on first use, so constructing a backend stays cheap and importable."""
        if self._model is None:
            from mlx_vlm import load

            self._model, self._processor = load(self.model_id)
        return self._model, self._processor

    def health(self) -> bool:
        """No server to reach; the weights are loaded in this process."""
        return True

    def generate(self, system, user, image, *, seed=None) -> Reply:
        from mlx_vlm import generate as mlx_generate
        from mlx_vlm.prompt_utils import apply_chat_template

        model, processor = self._ensure_loaded()
        text = f"{system}\n\n{user}" if system else user
        images = [str(image)] if image is not None else None
        prompt = apply_chat_template(
            processor,
            getattr(model, "config", None),
            text,
            num_images=1 if image is not None else 0,
        )
        t0 = time.perf_counter()
        result = mlx_generate(
            model,
            processor,
            prompt,
            image=images,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            verbose=False,
        )
        latency = time.perf_counter() - t0
        out = getattr(result, "text", result)
        return Reply(
            str(out).strip(),
            latency,
            getattr(result, "prompt_tokens", None),
            getattr(result, "generation_tokens", None),
            None,
        )

    # `image_max_side` is accepted for interface parity. mlx_vlm resizes with the model's own
    # processor, so downscaling here would only fight it; the difference from the server path is
    # recorded in the design note rather than hidden.
    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"MlxDirectBackend({self.model_id})"
