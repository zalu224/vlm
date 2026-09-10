import json

import pytest

from lvnav.config import load_config
from lvnav.eval import judge_run, parse_judge_output, write_report
from lvnav.perception import build_perception
from lvnav.pipeline import read_jsonl, run_pipeline
from lvnav.vlm import build_backend


def _cfg(tmp_path):
    cfg = load_config()
    cfg.results_root = str(tmp_path / "results")
    cfg.vlm.backend = "mock"
    cfg.judge.backend = "mock"
    return cfg


def test_naive_and_context_end_to_end(frames_dir, tmp_path):
    cfg = _cfg(tmp_path)
    backend = build_backend("mock", cfg.vlm)
    perception = build_perception(cfg.perception, use_mock=True)

    a = run_pipeline(frames_dir, "naive", backend, cfg)
    b = run_pipeline(frames_dir, "context", backend, cfg, perception=perception)

    ra, rb = read_jsonl(a / "records.jsonl"), read_jsonl(b / "records.jsonl")
    assert len(ra) == len(rb) == 6
    assert ra[0]["cues"] is None and rb[0]["cues"].startswith("Free space:")
    assert "start of the walk" in rb[0]["memory"]
    assert "Last instruction given" in rb[3]["memory"]
    assert (a / "config.yaml").exists()

    judge_run(a, backend, cues_from=b)
    judge_run(b, backend)
    ja = read_jsonl(a / "judged.jsonl")
    assert set(ja[0]["scores"]) == {
        "safety",
        "actionability",
        "spatial_accuracy",
        "conciseness",
        "hallucination",
    }

    report = write_report(a, b)
    text = report.read_text()
    assert "Paired comparison" in text and "| safety |" in text


def test_parse_judge_output_tolerates_wrapping():
    text = 'Sure:\n```json\n{"scores": {"safety": 5, "actionability": 4, "spatial_accuracy": 3, "conciseness": 9, "hallucination": 2}, "rationale": "ok"}\n```'
    scores, rationale = parse_judge_output(text)
    assert scores["safety"] == 5 and scores["conciseness"] is None
    assert rationale == "ok"


def test_records_are_valid_jsonl(frames_dir, tmp_path):
    cfg = _cfg(tmp_path)
    run_dir = run_pipeline(frames_dir, "naive", build_backend("mock", cfg.vlm), cfg, limit=2)
    lines = (run_dir / "records.jsonl").read_text().splitlines()
    assert len(lines) == 2
    for line in lines:
        json.loads(line)


def test_four_conditions_isolate_context_components(frames_dir, tmp_path):
    """cues-only carries no history; memory-only carries no sensor cues."""
    cfg = _cfg(tmp_path)
    backend = build_backend("mock", cfg.vlm)
    perception = build_perception(cfg.perception, use_mock=True)

    runs = {
        "naive": run_pipeline(frames_dir, "naive", backend, cfg),
        "cues": run_pipeline(frames_dir, "cues", backend, cfg, perception=perception),
        "memory": run_pipeline(frames_dir, "memory", backend, cfg),
        "context": run_pipeline(frames_dir, "context", backend, cfg, perception=perception),
    }
    rows = {k: read_jsonl(v / "records.jsonl") for k, v in runs.items()}
    assert {len(r) for r in rows.values()} == {6}

    assert rows["naive"][3]["cues"] is None and rows["naive"][3]["memory"] is None
    assert rows["cues"][3]["cues"] and rows["cues"][3]["memory"] is None
    assert rows["memory"][3]["memory"] and rows["memory"][3]["cues"] is None
    assert rows["context"][3]["cues"] and rows["context"][3]["memory"]

    # Memory-only recalls prior instructions, not cue text it never received.
    assert "Free space:" not in rows["memory"][3]["memory"]
    assert "Free space:" in rows["context"][3]["memory"]

    assert rows["cues"][0]["prompt_version"] == "cues-v1"
    assert rows["memory"][0]["prompt_version"] == "memory-v1"


def test_cues_mode_requires_perception(frames_dir, tmp_path):
    cfg = _cfg(tmp_path)
    with pytest.raises(ValueError, match="requires a perception stack"):
        run_pipeline(frames_dir, "cues", build_backend("mock", cfg.vlm), cfg)
