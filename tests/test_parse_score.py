from navbench.parse import parse_answer
from navbench.score import score_rows


def test_parse_int_choice_yesno():
    assert parse_answer("There are 3 chairs in the scene.", "int") == 3
    assert parse_answer("I count three chairs.", "int") == 3
    assert parse_answer("No chairs are visible.", "int") is None
    assert (
        parse_answer(
            "The chair on the left is closer to the viewpoint.", "choice", ["left", "right"]
        )
        == "left"
    )
    assert (
        parse_answer(
            "The yellow chair is nearer than the orange one.", "choice", ["orange", "yellow"]
        )
        == "yellow"
    )
    assert parse_answer("Both chairs are equally far.", "choice", ["left", "right"]) is None
    assert parse_answer("Yes. The chair on the right is free.", "yesno") == "yes"
    assert parse_answer("No, there are no vacant seats: a coat is on the chair.", "yesno") == "no"
    assert parse_answer("It is hard to tell.", "yesno") is None


def test_score_rows_accuracy_mean_variance_by_scene():
    q = {
        "c1": {"task": "counting", "answer": 3, "answer_type": "int", "scene": "3 chairs"},
        "s1": {
            "task": "spatial",
            "answer": "left",
            "answer_type": "choice",
            "choices": ["left", "right"],
            "scene": "case 1",
        },
    }
    rows = [
        {"qid": "c1", "parsed": 3},
        {"qid": "c1", "parsed": 3},
        {"qid": "c1", "parsed": 4},
        {"qid": "c1", "parsed": None},
        {"qid": "s1", "parsed": "left"},
        {"qid": "s1", "parsed": "right"},
    ]
    s = score_rows(rows, q)
    c = s["by_qid"]["c1"]
    assert c["n"] == 4 and c["accuracy"] == 0.5 and c["parse_fail"] == 1
    assert c["mean"] == round((3 + 3 + 4) / 3, 3) and c["variance"] > 0
    assert (
        s["by_task"]["counting"]["accuracy"] == 0.5 and s["by_task"]["spatial"]["accuracy"] == 0.5
    )
