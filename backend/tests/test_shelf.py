import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from lvnav.config import load_config
from lvnav.perception import build_perception
from lvnav.shelf.annotate import build_template, load_ready_trials, write_trials
from lvnav.shelf.catalog import Catalog, build_catalog
from lvnav.shelf.correction import parse_correction, run_correction
from lvnav.shelf.detect import crop, detect_shelves
from lvnav.shelf.embed import MockEmbedder
from lvnav.shelf.evaluate import correction_metrics, search_metrics, write_report
from lvnav.shelf.matcher import (
    Candidate,
    SearchVariant,
    color_histogram,
    hardest_distractor,
    histogram_similarity,
    rank_candidates,
)
from lvnav.shelf.search import load_jsonl, run_search
from lvnav.vlm import build_backend


# ------------------------------------------------------------------ matcher maths
def test_color_histogram_normalised_and_discriminative():
    red = Image.new("RGB", (32, 32), (220, 30, 30))
    blue = Image.new("RGB", (32, 32), (30, 30, 220))
    hr, hb = color_histogram(red), color_histogram(blue)
    assert pytest.approx(hr.sum(), abs=1e-5) == 1.0
    assert histogram_similarity(hr, hr) == pytest.approx(1.0, abs=1e-5)
    assert histogram_similarity(hr, hb) < 0.2


def test_ranking_arms_use_different_signals():
    cands = [
        Candidate(0, (0, 0, 1, 1), det_conf=0.9, embed_sim=0.10, color_sim=0.1),
        Candidate(1, (0, 0, 1, 1), det_conf=0.4, embed_sim=0.80, color_sim=0.9),
    ]
    assert rank_candidates(cands, SearchVariant.DETECTION)[0].box_id == 0
    assert rank_candidates(cands, SearchVariant.EMBED)[0].box_id == 1
    assert rank_candidates(cands, SearchVariant.EMBED_COLOR)[0].box_id == 1


def test_color_can_flip_a_close_embedding_call():
    cands = [
        Candidate(0, (0, 0, 1, 1), det_conf=0.5, embed_sim=0.62, color_sim=0.05),
        Candidate(1, (0, 0, 1, 1), det_conf=0.5, embed_sim=0.55, color_sim=0.95),
    ]
    assert rank_candidates(cands, SearchVariant.EMBED)[0].box_id == 0
    assert rank_candidates(cands, SearchVariant.EMBED_COLOR)[0].box_id == 1


def test_hardest_distractor_skips_ground_truth():
    ranked = [Candidate(2, (0, 0, 1, 1), 0.9, 0.9, 0.9), Candidate(5, (0, 0, 1, 1), 0.8, 0.8, 0.8)]
    assert hardest_distractor(ranked, gt_box_id=2).box_id == 5
    assert hardest_distractor([], gt_box_id=2) is None


def test_crop_pads_without_leaving_the_frame():
    im = Image.new("RGB", (100, 100))
    c = crop(im, (0, 0, 10, 10), pad=0.5)
    assert c.size[0] <= 100 and c.size[1] <= 100 and c.size[0] >= 10


# ------------------------------------------------------------------------ parsing
@pytest.mark.parametrize(
    "raw,expected",
    [
        ('{"verdict": "yes", "identified_as": "", "spoken": "That is it."}', "yes"),
        ('```json\n{"verdict":"NO","identified_as":"paprika","spoken":"x"}\n```', "no"),
        ('Sure! {"verdict": "unsure", "identified_as": "", "spoken": "Too blurry."}', "unsure"),
        ('{"verdict": "maybe", "identified_as": "", "spoken": ""}', None),
    ],
)
def test_parse_correction(raw, expected):
    assert parse_correction(raw)["verdict"] == expected


def test_parse_correction_rejects_non_json():
    with pytest.raises(ValueError):
        parse_correction("I think that is the cinnamon.")


# ------------------------------------------------------------------------- catalog
@pytest.fixture
def shelf_data(tmp_path):
    cat_dir = tmp_path / "catalog"
    for name, col in {"cinnamon": (150, 80, 40), "oats": (220, 200, 150)}.items():
        d = cat_dir / name
        d.mkdir(parents=True)
        for r in range(2):
            Image.new("RGB", (64, 64), col).save(d / f"ref{r}.jpg")
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    rng = np.random.default_rng(0)
    for i in range(4):
        Image.fromarray(rng.integers(0, 255, (120, 200, 3), dtype=np.uint8)).save(
            img_dir / f"shelf{i:03d}.jpg"
        )
    return cat_dir, img_dir


