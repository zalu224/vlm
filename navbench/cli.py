"""nav <stage>: ingest | questions | run | score | judge | report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import load_models_config
from .questions import load_questions, validate_questions


def _manifest_ids(data: Path) -> set[str]:
    m = data / "manifest.jsonl"
    if not m.exists():
        return set()
    return {json.loads(line)["image_id"] for line in m.read_text().splitlines() if line.strip()}


def cmd_ingest(a) -> int:
    from .data import ingest

    print(f"Wrote {ingest(a.src, a.out, max_side=a.max_side)}")
    return 0


def cmd_questions(a) -> int:
    qs = load_questions(a.questions)
    known = _manifest_ids(Path(a.data)) if Path(a.data, "manifest.jsonl").exists() else None
    problems = validate_questions(qs, known)
    by = {}
    for q in qs.values():
        by.setdefault((q["tier"], q["task"]), 0)
        by[(q["tier"], q["task"])] += 1
    for (tier, task), n in sorted(by.items()):
        print(f"  {tier:5s} {task:12s} {n}")
    if problems:
        print("\n".join(f"  ! {p}" for p in problems))
        return 1 if a.check else 0
    print(f"{len(qs)} questions, all valid")
    return 0


def cmd_run(a) -> int:
    from .backends.registry import build_backend
    from .runner import run_task

    cfg = load_models_config(a.config)
    entry = cfg["models"].get(a.model)
    if entry is None:
        print(f"unknown model {a.model!r}; known: {sorted(cfg['models'])}", file=sys.stderr)
        return 2
    backend = build_backend(entry, cfg.get("sampling", {}), cfg.get("server"))
    if hasattr(backend, "health") and not backend.health():
        print(
            f"no server at {backend.base_url}; start one with: make serve MODEL={entry['served']}",
            file=sys.stderr,
        )
        return 2
    qs = load_questions(a.questions)
    tasks = [a.task] if a.task != "all" else ["counting", "spatial", "commonsense", "navigation"]
    for task in tasks:
        reps = a.repeats if task != "navigation" or a.nav_repeats is None else a.nav_repeats
        out = run_task(
            qs,
            task,
            backend,
            Path(a.runs) / a.model,
            Path(a.data),
            repeats=reps,
            model_name=a.model,
            tier=a.tier,
            limit=a.limit,
        )
        print(f"{task}: {out}")
    return 0


def cmd_score(a) -> int:
    from .score import score_all

    res = score_all(Path(a.runs), load_questions(a.questions))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=1))
    for model, r in res.items():
        line = "  ".join(f"{t}={v['accuracy']:.0%}(n={v['n']})" for t, v in r["by_task"].items())
        print(f"{model:24s} {line}")
    print(f"Wrote {out / 'results.json'}")
    return 0


def cmd_judge(a) -> int:
    from .judge import judge_rows

    cfg = load_models_config(a.config)
    judge_cfg = cfg.get("judge", {})
    rows = []
    for p in sorted(Path(a.runs).glob("*/navigation.jsonl")):
        if a.model and p.parent.name != a.model:
            continue
        rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    if a.limit:
        rows = rows[: a.limit]
    out = judge_rows(
        rows,
        load_questions(a.questions),
        Path(a.data),
        Path(a.runs) / "judged.jsonl",
        model=a.judge_model or judge_cfg.get("served", "claude-fable-5-1"),
    )
    print(f"Judged {len(rows)} outputs -> {out}")
    return 0


def cmd_judge_export(a) -> int:
    """Write per-case rating tasks for a judge with no API key (a Claude session, or a person)."""
    from .judge_local import export_tasks

    out = export_tasks(Path(a.runs), load_questions(a.questions), Path(a.data), Path(a.tasks))
    cases = sorted(out.glob("nav_*.json"))
    n = sum(len(json.loads(c.read_text())["outputs"]) for c in cases)
    if not cases:
        print(f"nothing to rate: every navigation output is already in {a.runs}/judged.jsonl")
        return 0
    print(f"{n} unrated outputs across {len(cases)} cases -> {out}")
    print(f"Rate each case, write <case>.jsonl into {a.ratings}, then: nav judge-import")
    return 0


def cmd_judge_import(a) -> int:
    from .judge_local import import_ratings

    out = import_ratings(
        Path(a.tasks), Path(a.ratings), Path(a.runs) / "judged.jsonl", judge_model=a.judge_model
    )
    n = sum(1 for line in out.read_text().splitlines() if line.strip())
    print(f"{n} judged outputs -> {out}")
    return 0


def cmd_sheet(a) -> int:
    from .spotcheck import write_sheet

    sheet, key = write_sheet(
        Path(a.runs) / "judged.jsonl", load_questions(a.questions), a.out, n=a.n, seed=a.seed
    )
    print(f"Blinded sheet -> {sheet}\nKey (do not open while rating) -> {key}")
    return 0


def cmd_agreement(a) -> int:
    from .spotcheck import agreement

    res = agreement(a.sheet, a.key, Path(a.runs) / "judged.jsonl")
    print("| criterion | n | agreement | kappa |\n|---|---|---|---|")
    for c, r in res.items():
        print(f"| {c} | {r['n']} | {r['agreement']} | {r['kappa']} |")
    return 0


def cmd_report(a) -> int:
    from .report import write_report

    print(f"Wrote {write_report(Path(a.runs), load_questions(a.questions), Path(a.out))}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="nav", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--questions", type=Path, default=None)
        sp.add_argument("--data", type=Path, default=Path("data/pblv_nav"))
        sp.add_argument("--runs", type=Path, default=Path("runs"))
        sp.add_argument("--config", type=Path, default=None)

    s = sub.add_parser("ingest", help="EXIF-correct, downscale and index the dataset repo")
    s.add_argument("--src", type=Path, default=Path("data/pblv_nav_src"))
    s.add_argument("--out", type=Path, default=Path("data/pblv_nav"))
    s.add_argument("--max-side", type=int, default=1600)
    s.set_defaults(func=cmd_ingest)

    s = sub.add_parser("questions", help="validate and summarise questions.jsonl")
    s.add_argument("--check", action="store_true", help="exit 1 on any problem (CI)")
    common(s)
    s.set_defaults(func=cmd_questions)

    s = sub.add_parser("run", help="query one model on one task, N repeats per question")
    s.add_argument("--model", required=True, help="key in configs/models.yaml, or mock")
    s.add_argument(
        "--task", default="all", choices=["all", "counting", "spatial", "commonsense", "navigation"]
    )
    s.add_argument("--repeats", type=int, default=100)
    s.add_argument("--nav-repeats", type=int, default=None, help="navigation repeats (default: 10)")
    s.add_argument("--tier", choices=["paper", "ext"], default=None)
    s.add_argument("--limit", type=int, default=None, help="first N questions only")
    common(s)
    s.set_defaults(func=cmd_run, nav_repeats=10)

    s = sub.add_parser("score", help="accuracy / mean / variance tables -> reports/results.json")
    s.add_argument("--out", type=Path, default=Path("reports"))
    common(s)
    s.set_defaults(func=cmd_score)

    s = sub.add_parser("judge", help="LLM judge on navigation outputs (needs ANTHROPIC_API_KEY)")
    s.add_argument("--model", default=None, help="only this model's outputs")
    s.add_argument("--judge-model", default=None)
    s.add_argument("--limit", type=int, default=None)
    common(s)
    s.set_defaults(func=cmd_judge)

    s = sub.add_parser("judge-export", help="per-case rating tasks (no API key; rated in-session)")
    s.add_argument("--tasks", type=Path, default=Path("runs/judge_tasks"))
    s.add_argument("--ratings", type=Path, default=Path("runs/judge_ratings"))
    common(s)
    s.set_defaults(func=cmd_judge_export)

    s = sub.add_parser("judge-import", help="merge rating files into runs/judged.jsonl")
    s.add_argument("--tasks", type=Path, default=Path("runs/judge_tasks"))
    s.add_argument("--ratings", type=Path, default=Path("runs/judge_ratings"))
    s.add_argument("--judge-model", default="claude-opus-5-in-session")
    common(s)
    s.set_defaults(func=cmd_judge_import)

    s = sub.add_parser("sheet", help="blinded human spot-check sheet from judged.jsonl")
    s.add_argument("--n", type=int, default=40)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", type=Path, default=Path("reports/spotcheck.csv"))
    common(s)
    s.set_defaults(func=cmd_sheet)

    s = sub.add_parser("agreement", help="judge-human agreement and kappa from a rated sheet")
    s.add_argument("--sheet", type=Path, default=Path("reports/spotcheck.csv"))
    s.add_argument("--key", type=Path, default=Path("reports/spotcheck_key.csv"))
    common(s)
    s.set_defaults(func=cmd_agreement)

    s = sub.add_parser("report", help="docs/RESULTS.md from runs and judged outputs")
    s.add_argument("--out", type=Path, default=Path("docs/RESULTS.md"))
    common(s)
    s.set_defaults(func=cmd_report)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
