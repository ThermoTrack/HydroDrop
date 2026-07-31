"""Spill and overflow metadata extraction."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .basin import BasinInfo
from .dephier_cache import DepressionHierarchy


def extract_spill_info(
    hierarchy: DepressionHierarchy,
    wtd: np.ndarray,
    basin: BasinInfo,
) -> Dict[str, Any]:
    """Summarise overflow relative to requested pour volume."""
    dem = hierarchy.dem
    depth = np.maximum(wtd, 0.0)
    flooded = depth > 1e-6

    spill_x = None
    spill_y = None
    spill_row = None
    spill_col = None

    if np.any(flooded):
        edge = flooded & (
            np.pad(flooded[:-1, :], ((1, 0), (0, 0)), constant_values=False)
            | np.pad(flooded[1:, :], ((0, 1), (0, 0)), constant_values=False)
            | np.pad(flooded[:, :-1], ((0, 0), (1, 0)), constant_values=False)
            | np.pad(flooded[:, 1:], ((0, 0), (0, 1)), constant_values=False)
        )
        edge &= flooded
        indices = np.argwhere(edge)
        if len(indices):
            spill_row, spill_col = int(indices[0][0]), int(indices[0][1])
            spill_x, spill_y = dem.cell_to_world(spill_row, spill_col)

    return {
        "depression_id": basin.depression_id,
        "spill_x": spill_x,
        "spill_y": spill_y,
        "spill_row": spill_row,
        "spill_col": spill_col,
        "pour_x": basin.pour_x,
        "pour_y": basin.pour_y,
        "pour_elevation": basin.pour_elevation,
    }
