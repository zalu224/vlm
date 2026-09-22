"""In-session judging: rate navigation outputs without an API key.

`export_tasks` writes one file per navigation case holding the photograph, the ground truth
and every model output for that case, with the model names withheld so the rater is blind in
the same way the paper's annotators were. A rater (a Claude session, or a person) writes one
JSONL of verdicts per case; `import_ratings` merges them into runs/judged.jsonl in exactly the
schema the API judge produces, so `nav report`, `nav sheet` and `nav agreement` are unchanged.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from .judge import CRITERIA, CRITERIA_BLOCK

INSTRUCTIONS = f"""You are rating navigation instructions given to a person who is blind or has low vision, as an annotator in the study. The attached photograph is the user's current viewpoint: they stand where the camera is, facing the way it faces.

{CRITERIA_BLOCK}

Rate only what is in front of you. Do not reward length or confidence. Judge every output independently; several outputs describe the same photograph and may disagree with each other."""


def rating_id(model: str, qid: str, repeat: int) -> str:
    """Stable id that does not reveal the model to the rater."""
    return hashlib.sha1(f"{model}|{qid}|{repeat}".encode()).hexdigest()[:12]


def _case_of(q: dict, qid: str) -> str:
    return f"nav_{q['case']}" if q.get("case") else qid.rsplit("_q", 1)[0]


def export_tasks(
    runs_root: Path, questions: dict, data_root: Path, out_dir: Path, *, judged: Path | None = None
) -> Path:
    runs_root, out_dir = Path(runs_root), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    already = set()
    judged = judged or runs_root / "judged.jsonl"
    if Path(judged).exists():
        for line in Path(judged).read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                already.add(rating_id(r["model"], r["qid"], int(r["repeat"])))

    by_case: dict[str, list[dict]] = defaultdict(list)
    index: dict[str, dict] = {}
    for f in sorted(runs_root.glob("*/navigation.jsonl")):
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rid = rating_id(r["model"], r["qid"], int(r["repeat"]))
            if rid in already:
                continue
            by_case[_case_of(questions.get(r["qid"], {}), r["qid"])].append(
                {"rating_id": rid, "prompt": r["prompt"], "output": r["output"]}
            )
            index[rid] = {
                k: r[k] for k in ("model", "task", "qid", "repeat", "image", "prompt", "output")
            }

    # Case files for work that is already judged must not survive: a rater opening the directory
    # would re-rate outputs that are in judged.jsonl. Remove them, then write the current batch.
    for stale in out_dir.glob("nav_*.json"):
        stale.unlink()

    for case, outputs in sorted(by_case.items()):
        qid = next(
            i["qid"]
            for i in index.values()
            if _case_of(questions.get(i["qid"], {}), i["qid"]) == case
        )
        q = questions[qid]
        (out_dir / f"{case}.json").write_text(
            json.dumps(
                {
                    "case": case,
                    "image": str((Path(data_root) / "images" / f"{q['image']}.jpg").resolve()),
                    "gold": q["gold"],
                    "instructions": INSTRUCTIONS,
                    "output_format": (
                        "One JSON object per line, one line per output: "
                        '{"rating_id": "...", "destination": "yes|no", "route": "yes|no", '
                        '"obstacles": "yes|no", "reason": "one short sentence"}'
                    ),
                    "outputs": sorted(outputs, key=lambda o: o["rating_id"]),
                },
                indent=1,
            )
        )
    # index.json maps rating_id -> model for every batch ever exported, so a rating can be traced
    # back after the fact. Merge rather than overwrite: a later batch must not erase earlier work.
    index_path = out_dir / "index.json"
    merged: dict[str, dict] = {}
    if index_path.exists():
        try:
            merged = json.loads(index_path.read_text())
        except json.JSONDecodeError:
            merged = {}
    merged.update(index)
    index_path.write_text(json.dumps(merged, indent=1))
    return out_dir


def import_ratings(
    tasks_dir: Path, ratings_dir: Path, judged_path: Path, *, judge_model: str
) -> Path:
    index = json.loads((Path(tasks_dir) / "index.json").read_text())
    judged_path = Path(judged_path)
    judged_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if judged_path.exists():
        for line in judged_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add(rating_id(r["model"], r["qid"], int(r["repeat"])))

    seen_in_files: set[str] = set()
    with judged_path.open("a") as fh:
        for f in sorted(Path(ratings_dir).glob("*.jsonl")):
            for line in f.read_text().splitlines():
                if not line.strip():
                    continue
                v = json.loads(line)
                rid = v["rating_id"]
                if rid in done or rid in seen_in_files or rid not in index:
                    continue
                seen_in_files.add(rid)
                src = index[rid]
                fh.write(
                    json.dumps(
                        {
                            **src,
                            "judge_model": judge_model,
                            "ratings": {
                                c: str(v.get(c, "")).strip().lower() == "yes" for c in CRITERIA
                            },
                            "reasons": {"all": v.get("reason", "")},
                            "stop_reason": None,
                            "judge_error": None,
                            "judge_raw": json.dumps(v)[:600],
                        }
                    )
                    + "\n"
                )
    return judged_path
