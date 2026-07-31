"""RichDEM availability check and shared import helpers."""

from .exceptions import RichDEMNotAvailableError

_RICHDEM = None
_RICHDEM_CHECKED = False


def get_richdem():
    """Return the richdem module, raising if unavailable."""
    global _RICHDEM, _RICHDEM_CHECKED
    if not _RICHDEM_CHECKED:
        _RICHDEM_CHECKED = True
        try:
            import richdem as rd
            _RICHDEM = rd
        except ImportError:
            _RICHDEM = None
    if _RICHDEM is None:
        raise RichDEMNotAvailableError(
            "The richdem Python package is required.\n\n"
            "Install it in the QGIS Python environment:\n"
            "  Windows: \"D:\\Program Files\\QGIS 4.2.0\\apps\\Python312\\python.exe\" -m pip install richdem2\n"
            "  Or OSGeo4W Shell: python -m pip install richdem2\n"
            "  Linux/macOS: pip install richdem2"
        )
    return _RICHDEM


def richdem_available() -> bool:
    """Return True if richdem can be imported."""
    try:
        get_richdem()
        return True
    except RichDEMNotAvailableError:
        return False


def get_depression_hierarchy_labels(dem_shape):
    """Compatible wrapper for old/new RichDEM label API."""
    rd = get_richdem()
    if hasattr(rd, "get_new_depression_hierarchy_labels"):
        return rd.get_new_depression_hierarchy_labels(dem_shape)
    return rd.get_depression_hierarchy_labels(dem_shape)
