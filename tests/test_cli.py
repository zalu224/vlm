import json

from navbench.cli import main


def test_cli_help_lists_stages(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    for s in ("ingest", "questions", "run", "score", "judge", "report"):
        assert s in out


def test_cli_run_mock_then_score(tmp_path, images_dir, monkeypatch):
    data = tmp_path / "data"
    assert main(["ingest", "--src", str(images_dir), "--out", str(data)]) == 0
    q = tmp_path / "q.jsonl"
    q.write_text(
        json.dumps(
            {
                "qid": "count_1",
                "task": "counting",
                "tier": "paper",
                "image": "campus/classroom_chairs_1",
                "answer": 2,
                "answer_type": "int",
                "scene": "2 chairs",
                "verified": True,
            }
        )
        + "\n"
    )
    assert main(["questions", "--check", "--questions", str(q), "--data", str(data)]) == 0
    assert (
        main(
            [
                "run",
                "--model",
                "mock",
                "--task",
                "counting",
                "--repeats",
                "4",
                "--questions",
                str(q),
                "--data",
                str(data),
                "--runs",
                str(tmp_path / "runs"),
            ]
        )
        == 0
    )
    rows = [
        json.loads(line)
        for line in (tmp_path / "runs" / "mock" / "counting.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 4
    assert (
        main(
            [
                "score",
                "--questions",
                str(q),
                "--runs",
                str(tmp_path / "runs"),
                "--out",
                str(tmp_path / "reports"),
            ]
        )
        == 0
    )
    res = json.loads((tmp_path / "reports" / "results.json").read_text())
    assert "mock" in res and res["mock"]["by_task"]["counting"]["n"] == 4
