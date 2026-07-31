"""DEM loading and coordinate utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from .exceptions import InvalidDemError, InvalidPourPointError

try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False

try:
    from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsMapLayer,
        QgsPointXY,
        QgsProject,
        QgsRaster,
        QgsRasterLayer,
    )
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


@dataclass
class DemData:
    """In-memory DEM representation used by the engine."""

    elevation: np.ndarray
    geotransform: Tuple[float, float, float, float, float, float]
    nodata: Optional[float]
    crs_wkt: str
    source_id: str
    cell_area_m2: float
    crs_authid: str = ""

    @property
    def rows(self) -> int:
        return self.elevation.shape[0]

    @property
    def cols(self) -> int:
        return self.elevation.shape[1]

    def world_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        gt = self.geotransform
        col = int((x - gt[0]) / gt[1])
        row = int((y - gt[3]) / gt[5])
        return row, col

    def cell_to_world(self, row: int, col: int) -> Tuple[float, float]:
        gt = self.geotransform
        x = gt[0] + (col + 0.5) * gt[1]
        y = gt[3] + (row + 0.5) * gt[5]
        return x, y

    def is_valid_cell(self, row: int, col: int) -> bool:
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return False
        value = self.elevation[row, col]
        if self.nodata is not None and np.isclose(value, self.nodata):
            return False
        if np.isnan(value):
            return False
        return True

    def validate_pour_point(self, x: float, y: float) -> Tuple[int, int]:
        row, col = self.world_to_cell(x, y)
        if self.is_valid_cell(row, col):
            return row, col

        nearest = self._nearest_valid_cell(row, col, max_radius=12)
        if nearest is not None:
            return nearest

        raise InvalidPourPointError(
            f"Pour point ({x:.2f}, {y:.2f}) is outside the DEM or on NoData.\n"
            f"DEM CRS: {self.crs_authid or 'unknown'}"
        )

    def _nearest_valid_cell(
        self, row: int, col: int, max_radius: int = 12
    ) -> Optional[Tuple[int, int]]:
        best = None
        best_dist = float("inf")
        for radius in range(1, max_radius + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if abs(dr) != radius and abs(dc) != radius:
                        continue
                    r, c = row + dr, col + dc
                    if not self.is_valid_cell(r, c):
                        continue
                    dist = dr * dr + dc * dc
                    if dist < best_dist:
                        best_dist = dist
                        best = (r, c)
            if best is not None:
                return best
        return None


def cell_area_from_geotransform(gt: Tuple[float, float, float, float, float, float]) -> float:
    return abs(gt[1] * gt[5])


def utm_epsg_for_lon_lat(lon: float, lat: float) -> int:
    zone = int((lon + 180.0) / 6.0) + 1
    zone = max(1, min(60, zone))
    return (32700 + zone) if lat < 0 else (32600 + zone)


def _transform_point(point, source_crs, dest_crs) -> "QgsPointXY":
    transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
    return transform.transform(point)


def _dem_from_gdal_dataset(ds, source_id: str, crs_authid: str, crs_wkt: str) -> DemData:
    if ds is None:
        raise InvalidDemError("Could not open DEM dataset.")

    band = ds.GetRasterBand(1)
    elevation = band.ReadAsArray().astype(np.float64)
    nodata = band.GetNoDataValue()
    if nodata is not None:
        elevation = np.where(np.isclose(elevation, nodata), np.nan, elevation)

    gt = ds.GetGeoTransform()
    geotransform = (gt[0], gt[1], gt[2], gt[3], gt[4], gt[5])

    return DemData(
        elevation=elevation,
        geotransform=geotransform,
        nodata=nodata,
        crs_wkt=crs_wkt,
        crs_authid=crs_authid,
        source_id=source_id,
        cell_area_m2=cell_area_from_geotransform(geotransform),
    )


def _warp_gdal_dataset(src_ds, epsg: int, nodata: Optional[float]):
    if not GDAL_AVAILABLE:
        raise RuntimeError("GDAL is required.")

    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(epsg)

    options = gdal.WarpOptions(
        dstSRS=dst_srs.ExportToWkt(),
        resampleAlg="near",
        srcNodata=nodata,
        dstNodata=nodata,
        format="MEM",
    )
    return gdal.Warp("", src_ds, options=options)


def load_dem_from_gdal_source(
    source: str,
    crs_authid: str,
    crs_wkt: str,
    lon: Optional[float] = None,
    lat: Optional[float] = None,
    source_id: Optional[str] = None,
) -> DemData:
    """Load DEM using GDAL only — safe to call from background threads."""
    if not GDAL_AVAILABLE:
        raise RuntimeError("GDAL is required.")

    src = gdal.Open(source)
    if src is None:
        raise InvalidDemError(f"Could not open DEM: {source}")

    band = src.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    src_srs = src.GetProjection()

    geographic = False
    if crs_authid and ("4326" in crs_authid or crs_authid.upper().endswith("CRS:84")):
        geographic = True
    elif src_srs:
        srs = osr.SpatialReference(wkt=src_srs)
        geographic = srs.IsGeographic() == 1

    sid = source_id or source

    if geographic:
        gt = src.GetGeoTransform()
        width = src.RasterXSize
        height = src.RasterYSize
        if lon is None or lat is None:
            lon = gt[0] + width * gt[1] * 0.5
            lat = gt[3] + height * gt[5] * 0.5
        epsg = utm_epsg_for_lon_lat(lon, lat)
        warped = _warp_gdal_dataset(src, epsg, nodata)
        dst_srs = osr.SpatialReference()
        dst_srs.ImportFromEPSG(epsg)
        return _dem_from_gdal_dataset(
            warped,
            f"{sid}|EPSG:{epsg}",
            f"EPSG:{epsg}",
            dst_srs.ExportToWkt(),
        )

    return _dem_from_gdal_dataset(src, sid, crs_authid, crs_wkt or src_srs)


def capture_layer_spec(layer) -> dict:
    """Read QGIS layer metadata on the main thread before background work."""
    if layer is None or not layer.isValid():
        raise InvalidDemError("The selected DEM layer is not valid.")
    if layer.type() != QgsMapLayer.RasterLayer:
        raise InvalidDemError("Please select a raster DEM layer.")

    crs = layer.crs()
    provider = layer.dataProvider()
    return {
        "source": provider.dataSourceUri() or layer.source(),
        "crs_authid": crs.authid(),
        "crs_wkt": crs.toWkt(),
        "source_id": f"{layer.id()}|{layer.source()}",
        "geographic": crs.isGeographic(),
    }


def load_dem_from_layer(layer, lon: Optional[float] = None, lat: Optional[float] = None) -> DemData:
    """Load a QgsRasterLayer into DemData (main thread)."""
    if not QGIS_AVAILABLE:
        raise RuntimeError("QGIS is required to load raster layers.")
    spec = capture_layer_spec(layer)
    return load_dem_from_gdal_source(
        spec["source"],
        spec["crs_authid"],
        spec["crs_wkt"],
        lon=lon,
        lat=lat,
        source_id=spec["source_id"],
    )


def resolve_pour_point_from_layer(layer, point, point_crs=None):
    """
    Fast pour-point check on map click — no full DEM load or warp.
    Returns (eng_x, eng_y, elevation, reproject_message).
    """
    if not QGIS_AVAILABLE:
        raise RuntimeError("QGIS is required.")

    if layer is None or not layer.isValid():
        raise InvalidDemError("The selected DEM layer is not valid.")
    if layer.type() != QgsMapLayer.RasterLayer:
        raise InvalidDemError("Please select a raster DEM layer.")

    layer_crs = layer.crs()
    if point_crs is None:
        point_crs = layer_crs

    layer_point = (
        _transform_point(point, point_crs, layer_crs)
        if point_crs != layer_crs
        else point
    )

    ident = layer.dataProvider().identify(
        layer_point, QgsRaster.IdentifyFormatValue
    )
    if not ident.isValid():
        raise InvalidPourPointError(
            f"Pour point ({layer_point.x():.2f}, {layer_point.y():.2f}) "
            "is outside the DEM or on NoData."
        )

    values = ident.results()
    if not values:
        raise InvalidPourPointError("Could not read elevation at pour point.")

    elevation = next(iter(values.values()))
    if elevation is None:
        raise InvalidPourPointError("Pour point is on NoData.")

    reproject_msg = None
    wgs84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)
    if layer_crs.isGeographic():
        warp_lon, warp_lat = layer_point.x(), layer_point.y()
        epsg = utm_epsg_for_lon_lat(warp_lon, warp_lat)
        target_crs = QgsCoordinateReferenceSystem.fromEpsgId(epsg)
        eng_point = _transform_point(layer_point, layer_crs, target_crs)
        reproject_msg = (
            f"DEM is geographic ({layer_crs.authid()}). "
            f"HydroDrop will reproject to {target_crs.authid()} when you Run."
        )
    else:
        eng_point = layer_point
        wgs_point = (
            _transform_point(layer_point, layer_crs, wgs84)
            if layer_crs != wgs84
            else layer_point
        )
        warp_lon, warp_lat = wgs_point.x(), wgs_point.y()

    return (
        eng_point.x(),
        eng_point.y(),
        float(elevation),
        reproject_msg,
        warp_lon,
        warp_lat,
    )


def load_dem_from_qgis_point(layer, point, point_crs=None):
    """Legacy full load — prefer resolve_pour_point_from_layer on click."""
    eng_x, eng_y, elevation, reproject_msg, _warp_lon, _warp_lat = (
        resolve_pour_point_from_layer(layer, point, point_crs)
    )
    dem = load_dem_from_layer(
        layer,
        lon=point.x() if layer.crs().isGeographic() else None,
        lat=point.y() if layer.crs().isGeographic() else None,
    )
    row, col = dem.validate_pour_point(eng_x, eng_y)
    return dem, row, col, elevation, reproject_msg, eng_x, eng_y


def array_to_dem(
    elevation: np.ndarray,
    geotransform: Tuple[float, float, float, float, float, float],
    nodata: Optional[float] = None,
    crs_wkt: str = "",
    source_id: str = "array",
    crs_authid: str = "",
) -> DemData:
    return DemData(
        elevation=np.asarray(elevation, dtype=np.float64),
        geotransform=geotransform,
        nodata=nodata,
        crs_wkt=crs_wkt,
        crs_authid=crs_authid,
        source_id=source_id,
        cell_area_m2=cell_area_from_geotransform(geotransform),
    )
