"""Custom exceptions for the HydroDrop engine."""


class HydroDropError(Exception):
    """Base exception for HydroDrop engine errors."""


class RichDEMNotAvailableError(HydroDropError):
    """Raised when the richdem package is not installed."""


class CrsNotProjectedError(HydroDropError):
    """Raised when the DEM uses a geographic (non-projected) CRS."""


class InvalidPourPointError(HydroDropError):
    """Raised when the pour point is NoData or outside the raster extent."""


class InvalidDemError(HydroDropError):
    """Raised when the input is not a valid single-band elevation raster."""
