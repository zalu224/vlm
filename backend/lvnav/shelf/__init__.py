"""Last-shelf: open-vocabulary item retrieval and VLM verification on shelf images.

A fast, image-only replication of the search and correction phases of Ruan et al.
(arXiv 2601.12486). No sonification, no human trials: everything is measured on a
fixed set of shelf photographs.
"""

from .catalog import Catalog, CatalogItem, build_catalog
from .dataset import check, target_from_filename
from .matcher import SearchVariant, color_histogram, histogram_similarity, rank_candidates

__all__ = [
    "Catalog",
    "check",
    "target_from_filename",
    "CatalogItem",
    "build_catalog",
    "SearchVariant",
    "rank_candidates",
    "color_histogram",
    "histogram_similarity",
]
