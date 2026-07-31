"""HydroDrop toolbar widget."""

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class HydroDropToolbarWidget(QWidget):
    """Embedded toolbar controls for HydroDrop."""

    activateToolRequested = pyqtSignal()
    runRequested = pyqtSignal(float)
    volumeChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.activate_btn = QPushButton("💧 HydroDrop")
        self.activate_btn.setToolTip("Activate drop-water map tool")
        self.activate_btn.clicked.connect(self.activateToolRequested.emit)

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(1.0, 10_000_000.0)
        self.volume_spin.setValue(5000.0)
        self.volume_spin.setSuffix(" m³")
        self.volume_spin.setDecimals(1)
        self.volume_spin.valueChanged.connect(self.volumeChanged.emit)

        self.animate_cb = QCheckBox("Animate")
        self.animate_cb.setChecked(False)

        self.export_raster_cb = QCheckBox("Export Raster")
        self.export_raster_cb.setChecked(True)

        self.export_polygon_cb = QCheckBox("Export Polygon")
        self.export_polygon_cb.setChecked(True)

        self.stats_cb = QCheckBox("Show Statistics")
        self.stats_cb.setChecked(True)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(lambda: self.runRequested.emit(self.volume_spin.value()))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.activate_btn)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_spin)
        layout.addWidget(self.animate_cb)
        layout.addWidget(self.export_raster_cb)
        layout.addWidget(self.export_polygon_cb)
        layout.addWidget(self.stats_cb)
        layout.addWidget(self.run_btn)

    @property
    def animate(self) -> bool:
        return self.animate_cb.isChecked()

    @property
    def export_raster(self) -> bool:
        return self.export_raster_cb.isChecked()

    @property
    def export_polygon(self) -> bool:
        return self.export_polygon_cb.isChecked()

    @property
    def show_statistics(self) -> bool:
        return self.stats_cb.isChecked()

    def set_volume(self, value: float) -> None:
        self.volume_spin.blockSignals(True)
        self.volume_spin.setValue(value)
        self.volume_spin.blockSignals(False)
