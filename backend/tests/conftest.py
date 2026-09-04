import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def frames_dir(tmp_path):
    """Six synthetic frames with distinct content so mock perception varies."""
    d = tmp_path / "frames"
    d.mkdir()
    rng = np.random.default_rng(0)
    for i in range(6):
        arr = rng.integers(0, 255, size=(120, 160, 3), dtype=np.uint8)
        Image.fromarray(arr).save(d / f"{i:06d}.jpg")
    return d
