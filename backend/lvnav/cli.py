"""Command-line interface: `lvnav <subcommand>`.

Subcommands
-----------
extract-frames   Sample frames from a video at a fixed rate.
shelf            Last-Shelf study: item retrieval and VLM verification on shelf images.
run              Generate instructions for every frame under one condition.
judge            Score a run with the LLM judge.
report           Build a paired comparison report from two judged runs.
manual-sheet     Export a CSV for human spot-check scoring.
"""

from __future__ import annotations

import argparse
import csv
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
    )
    print(f"Judged: {out}")
    return 0


def cmd_report(args) -> int:
    from .eval import write_report

    out = write_report(args.a, args.b, args.out)
    print(f"Report: {out}")
    print(out.read_text())
    return 0


def cmd_manual_sheet(args) -> int:
    """Write a CSV with blank score columns for human spot-checking (Day 5)."""
    from .eval.rubric import DIMENSIONS
    from .pipeline import read_jsonl

    rows = read_jsonl(Path(args.run) / "records.jsonl")
    if args.every > 1:
        rows = rows[:: args.every]
    out = Path(args.out or Path(args.run) / "manual_scores.csv")
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame_id", "frame_path", "cues", "instruction", *DIMENSIONS, "notes"])
        for r in rows:
            w.writerow(
                [r["frame_id"], r["frame_path"], r.get("cues") or "", r["instruction"]]
                + [""] * (len(DIMENSIONS) + 1)
            )
    print(f"Manual scoring sheet with {len(rows)} rows: {out}")
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
    _add_common(p)
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("report", help="paired comparison of two judged runs")
    p.add_argument("--a", type=Path, required=True, help="baseline run dir")
    p.add_argument("--b", type=Path, required=True, help="treatment run dir")
    p.add_argument("--out", type=Path, default=None)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("manual-sheet", help="CSV for human spot-check scoring")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--every", type=int, default=1, help="take every Nth frame")
    p.add_argument("--out", type=Path, default=None)
    p.set_defaults(func=cmd_manual_sheet)

    from .shelf.cli import register as register_shelf

    register_shelf(sub)

    args = parser.parse_args(argv)
    if getattr(args, "shelf_cmd", None):
        return args.func(args, _resolve(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
