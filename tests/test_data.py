import json

from PIL import Image

from navbench.data import ingest


def test_ingest_transposes_exif_downscales_and_writes_manifest(images_dir, tmp_path):
    out = tmp_path / "data" / "pblv_nav"
    manifest = ingest(images_dir, out, max_side=200)
    rows = [json.loads(line) for line in manifest.read_text().splitlines()]
    assert len(rows) == 5
    r = {row["image_id"]: row for row in rows}
    assert set(r) == {
        "campus/classroom_chairs_1",
        "campus/classroom_chairs_2",
        "campus/indoor_left_closer",
        "chairs/IMG_Cl",
        "chairs/IMG_Cl_Coat",
    }
    row = r["campus/classroom_chairs_1"]
    im = Image.open(out / row["path"])
    # source was 400x300 with orientation 6 -> displayed 300x400 -> longest side capped at 200
    assert im.size == (150, 200) and row["width"] == 150 and row["height"] == 200
    assert row["folder"] == "campus" and row["source"].endswith("classroom_chairs_1.JPG")
    # second run is idempotent
    assert ingest(images_dir, out, max_side=200).read_text() == manifest.read_text()
