import numpy as np

from lvnav.perception.cues import Detection, free_space_from_depth, fuse, proximity_from_depth


def test_proximity_buckets():
    assert proximity_from_depth(0.9) == "near"
    assert proximity_from_depth(0.5) == "mid"
    assert proximity_from_depth(0.1) == "far"


def test_free_space_zones():
    depth = np.full((100, 90), 0.1, dtype=np.float32)
    depth[50:, 60:] = 0.9  # obstacle in lower-right
    fs = free_space_from_depth(depth)
    assert fs == {"left": "clear", "centre": "clear", "right": "blocked"}


def test_fuse_ranks_near_first_and_limits():
    depth = np.full((100, 90), 0.2, dtype=np.float32)
    depth[:, 0:30] = 0.9  # left column is close
    dets = [
        Detection("pole", 0.5, (60, 10, 80, 90)),  # right, far
        Detection("person", 0.9, (0, 10, 25, 90)),  # left, near
        Detection("bench", 0.6, (35, 10, 55, 90)),  # centre, far
        Detection("dog", 0.4, (5, 10, 20, 90)),  # left, near
        Detection("car", 0.3, (62, 10, 85, 90)),  # right, far
    ]
    cues = fuse(depth, dets, image_size=(90, 100), max_obstacles=3)
    assert [o.label for o in cues.obstacles] == ["person", "dog", "bench"]
    assert cues.obstacles[0].zone == "left" and cues.obstacles[0].proximity == "near"
    text = cues.to_text()
    assert text.startswith("Free space: left=blocked")
    assert "person (left, near)" in text


def test_fuse_without_depth_uses_box_bottom():
    dets = [Detection("person", 0.8, (10, 10, 30, 95))]
    cues = fuse(None, dets, image_size=(100, 100))
    assert cues.free_space["centre"] == "unknown"
    assert cues.obstacles[0].proximity == "near"
