"""Spatial cues: fuse a relative-depth map and object detections into short text.

This module is deliberately model-free so it can be unit-tested and so the fusion
logic (zones, proximity buckets, wording) is auditable independently of the
perception networks that feed it.

Conventions
-----------
* Depth maps are 2-D float arrays normalised to [0, 1] where **1 = closest**.
  Depth Anything outputs relative inverse depth, so this matches its native
  orientation after min-max normalisation.
* The image is split into three vertical zones (left / centre / right) and only
  the lower `roi_fraction` of the image is used for free-space estimation, which
  is where the walkable surface and near obstacles appear in egocentric video.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

ZONES = ("left", "centre", "right")
PROXIMITY_LABELS = ("far", "mid", "near")


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: tuple[float, float, float, float]  # x1, y1, x2, y2 in pixels

    def zone(self, image_width: int) -> str:
        cx = (self.box[0] + self.box[2]) / 2.0
        idx = min(int(cx / image_width * 3), 2)
        return ZONES[idx]


@dataclass(frozen=True)
class ObstacleCue:
    label: str
    zone: str
    proximity: str  # far | mid | near
    confidence: float


@dataclass
class SpatialCues:
    """Text-ready summary of the walkable scene in front of the user."""

    free_space: dict[str, str] = field(default_factory=dict)  # zone -> clear|partly blocked|blocked
    obstacles: list[ObstacleCue] = field(default_factory=list)

    def to_text(self) -> str:
        fs = ", ".join(f"{z}={self.free_space.get(z, 'unknown')}" for z in ZONES)
        if self.obstacles:
            obs = "; ".join(f"{o.label} ({o.zone}, {o.proximity})" for o in self.obstacles)
        else:
            obs = "none detected"
        return f"Free space: {fs}. Obstacles: {obs}."

    def to_dict(self) -> dict:
        return {
            "free_space": dict(self.free_space),
            "obstacles": [o.__dict__ for o in self.obstacles],
        }


def proximity_from_depth(value: float, near_thresh: float = 0.65, mid_thresh: float = 0.40) -> str:
    """Bucket a normalised closeness value (1 = closest) into far / mid / near."""
    if value >= near_thresh:
        return "near"
    if value >= mid_thresh:
        return "mid"
    return "far"


def free_space_from_depth(
    depth: np.ndarray,
    roi_fraction: float = 0.5,
    blocked_thresh: float = 0.65,
    partial_thresh: float = 0.45,
) -> dict[str, str]:
    """Classify each vertical zone of the lower ROI as clear / partly blocked / blocked.

    Uses the 90th percentile of closeness in each zone so that a single thin pole
    still registers, while remaining robust to noisy pixels.
    """
    if depth.ndim != 2:
        raise ValueError("depth must be a 2-D array")
    h, w = depth.shape
    roi = depth[int(h * (1.0 - roi_fraction)) :, :]
    edges = np.linspace(0, w, 4).astype(int)
    out: dict[str, str] = {}
    for zone, (a, b) in zip(ZONES, zip(edges[:-1], edges[1:], strict=True), strict=True):
        col = roi[:, a:b]
        if col.size == 0:
            out[zone] = "unknown"
            continue
        p90 = float(np.percentile(col, 90))
        if p90 >= blocked_thresh:
            out[zone] = "blocked"
        elif p90 >= partial_thresh:
            out[zone] = "partly blocked"
        else:
            out[zone] = "clear"
    return out


def fuse(
    depth: np.ndarray | None,
    detections: list[Detection],
    image_size: tuple[int, int],
    max_obstacles: int = 4,
) -> SpatialCues:
    """Combine a depth map and detections into ranked obstacle cues.

    Obstacles are ranked by proximity (near first) then confidence. If no depth
    map is available, proximity is estimated from the box's bottom edge: boxes
    whose bottom edge is lower in the frame are closer to the camera.
    """
    width, height = image_size
    cues = SpatialCues()
    if depth is not None:
        cues.free_space = free_space_from_depth(depth)
    else:
        cues.free_space = {z: "unknown" for z in ZONES}

    ranked: list[tuple[int, float, ObstacleCue]] = []
    for det in detections:
        x1, y1, x2, y2 = det.box
        if depth is not None:
            dh, dw = depth.shape
            sx, sy = dw / width, dh / height
            patch = depth[
                max(int(y1 * sy), 0) : min(int(y2 * sy), dh),
                max(int(x1 * sx), 0) : min(int(x2 * sx), dw),
            ]
            closeness = float(np.median(patch)) if patch.size else 0.0
        else:
            closeness = float(y2 / height)
        prox = proximity_from_depth(closeness)
        cue = ObstacleCue(det.label, det.zone(width), prox, round(det.confidence, 3))
        ranked.append((PROXIMITY_LABELS.index(prox), det.confidence, cue))

    ranked.sort(key=lambda t: (-t[0], -t[1]))
    cues.obstacles = [c for _, _, c in ranked[:max_obstacles]]
    return cues
