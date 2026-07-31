"""Compute engineering statistics from fill results."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import numpy as np

from .fill import FillResult


@dataclass
class SimulationStatistics:
    requested_volume_m3: float
    stored_volume_m3: float
    overflow_volume_m3: float
    flooded_area_m2: float
    max_depth_m: float
    average_depth_m: float
    surface_elevation_m: float
    pour_x: float
    pour_y: float
    pour_elevation_m: float
    spill_x: Optional[float]
    spill_y: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_csv_rows(self) -> list:
        return [
            ["Metric", "Value", "Unit"],
            ["Requested Volume", f"{self.requested_volume_m3:.2f}", "m3"],
            ["Stored Volume", f"{self.stored_volume_m3:.2f}", "m3"],
            ["Overflow Volume", f"{self.overflow_volume_m3:.2f}", "m3"],
            ["Flooded Area", f"{self.flooded_area_m2:.2f}", "m2"],
            ["Maximum Depth", f"{self.max_depth_m:.3f}", "m"],
            ["Average Depth", f"{self.average_depth_m:.3f}", "m"],
            ["Surface Elevation", f"{self.surface_elevation_m:.3f}", "m"],
            ["Pour X", f"{self.pour_x:.3f}", "m"],
            ["Pour Y", f"{self.pour_y:.3f}", "m"],
            ["Pour Elevation", f"{self.pour_elevation_m:.3f}", "m"],
            ["Spill X", "" if self.spill_x is None else f"{self.spill_x:.3f}", "m"],
            ["Spill Y", "" if self.spill_y is None else f"{self.spill_y:.3f}", "m"],
        ]


def compute_statistics(result: FillResult, cell_area_m2: float) -> SimulationStatistics:
    depth = result.depth
    flooded = depth > 1e-6
    flooded_depths = depth[flooded]

    if flooded_depths.size:
        max_depth = float(np.max(flooded_depths))
        avg_depth = float(np.mean(flooded_depths))
        surface_elev = float(np.max(result.surface[flooded]))
        area = float(np.count_nonzero(flooded) * cell_area_m2)
    else:
        max_depth = 0.0
        avg_depth = 0.0
        surface_elev = result.basin.pour_elevation
        area = 0.0

    stored = result.stored_volume_m3
    requested = result.requested_volume_m3
    incremental = result.incremental_stored_m3
    overflow = max(0.0, requested - incremental)

    spill = result.spill_info
    return SimulationStatistics(
        requested_volume_m3=requested,
        stored_volume_m3=stored,
        overflow_volume_m3=overflow,
        flooded_area_m2=area,
        max_depth_m=max_depth,
        average_depth_m=avg_depth,
        surface_elevation_m=surface_elev,
        pour_x=spill["pour_x"],
        pour_y=spill["pour_y"],
        pour_elevation_m=spill["pour_elevation"],
        spill_x=spill.get("spill_x"),
        spill_y=spill.get("spill_y"),
    )
