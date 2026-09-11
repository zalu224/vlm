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
            imgsz=args.imgsz,
        )
    detect_shelves(args.images, detector, out, max_boxes=args.max_boxes)
    print(f"Detections -> {out}")
    return 0


def cmd_trials(args, cfg) -> int:
    from .annotate import build_template

    dets = Path(args.results) / "detections.jsonl" if not args.detections else args.detections
    out = Path(args.out or Path(args.results) / "trials.jsonl")
    build_template(
        dets,
        [args.targets] if args.targets else None,
        out,
        args.default_target,
        from_filename=args.from_filename,
    )
    if args.gt_boxes:
        import json

        from .annotate import MISSED, fill_gt_from_boxes, write_trials
        from .search import load_jsonl

        gt = json.loads(Path(args.gt_boxes).read_text())
        trials = fill_gt_from_boxes(
            load_jsonl(out), dets, gt, min_iou=args.min_iou, match=args.match
        )
        write_trials(trials, out)
        done = [t for t in trials if t.get("gt_box") is not None]
        missed = sum(1 for t in done if t["gt_box"] == MISSED)
        print(
            f"Trial template -> {out}\nAuto-annotated {len(done)}/{len(trials)} from ground-truth "
            f"boxes (IoU >= {args.min_iou}); detector missed the target in {missed}."
        )
        return 0
    print(f"Trial template -> {out}\nFill in gt_box with `lvnav shelf annotate` or the viewer.")
    return 0


def cmd_import(args, cfg) -> int:
    """Convert a public dataset into data/<name>/{catalog,images,gt_boxes.json}."""
    from . import importers

    if args.source == "grocery":
        stats = importers.import_grocery_store(
            args.src, args.out, composites_per_target=args.per_target, seed=args.seed
        )
    else:
        stats = importers.import_grozi(args.src, args.out, subsets=args.subsets, seed=args.seed)
    print(f"Imported {args.source} -> {args.out}: {stats}")
    return 0


def cmd_check(args, cfg) -> int:
    from .dataset import check

    res = check(args.catalog, args.images)
    print(res.render())
    return 0 if res.ok else 1


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
        mode=args.mode,
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

    s = sub.add_parser("check", help="validate the dataset before running anything")
    s.add_argument("--catalog", type=Path, default=Path("data/shelf/catalog"))
    s.add_argument("--images", type=Path, default=Path("data/shelf/images"))
    common(s)
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("index", help="embed catalogue reference photos")
    s.add_argument("--catalog", type=Path, required=True)
    s.add_argument("--max-refs", type=int, default=3)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("detect", help="run open-vocabulary detection over shelf images")
    s.add_argument("--images", type=Path, required=True)
    s.add_argument("--conf", type=float, default=0.15)
    s.add_argument(
        "--imgsz",
        type=int,
        default=1280,
        help="detector inference size; 640 (ultralytics default) halves recall on dense shelves",
    )
    s.add_argument("--max-boxes", type=int, default=30)
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_detect)

    s = sub.add_parser("trials", help="build the annotation template")
    s.add_argument(
        "--from-filename",
        action="store_true",
        help="read the target from the filename prefix, e.g. cinnamon__d1_03.jpg",
    )
    s.add_argument("--targets", type=Path, default=None, help="JSON {image_stem: item_id}")
    s.add_argument("--default-target", default=None)
    s.add_argument(
        "--gt-boxes",
        type=Path,
        default=None,
        help="JSON {image: [x1,y1,x2,y2]} from an importer; fills gt_box by IoU, no human needed",
    )
    s.add_argument("--min-iou", type=float, default=0.5)
    s.add_argument(
        "--match",
        choices=["iou", "contain"],
        default="iou",
        help="contain: for composite shelves whose ground truth is the whole tile",
    )
    s.add_argument("--out", type=Path, default=None)
    common(s)
    s.set_defaults(func=cmd_trials)

    s = sub.add_parser(
        "import", help="import a public dataset (grocery | grozi) into the study layout"
    )
    s.add_argument("source", choices=["grocery", "grozi"])
    s.add_argument("--src", type=Path, required=True, help="downloaded dataset root")
    s.add_argument("--out", type=Path, required=True, help="e.g. data/grocery")
    s.add_argument("--per-target", type=int, default=4, help="grocery: composites per item")
    s.add_argument("--subsets", default="val", help="grozi: val (84 shelves) | train | all")
    s.add_argument("--seed", type=int, default=0)
    common(s)
    s.set_defaults(func=cmd_import)

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
    s.add_argument(
        "--mode",
        choices=["name", "reference"],
        default="name",
        help="name: prompt names the item (needs names); reference: compare with the catalogue photo",
    )
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
