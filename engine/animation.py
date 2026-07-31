"""Animation frame generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from .dem import DemData
from .dephier_cache import DepressionHierarchy
from .fill import FillResult, fill_volume


@dataclass
class AnimationFrame:
    index: int
    volume_m3: float
    depth: np.ndarray
    surface: np.ndarray
    inundation_mask: np.ndarray


def generate_animation_frames(
    dem: DemData,
    pour_row: int,
    pour_col: int,
    total_volume_m3: float,
    hierarchy: DepressionHierarchy,
    frame_count: int = 20,
    initial_wtd: Optional[np.ndarray] = None,
    progress_callback=None,
) -> List[AnimationFrame]:
    frames: List[AnimationFrame] = []
    if frame_count < 1:
        frame_count = 1

    for i in range(1, frame_count + 1):
        fraction = i / frame_count
        volume = total_volume_m3 * fraction
        if progress_callback:
            pct = int(fraction * 100)
            progress_callback(pct, f"Generating animation frame {i}/{frame_count}…")

        result = fill_volume(
            dem,
            pour_row,
            pour_col,
            volume,
            hierarchy=hierarchy,
            initial_wtd=initial_wtd,
            progress_callback=None,
        )
        frames.append(
            AnimationFrame(
                index=i - 1,
                volume_m3=volume,
                depth=result.depth.copy(),
                surface=result.surface.copy(),
                inundation_mask=result.inundation_mask.copy(),
            )
        )
    return frames
