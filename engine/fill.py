"""Volume fill engine using RichDEM Fill-Spill-Merge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .basin import BasinInfo, identify_basin
from .dephier_cache import DepressionHierarchy, compute_depression_hierarchy
from .dem import DemData
from .richdem_utils import get_richdem
from .spill import extract_spill_info


@dataclass
class FillResult:
    depth: np.ndarray
    surface: np.ndarray
    inundation_mask: np.ndarray
    wtd: np.ndarray
    stored_volume_m3: float
    incremental_stored_m3: float
    requested_volume_m3: float
    basin: BasinInfo
    spill_info: dict


def _stored_volume(wtd: np.ndarray, cell_area_m2: float) -> float:
    return float(np.nansum(np.maximum(wtd, 0.0)) * cell_area_m2)


def _wtd_to_rdarray(wtd: np.ndarray):
    rd = get_richdem()
    return rd.rdarray(wtd.copy(), no_data=-9999.0)


def _run_fsm(hierarchy: DepressionHierarchy, wtd: np.ndarray) -> np.ndarray:
    rd = get_richdem()
    from .dephier_cache import _numpy_to_rdarray

    wtd_rd = _wtd_to_rdarray(wtd)
    labels_rd = _numpy_to_rdarray(hierarchy.labels)
    flowdirs_rd = _numpy_to_rdarray(hierarchy.flowdirs)
    rd.fill_spill_merge(
        hierarchy.dem_rd,
        labels_rd,
        flowdirs_rd,
        hierarchy.dephier,
        wtd_rd,
    )
    return np.asarray(wtd_rd, dtype=np.float64)


def fill_volume(
    dem: DemData,
    pour_row: int,
    pour_col: int,
    volume_m3: float,
    hierarchy: Optional[DepressionHierarchy] = None,
    initial_wtd: Optional[np.ndarray] = None,
    volume_tolerance_m3: float = 0.5,
    max_iterations: int = 40,
    progress_callback=None,
) -> FillResult:
    """
    Pour ``volume_m3`` at (pour_row, pour_col) using binary search + FSM.
    """
    if volume_m3 <= 0:
        raise ValueError("Volume must be positive.")

    if hierarchy is None:
        hierarchy = compute_depression_hierarchy(dem, progress_callback)

    basin = identify_basin(hierarchy, pour_row, pour_col)
    base_wtd = (
        np.zeros_like(dem.elevation, dtype=np.float64)
        if initial_wtd is None
        else initial_wtd.copy()
    )

    existing = _stored_volume(base_wtd, dem.cell_area_m2)
    target_total = existing + volume_m3

    lo = 0.0
    hi = max(1.0, volume_m3 / dem.cell_area_m2 * 4.0)
    best_wtd = base_wtd.copy()
    best_stored = existing

    for _ in range(max_iterations):
        mid = (lo + hi) / 2.0
        trial = base_wtd.copy()
        trial[pour_row, pour_col] += mid
        trial = _run_fsm(hierarchy, trial)
        stored = _stored_volume(trial, dem.cell_area_m2)

        if stored < target_total:
            lo = mid
        else:
            hi = mid

        if abs(stored - target_total) < volume_tolerance_m3:
            best_wtd = trial
            best_stored = stored
            break

        if abs(stored - target_total) < abs(best_stored - target_total):
            best_wtd = trial
            best_stored = stored

    depth = np.maximum(best_wtd, 0.0)
    surface = dem.elevation + depth
    inundation = depth > 1e-6
    spill_info = extract_spill_info(hierarchy, best_wtd, basin)
    incremental = best_stored - existing

    return FillResult(
        depth=depth,
        surface=surface,
        inundation_mask=inundation,
        wtd=best_wtd,
        stored_volume_m3=best_stored,
        incremental_stored_m3=incremental,
        requested_volume_m3=volume_m3,
        basin=basin,
        spill_info=spill_info,
    )