def test_catalog_roundtrip(shelf_data, tmp_path):
    cat_dir, _ = shelf_data
    cat = build_catalog(cat_dir, MockEmbedder())
    assert len(cat) == 2
    assert cat["cinnamon"].name == "cinnamon"
    assert cat["cinnamon"].embedding is not None
    path = tmp_path / "catalog.json"
    cat.save(path)
    again = Catalog.load(path)
    assert np.allclose(again["oats"].histogram, cat["oats"].histogram)
    with pytest.raises(KeyError):
        again["nutmeg"]


def test_catalog_name_overrides(shelf_data):
    cat_dir, _ = shelf_data
    (cat_dir / "names.json").write_text(json.dumps({"oats": "rolled oats, big blue tub"}))
    cat = build_catalog(cat_dir, MockEmbedder())
    assert cat["oats"].name.startswith("rolled oats")


# ------------------------------------------------------------------- full pipeline
def test_shelf_pipeline_end_to_end(shelf_data, tmp_path):
    cat_dir, img_dir = shelf_data
    cfg = load_config()
    cfg.vlm.backend = "mock"
    results = tmp_path / "results"
    embedder = MockEmbedder()

    cat = build_catalog(cat_dir, embedder)
    cat.save(results / "catalog.json")

    detector = build_perception(cfg.perception, use_mock=True).detector
    det_path = detect_shelves(img_dir, detector, results / "detections.jsonl")
    assert len(load_jsonl(det_path)) == 4

    trials_path = build_template(det_path, None, results / "trials.jsonl", "cinnamon")
    rows = load_jsonl(trials_path)
    assert all(r["gt_box"] is None for r in rows)
    with pytest.raises(ValueError):
        load_ready_trials(trials_path)

    for i, r in enumerate(rows):
        r["gt_box"] = -1 if r["n_boxes"] == 0 else (i % r["n_boxes"])
    write_trials(rows, trials_path)
    ready = load_ready_trials(trials_path)

    search_path = run_search(ready, det_path, cat, embedder, results / "search.jsonl")
    srows = load_jsonl(search_path)
    assert len(srows) == len(ready)
    assert set(srows[0]["variants"]) == {"det", "embed", "embed+color"}

    backend = build_backend("mock", cfg.vlm)
    corr_path = run_correction(
        search_path, det_path, cat, backend, results / "correction_mock.jsonl", "mock"
    )
    crows = load_jsonl(corr_path)
    assert crows, "no correction cases generated"
    assert all(r["parse_error"] is None for r in crows)
    assert {r["case"] for r in crows} <= {"positive", "negative"}

    sm = search_metrics(srows)
    assert sm["n_trials"] == len(ready)
    cm = correction_metrics(crows)
    assert cm["mock"]["n"] == len(crows)

    report = write_report(search_path, [corr_path], results / "report.md")
    text = report.read_text()
    assert "Phase 1 — search" in text and "False confirm" in text


def test_detector_miss_excluded_from_ranking_accuracy():
    rows = [
        {"detector_recall": False, "n_candidates": 3, "latency_s": 0.1, "variants": {}},
        {
            "detector_recall": True,
            "n_candidates": 3,
            "latency_s": 0.1,
            "variants": {v.value: {"top1": True, "top3": True} for v in SearchVariant.all()},
        },
    ]
    m = search_metrics(rows)
    assert m["detector_recall_pct"] == "50.0%"
    assert m["variants"]["embed"]["top1_pct"] == "100.0%"
    assert m["variants"]["embed"]["end_to_end_top1_pct"] == "50.0%"


def test_false_confirm_is_counted_separately():
    rows = [
        {
            "model": "m",
            "case": "negative",
            "verdict": "yes",
            "correct": False,
            "false_confirm": True,
            "identified_as": "",
            "latency_s": 1.0,
            "parse_error": None,
        },
        {
            "model": "m",
            "case": "positive",
            "verdict": "yes",
            "correct": True,
            "false_confirm": False,
            "identified_as": "",
            "latency_s": 1.0,
            "parse_error": None,
        },
    ]
    m = correction_metrics(rows)["m"]
    assert m["false_confirm_n"] == 1 and m["false_confirm_pct"] == "100.0%"
    assert m["accuracy_pct"] == "50.0%"


