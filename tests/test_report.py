import json

from navbench.report import count_table, scene_table, spatial_table, write_report


def _q():
    return {
        "count_1": {
            "task": "counting",
            "tier": "paper",
            "answer": 1,
            "answer_type": "int",
            "scene": "1 chairs",
        },
        "count_3": {
            "task": "counting",
            "tier": "paper",
            "answer": 3,
            "answer_type": "int",
            "scene": "3 chairs",
        },
        "spatial_1": {
            "task": "spatial",
            "tier": "paper",
            "answer": "left",
            "answer_type": "choice",
            "choices": ["left", "right"],
            "scene": "case 1",
        },
        "spatial_2": {
            "task": "spatial",
            "tier": "paper",
            "answer": "right",
            "answer_type": "choice",
            "choices": ["left", "right"],
            "scene": "case 1 mirrored",
        },
        "vacant_1": {
            "task": "commonsense",
            "tier": "paper",
            "answer": "yes",
            "answer_type": "yesno",
            "scene": "empty chair",
        },
    }


def _rows():
    return [
        {"qid": "count_1", "parsed": 1},
        {"qid": "count_1", "parsed": 1},
        {"qid": "count_3", "parsed": 3},
        {"qid": "count_3", "parsed": 4},
        {"qid": "spatial_1", "parsed": "left"},
        {"qid": "spatial_2", "parsed": "left"},
        {"qid": "vacant_1", "parsed": "yes"},
        {"qid": "vacant_1", "parsed": "no"},
    ]


def test_tables_mirror_the_papers_breakdowns():
    q = _q()
    ct = count_table({"m": _rows()}, q)
    assert ct[1]["m"] == 1.0 and ct[3]["m"] == 0.5
    st = spatial_table({"m": _rows()}, q)
    assert st["case 1"]["m"] == 1.0 and st["case 1 mirrored"]["m"] == 0.0
    sc = scene_table({"m": _rows()}, q, "commonsense")
    assert sc["empty chair"]["m"] == 0.5


def test_write_report_includes_paper_numbers(tmp_path):
    runs = tmp_path / "runs" / "m"
    runs.mkdir(parents=True)
    for task in ("counting", "spatial", "commonsense"):
        rows = [
            r
            for r in _rows()
            if r["qid"].startswith(
                {"counting": "count", "spatial": "spatial", "commonsense": "vacant"}[task]
            )
        ]
        (runs / f"{task}.jsonl").write_text(
            "".join(json.dumps({**r, "model": "m", "task": task}) + "\n" for r in rows)
        )
    out = write_report(tmp_path / "runs", _q(), tmp_path / "RESULTS.md")
    text = out.read_text()
    assert (
        "GPT-4o" in text and "| 3 |" in text and "case 1 mirrored" in text and "empty chair" in text
    )
