"""LLM-as-judge scoring of records.jsonl → judged.jsonl.

The judge sees the frame, the perception cues (if any) and the instruction, but
not the prompt that produced the instruction, so both conditions are judged on
identical evidence. Cues for naive runs can be borrowed from a matching context
run via `--cues-from` so the judge is not blind for the baseline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from tqdm import tqdm

from ..pipeline import read_jsonl
from ..vlm.base import VLMBackend
from .rubric import DIMENSIONS, build_judge_prompt

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_judge_output(text: str) -> tuple[dict[str, int], str]:
    """Extract scores robustly; missing or out-of-range values become None."""
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError(f"Judge returned no JSON: {text[:200]!r}")
    data = json.loads(m.group(0))
    raw = data.get("scores", {})
    scores: dict[str, int] = {}
    for dim in DIMENSIONS:
        v = raw.get(dim)
        scores[dim] = int(v) if isinstance(v, int | float) and 1 <= v <= 5 else None
    return scores, str(data.get("rationale", "")).strip()


def judge_run(
    run_dir: Path,
    backend: VLMBackend,
    cues_from: Path | None = None,
    max_tokens: int = 300,
    temperature: float = 0.0,
) -> Path:
    run_dir = Path(run_dir)
    records = read_jsonl(run_dir / "records.jsonl")

    borrowed: dict[str, str] = {}
    if cues_from is not None:
        for r in read_jsonl(Path(cues_from) / "records.jsonl"):
            if r.get("cues"):
                borrowed[r["frame_id"]] = r["cues"]

    out_path = run_dir / "judged.jsonl"
    with out_path.open("w") as fh:
        for rec in tqdm(records, desc=f"judge {run_dir.name}", unit="frame"):
            cues = rec.get("cues") or borrowed.get(rec["frame_id"])
            system, user = build_judge_prompt(rec["instruction"], cues)
            resp = backend.generate(
                system,
                user,
                image=Path(rec["frame_path"]),
                max_tokens=max_tokens,
                temperature=temperature,
            )
            try:
                scores, rationale = parse_judge_output(resp.text)
            except (ValueError, json.JSONDecodeError) as exc:
                scores, rationale = dict.fromkeys(DIMENSIONS), f"PARSE_ERROR: {exc}"
            rec = {
                **rec,
                "scores": scores,
                "judge_rationale": rationale,
                "judge_latency_s": round(resp.latency_s, 3),
            }
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
    return out_path
