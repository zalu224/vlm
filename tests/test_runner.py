import json

from navbench.backends.mock import MockBackend
from navbench.runner import run_task


def _questions():
    return {
        "count_1": {
            "qid": "count_1",
            "task": "counting",
            "tier": "paper",
            "image": "campus/classroom_chairs_1",
            "answer": 2,
            "answer_type": "int",
            "scene": "2 chairs",
            "verified": True,
        },
        "nav_1": {
            "qid": "nav_1",
            "task": "navigation",
            "tier": "paper",
            "image": "chairs/IMG_Cl",
            "answer": None,
            "answer_type": "free",
            "gold": "vacant chair right of table",
            "verified": True,
            "query": "I want to sit down. Guide me to a vacant seat.",
        },
    }


def test_run_task_writes_one_row_per_repeat_and_resumes(tmp_path):
    data = tmp_path / "data"
    (data / "images" / "campus").mkdir(parents=True)
    (data / "images" / "campus" / "classroom_chairs_1.jpg").write_bytes(b"")
    out = run_task(
        _questions(),
        "counting",
        MockBackend(),
        tmp_path / "runs" / "mock",
        data,
        repeats=3,
        model_name="mock",
    )
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == 3 and {r["repeat"] for r in rows} == {0, 1, 2}
    assert (
        rows[0]["qid"] == "count_1"
        and rows[0]["parsed"] in (2, 3, 4)
        and rows[0]["model"] == "mock"
    )
    assert rows[0]["prompt"] == "Count the number of chairs in the scene."
    # resume: asking for 5 repeats adds two rows, keeps the first three untouched
    out2 = run_task(
        _questions(),
        "counting",
        MockBackend(),
        tmp_path / "runs" / "mock",
        data,
        repeats=5,
        model_name="mock",
    )
    rows2 = [json.loads(line) for line in out2.read_text().splitlines()]
    assert len(rows2) == 5 and rows2[:3] == rows


def test_run_navigation_uses_system_prompt_and_query(tmp_path):
    data = tmp_path / "data"
    (data / "images" / "chairs").mkdir(parents=True)
    (data / "images" / "chairs" / "IMG_Cl.jpg").write_bytes(b"")
    out = run_task(
        _questions(),
        "navigation",
        MockBackend(),
        tmp_path / "runs" / "mock",
        data,
        repeats=2,
        model_name="mock",
    )
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == 2 and rows[0]["system"] and rows[0]["parsed"] == rows[0]["output"]
