"""Raster and vector export helpers."""

from __future__ import annotations

import csv
import os
import uuid
from typing import Optional, Tuple

import numpy as np

from .dem import DemData
from .statistics import SimulationStatistics

try:
    from osgeo import gdal, ogr, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False


def _ensure_gdal():
    if not GDAL_AVAILABLE:
        raise RuntimeError("GDAL is required for raster export.")


def write_geotiff(
    path: str,
    array: np.ndarray,
    dem: DemData,
    nodata: float = -9999.0,
) -> str:
    _ensure_gdal()
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = array.shape

    target = path
    if os.path.exists(target):
        try:
            os.remove(target)
        except OSError:
            base, ext = os.path.splitext(path)
            target = f"{base}_{uuid.uuid4().hex[:8]}{ext}"

    ds = driver.Create(target, cols, rows, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(dem.geotransform)
    if dem.crs_wkt:
        srs = osr.SpatialReference()
        srs.ImportFromWkt(dem.crs_wkt)
        ds.SetProjection(srs.ExportToWkt())
    band = ds.GetRasterBand(1)
    band.WriteArray(array.astype(np.float32))
    band.SetNoDataValue(nodata)
    band.FlushCache()
    ds = None
    return target


def polygonize_mask(
    path: str,
    mask: np.ndarray,
    dem: DemData,
) -> str:
    _ensure_gdal()
    mem_drv = gdal.GetDriverByName("MEM")
    rows, cols = mask.shape
    src = mem_drv.Create("", cols, rows, 1, gdal.GDT_Byte)
    src.SetGeoTransform(dem.geotransform)
    if dem.crs_wkt:
        srs = osr.SpatialReference()
        srs.ImportFromWkt(dem.crs_wkt)
        src.SetProjection(srs.ExportToWkt())
    band = src.GetRasterBand(1)
    band.WriteArray(mask.astype(np.uint8))
    band.SetNoDataValue(0)

    drv = ogr.GetDriverByName("GPKG")
    if os.path.exists(path):
        os.remove(path)
    dst = drv.CreateDataSource(path)
    layer = dst.CreateLayer("flood_extent", srs=srs if dem.crs_wkt else None)
    field = ogr.FieldDefn("inundated", ogr.OFTInteger)
    layer.CreateField(field)
    gdal.Polygonize(band, band, layer, 0, [], callback=None)
    dst = None
    src = None
    return path


def write_statistics_csv(path: str, stats: SimulationStatistics) -> str:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(stats.to_csv_rows())
    return path


def export_simulation_outputs(
    output_dir: str,
    dem: DemData,
    depth: np.ndarray,
    surface: np.ndarray,
    stats: SimulationStatistics,
    prefix: str = "",
) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    p = prefix
    paths = {
        "WaterDepth.tif": write_geotiff(
            os.path.join(output_dir, f"{p}WaterDepth.tif"), depth, dem
        ),
        "WaterSurface.tif": write_geotiff(
            os.path.join(output_dir, f"{p}WaterSurface.tif"), surface, dem
        ),
        "FloodExtent.gpkg": polygonize_mask(
            os.path.join(output_dir, f"{p}FloodExtent.gpkg"),
            depth > 1e-6,
            dem,
        ),
        "Statistics.csv": write_statistics_csv(
            os.path.join(output_dir, f"{p}Statistics.csv"), stats
        ),
    }
    return paths
