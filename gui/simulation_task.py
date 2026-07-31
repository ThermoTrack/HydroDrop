"""Background simulation tasks for HydroDrop."""

from __future__ import annotations

from qgis.core import QgsApplication, QgsTask
from qgis.PyQt.QtCore import pyqtSignal


class HydroDropSimulationTask(QgsTask):
    """Run HydroDrop engine work off the UI thread."""

    progressChanged = pyqtSignal(int, str)

    def __init__(self, description: str, runner, on_success, on_failure):
        super().__init__(description, QgsTask.CanCancel)
        self.runner = runner
        self.on_success = on_success
        self.on_failure = on_failure
        self.result_data = None
        self.exception = None

    def report_progress(self, value: int, text: str) -> None:
        self.setProgress(value)
        self.progressChanged.emit(value, text)

    def run(self):
        try:
            self.result_data = self.runner(self)
            return True
        except Exception as exc:
            self.exception = exc
            return False

    def finished(self, result):
        if result and self.result_data is not None:
            self.on_success(self.result_data)
        elif self.exception is not None:
            self.on_failure(self.exception)
        else:
            self.on_failure(RuntimeError("Simulation was cancelled."))

    @staticmethod
    def add(description, runner, on_success, on_failure, on_progress=None) -> "HydroDropSimulationTask":
        task = HydroDropSimulationTask(description, runner, on_success, on_failure)
        if on_progress is not None:
            task.progressChanged.connect(on_progress)
        QgsApplication.taskManager().addTask(task)
        return task
