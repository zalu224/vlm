"""Frame extraction from video and iteration over extracted frame directories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


@dataclass(frozen=True)
class Frame:
    frame_id: str
    path: Path


def extract_frames(
    video: Path, out_dir: Path, fps: float = 1.0, max_side: int | None = None
) -> int:
    """Sample `fps` frames per second from `video` into `out_dir` as zero-padded JPEGs.

    Returns the number of frames written. Uses OpenCV so it works on any platform
    without ffmpeg on PATH.
    """
    video = Path(video)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(int(round(src_fps / fps)), 1)

    written = 0
    index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if index % step == 0:
            if max_side:
                h, w = frame.shape[:2]
                scale = max_side / max(h, w)
                if scale < 1.0:
                    frame = cv2.resize(frame, (int(w * scale), int(h * scale)), cv2.INTER_AREA)
            cv2.imwrite(str(out_dir / f"{written:06d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
            written += 1
        index += 1
    cap.release()
    return written


def list_frames(frames_dir: Path, limit: int | None = None) -> list[Frame]:
    """Return frames in a directory sorted by filename."""
    frames_dir = Path(frames_dir)
    if not frames_dir.is_dir():
        raise FileNotFoundError(f"Frames directory not found: {frames_dir}")
    paths = sorted(p for p in frames_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if limit:
        paths = paths[:limit]
    return [Frame(frame_id=p.stem, path=p) for p in paths]
