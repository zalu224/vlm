# Repository-wide entry points. Backend-specific details: backend/README.md

PY        ?= python3
VENV      ?= .venv
BIN       := $(VENV)/bin
# BACKEND: http (local VLM server) or mock (no models, for testing)
BACKEND   ?= http
VLM_MODEL ?= mlx-community/Qwen2.5-VL-7B-Instruct-4bit
VLM_PORT  ?= 8080
FPS       ?= 1

.PHONY: setup serve-vlm frames run-naive run-context run-context-v2 judge judge-v2 report report-v2 viewer test lint clean

setup:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e "backend[dev,perception]"
	$(BIN)/pip install -r frontend/requirements.txt
	@echo "\nDone. Activate with: source $(VENV)/bin/activate"

# macOS / Apple Silicon only. Downloads the model on first run.
serve-vlm:
	$(BIN)/pip install -q mlx-vlm
	$(BIN)/python -m mlx_vlm.server --model $(VLM_MODEL) --port $(VLM_PORT)

frames:
	$(BIN)/lvnav extract-frames --video $(VIDEO) --out $(OUT) --fps $(FPS)

run-naive:
	$(BIN)/lvnav run --frames $(FRAMES) --mode naive --backend $(BACKEND)

run-context:
	$(BIN)/lvnav run --frames $(FRAMES) --mode context --backend $(BACKEND)

# Best arm from the Day-4 iteration: prompt v2, last instruction not echoed into memory.
run-context-v2:
	$(BIN)/lvnav run --frames $(FRAMES) --mode context --backend $(BACKEND) \
	  --config backend/configs/context_v2_nomem.yaml --run-name $(notdir $(FRAMES))_context_v2_nomem

judge:
	$(BIN)/lvnav judge --run $(RUN) --backend $(BACKEND)

# Judge v2 (reason before each score) on every EVERY-th frame; CUES_FROM for naive runs.
EVERY ?= 4
judge-v2:
	$(BIN)/lvnav judge --run $(RUN) --backend $(BACKEND) --judge-version v2 --every $(EVERY) \
	  $(if $(CUES_FROM),--cues-from $(CUES_FROM),)

report:
	$(BIN)/lvnav report --a $(A) --b $(B)

report-v2:
	$(BIN)/lvnav report --a $(A) --b $(B) --judged-name judged_v2_every$(EVERY).jsonl

viewer:
	$(BIN)/streamlit run frontend/app.py

test:
	$(BIN)/pytest backend/tests -q

lint:
	$(BIN)/ruff check backend frontend
	$(BIN)/ruff format --check backend frontend

clean:
	rm -rf $(VENV) backend/*.egg-info .pytest_cache .ruff_cache
