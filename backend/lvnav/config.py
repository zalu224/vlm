"""Typed configuration loaded from YAML with CLI overrides."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "default.yaml"


@dataclass
class VLMConfig:
    backend: str = "http"
    base_url: str = "http://localhost:8080/v1"
    model: str = "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"
    temperature: float = 0.0
    max_tokens: int = 80
    timeout_s: int = 120
    image_max_side: int = 768


@dataclass
class PerceptionConfig:
    enabled: bool = True
    device: str = "auto"
    depth_model: str = "depth-anything/Depth-Anything-V2-Small-hf"
    detector_model: str = "yolov8s-worldv2.pt"
    detector_conf: float = 0.30
    vocabulary: list[str] = field(default_factory=lambda: ["person", "car", "pole", "stairs"])


@dataclass
class ContextConfig:
    memory_frames: int = 3
    include_last_instruction: bool = True
    prompt_version: str = "v1"


@dataclass
class JudgeConfig:
    backend: str = "http"
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int = 300
    version: str = "v1"  # judge prompt version, see eval/rubric.py


@dataclass
class Config:
    run_name: str | None = None
    results_root: str = "results"
    vlm: VLMConfig = field(default_factory=VLMConfig)
    perception: PerceptionConfig = field(default_factory=PerceptionConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    judge: JudgeConfig = field(default_factory=JudgeConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(self.to_dict(), sort_keys=False))


def _merge(section_cls, raw: dict[str, Any] | None):
    raw = raw or {}
    known = {f: raw[f] for f in section_cls.__dataclass_fields__ if f in raw}
    return section_cls(**known)


def load_config(path: Path | None = None) -> Config:
    """Load YAML config; unknown keys are ignored so configs stay forward-compatible."""
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    return Config(
        run_name=raw.get("run_name"),
        results_root=raw.get("results_root", "results"),
        vlm=_merge(VLMConfig, raw.get("vlm")),
        perception=_merge(PerceptionConfig, raw.get("perception")),
        context=_merge(ContextConfig, raw.get("context")),
        judge=_merge(JudgeConfig, raw.get("judge")),
    )
