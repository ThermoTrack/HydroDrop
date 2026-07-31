"""Water depth raster styling."""

from typing import Optional

import numpy as np

from qgis.core import (
    QgsColorRampShader,
    QgsRasterLayer,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
)
from qgis.PyQt.QtGui import QColor

if hasattr(QgsColorRampShader, "ColorRampType"):
    COLOR_RAMP_INTERPOLATED = QgsColorRampShader.ColorRampType.Interpolated
else:
    COLOR_RAMP_INTERPOLATED = QgsColorRampShader.Interpolated


def apply_depth_style(
    layer: QgsRasterLayer,
    max_depth: Optional[float] = None,
    *,
    vivid: bool = False,
) -> None:
    """Apply semi-transparent blue depth ramp scaled to the data."""
    if max_depth is None:
        provider = layer.dataProvider()
        stats = provider.bandStatistics(1)
        max_depth = float(stats.maximumValue) if stats.maximumValue > 0 else 1.0

    if not np.isfinite(max_depth) or max_depth <= 0:
        max_depth = 1.0

    max_depth = max(max_depth, 0.001)
    opacity = 0.92 if vivid else 0.85

    shader = QgsRasterShader()
    color_ramp = QgsColorRampShader()
    color_ramp.setColorRampType(COLOR_RAMP_INTERPOLATED)

    items = [
        QgsColorRampShader.ColorRampItem(0.0, QColor(0, 0, 0, 0), "0 m"),
        QgsColorRampShader.ColorRampItem(
            max_depth * 0.02,
            QColor(100, 180, 255, 200 if vivid else 160),
            "shallow",
        ),
        QgsColorRampShader.ColorRampItem(
            max_depth * 0.35,
            QColor(30, 120, 255, 220 if vivid else 190),
            "mid",
        ),
        QgsColorRampShader.ColorRampItem(
            max_depth,
            QColor(0, 0, 160, 240 if vivid else 220),
            f"{max_depth:.2f} m",
        ),
    ]
    color_ramp.setColorRampItemList(items)
    shader.setRasterShaderFunction(color_ramp)

    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    layer.setRenderer(renderer)
    layer.setOpacity(opacity)
    layer.triggerRepaint()
