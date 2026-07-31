"""Batch drop-water processing algorithm."""

import os

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterNumber,
    QgsProcessingParameterPoint,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
)
from qgis.PyQt.QtCore import QCoreApplication


class DropWaterAlgorithm(QgsProcessingAlgorithm):
    INPUT_DEM = "INPUT_DEM"
    POUR_POINT = "POUR_POINT"
    VOLUME = "VOLUME"
    OUTPUT_DEPTH = "OUTPUT_DEPTH"
    OUTPUT_SURFACE = "OUTPUT_SURFACE"
    OUTPUT_EXTENT = "OUTPUT_EXTENT"
    OUTPUT_STATS = "OUTPUT_STATS"
    STORED_VOLUME = "STORED_VOLUME"
    FLOODED_AREA = "FLOODED_AREA"

    def tr(self, string):
        return QCoreApplication.translate("DropWaterAlgorithm", string)

    def createInstance(self):
        return DropWaterAlgorithm()

    def name(self):
        return "dropwater"

    def displayName(self):
        return self.tr("Drop water volume")

    def group(self):
        return "hydrop"

    def groupId(self):
        return "hydrop"

    def shortHelpString(self):
        return self.tr(
            "Pour a specified water volume at a point on a DEM and simulate "
            "ponding and overflow using RichDEM Fill-Spill-Merge."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_DEM, self.tr("DEM"))
        )
        self.addParameter(
            QgsProcessingParameterPoint(self.POUR_POINT, self.tr("Pour point"))
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.VOLUME,
                self.tr("Water volume"),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=5000.0,
                minValue=0.1,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT_DEPTH, self.tr("Water depth"))
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_SURFACE, self.tr("Water surface"), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_EXTENT, self.tr("Flood extent"), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_STATS,
                self.tr("Statistics CSV"),
                self.tr("CSV files (*.csv)"),
                optional=True,
            )
        )
        self.addOutput(QgsProcessingOutputNumber(self.STORED_VOLUME, self.tr("Stored volume (m³)")))
        self.addOutput(QgsProcessingOutputNumber(self.FLOODED_AREA, self.tr("Flooded area (m²)")))

    def processAlgorithm(self, parameters, context, feedback):
        from ..engine.dem import load_dem_from_layer
        from ..engine.dephier_cache import compute_depression_hierarchy
        from ..engine.fill import fill_volume
        from ..engine.statistics import compute_statistics
        from ..engine.raster import write_geotiff, polygonize_mask, write_statistics_csv

        layer = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        point = self.parameterAsPoint(parameters, self.POUR_POINT, context)
        volume = self.parameterAsDouble(parameters, self.VOLUME, context)

        dem = load_dem_from_layer(layer)
        row, col = dem.validate_pour_point(point.x(), point.y())

        def progress(value, text):
            feedback.setProgress(value)
            feedback.setProgressText(text)

        hierarchy = compute_depression_hierarchy(dem, progress)
        result = fill_volume(dem, row, col, volume, hierarchy=hierarchy)
        stats = compute_statistics(result, dem.cell_area_m2)

        depth_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_DEPTH, context)
        write_geotiff(depth_path, result.depth, dem)

        surface_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_SURFACE, context)
        if surface_path:
            write_geotiff(surface_path, result.surface, dem)

        extent_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_EXTENT, context)
        if extent_path:
            polygonize_mask(extent_path, result.inundation_mask, dem)

        stats_path = self.parameterAsFileOutput(parameters, self.OUTPUT_STATS, context)
        if stats_path:
            write_statistics_csv(stats_path, stats)

        return {
            self.OUTPUT_DEPTH: depth_path,
            self.OUTPUT_SURFACE: surface_path or "",
            self.OUTPUT_EXTENT: extent_path or "",
            self.OUTPUT_STATS: stats_path or "",
            self.STORED_VOLUME: stats.stored_volume_m3,
            self.FLOODED_AREA: stats.flooded_area_m2,
        }
