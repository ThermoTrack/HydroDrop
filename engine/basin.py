"""Basin identification from pour point."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from .dephier_cache import DepressionHierarchy


@dataclass
class BasinInfo:
    depression_id: int
    pour_row: int
    pour_col: int
    pour_elevation: float
    pour_x: float
    pour_y: float


def identify_basin(hierarchy: DepressionHierarchy, row: int, col: int) -> BasinInfo:
    labels = hierarchy.labels
    dem = hierarchy.dem
    depression_id = int(labels[row, col])
    pour_x, pour_y = dem.cell_to_world(row, col)
    return BasinInfo(
        depression_id=depression_id,
        pour_row=row,
        pour_col=col,
        pour_elevation=float(dem.elevation[row, col]),
        pour_x=pour_x,
        pour_y=pour_y,
    )
