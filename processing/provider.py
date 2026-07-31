"""QGIS Processing provider for HydroDrop."""

import os

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .algorithm import DropWaterAlgorithm


class HydroDropProvider(QgsProcessingProvider):
    def id(self):
        return "hydrop"

    def name(self):
        return "HydroDrop"

    def longName(self):
        return "HydroDrop hydrology tools"

    def loadAlgorithms(self):
        self.addAlgorithm(DropWaterAlgorithm())

    def icon(self):
        path = os.path.join(os.path.dirname(__file__), "..", "icons", "waterdrop.svg")
        return QIcon(path)

    def svgIconPath(self):
        return os.path.join(os.path.dirname(__file__), "..", "icons", "waterdrop.svg")
