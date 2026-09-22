PY ?= python3.11
BIN := .venv/bin
.PHONY: setup test lint serve ingest
setup:
	uv venv --python $(PY) .venv
	uv pip install --python $(BIN)/python -e ".[dev,cloud]" mlx-vlm
test:
	$(BIN)/pytest -q
lint:
	$(BIN)/ruff check navbench tests && $(BIN)/ruff format --check navbench tests
# Serve one local model (MODEL=mlx-community/...) on :8080
serve:
	$(BIN)/python -m mlx_vlm.server --model $(MODEL) --port 8080
ingest:
	$(BIN)/nav ingest --src data/pblv_nav_src --out data/pblv_nav
