"""Perception: depth, detection and cue fusion.

Heavy model classes are imported lazily inside `build_perception` so that the
package can be imported (and the mock pipeline run) without torch installed.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from .cues import Detection, ObstacleCue, SpatialCues, fuse


@dataclass
class PerceptionStack:
    depth: object | None
    detector: object | None

    def __call__(self, image: Image.Image) -> SpatialCues:
        depth_map = self.depth(image) if self.depth is not None else None
        dets = self.detector(image) if self.detector is not None else []
        return fuse(depth_map, dets, image.size)


def build_perception(cfg, use_mock: bool = False) -> PerceptionStack:
    """Construct the perception stack from a PerceptionConfig.

    With `use_mock=True` returns deterministic synthetic cues so the full pipeline
    can be exercised in CI or before models are downloaded.
    """
    if use_mock:
        from .mock import MockDepth, MockDetector

        return PerceptionStack(MockDepth(), MockDetector())

    from .depth import DepthEstimator
    from .detector import ObstacleDetector

    depth = DepthEstimator(cfg.depth_model, cfg.device)
    detector = ObstacleDetector(cfg.detector_model, cfg.vocabulary, cfg.detector_conf, cfg.device)
    return PerceptionStack(depth, detector)


__all__ = [
    "Detection",
    "ObstacleCue",
    "SpatialCues",
    "PerceptionStack",
    "build_perception",
    "fuse",
]
