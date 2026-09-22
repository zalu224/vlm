import csv
import json

from navbench.spotcheck import agreement, cohens_kappa, write_sheet


def test_cohens_kappa_known_values():
    assert cohens_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0
    assert cohens_kappa([1, 0, 1, 0], [0, 1, 0, 1]) == -1.0
    assert round(cohens_kappa([1, 1, 1, 0, 0, 0, 1, 0], [1, 1, 0, 0, 0, 1, 1, 0]), 3) == 0.5


def test_sheet_is_blinded_and_agreement_reads_it_back(tmp_path):
    judged = tmp_path / "judged.jsonl"
    rows = []
    for m in ("a", "b"):
        for k in range(3):
            rows.append(
                {
                    "model": m,
                    "task": "navigation",
                    "qid": f"nav_{k}_q1",
                    "repeat": 0,
                    "image": "chairs/IMG_Cl",
                    "prompt": "Guide me.",
                    "output": f"out {m}{k}",
                    "judge_model": "j",
                    "ratings": {"destination": True, "route": k % 2 == 0, "obstacles": False},
                    "reasons": {},
                }
            )
    judged.write_text("".join(json.dumps(r) + "\n" for r in rows))
    questions = {f"nav_{k}_q1": {"gold": f"gold {k}"} for k in range(3)}
    sheet, key = write_sheet(judged, questions, tmp_path / "sheet.csv", n=4, seed=1)
    srows = list(csv.DictReader(sheet.open()))
    assert len(srows) == 4 and "model" not in srows[0] and "ratings" not in srows[0]
    assert set(srows[0]) >= {"item", "image", "gold", "output", "destination", "route", "obstacles"}
    # human copies the judge exactly for two rows, disagrees on route for the rest
    keys = {k["item"]: k for k in csv.DictReader(key.open())}
    for i, r in enumerate(srows):
        j = next(
            x
            for x in rows
            if x["model"] == keys[r["item"]]["model"] and x["qid"] == keys[r["item"]]["qid"]
        )
        r["destination"] = "yes" if j["ratings"]["destination"] else "no"
        r["route"] = (
            ("yes" if j["ratings"]["route"] else "no")
            if i < 2
            else ("no" if j["ratings"]["route"] else "yes")
        )
        r["obstacles"] = "no"
    with sheet.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(srows[0].keys()))
        w.writeheader()
        w.writerows(srows)
    res = agreement(sheet, key, judged)
    assert res["destination"]["n"] == 4 and res["destination"]["agreement"] == 1.0
    assert res["route"]["agreement"] == 0.5 and res["obstacles"]["agreement"] == 1.0
