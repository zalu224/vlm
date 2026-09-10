"""End-to-end frame → instruction pipeline for the naive and context conditions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from PIL import Image
from tqdm import tqdm

from .config import Config
from .context import RollingMemory, build_context_prompt, build_naive_prompt
from .data.frames import Frame, list_frames
from .vlm.base import VLMBackend

# Four conditions. `cues` and `memory` isolate the two context components so their
# individual contributions can be attributed; `context` supplies both.
Mode = Literal["naive", "cues", "memory", "context"]

USES_CUES = {"cues", "context"}
USES_MEMORY = {"memory", "context"}


@dataclass
class Record:
    run: str
    mode: str
    frame_id: str
    frame_path: str
    prompt_version: str
    cues: str | None
    cues_struct: dict | None
    memory: str | None
    instruction: str
    latency_s: float
    prompt_tokens: int | None
    completion_tokens: int | None


def run_pipeline(
    frames_dir: Path,
    mode: Mode,
    backend: VLMBackend,
    cfg: Config,
    perception=None,
    run_name: str | None = None,
    limit: int | None = None,
    save_cues_json: bool = True,
) -> Path:
    """Run one condition over a frame directory and write results/<run>/records.jsonl.

    Returns the run directory. In `context` mode a perception stack must be supplied.
    """
    frames_dir = Path(frames_dir)
    frames: list[Frame] = list_frames(frames_dir, limit)
    if not frames:
        raise ValueError(f"No image frames found in {frames_dir}")
    if mode in USES_CUES and perception is None:
        raise ValueError(f"{mode!r} mode requires a perception stack")

    run_name = run_name or cfg.run_name or f"{frames_dir.name}_{mode}"
    run_dir = Path(cfg.results_root) / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg.save(run_dir / "config.yaml")

    memory = RollingMemory(
        cfg.context.memory_frames,
        cfg.context.include_last_instruction,
        include_cues=mode in USES_CUES,
    )
    out_path = run_dir / "records.jsonl"

    with out_path.open("w") as fh:
        for frame in tqdm(frames, desc=f"{run_name}", unit="frame"):
            cues_text = cues_struct = memory_text = None
            if mode == "naive":
                prompt = build_naive_prompt()
            else:
                if mode in USES_CUES:
                    with Image.open(frame.path) as img:
                        cues = perception(img.convert("RGB"))
                    cues_text = cues.to_text()
                    cues_struct = cues.to_dict() if save_cues_json else None
                if mode in USES_MEMORY:
                    memory_text = memory.to_text()
                prompt = build_context_prompt(
                    cues_text, memory_text, cfg.context.prompt_version, label=mode
                )

            resp = backend.generate(prompt.system, prompt.user, image=frame.path)

            if mode in USES_MEMORY:
                memory.push(frame.frame_id, cues_text or "", resp.text)

            rec = Record(
                run=run_name,
                mode=mode,
                frame_id=frame.frame_id,
                frame_path=str(frame.path),
                prompt_version=prompt.version,
                cues=cues_text,
                cues_struct=cues_struct,
                memory=memory_text,
                instruction=resp.text,
                latency_s=round(resp.latency_s, 3),
                prompt_tokens=resp.prompt_tokens,
                completion_tokens=resp.completion_tokens,
            )
            fh.write(json.dumps(asdict(rec)) + "\n")
            fh.flush()
    return run_dir


def read_jsonl(path: Path) -> list[dict]:
    with Path(path).open() as fh:
        return [json.loads(line) for line in fh if line.strip()]
