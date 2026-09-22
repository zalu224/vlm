#!/bin/sh
# The two models the first chain could not finish. Resumable: rerun to continue.
#
# What went wrong the first time, and what is different here:
#
#   internvl3-2b            Every request to mlx_vlm.server returned 500 "There is no Stream(gpu, 2)
#                           in current thread" from the prompt cache, because the server generates
#                           on a pool thread. Zero outputs. Now runs on the mlx-direct backend,
#                           in-process, which the models.yaml entry selects: no server involved.
#
#   llava-1.6-mistral-7b    The server was still downloading 4.26 GB of weights when the readiness
#                           loop gave up after 600 s, and the chain's cleanup then killed the
#                           download. Now the weights are fetched to completion first (hf download
#                           is a no-op once cached), and only then is the server started, with a
#                           readiness window of 30 min for the load itself.
cd /Users/aaronlu/vlmproj || exit 1
N=.venv/bin/nav

run_tasks() {  # $1 = roster key
  echo "[local] $1 start $(date)"
  $N run --model "$1" --task all --repeats 100 --nav-repeats 10 --tier paper || echo "[local] $1 paper tier FAILED"
  $N run --model "$1" --task counting   --repeats 20 --tier ext || true
  $N run --model "$1" --task commonsense --repeats 20 --tier ext || true
  echo "[local] $1 done $(date)"
}

# 1. InternVL3-2B — in-process, no server. Make sure nothing is holding the GPU.
pkill -f mlx_vlm.server
sleep 3
run_tasks internvl3-2b

# 2. LLaVA-v1.6-Mistral-7B — weights first, then serve.
echo "[local] llava: fetching weights $(date)"
# `hf download` does NOT resume: each attempt writes a new <etag>.<random>.incomplete and starts
# from zero, so every killed download leaves a multi-GB orphan behind and the next try needs the
# full 4.26 GB again. Three interrupted attempts filled this disk. Clear any orphan first, so the
# space needed is the size of the model and not a multiple of it.
LLAVA_BLOBS="$HOME/.cache/huggingface/hub/models--mlx-community--llava-v1.6-mistral-7b-4bit/blobs"
rm -f "$LLAVA_BLOBS"/*.incomplete
.venv/bin/hf download mlx-community/llava-v1.6-mistral-7b-4bit > logs/llava_download.log 2>&1 \
  || { echo "[local] llava: download FAILED (disk? network?)"; rm -f "$LLAVA_BLOBS"/*.incomplete; exit 1; }
echo "[local] llava: weights ready $(date)"

nohup .venv/bin/python -m mlx_vlm.server --model mlx-community/llava-v1.6-mistral-7b-4bit \
  --port 8080 > logs/server_llava-1.6-mistral-7b.log 2>&1 &
for i in $(seq 1 360); do
  curl -sf http://localhost:8080/v1/models > /dev/null && break
  sleep 5
done
if curl -sf http://localhost:8080/v1/models > /dev/null; then
  run_tasks llava-1.6-mistral-7b
else
  echo "[local] llava-1.6-mistral-7b: server failed to start after 30 min"
fi

pkill -f mlx_vlm.server
$N score
echo "[local] REMAINING MODELS DONE $(date)"
