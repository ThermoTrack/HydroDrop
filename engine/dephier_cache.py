"""Depression hierarchy caching backed by RichDEM."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from .dem import DemData
from .richdem_utils import get_richdem, get_depression_hierarchy_labels


@dataclass
class DepressionHierarchy:
    """Cached RichDEM depression hierarchy for a DEM."""

    dem: DemData
    dem_rd: Any
    labels: np.ndarray
    flowdirs: np.ndarray
    dephier: Any
    cache_path: Optional[str] = None


CACHE_VERSION = 2


def _cache_dir() -> str:
    base = os.path.join(os.path.expanduser("~"), ".hydrodrop", "cache")
    os.makedirs(base, exist_ok=True)
    return base


def _cache_key(dem: DemData) -> str:
    digest = hashlib.sha256(dem.source_id.encode("utf-8")).hexdigest()[:16]
    return f"{digest}_{dem.rows}x{dem.cols}"


def _cache_path(dem: DemData) -> str:
    return os.path.join(_cache_dir(), f"{_cache_key(dem)}.npz")


def _numpy_to_rdarray(elevation: np.ndarray, no_data: float = -9999.0):
    rd = get_richdem()
    arr = rd.rdarray(np.asarray(elevation).copy(), no_data=no_data)
    return arr


def _build_hierarchy(dem_rd, labels):
    rd = get_richdem()
    dephier, flowdirs = rd.get_depression_hierarchy(dem_rd, labels)
    return dephier, np.asarray(flowdirs), np.asarray(labels)


def _rebuild_dephier(dem_rd):
    """Rebuild the depression tree using fresh NO_DEP/OCEAN seed labels."""
    rd = get_richdem()
    initial_labels = get_depression_hierarchy_labels(dem_rd.shape)
    dephier, _flowdirs = rd.get_depression_hierarchy(dem_rd, initial_labels)
    return dephier


def _load_cached_hierarchy(dem: DemData, path: str, progress_callback=None) -> Optional[DepressionHierarchy]:
    """Load cached flowdirs/labels and rebuild the non-serializable depression tree."""
    data = np.load(path, allow_pickle=True)
    if int(data.get("cache_version", 0)) < CACHE_VERSION:
        return None

    flowdirs = np.asarray(data["flowdirs"])
    labels = np.asarray(data["labels"])
    if flowdirs.shape != dem.elevation.shape or labels.shape != dem.elevation.shape:
        return None

    if progress_callback:
        progress_callback(50, "Loading cached depression hierarchy…")

    dem_rd = _numpy_to_rdarray(dem.elevation)

    if progress_callback:
        progress_callback(70, "Rebuilding depression tree…")

    dephier = _rebuild_dephier(dem_rd)

    if progress_callback:
        progress_callback(100, "Depression hierarchy ready.")

    return DepressionHierarchy(
        dem=dem,
        dem_rd=dem_rd,
        labels=labels,
        flowdirs=flowdirs,
        dephier=dephier,
        cache_path=path,
    )


def compute_depression_hierarchy(dem: DemData, progress_callback=None) -> DepressionHierarchy:
    """Compute or load cached depression hierarchy."""
    rd = get_richdem()
    path = _cache_path(dem)

    if os.path.exists(path):
        cached = _load_cached_hierarchy(dem, path, progress_callback)
        if cached is not None:
            return cached
        try:
            os.remove(path)
        except OSError:
            pass

    if progress_callback:
        progress_callback(10, "Computing depression hierarchy (first run may take a while)…")

    dem_rd = _numpy_to_rdarray(dem.elevation)
    labels = get_depression_hierarchy_labels(dem_rd.shape)
    if progress_callback:
        progress_callback(40, "Building depression tree…")
    dephier, flowdirs, labels_arr = _build_hierarchy(dem_rd, labels)

    np.savez_compressed(
        path,
        cache_version=CACHE_VERSION,
        labels=labels_arr,
        flowdirs=flowdirs,
    )

    if progress_callback:
        progress_callback(100, "Depression hierarchy cached.")

    return DepressionHierarchy(
        dem=dem,
        dem_rd=dem_rd,
        labels=labels_arr,
        flowdirs=flowdirs,
        dephier=dephier,
        cache_path=path,
    )
