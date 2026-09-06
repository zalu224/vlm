"""Command-line interface: `lvnav <subcommand>`.

Subcommands
-----------
extract-frames   Sample frames from a video at a fixed rate.
run              Generate instructions for every frame under one condition.
judge            Score a run with the LLM judge.
report           Build a paired comparison report from two judged runs.
manual-sheet     Export a blinded, shuffled CSV for human spot-check scoring.
agreement        Judge–human agreement from a scored sheet.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Config, load_config


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--config", type=Path, default=None, help="YAML config (default: configs/default.yaml)"
    )
    p.add_argument("--backend", choices=["http", "mock"], default=None, help="override vlm.backend")
    p.add_argument("--model", default=None, help="override vlm.model")
    p.add_argument("--base-url", default=None, help="override vlm.base_url")


def _resolve(args) -> Config:
    cfg = load_config(args.config)
    if getattr(args, "backend", None):
        cfg.vlm.backend = args.backend
        cfg.judge.backend = args.backend
    if getattr(args, "model", None):
        cfg.vlm.model = args.model
    if getattr(args, "base_url", None):
        cfg.vlm.base_url = args.base_url
    return cfg


def cmd_extract(args) -> int:
    from .data.frames import extract_frames

    n = extract_frames(args.video, args.out, fps=args.fps, max_side=args.max_side)
    print(f"Wrote {n} frames to {args.out}")
    return 0


def cmd_run(args) -> int:
    from .perception import build_perception
    from .pipeline import run_pipeline
    from .vlm import build_backend

    cfg = _resolve(args)
    if args.no_perception:
        cfg.perception.enabled = False
    backend = build_backend(cfg.vlm.backend, cfg.vlm)

    perception = None
    if args.mode == "context":
        if not cfg.perception.enabled:
            print("error: context mode requires perception; drop --no-perception", file=sys.stderr)
            return 2
        perception = build_perception(cfg.perception, use_mock=(cfg.vlm.backend == "mock"))

    run_dir = run_pipeline(
        args.frames,
        args.mode,
        backend,
        cfg,
        perception=perception,
        run_name=args.run_name,
        limit=args.limit,
    )
    print(f"Run complete: {run_dir / 'records.jsonl'}")
    return 0


def cmd_judge(args) -> int:
    from .eval import judge_run
    from .vlm import build_backend

    cfg = _resolve(args)
    backend = build_backend(cfg.judge.backend, cfg.vlm, model_override=cfg.judge.model)
    out = judge_run(
        args.run,
        backend,
        cues_from=args.cues_from,
        max_tokens=cfg.judge.max_tokens,
        temperature=cfg.judge.temperature,
        version=args.judge_version or cfg.judge.version,
        every=args.every,
        out_name=args.out_name,
    )
    print(f"Judged: {out}")
    return 0


def cmd_report(args) -> int:
    from .eval import write_report

    try:
        out = write_report(args.a, args.b, args.out, judged_name=args.judged_name)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Report: {out}")
    print(out.read_text())
    return 0


def cmd_manual_sheet(args) -> int:
    """Write a blinded, shuffled CSV (plus a key file) for human spot-check scoring."""
    from .eval.spotcheck import write_blinded_sheet

    out = Path(args.out or Path(args.runs[0]).parent / "manual_sheet.csv")
    sheet, key = write_blinded_sheet(args.runs, out, every=args.every, seed=args.seed)
    n = sum(1 for _ in key.open()) - 1  # key has one line per row; the sheet has multi-line cells
    print(f"Blinded sheet with {n} rows: {sheet}\nKey (do not open while scoring): {key}")
    return 0


def cmd_agreement(args) -> int:
    """Judge–human agreement (Spearman rho per dimension) from a scored sheet."""
    import json

    from .eval.spotcheck import agreement

    res = agreement(args.sheet, args.key, args.results_root, judged_name=args.judged_name)
    print(f"Agreement against `{args.judged_name}`:")
    print("| dimension | n | Spearman rho | mean human | mean judge | exact match |")
    print("|---|---|---|---|---|---|")
    for d, r in res.items():
        print(
            f"| {d.replace('_', ' ')} | {r['n']} | {r['rho']} | {r['mean_human']} | "
            f"{r['mean_judge']} | {r['exact']} |"
        )
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"Saved: {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lvnav", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("extract-frames", help="sample frames from a video")
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--fps", type=float, default=1.0)
    p.add_argument("--max-side", type=int, default=1024)
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("run", help="generate instructions for a frame directory")
    p.add_argument("--frames", type=Path, required=True)
    p.add_argument("--mode", choices=["naive", "context"], required=True)
    p.add_argument("--run-name", default=None)
    p.add_argument("--limit", type=int, default=None, help="only process the first N frames")
    p.add_argument("--no-perception", action="store_true")
    _add_common(p)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("judge", help="score a run with the LLM judge")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument(
        "--cues-from",
        type=Path,
        default=None,
        help="borrow perception cues from another run (e.g. judge naive with context cues)",
    )
    p.add_argument("--judge-version", default=None, help="judge prompt version (default: config)")
    p.add_argument("--every", type=int, default=1, help="score every Nth frame only")
    p.add_argument("--out-name", default=None, help="output filename inside the run dir")
    _add_common(p)
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("report", help="paired comparison of two judged runs")
    p.add_argument("--a", type=Path, required=True, help="baseline run dir")
    p.add_argument("--b", type=Path, required=True, help="treatment run dir")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument(
        "--judged-name", default="judged.jsonl", help="judged file to read in both run dirs"
    )
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("manual-sheet", help="blinded CSV for human spot-check scoring")
    p.add_argument("--runs", type=Path, nargs="+", required=True, help="run dirs to interleave")
    p.add_argument("--every", type=int, default=8, help="take every Nth frame of each run")
    p.add_argument("--seed", type=int, default=0, help="shuffle seed")
    p.add_argument("--out", type=Path, default=None, help="default: results/manual_sheet.csv")
    p.set_defaults(func=cmd_manual_sheet)

    p = sub.add_parser("agreement", help="judge-human agreement from a scored sheet")
    p.add_argument("--sheet", type=Path, required=True, help="scored manual_sheet.csv")
    p.add_argument("--key", type=Path, required=True, help="matching _key.csv")
    p.add_argument("--results-root", type=Path, default=Path("results"))
    p.add_argument("--judged-name", default="judged.jsonl")
    p.add_argument("--out", type=Path, default=None, help="save the table as JSON")
    p.set_defaults(func=cmd_agreement)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