# ------------------------------------------------------------------------ dataset
def test_target_parsed_from_filename():
    from lvnav.shelf.dataset import target_from_filename

    assert target_from_filename(Path("cinnamon__d1_bright_03.jpg")) == "cinnamon"
    assert target_from_filename(Path("black_beans__d2_05.png")) == "black_beans"
    assert target_from_filename(Path("IMG_4821.jpg")) is None


def _make_dataset(tmp_path, n_items=2, n_images=4, named=True, refs=2):
    cat = tmp_path / "catalog"
    imgs = tmp_path / "images"
    imgs.mkdir(parents=True)
    names = [f"item_{i}" for i in range(n_items)]
    for j, name in enumerate(names):
        d = cat / name
        d.mkdir(parents=True)
        for r in range(refs):
            Image.new("RGB", (700, 700), (40 * j, 90, 120)).save(d / f"ref{r}.jpg")
    for i in range(n_images):
        target = names[i % len(names)]
        stem = f"{target}__d1_{i:02d}" if named else f"IMG_{i:04d}"
        Image.new("RGB", (900, 700), (200, 195, 185)).save(imgs / f"{stem}.jpg")
    return cat, imgs


def test_check_passes_on_a_well_formed_dataset(tmp_path):
    from lvnav.shelf.dataset import check

    cat, imgs = _make_dataset(tmp_path, n_items=3, n_images=12)
    res = check(cat, imgs)
    assert res.ok, res.errors
    assert res.stats["catalogue items"] == 3
    assert res.stats["images with a valid target"] == 12
    assert "Dataset check" in res.render()


def test_check_flags_unconventional_filenames(tmp_path):
    from lvnav.shelf.dataset import check

    cat, imgs = _make_dataset(tmp_path, named=False)
    res = check(cat, imgs)
    assert not res.ok
    assert any("item_id" in e for e in res.errors)


def test_check_flags_missing_references_and_unknown_targets(tmp_path):
    from lvnav.shelf.dataset import check

    cat, imgs = _make_dataset(tmp_path)
    (cat / "empty_item").mkdir()
    Image.new("RGB", (900, 700)).save(imgs / "not_in_catalog__d1_00.jpg")
    res = check(cat, imgs)
    assert not res.ok
    assert any("no reference photos" in e for e in res.errors)
    assert any("no catalogue folder" in e for e in res.errors)


def test_check_warns_on_thin_coverage_and_small_images(tmp_path):
    from lvnav.shelf.dataset import check

    cat, imgs = _make_dataset(tmp_path, n_items=2, n_images=2, refs=1)
    Image.new("RGB", (320, 240)).save(imgs / "item_0__tiny.jpg")
    res = check(cat, imgs)
    assert res.ok  # warnings only; a small pilot still runs
    joined = " ".join(res.warnings)
    assert "reference photo" in joined
    assert "short side" in joined


def test_template_prefers_filename_target(tmp_path):
    from lvnav.shelf.annotate import build_template

    det = tmp_path / "detections.jsonl"
    det.write_text(
        json.dumps({"image": "/x/cinnamon__d1_00.jpg", "size": [9, 9], "boxes": []})
        + "\n"
        + json.dumps({"image": "/x/IMG_0001.jpg", "size": [9, 9], "boxes": []})
        + "\n"
    )
    out = build_template(det, None, tmp_path / "trials.jsonl", None, from_filename=True)
    rows = load_jsonl(out)
    assert rows[0]["target"] == "cinnamon"
    assert rows[1]["target"] is None  # falls through to the annotator


def test_template_default_target_fills_the_gap(tmp_path):
    from lvnav.shelf.annotate import build_template

    det = tmp_path / "detections.jsonl"
    det.write_text(json.dumps({"image": "/x/IMG_1.jpg", "size": [9, 9], "boxes": []}) + "\n")
    out = build_template(det, None, tmp_path / "t.jsonl", "oats", from_filename=True)
    assert load_jsonl(out)[0]["target"] == "oats"
