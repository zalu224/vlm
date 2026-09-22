import json

import pytest

from navbench.questions import PROMPTS, build_prompt, load_questions, validate_questions


def test_prompts_are_the_papers_wording():
    assert PROMPTS["counting"] == "Count the number of chairs in the scene."
    assert PROMPTS["spatial"] == "Which chair is closer to the viewpoint?"
    assert PROMPTS["commonsense"].startswith("Are there any vacant seats in this image?")
    assert "Answer yes or no before providing details." in PROMPTS["commonsense"]


def test_build_prompt_navigation_has_system_and_user():
    q = {"task": "navigation", "query": "I want to sit down. Guide me to a vacant seat."}
    system, user = build_prompt(q)
    assert "vacant seat" in system.lower() and "do not" in system.lower()
    assert user == q["query"]
    s2, u2 = build_prompt({"task": "counting"})
    assert s2 is None and u2 == PROMPTS["counting"]


def test_validate_questions_catches_bad_rows(tmp_path):
    good = {
        "qid": "count_1",
        "task": "counting",
        "tier": "paper",
        "image": "campus/classroom_chairs_1",
        "answer": 1,
        "answer_type": "int",
        "scene": "1 chair",
        "verified": True,
    }
    p = tmp_path / "q.jsonl"
    p.write_text(json.dumps(good) + "\n")
    qs = load_questions(p)
    assert validate_questions(qs, known_images={"campus/classroom_chairs_1"}) == []
    bad = dict(good, qid="count_1", image="campus/missing", answer_type="int", answer="x")
    p.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n")
    with pytest.raises(ValueError):
        load_questions(p)  # duplicate qid
    bad["qid"] = "count_2"
    p.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n")
    problems = validate_questions(load_questions(p), known_images={"campus/classroom_chairs_1"})
    assert any("missing" in m for m in problems) and any("answer" in m for m in problems)
