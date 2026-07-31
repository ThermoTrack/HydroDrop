"""Volume dialog with slider and multi-drop controls."""

from qgis.PyQt.QtCore import QTimer, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .qt_compat import DIALOG_CLOSE, HORIZONTAL


class WaterDialog(QDialog):
    """Dialog for volume input, slider, and session controls."""

    volumeChanged = pyqtSignal(float)
    runRequested = pyqtSignal(float)
    animateRequested = pyqtSignal(float)
    addDropRequested = pyqtSignal(float)
    newLocationRequested = pyqtSignal()
    resetSessionRequested = pyqtSignal()

    def __init__(self, pour_x, pour_y, pour_elevation, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HydroDrop — Pour Water")
        self.setMinimumWidth(420)

        self.pour_info = QLabel(
            f"Pour point: ({pour_x:.2f}, {pour_y:.2f})\n"
            f"Ground elevation: {pour_elevation:.2f} m"
        )

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(1.0, 10_000_000.0)
        self.volume_spin.setValue(5000.0)
        self.volume_spin.setSuffix(" m³")
        self.volume_spin.setDecimals(1)

        self.slider = QSlider()
        self.slider.setOrientation(HORIZONTAL)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100000)
        self.slider.setValue(5000)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(400)
        self._debounce.timeout.connect(self._emit_volume_changed)

        self.volume_spin.valueChanged.connect(self._on_spin_changed)
        self.slider.valueChanged.connect(self._on_slider_changed)

        preset_row = QHBoxLayout()
        for preset in (100, 500, 1000, 5000, 10000, 50000):
            btn = QPushButton(str(preset))
            btn.clicked.connect(lambda _checked, v=preset: self._set_volume(v))
            preset_row.addWidget(btn)

        run_btn = QPushButton("Run")
        run_btn.clicked.connect(lambda: self.runRequested.emit(self.volume_spin.value()))

        animate_btn = QPushButton("Animate")
        animate_btn.clicked.connect(lambda: self.animateRequested.emit(self.volume_spin.value()))

        add_drop_btn = QPushButton("Add Drop")
        add_drop_btn.clicked.connect(lambda: self.addDropRequested.emit(self.volume_spin.value()))

        new_loc_btn = QPushButton("New Location")
        new_loc_btn.clicked.connect(self.newLocationRequested.emit)

        reset_btn = QPushButton("Reset Session")
        reset_btn.clicked.connect(self.resetSessionRequested.emit)

        self._action_buttons = [run_btn, animate_btn, add_drop_btn, new_loc_btn, reset_btn]

        self.busy_widget = QWidget()
        busy_layout = QVBoxLayout(self.busy_widget)
        busy_layout.setContentsMargins(0, 0, 0, 0)

        self.busy_heading = QLabel("💧 HydroDrop is working…")
        self.busy_heading.setStyleSheet("font-weight: bold; color: #0066cc;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% — working")

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        busy_layout.addWidget(self.busy_heading)
        busy_layout.addWidget(self.progress_bar)
        busy_layout.addWidget(self.status_label)
        self.busy_widget.hide()

        buttons = QDialogButtonBox(DIALOG_CLOSE)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pour_info)
        layout.addWidget(QLabel("Water volume"))
        layout.addWidget(self.volume_spin)
        layout.addWidget(QLabel("Live volume slider"))
        layout.addWidget(self.slider)
        layout.addLayout(preset_row)

        action_row = QHBoxLayout()
        for btn in self._action_buttons:
            action_row.addWidget(btn)
        layout.addLayout(action_row)
        layout.addWidget(self.busy_widget)
        layout.addWidget(buttons)

    def update_pour_point(self, pour_x, pour_y, pour_elevation) -> None:
        self.pour_info.setText(
            f"Pour point: ({pour_x:.2f}, {pour_y:.2f})\n"
            f"Ground elevation: {pour_elevation:.2f} m"
        )

    def set_busy(self, busy: bool, message: str = "") -> None:
        for btn in self._action_buttons:
            btn.setEnabled(not busy)
        self.volume_spin.setEnabled(not busy)
        self.slider.setEnabled(not busy)
        if busy:
            self.busy_widget.show()
            self.progress_bar.setRange(0, 0)  # indeterminate pulse
            self.progress_bar.setFormat("Working…")
            self.status_label.setText(message or "Starting…")
        else:
            self.busy_widget.hide()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")
            self.status_label.setText("")

    def set_progress(self, value: int, message: str = "") -> None:
        if self.progress_bar.minimum() == 0 and self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(max(0, min(100, value)))
        self.progress_bar.setFormat(f"%p% — {message}" if message else "%p%")
        if message:
            self.status_label.setText(message)

    def _set_volume(self, value: float) -> None:
        self.volume_spin.blockSignals(True)
        self.slider.blockSignals(True)
        self.volume_spin.setValue(value)
        self.slider.setValue(int(min(value, self.slider.maximum())))
        self.volume_spin.blockSignals(False)
        self.slider.blockSignals(False)
        self._debounce.start()

    def _on_spin_changed(self, value: float) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(int(min(value, self.slider.maximum())))
        self.slider.blockSignals(False)
        self._debounce.start()

    def _on_slider_changed(self, value: int) -> None:
        self.volume_spin.blockSignals(True)
        self.volume_spin.setValue(float(value))
        self.volume_spin.blockSignals(False)
        self._debounce.start()

    def _emit_volume_changed(self) -> None:
        self.volumeChanged.emit(self.volume_spin.value())

    def current_volume(self) -> float:
        return self.volume_spin.value()
