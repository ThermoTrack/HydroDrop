"""Multi-drop session management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

import numpy as np

from .dephier_cache import DepressionHierarchy
from .dem import DemData
from .fill import FillResult, fill_volume
from .statistics import SimulationStatistics, compute_statistics


@dataclass
class WaterDrop:
    drop_id: str
    pour_x: float
    pour_y: float
    pour_row: int
    pour_col: int
    volume_m3: float


@dataclass
class DropSession:
    dem: DemData
    hierarchy: Optional[DepressionHierarchy] = None
    drops: List[WaterDrop] = field(default_factory=list)
    cumulative_wtd: Optional[np.ndarray] = None
    last_result: Optional[FillResult] = None
    last_stats: Optional[SimulationStatistics] = None

    def reset(self) -> None:
        self.drops.clear()
        self.cumulative_wtd = None
        self.last_result = None
        self.last_stats = None

    def add_drop(self, pour_x: float, pour_y: float, volume_m3: float) -> FillResult:
        row, col = self.dem.validate_pour_point(pour_x, pour_y)
        drop = WaterDrop(
            drop_id=str(uuid4())[:8],
            pour_x=pour_x,
            pour_y=pour_y,
            pour_row=row,
            pour_col=col,
            volume_m3=volume_m3,
        )
        self.drops.append(drop)
        return self.replay(progress_callback=None)

    def replay(
        self,
        progress_callback=None,
        drop_volumes: Optional[List[float]] = None,
    ) -> FillResult:
        if not self.drops:
            raise ValueError("No drops in session.")

        wtd = np.zeros_like(self.dem.elevation, dtype=np.float64)
        result = None

        volumes = drop_volumes or [d.volume_m3 for d in self.drops]
        for drop, volume in zip(self.drops, volumes):
            result = fill_volume(
                self.dem,
                drop.pour_row,
                drop.pour_col,
                volume,
                hierarchy=self.hierarchy,
                initial_wtd=wtd,
                progress_callback=progress_callback,
            )
            wtd = result.wtd.copy()

        self.cumulative_wtd = wtd
        self.last_result = result
        self.last_stats = compute_statistics(result, self.dem.cell_area_m2)
        return result

    def update_active_drop_volume(self, drop_index: int, volume_m3: float) -> FillResult:
        if drop_index < 0 or drop_index >= len(self.drops):
            raise IndexError("Invalid drop index.")
        self.drops[drop_index].volume_m3 = volume_m3
        return self.replay()
