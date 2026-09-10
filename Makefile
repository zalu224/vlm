# Repository-wide entry points. Backend-specific details: backend/README.md

PY        ?= python3
VENV      ?= .venv
BIN       := $(VENV)/bin
# BACKEND: http (local VLM server) or mock (no models, for testing)
BACKEND   ?= http
VLM_MODEL ?= mlx-community/Qwen2.5-VL-7B-Instruct-4bit
VLM_PORT  ?= 8080
FPS       ?= 1

.PHONY: setup serve-vlm frames run-naive run-context judge report viewer test lint clean \
        shelf-index shelf-detect shelf-trials shelf-annotate shelf-search shelf-correct shelf-report

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

judge:
	$(BIN)/lvnav judge --run $(RUN) --backend $(BACKEND)

report:
	$(BIN)/lvnav report --a $(A) --b $(B)

viewer:
	$(BIN)/streamlit run frontend/app.py

# --- Last-Shelf study (docs/LASTSHELF.md) ---------------------------------
SHELF_DATA ?= data/shelf
SHELF_RES  ?= results/shelf

shelf-index:
	$(BIN)/lvnav shelf index --catalog $(SHELF_DATA)/catalog --results $(SHELF_RES) --backend $(BACKEND)

shelf-detect:
	$(BIN)/lvnav shelf detect --images $(SHELF_DATA)/images --results $(SHELF_RES) --backend $(BACKEND)

shelf-trials:
	$(BIN)/lvnav shelf trials --results $(SHELF_RES) --default-target $(TARGET)

shelf-annotate:
	$(BIN)/lvnav shelf annotate --results $(SHELF_RES)

shelf-search:
	$(BIN)/lvnav shelf search --results $(SHELF_RES) --backend $(BACKEND)

# LABEL names the model in the report; MODEL overrides the served checkpoint.
shelf-correct:
	$(BIN)/lvnav shelf correct --results $(SHELF_RES) --backend $(BACKEND) \
		$(if $(LABEL),--label $(LABEL)) $(if $(MODEL),--model $(MODEL))

shelf-report:
	$(BIN)/lvnav shelf report --results $(SHELF_RES)
	$(BIN)/lvnav shelf summary --results $(SHELF_RES)

test:
	$(BIN)/pytest backend/tests -q

lint:
	$(BIN)/ruff check backend frontend
	$(BIN)/ruff format --check backend frontend

clean:
	rm -rf $(VENV) backend/*.egg-info .pytest_cache .ruff_cache
