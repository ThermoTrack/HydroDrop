"""Generate synthetic bowl DEM for tests."""

import numpy as np

from engine.dem import array_to_dem


def make_bowl_dem(size=50, cell_size=5.0, depth=5.0):
    """Inverted cone bowl centred in the raster."""
    rows = cols = size
    centre = (size - 1) / 2.0
    elevation = np.full((rows, cols), 100.0, dtype=np.float64)
    for r in range(rows):
        for c in range(cols):
            dist = np.hypot(r - centre, c - centre)
            elevation[r, c] = 100.0 + min(depth, dist * 0.15)

    gt = (0.0, cell_size, 0.0, size * cell_size, 0.0, -cell_size)
    return array_to_dem(elevation, gt, nodata=-9999.0, source_id="synthetic_bowl")


def make_two_pit_dem(size=60, cell_size=5.0):
    """Two separated depressions with a saddle."""
    rows = cols = size
    elevation = np.full((rows, cols), 120.0, dtype=np.float64)
    for r in range(rows):
        for c in range(cols):
            d1 = np.hypot(r - 15, c - 15)
            d2 = np.hypot(r - 45, c - 45)
            pit = min(d1, d2)
            elevation[r, c] = 120.0 + min(8.0, pit * 0.2)
    gt = (0.0, cell_size, 0.0, size * cell_size, 0.0, -cell_size)
    return array_to_dem(elevation, gt, nodata=-9999.0, source_id="synthetic_two_pit")
