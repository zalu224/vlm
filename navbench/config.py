"""configs/models.yaml loader."""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parent.parent / "configs" / "models.yaml"


def load_models_config(path: Path | None = None) -> dict:
    cfg = yaml.safe_load(Path(path or DEFAULT).read_text()) or {}
    cfg.setdefault("models", {})
    cfg["models"]["mock"] = {
        "backend": "mock",
        "served": "mock",
        "status": "local",
        "group": "test",
    }
    return cfg
