"""Qt5/Qt6 compatibility shims for QGIS 3 and QGIS 4."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox

if hasattr(Qt, "DockWidgetArea"):
    BOTTOM_DOCK_WIDGET_AREA = Qt.DockWidgetArea.BottomDockWidgetArea
    WINDOW_MODAL = Qt.WindowModality.WindowModal
    KEEP_ASPECT_RATIO = Qt.AspectRatioMode.KeepAspectRatio
    SMOOTH_TRANSFORMATION = Qt.TransformationMode.SmoothTransformation
    CROSS_CURSOR = Qt.CursorShape.CrossCursor
    LEFT_BUTTON = Qt.MouseButton.LeftButton
    HORIZONTAL = Qt.Orientation.Horizontal
    WAIT_CURSOR = Qt.CursorShape.WaitCursor
else:
    BOTTOM_DOCK_WIDGET_AREA = Qt.BottomDockWidgetArea
    WINDOW_MODAL = Qt.WindowModal
    KEEP_ASPECT_RATIO = Qt.KeepAspectRatio
    SMOOTH_TRANSFORMATION = Qt.SmoothTransformation
    CROSS_CURSOR = Qt.CrossCursor
    LEFT_BUTTON = Qt.LeftButton
    HORIZONTAL = Qt.Horizontal
    WAIT_CURSOR = Qt.WaitCursor

if hasattr(QDialogButtonBox, "StandardButton"):
    DIALOG_CLOSE = QDialogButtonBox.StandardButton.Close
else:
    DIALOG_CLOSE = QDialogButtonBox.Close