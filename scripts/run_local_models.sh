#!/bin/sh
# Full benchmark on every local model, one served at a time. Resumable: rerun to continue.
cd /Users/aaronlu/vlmproj
N=.venv/bin/nav
run_model() {  # $1 = roster key, $2 = served id
  pkill -f mlx_vlm.server; sleep 3
  nohup .venv/bin/python -m mlx_vlm.server --model "$2" --port 8080 > "logs/server_$1.log" 2>&1 &
  for i in $(seq 1 120); do curl -sf http://localhost:8080/v1/models >/dev/null && break; sleep 5; done
  curl -sf http://localhost:8080/v1/models >/dev/null || { echo "[local] $1: server failed to start"; return 1; }
  echo "[local] $1 start $(date)"
  $N run --model "$1" --task all --repeats 100 --nav-repeats 10 --tier paper || echo "[local] $1 paper tier FAILED"
  $N run --model "$1" --task counting --repeats 20 --tier ext || true
  $N run --model "$1" --task commonsense --repeats 20 --tier ext || true
  echo "[local] $1 done $(date)"
}
run_model qwen2.5-vl-7b mlx-community/Qwen2.5-VL-7B-Instruct-4bit
run_model qwen2.5-vl-3b mlx-community/Qwen2.5-VL-3B-Instruct-4bit
run_model qwen3-vl-2b mlx-community/Qwen3-VL-2B-Instruct-4bit
run_model internvl3-2b mlx-community/InternVL3-2B-4bit
run_model llava-1.6-mistral-7b mlx-community/llava-v1.6-mistral-7b-4bit
pkill -f mlx_vlm.server
$N score
echo "[local] ALL DONE $(date)"
