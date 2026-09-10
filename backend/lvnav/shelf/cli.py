"""`lvnav shelf <subcommand>` — the Last-Shelf study pipeline."""

from __future__ import annotations

import json
from pathlib import Path


def _embedder(args, cfg):
    from .embed import build_embedder

    return build_embedder(args.clip_model, cfg.perception.device, use_mock=args.backend == "mock")


def cmd_index(args, cfg) -> int:
    from .catalog import build_catalog

    cat = build_catalog(args.catalog, _embedder(args, cfg), max_refs=args.max_refs)
    out = Path(args.out or Path(args.results) / "catalog.json")
    cat.save(out)
    print(f"Indexed {len(cat)} items -> {out}")
    return 0


def cmd_detect(args, cfg) -> int:
    from ..perception import build_perception
    from ..perception.detector import ObstacleDetector
    from .detect import CONTAINER_VOCABULARY, detect_shelves

    out = Path(args.out or Path(args.results) / "detections.jsonl")
    if args.backend == "mock":
        detector = build_perception(cfg.perception, use_mock=True).detector
    else:
        detector = ObstacleDetector(
            cfg.perception.detector_model,
            CONTAINER_VOCABULARY,
            args.conf,
            cfg.perception.device,
        )
    detect_shelves(args.images, detector, out, max_boxes=args.max_boxes)
    print(f"Detections -> {out}")
    return 0


def cmd_trials(args, cfg) -> int:
    from .annotate import build_template

    out = Path(args.out or Path(args.results) / "trials.jsonl")
    build_template(
        Path(args.results) / "detections.jsonl" if not args.detections else args.detections,
        [args.targets] if args.targets else None,
        out,
        args.default_target,
    )
    print(f"Trial template -> {out}\nFill in gt_box with `lvnav shelf annotate` or the viewer.")
    return 0


def cmd_annotate(args, cfg) -> int:
    from .annotate import annotate_cli
    from .catalog import Catalog

    results = Path(args.results)
    cat = Catalog.load(args.catalog_json or results / "catalog.json")
    annotate_cli(
        args.trials or results / "trials.jsonl",
        args.detections or results / "detections.jsonl",
        list(cat.items),
    )
    return 0


def cmd_search(args, cfg) -> int:
    from .annotate import load_ready_trials
    from .catalog import Catalog
    from .search import run_search

    results = Path(args.results)
    cat = Catalog.load(args.catalog_json or results / "catalog.json")
    trials = load_ready_trials(args.trials or results / "trials.jsonl")
    out = Path(args.out or results / "search.jsonl")
    run_search(
        trials,
        args.detections or results / "detections.jsonl",
        cat,
        _embedder(args, cfg),
        out,
        text_weight=args.text_weight,
    )
    print(f"Search results ({len(trials)} trials) -> {out}")
    return 0


def cmd_correct(args, cfg) -> int:
    from ..vlm import build_backend
    from .catalog import Catalog
    from .correction import run_correction

    results = Path(args.results)
    if args.model:
        cfg.vlm.model = args.model
    label = args.label or cfg.vlm.model.split("/")[-1]
    backend = build_backend(args.backend, cfg.vlm)
    cat = Catalog.load(args.catalog_json or results / "catalog.json")
    out = Path(args.out or results / f"correction_{label}.jsonl")
    run_correction(
        args.search or results / "search.jsonl",
        args.detections or results / "detections.jsonl",
        cat,
        backend,
        out,
        model_label=label,
        limit=args.limit,
    )
    print(f"Correction results -> {out}")
    return 0


def cmd_report(args, cfg) -> int:
    from .evaluate import write_report

    results = Path(args.results)
    corrections = args.correction or sorted(results.glob("correction_*.jsonl"))
    out = write_report(args.search or results / "search.jsonl", corrections, results / "report.md")
    print(f"Report -> {out}\n")
    print(out.read_text())
    return 0


def cmd_summary(args, cfg) -> int:
    """Machine-readable metrics for the write-up."""
    from .evaluate import correction_metrics, search_metrics
    from .search import load_jsonl

    results = Path(args.results)
    srows = load_jsonl(results / "search.jsonl")
    crows: list[dict] = []
    for p in sorted(results.glob("correction_*.jsonl")):
        crows.extend(load_jsonl(p))
    payload = {"search": search_metrics(srows), "correction": correction_metrics(crows)}
    out = results / "summary.json"
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0


def register(subparsers) -> None:
    """Attach `lvnav shelf ...` to the top-level parser."""
    p = subparsers.add_parser("shelf", help="Last-Shelf study: item retrieval on shelf images")
    sub = p.add_subparsers(dest="shelf_cmd", required=True)

    def common(sp):
        sp.add_argument("--results", type=Path, default=Path("results/shelf"))
        sp.add_argument("--backend", choices=["http", "mock"], default="http")
        sp.add_argument("--clip-model", default="openai/clip-vit-base-patch32")
        sp.add_argument("--config", type=Path, default=None)
        sp.add_argument("--detections", type=Path, default=None)
        sp.add_argument("--catalog-json", type=Path, default=None)

    s = sub.add_parser("index", help="embed catalogue reference photos")
    s.add_argument("--catalog", type=Path, required=True)
    s.add_argument("--max-refs", type=int, default=3)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("detect", help="run open-vocabulary detection over shelf images")
    s.add_argument("--images", type=Path, required=True)
    s.add_argument("--conf", type=float, default=0.15)
    s.add_argument("--max-boxes", type=int, default=30)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_detect)

    s = sub.add_parser("trials", help="build the annotation template")
    s.add_argument("--targets", type=Path, default=None, help="JSON {image_stem: item_id}")
    s.add_argument("--default-target", default=None)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_trials)

    s = sub.add_parser("annotate", help="fill in ground-truth boxes in the terminal")
    s.add_argument("--trials", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_annotate)

    s = sub.add_parser("search", help="rank candidates under every ablation arm")
    s.add_argument("--trials", type=Path, default=None)
    s.add_argument("--text-weight", type=float, default=0.25)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("correct", help="VLM verification of positives and hard negatives")
    s.add_argument("--search", type=Path, default=None)
    s.add_argument("--model", default=None, help="override vlm.model for this run")
    s.add_argument("--label", default=None, help="name for this model in the report")
    s.add_argument("--limit", type=int, default=None)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_correct)

    s = sub.add_parser("report", help="markdown report over search + correction")
    s.add_argument("--search", type=Path, default=None)
    s.add_argument("--correction", type=Path, nargs="*", default=None)
    common(s)
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("summary", help="write summary.json")
    common(s)
    s.set_defaults(func=cmd_summary)
