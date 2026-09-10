"""Reference catalogue: one entry per household item the system can be asked for.

Directory layout expected under `--catalog`:

    catalog/
      cinnamon/            <- directory name is the item id
        ref01.jpg          <- one to three reference photos, item filling the frame
        ref02.jpg
      smoked_paprika/
        ref01.jpg

Item ids use underscores; the prompt-facing name is derived by replacing them with
spaces, or overridden per item in `catalog/names.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from .matcher import color_histogram

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class CatalogItem:
    item_id: str
    name: str
    ref_paths: list[Path]
    embedding: np.ndarray | None = None  # mean of reference image embeddings
    text_embedding: np.ndarray | None = None
    histogram: np.ndarray | None = None  # mean of reference histograms

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "ref_paths": [str(p) for p in self.ref_paths],
            "embedding": None if self.embedding is None else self.embedding.tolist(),
            "text_embedding": (
                None if self.text_embedding is None else self.text_embedding.tolist()
            ),
            "histogram": None if self.histogram is None else self.histogram.tolist(),
        }

    @staticmethod
    def from_dict(d: dict) -> CatalogItem:
        def arr(key):
            return None if d.get(key) is None else np.asarray(d[key], dtype=np.float32)

        return CatalogItem(
            item_id=d["item_id"],
            name=d["name"],
            ref_paths=[Path(p) for p in d.get("ref_paths", [])],
            embedding=arr("embedding"),
            text_embedding=arr("text_embedding"),
            histogram=arr("histogram"),
        )


@dataclass
class Catalog:
    items: dict[str, CatalogItem] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, item_id: str) -> CatalogItem:
        if item_id not in self.items:
            raise KeyError(f"Unknown catalogue item {item_id!r}. Known: {sorted(self.items)[:10]}")
        return self.items[item_id]

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([i.to_dict() for i in self.items.values()], indent=1))

    @staticmethod
    def load(path: Path) -> Catalog:
        rows = json.loads(Path(path).read_text())
        return Catalog({r["item_id"]: CatalogItem.from_dict(r) for r in rows})


def _display_name(item_id: str, overrides: dict[str, str]) -> str:
    return overrides.get(item_id, item_id.replace("_", " "))


def build_catalog(catalog_dir: Path, embedder, max_refs: int = 3) -> Catalog:
    """Embed every catalogue item's reference photos and average them.

    Averaging two or three reference views is what makes matching robust to the
    angle the item happens to sit at on the shelf; a single frontal reference
    overfits to that one pose.
    """
    catalog_dir = Path(catalog_dir)
    if not catalog_dir.is_dir():
        raise FileNotFoundError(f"Catalogue directory not found: {catalog_dir}")

    names_file = catalog_dir / "names.json"
    overrides = json.loads(names_file.read_text()) if names_file.exists() else {}

    items: dict[str, CatalogItem] = {}
    for sub in sorted(p for p in catalog_dir.iterdir() if p.is_dir()):
        refs = sorted(p for p in sub.iterdir() if p.suffix.lower() in IMAGE_EXTS)[:max_refs]
        if not refs:
            continue
        images = [Image.open(p).convert("RGB") for p in refs]
        emb = embedder.embed_images(images).mean(axis=0)
        hist = np.mean([color_histogram(im) for im in images], axis=0)
        name = _display_name(sub.name, overrides)
        text_emb = embedder.embed_texts([f"a photo of {name}"])[0]
        for im in images:
            im.close()
        items[sub.name] = CatalogItem(sub.name, name, refs, emb, text_emb, hist)

    if not items:
        raise ValueError(f"No catalogue items with reference images under {catalog_dir}")
    return Catalog(items)
