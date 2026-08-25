"""Main window — interactive engineering console (PySide6 only, no viz toolkit)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from auv_fin_design.application.pipeline import DesignResult, run_design_pipeline
from auv_fin_design.infrastructure.config.loader import repo_root
from auv_fin_design.ui.gui.viewmodels.design_result_vm import DesignResultView
from auv_fin_design.ui.gui.widgets.input_panel import InputPanel
from auv_fin_design.ui.gui.widgets.results_panel import ResultsPanel
from auv_fin_design.ui.gui.workers.pipeline_worker import PipelineWorker

_PIPELINE_STEPS = (
    "Hydrodynamics",
    "Control",
    "Sizing",
    "CoP",
    "Structure",
    "Validation",
)


def _theme_path() -> Path:
    return Path(__file__).resolve().parent / "themes" / "dark_ocean.qss"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Torpedo AUV Fin Design & Optimization Suite")
        self.resize(1280, 860)
        self._last_result: DesignResult | None = None
        self._worker: PipelineWorker | None = None

        self._build_menu()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.addLayout(self._build_toolbar())
        root.addWidget(self._build_step_indicator())
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        root.addWidget(self.progress)
        root.addWidget(self._build_main_splitter(), stretch=1)
        self.summary = QLabel("")
        self.summary.setObjectName("StatusLine")
        self.summary.setWordWrap(True)
        root.addWidget(self.summary)

        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Ready — Ctrl+R run  ·  Ctrl+G golden  ·  double-click cells to copy")

        QShortcut(QKeySequence("Ctrl+R"), self, self._on_run)
        QShortcut(QKeySequence("Ctrl+G"), self, self._load_golden)
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_report)
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, self._export_bundle)

        self.input_panel.validation_changed.connect(self._on_input_hint)
        self._load_golden()

    def _build_menu(self) -> None:
        menu = self.menuBar()
        file_m = menu.addMenu("&File")
        run_a = QAction("&Run Design", self)
        run_a.setShortcut("Ctrl+R")
        run_a.triggered.connect(self._on_run)
        file_m.addAction(run_a)
        file_m.addAction("Load &Golden Vehicle", self._load_golden)
        file_m.addSeparator()
        file_m.addAction("Export &Report…", self._export_report)
        file_m.addAction("Export CAD/&Sim…", self._export_bundle)
        file_m.addSeparator()
        file_m.addAction("E&xit", self.close)
        help_m = menu.addMenu("&Help")
        help_m.addAction("About", self._show_about)

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        self.run_btn = QPushButton("▶  Run Design")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.clicked.connect(self._on_run)
        self.golden_btn = QPushButton("Golden Vehicle")
        self.golden_btn.clicked.connect(self._load_golden)
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self._export_report)
        self.stl_btn = QPushButton("Export CAD/Sim")
        self.stl_btn.clicked.connect(self._export_bundle)
        toolbar.addWidget(self.run_btn)
        toolbar.addWidget(self.golden_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.stl_btn)
        toolbar.addStretch(1)
        self.status_banner = QLabel("Ready")
        self.status_banner.setObjectName("StatusLine")
        toolbar.addWidget(self.status_banner)
        return toolbar

    def _build_step_indicator(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("StepIndicator")
        row = QHBoxLayout(frame)
        row.setContentsMargins(4, 4, 4, 4)
        self._step_labels: list[QLabel] = []
        for i, step in enumerate(_PIPELINE_STEPS):
            lbl = QLabel(step)
            lbl.setObjectName("StepLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("active", False)
            lbl.setProperty("done", False)
            self._step_labels.append(lbl)
            row.addWidget(lbl, stretch=1)
            if i < len(_PIPELINE_STEPS) - 1:
                arrow = QLabel("→")
                arrow.setObjectName("StepArrow")
                row.addWidget(arrow)
        return frame

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.input_panel = InputPanel()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.input_panel)
        scroll.setMinimumWidth(300)
        scroll.setMaximumWidth(400)
        splitter.addWidget(scroll)
        self.results = ResultsPanel()
        splitter.addWidget(self.results)
        splitter.setSizes([360, 920])
        return splitter

    def _set_steps(self, active: int | None = None, done: int = -1) -> None:
        for i, lbl in enumerate(self._step_labels):
            lbl.setProperty("active", active is not None and i == active)
            lbl.setProperty("done", i <= done)
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self.run_btn.setEnabled(not busy)
        self.golden_btn.setEnabled(not busy)
        self.export_btn.setEnabled(not busy)
        self.stl_btn.setEnabled(not busy)
        self.progress.setVisible(busy)
        if busy:
            self._set_steps(active=0)
        else:
            self._set_steps(done=len(_PIPELINE_STEPS) - 1)
        if message:
            self.status_banner.setText(message)

    def _on_input_hint(self, msg: str) -> None:
        if msg:
            self.statusBar().showMessage(f"Input: {msg}", 4000)

    def _load_golden(self) -> None:
        self.input_panel.load_golden()
        self.status_banner.setText("Golden vehicle loaded")
        self.summary.setText("Aft X-tail · T=30 s · freshwater · PLA")

    def _on_run(self) -> None:
        err = self.input_panel.validate()
        if err:
            QMessageBox.warning(self, "Input", err)
            return
        if self._worker and self._worker.isRunning():
            return
        inputs = self.input_panel.gather()

        def _run() -> DesignResult:
            return run_design_pipeline(
                inputs.vehicle,
                inputs.mission,
                material=inputs.material,
                servo=inputs.servo,
                defaults=inputs.defaults,
                airfoil_name=inputs.airfoil_name,
                geometry_override=inputs.geometry_override,
                run_sensitivity=inputs.run_sensitivity,
                run_optimization=inputs.run_optimization,
            )

        self._set_busy(True, "Running pipeline…")
        self.summary.setText("Computing: " + " → ".join(_PIPELINE_STEPS))
        self._worker = PipelineWorker(_run, self)
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.finished_ok.connect(self._on_pipeline_done)
        self._worker.failed.connect(self._on_pipeline_failed)
        self._worker.start()

    def _on_worker_progress(self, msg: str) -> None:
        self.status_banner.setText(msg)
        for i, step in enumerate(_PIPELINE_STEPS):
            if step.lower() in msg.lower():
                self._set_steps(active=i, done=i - 1)
                break

    def _on_pipeline_done(self, result: DesignResult) -> None:
        self._set_busy(False)
        self._last_result = result
        view = DesignResultView.from_result(result)
        self.results.show_result(view)
        status = "PASSED" if view.passed else f"FAILED ({view.failure_count} violations)"
        self.status_banner.setText(f"{status} — {result.airfoil_name}")
        self.summary.setText(
            f"M_design = {result.control_req.M_design:.4f} N·m  ·  "
            f"span = {result.geometry.span * 1000:.2f} mm  ·  "
            f"CL = {result.aero.cl:.4f}  ·  "
            f"servo util = {result.servo_result.utilization:.1%}"
        )
        self.statusBar().showMessage(
            "Done — browse sections on the left; double-click table cells to copy",
            8000,
        )

    def _on_pipeline_failed(self, message: str) -> None:
        self._set_busy(False)
        self._set_steps(active=None, done=-1)
        self.status_banner.setText("Error")
        QMessageBox.critical(self, "Design failed", message)

    def _export_report(self) -> None:
        if self._last_result is None:
            QMessageBox.information(self, "Export", "Run a design first.")
            return
        from auv_fin_design.domain.reporting.export import write_all_reports

        paths = write_all_reports(self._last_result, repo_root() / "reports")
        self.results.set_export_paths({k: str(v) for k, v in paths.items()})
        QMessageBox.information(
            self,
            "Export",
            "Reports written to reports/\n(JSON, HTML, TXT — click paths in Exports section to copy)",
        )

    def _export_bundle(self) -> None:
        if self._last_result is None:
            QMessageBox.information(self, "Export", "Run a design first.")
            return
        from auv_fin_design.adapters.export_bundle import export_simulation_bundle

        paths = export_simulation_bundle(
            self._last_result, repo_root() / "exports" / "sim_bundle"
        )
        self.results.set_export_paths({k: str(v) for k, v in paths.items()})
        QMessageBox.information(self, "Export", "CAD/sim bundle written — see Exports section.")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "AUV Fin Design Suite",
            "Torpedo AUV fin sizing pipeline\n\n"
            "PySide6 desktop UI — no external visualization toolkit.\n"
            "Shortcuts: Ctrl+R run · Ctrl+G golden · Ctrl+E report · Ctrl+Shift+E CAD",
        )


def run_app() -> int:
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("AUV Fin Design Suite")
    theme = _theme_path()
    if theme.exists():
        app.setStyleSheet(theme.read_text(encoding="utf-8"))
    win = MainWindow()
    win.show()
    return app.exec()
