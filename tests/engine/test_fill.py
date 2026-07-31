"""Engine tests for HydroDrop."""

import numpy as np
import pytest

from engine.dem import array_to_dem
from engine.exceptions import InvalidPourPointError
from engine.richdem_utils import richdem_available
from tests.fixtures.make_synthetic_dem import make_bowl_dem, make_two_pit_dem


def test_cell_volume_calculation():
    dem = make_bowl_dem(size=10, cell_size=5.0)
    assert dem.cell_area_m2 == 25.0
    depth = 0.4
    assert dem.cell_area_m2 * depth == pytest.approx(10.0)


def test_invalid_pour_point_nodata():
    arr = np.full((10, 10), np.nan)
    dem = array_to_dem(arr, (0, 1, 0, 10, 0, -1), source_id="nan")
    with pytest.raises(InvalidPourPointError):
        dem.validate_pour_point(5.5, 5.5)


@pytest.mark.skipif(not richdem_available(), reason="richdem is not installed")
def test_single_pit_fill():
    from engine.dephier_cache import compute_depression_hierarchy
    from engine.fill import fill_volume
    from engine.statistics import compute_statistics

    dem = make_bowl_dem(size=40, cell_size=5.0, depth=6.0)
    hierarchy = compute_depression_hierarchy(dem)
    centre = dem.rows // 2
    volume = 500.0
    result = fill_volume(dem, centre, centre, volume, hierarchy=hierarchy)
    stats = compute_statistics(result, dem.cell_area_m2)

    assert stats.flooded_area_m2 > 0
    assert stats.max_depth_m > 0
    assert result.incremental_stored_m3 == pytest.approx(volume, rel=0.05)


@pytest.mark.skipif(not richdem_available(), reason="richdem is not installed")
def test_depression_hierarchy_cache_reload():
    from engine.dephier_cache import compute_depression_hierarchy

    dem = make_bowl_dem(size=30, cell_size=5.0, depth=4.0)
    first = compute_depression_hierarchy(dem)
    second = compute_depression_hierarchy(dem)

    assert np.array_equal(first.labels, second.labels)
    assert np.array_equal(first.flowdirs, second.flowdirs)


@pytest.mark.skipif(not richdem_available(), reason="richdem is not installed")
def test_multi_drop_session_replay():
    from engine.dephier_cache import compute_depression_hierarchy
    from engine.session import DropSession

    dem = make_two_pit_dem(size=50, cell_size=5.0)
    hierarchy = compute_depression_hierarchy(dem)
    session = DropSession(dem=dem, hierarchy=hierarchy)

    session.add_drop(5 * 12.5, 5 * 12.5, 200.0)
    first_stored = session.last_stats.stored_volume_m3

    session.add_drop(5 * 37.5, 5 * 37.5, 300.0)
    assert session.last_stats.stored_volume_m3 >= first_stored
    assert session.last_result.depth.max() > 0
