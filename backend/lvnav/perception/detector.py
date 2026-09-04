"""Open-vocabulary obstacle detection with YOLO-World via ultralytics."""

from __future__ import annotations

from PIL import Image

from .cues import Detection
from .device import resolve_device


class ObstacleDetector:
    """Wraps YOLO-World with a BLV-relevant vocabulary set at construction time.

    The vocabulary lives in `configs/default.yaml` so it can be tuned per environment
    (indoor vs. outdoor) without touching code. Weights download on first use.
    """

    def __init__(
        self, model_path: str, vocabulary: list[str], conf: float = 0.3, device: str = "auto"
    ) -> None:
        from ultralytics import YOLOWorld

        self.device = resolve_device(device)
        self.model = YOLOWorld(model_path)
        self.model.set_classes(vocabulary)
        self.vocabulary = list(vocabulary)
        self.conf = conf

    def __call__(self, image: Image.Image) -> list[Detection]:
        results = self.model.predict(image, conf=self.conf, device=self.device, verbose=False)
        dets: list[Detection] = []
        for r in results:
            if r.boxes is None:
                continue
            for box, cls, score in zip(
                r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist(), strict=True
            ):
                dets.append(Detection(self.vocabulary[int(cls)], float(score), tuple(box)))
        return dets
