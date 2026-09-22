import json

from navbench.judge_local import export_tasks, import_ratings


def _runs(tmp_path):
    """Two models, one case, two queries x two repeats."""
    for model in ("m1", "m2"):
        d = tmp_path / "runs" / model
        d.mkdir(parents=True)
        rows = []
        for qi in (1, 2):
            for rep in (0, 1):
                rows.append(
                    {
                        "model": model,
                        "task": "navigation",
                        "qid": f"nav_1_q{qi}",
                        "repeat": rep,
                        "image": "chairs/IMG_Cl",
                        "prompt": f"query {qi}",
                        "output": f"{model} out q{qi} r{rep}",
                    }
                )
        (d / "navigation.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return tmp_path / "runs"


def _questions():
    return {
        f"nav_1_q{i}": {
            "qid": f"nav_1_q{i}",
            "task": "navigation",
            "case": 1,
            "image": "chairs/IMG_Cl",
            "gold": "vacant chair right of table; box on floor",
        }
        for i in (1, 2)
    }


def test_export_groups_by_case_blinds_model_and_embeds_criteria(tmp_path):
    runs = _runs(tmp_path)
    out = export_tasks(runs, _questions(), tmp_path / "data", tmp_path / "tasks")
    files = sorted(out.glob("nav_*.json"))  # index.json sits alongside the case files
    assert [f.name for f in files] == ["nav_1.json"]
    task = json.loads(files[0].read_text())
    assert task["image"].endswith("images/chairs/IMG_Cl.jpg") and task["gold"].startswith(
        "vacant chair"
    )
    assert len(task["outputs"]) == 8  # 2 models x 2 queries x 2 repeats
    o = task["outputs"][0]
    assert set(o) == {"rating_id", "prompt", "output"}  # model name withheld from the rater
    assert all(c in task["instructions"] for c in ("destination", "route", "obstacles"))
    index = json.loads((out / "index.json").read_text())
    assert index[o["rating_id"]]["model"] in ("m1", "m2")


def test_import_writes_judged_schema_and_is_incremental(tmp_path):
    runs = _runs(tmp_path)
    tasks = export_tasks(runs, _questions(), tmp_path / "data", tmp_path / "tasks")
    ids = [o["rating_id"] for o in json.loads((tasks / "nav_1.json").read_text())["outputs"]]
    ratings = tmp_path / "ratings"
    ratings.mkdir()
    (ratings / "nav_1.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "rating_id": i,
                    "destination": "yes",
                    "route": "no",
                    "obstacles": "yes",
                    "reason": "r",
                }
            )
            + "\n"
            for i in ids[:5]
        )
    )
    judged = import_ratings(tasks, ratings, runs / "judged.jsonl", judge_model="opus-5-in-session")
    rows = [json.loads(line) for line in judged.read_text().splitlines()]
    assert len(rows) == 5
    r = rows[0]
    assert r["ratings"] == {"destination": True, "route": False, "obstacles": True}
    assert r["judge_model"] == "opus-5-in-session" and r["model"] in ("m1", "m2")
    assert set(r) >= {"model", "task", "qid", "repeat", "image", "prompt", "output", "ratings"}
    # a second import adds only the new ids
    (ratings / "nav_1.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "rating_id": i,
                    "destination": "no",
                    "route": "no",
                    "obstacles": "no",
                    "reason": "r",
                }
            )
            + "\n"
            for i in ids
        )
    )
    judged = import_ratings(tasks, ratings, runs / "judged.jsonl", judge_model="opus-5-in-session")
    rows2 = [json.loads(line) for line in judged.read_text().splitlines()]
    assert len(rows2) == 8 and rows2[:5] == rows
