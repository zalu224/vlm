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
from .rubric import DIMENSIONS, JUDGE_VERSIONS

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _score(v) -> int | None:
    return int(v) if isinstance(v, int | float) and 1 <= v <= 5 else None


def parse_judge_output(text: str) -> tuple[dict[str, int], str]:
    """Extract scores robustly; missing or out-of-range values become None.

    Accepts the v1 shape ``{"scores": {dim: n}, "rationale": str}`` and the v2 shape
    ``{dim: {"reason": str, "score": n}}``; for v2 the rationale is the reasons joined.
    """
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError(f"Judge returned no JSON: {text[:200]!r}")
    data = json.loads(m.group(0))
    scores: dict[str, int] = {}
    if "scores" in data:  # v1
        raw = data.get("scores", {})
        for dim in DIMENSIONS:
            scores[dim] = _score(raw.get(dim))
        return scores, str(data.get("rationale", "")).strip()
    reasons = []
    for dim in DIMENSIONS:
        entry = data.get(dim)
        if isinstance(entry, dict):
            scores[dim] = _score(entry.get("score"))
            if entry.get("reason"):
                reasons.append(f"{dim}: {entry['reason']}")
        else:
            scores[dim] = _score(entry)
    return scores, " ".join(reasons).strip()


def judge_run(
    run_dir: Path,
    backend: VLMBackend,
    cues_from: Path | None = None,
    max_tokens: int = 300,
    temperature: float = 0.0,
    version: str = "v1",
    every: int = 1,
    out_name: str | None = None,
) -> Path:
    """Judge a run. `every` > 1 scores every Nth frame (stratified subset), `version`
    selects the judge prompt, `out_name` overrides the output filename."""
    run_dir = Path(run_dir)
    records = read_jsonl(run_dir / "records.jsonl")
    if every > 1:
        records = records[::every]
    try:
        build_prompt = JUDGE_VERSIONS[version]
    except KeyError:
        raise ValueError(f"Unknown judge version: {version}") from None

    borrowed: dict[str, str] = {}
    if cues_from is not None:
        for r in read_jsonl(Path(cues_from) / "records.jsonl"):
            if r.get("cues"):
                borrowed[r["frame_id"]] = r["cues"]

    default_name = (
        "judged.jsonl" if version == "v1" and every == 1 else f"judged_{version}_every{every}.jsonl"
    )
    out_path = run_dir / (out_name or default_name)
    with out_path.open("w") as fh:
        for rec in tqdm(records, desc=f"judge {run_dir.name}", unit="frame"):
            cues = rec.get("cues") or borrowed.get(rec["frame_id"])
            system, user = build_prompt(rec["instruction"], cues)
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
                # Keep the verbatim judge output so parse failures and score patterns can
                # be audited without re-running the judge.
                "judge_raw": resp.text,
                "judge_version": version,
            }
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
    return out_path
