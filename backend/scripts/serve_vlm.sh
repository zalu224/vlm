#!/usr/bin/env bash
# Start the local VLM server on Apple Silicon. Requires: pip install mlx-vlm
# Usage: scripts/serve_vlm.sh [model] [port]
set -euo pipefail
MODEL="${1:-mlx-community/Qwen2.5-VL-7B-Instruct-4bit}"
PORT="${2:-8080}"
echo "Serving ${MODEL} on http://localhost:${PORT}/v1"
python -m mlx_vlm.server --model "${MODEL}" --port "${PORT}"
