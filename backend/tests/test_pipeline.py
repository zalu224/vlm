import json

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
    assert ja[0]["judge_raw"].startswith("{")
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


def test_summarise_reports_repetition():
    from lvnav.eval.metrics import summarise

    rows = [
        {"instruction": "Path clear. Move forward.", "scores": {}, "latency_s": 1.0},
        {"instruction": "Path clear. Move forward.", "scores": {}, "latency_s": 1.0},
        {"instruction": "Path clear. Move forward.", "scores": {}, "latency_s": 1.0},
        {"instruction": "Stop. Person ahead.", "scores": {}, "latency_s": 1.0},
    ]
    s = summarise(rows)
    assert s["repetition"]["unique"] == 2
    assert s["repetition"]["unique_ratio"] == 0.5
    assert s["repetition"]["top_share"] == 0.75
    assert s["repetition"]["top"] == "Path clear. Move forward."


def test_parse_judge_output_v2_shape():
    text = (
        '{"safety": {"reason": "hazard first", "score": 4}, "actionability": {"reason": "verb", "score": 5},'
        ' "spatial_accuracy": {"reason": "ok", "score": 3}, "conciseness": {"reason": "two sentences", "score": 5},'
        ' "hallucination": {"reason": "none", "score": 7}}'
    )
    scores, rationale = parse_judge_output(text)
    assert scores["safety"] == 4 and scores["hallucination"] is None
    assert rationale.startswith("safety: hazard first")


def test_judge_v2_every_writes_subset_file(frames_dir, tmp_path):
    cfg = _cfg(tmp_path)
    backend = build_backend("mock", cfg.vlm)
    run = run_pipeline(frames_dir, "naive", backend, cfg)
    out = judge_run(run, backend, version="v2", every=2)
    assert out.name == "judged_v2_every2.jsonl"
    rows = read_jsonl(out)
    assert len(rows) == 3 and rows[0]["judge_version"] == "v2"


def test_conciseness_auto_anchors():
    from lvnav.eval.metrics import conciseness_auto

    assert conciseness_auto("Stop. Person directly ahead.") == 5
    assert (
        conciseness_auto("The person wearing the camera should continue walking forward, as the")
        == 1
    )
    assert conciseness_auto("Here is what to do:\n1. Listen for sounds.\n2. Use your cane.") == 1
    assert conciseness_auto(" ".join(["word"] * 40) + ".") == 3


def test_report_from_alternate_judged_file(frames_dir, tmp_path):
    cfg = _cfg(tmp_path)
    backend = build_backend("mock", cfg.vlm)
    perception = build_perception(cfg.perception, use_mock=True)
    a = run_pipeline(frames_dir, "naive", backend, cfg)
    b = run_pipeline(frames_dir, "context", backend, cfg, perception=perception)
    judge_run(a, backend, cues_from=b, version="v2", every=2)
    judge_run(b, backend, version="v2", every=2)
    report = write_report(a, b, judged_name="judged_v2_every2.jsonl")
    assert report.name == "report_v2_every2.md"
    assert "judged_v2_every2.jsonl" in report.read_text()
