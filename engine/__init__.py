"""HydroDrop hydrology engine."""

from .animation import AnimationFrame, generate_animation_frames
from .basin import BasinInfo, identify_basin
from .dem import DemData, array_to_dem, load_dem_from_layer
from .dephier_cache import DepressionHierarchy, compute_depression_hierarchy
from .fill import FillResult, fill_volume
from .session import DropSession, WaterDrop
from .statistics import SimulationStatistics, compute_statistics

__all__ = [
    "AnimationFrame",
    "BasinInfo",
    "DemData",
    "DepressionHierarchy",
    "DropSession",
    "FillResult",
    "SimulationStatistics",
    "WaterDrop",
    "array_to_dem",
    "compute_depression_hierarchy",
    "compute_statistics",
    "fill_volume",
    "generate_animation_frames",
    "identify_basin",
    "load_dem_from_layer",
]
