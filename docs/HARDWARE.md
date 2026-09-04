# Hardware Notes: 18 GB Apple Silicon

## Memory budget

| Component | Model | Memory (approx.) | Backend |
|---|---|---|---|
| VLM | Qwen2.5-VL-7B-Instruct, 4-bit | 5–6 GB | MLX / Metal |
| VLM (lighter) | Qwen2.5-VL-3B-Instruct, 4-bit | 2.5–3 GB | MLX / Metal |
| Depth | Depth Anything V2 Small | ~0.3 GB | PyTorch MPS |
| Detector | YOLO-World v2 (S) | ~0.3 GB | PyTorch MPS |
| Python/PyTorch/MLX runtime | | 2–3 GB | |
| Streamlit viewer | | ~0.3 GB | |
| **Total (7B)** | | **~9–11 GB** | |

Unified memory is shared between CPU and GPU, so the sum above is the number that matters. Close browsers with many tabs during long runs; keep at least 4 GB free for macOS.

## Why MLX and not PyTorch for the VLM

Running Qwen2.5-VL-7B in PyTorch on MPS needs bf16 weights (~15 GB) plus activations — over budget. 4-bit MLX weights are a quarter of that and MLX uses the unified memory zero-copy. The perception models are small enough that PyTorch MPS is fine, and keeping them in PyTorch means the code is portable to Linux/CUDA unchanged.

## Throughput expectations

Measured numbers vary by chip generation and frame resolution. Reasonable planning values for an M3 Pro-class machine with frames downscaled to 768 px on the long side:

| Stage | 3B | 7B |
|---|---|---|
| VLM per frame (image + ~250-token prompt, ≤ 80-token reply) | 1–3 s | 3–8 s |
| Depth + detector per frame | 0.3–0.7 s | same |
| Judge per frame (image + instruction, ≤ 300-token JSON) | 2–4 s | 4–10 s |

300 frames × 2 conditions × (generate + judge) ≈ 1.5–3 h at 7B. Run it overnight, or use `--limit` for iteration and the full set once.

## Decision rule for model size

Start with **7B** for quality. Drop to **3B** if median VLM latency exceeds ~8 s or if memory pressure (Activity Monitor → Memory Pressure turning yellow) appears. Record which model produced each run: it is saved in `results/<run>/config.yaml` automatically.

## Known issues and fixes (root-cause log)

Record environment problems here with the fix, so they do not recur.

- **`mlx_vlm.server` not found** — `mlx-vlm` is not in the backend requirements because it is macOS-only. Install with `pip install mlx-vlm` inside `.venv` (the `make serve-vlm` target does this).
- **First request is slow** — model weights are memory-mapped lazily; the first call after startup can take 30–60 s. Not a bug.
- **PyTorch MPS op not implemented** — set `PYTORCH_ENABLE_MPS_FALLBACK=1` only as a diagnostic; the proper fix is to update torch (`pip install -U torch`) since Depth Anything and YOLO-World ops are supported on recent releases.
- **Vision-token blowup** — very large frames produce thousands of vision tokens and slow every call. `vlm.image_max_side: 768` in the config bounds this; do not raise it without checking latency.
- **Server rejects data-URL images** — the client sends base64 data URLs in the standard OpenAI multimodal format. If a server build rejects them, check its README for the supported image field; do not fall back to sending file paths (non-portable).
