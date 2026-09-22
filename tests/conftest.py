import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def images_dir(tmp_path):
    """A fake clone of the dataset repo: data/<folder>/<name>.JPG, EXIF orientation 6."""
    root = tmp_path / "src" / "data"
    rng = np.random.default_rng(0)
    names = {
        "campus": ["classroom_chairs_1", "classroom_chairs_2", "indoor_left_closer"],
        "chairs": ["IMG_Cl", "IMG_Cl_Coat"],
    }
    for folder, stems in names.items():
        (root / folder).mkdir(parents=True)
        for s in stems:
            im = Image.fromarray(rng.integers(0, 255, (300, 400, 3), dtype=np.uint8))
            exif = im.getexif()
            exif[274] = 6  # rotate 90 CW on display, like the phone photos
            im.save(root / folder / f"{s}.JPG", exif=exif)
    return tmp_path / "src"
