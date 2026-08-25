"""Background pipeline execution."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QThread, Signal


class PipelineWorker(QThread):
    """Run design pipeline off the UI thread."""

    finished_ok = Signal(object)
    failed = Signal(str)
    progress = Signal(str)

    def __init__(self, run_fn: Any, parent=None) -> None:
        super().__init__(parent)
        self._run_fn = run_fn

    def run(self) -> None:
        try:
            self.progress.emit("Starting pipeline…")
            result = self._run_fn()
            self.progress.emit("Complete")
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
