"""Results dock widget showing simulation statistics."""

from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..engine.statistics import SimulationStatistics


class ResultsDockWidget(QDockWidget):
    def __init__(self, iface):
        super().__init__("HydroDrop Statistics", iface.mainWindow())
        self.iface = iface
        self.setObjectName("HydroDropResultsDock")
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Metric", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Latest simulation results"))
        layout.addWidget(self._table)
        self.setWidget(container)
        self.hide()

    def update_statistics(self, stats: SimulationStatistics) -> None:
        rows = stats.to_csv_rows()[1:]
        self._table.setRowCount(len(rows))
        for i, (metric, value, _unit) in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(metric))
            self._table.setItem(i, 1, QTableWidgetItem(value))
        self.show()
        self.raise_()
