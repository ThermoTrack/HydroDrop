"""Map tool for selecting pour points on a DEM."""

from qgis.core import Qgis, QgsMapLayer, QgsPointXY, QgsProject, QgsRaster, QgsWkbTypes
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QPixmap, QColor
from qgis.PyQt.QtWidgets import QMessageBox

import os

from ..engine.dem import resolve_pour_point_from_layer
from ..engine.exceptions import InvalidDemError, InvalidPourPointError
from .qt_compat import CROSS_CURSOR, KEEP_ASPECT_RATIO, LEFT_BUTTON, SMOOTH_TRANSFORMATION


class DropWaterMapTool(QgsMapToolEmitPoint):
    """Click the map to choose where water is poured."""

    pointClicked = pyqtSignal(
        float, float, float, float, float, float, float
    )  # eng_x, eng_y, elev, map_x, map_y, warp_lon, warp_lat

    def __init__(self, canvas, iface):
        super().__init__(canvas)
        self.iface = iface
        self.canvas = canvas
        self._dem_layer_id = None
        self._marker = QgsRubberBand(canvas, QgsWkbTypes.PointGeometry)
        self._marker.setColor(QColor("blue"))
        self._marker.setIconSize(12)
        self._marker.setWidth(3)
        self._set_droplet_cursor()

    def set_dem_layer(self, layer) -> None:
        if layer is not None and layer.isValid():
            self._dem_layer_id = layer.id()

    def _dem_layer_for_click(self):
        if self._dem_layer_id:
            layer = QgsProject.instance().mapLayer(self._dem_layer_id)
            if layer is not None and layer.isValid():
                return layer

        layer = self.iface.activeLayer()
        if (
            layer is not None
            and layer.isValid()
            and layer.type() == QgsMapLayer.RasterLayer
            and not layer.name().startswith("HydroDrop")
        ):
            return layer
        return None

    def _set_droplet_cursor(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "waterdrop.svg")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(24, 24, KEEP_ASPECT_RATIO, SMOOTH_TRANSFORMATION)
            self.setCursor(QCursor(pixmap, 12, 12))
        else:
            self.setCursor(CROSS_CURSOR)

    def canvasReleaseEvent(self, event):
        if event.button() != LEFT_BUTTON:
            return

        point = self.toMapCoordinates(event.pos())
        layer = self._dem_layer_for_click()
        if layer is None:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "HydroDrop",
                "Could not find the DEM layer.\n"
                "Select your DEM in the Layers panel, then click again.",
            )
            return

        canvas_crs = self.canvas.mapSettings().destinationCrs()
        try:
            eng_x, eng_y, elevation, reproject_msg, warp_lon, warp_lat = (
                resolve_pour_point_from_layer(layer, point, canvas_crs)
            )
        except (InvalidDemError, InvalidPourPointError) as exc:
            QMessageBox.warning(self.iface.mainWindow(), "HydroDrop", str(exc))
            return

        if reproject_msg:
            self.iface.messageBar().pushMessage(
                "HydroDrop",
                reproject_msg,
                level=Qgis.MessageLevel.Info,
                duration=8,
            )

        self._marker.reset(QgsWkbTypes.PointGeometry)
        self._marker.addPoint(QgsPointXY(point.x(), point.y()))
        self.pointClicked.emit(
            eng_x, eng_y, elevation, point.x(), point.y(), warp_lon, warp_lat
        )

    def deactivate(self):
        self._marker.reset(QgsWkbTypes.PointGeometry)
        super().deactivate()
