"""PySide6 main window — full SRDS Chapter 1 inputs and exports."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auv_fin_design.application.pipeline import (
    DesignResult,
    GeometryOverride,
    run_design_pipeline,
)
from auv_fin_design.domain.constants.materials import get_material, list_materials
from auv_fin_design.domain.geometry.sizing import format_fin_dimensions_lines
from auv_fin_design.domain.servo.analysis import ServoSpecification
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel
from auv_fin_design.infrastructure.config.loader import load_defaults, repo_root


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Torpedo AUV Fin Design & Optimization Suite")
        self.resize(1280, 820)
        self._defaults = load_defaults()
        self._last_result: DesignResult | None = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self._build_input_form())
        left_layout.addWidget(self._build_optional_geometry())
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run Design")
        self.run_btn.clicked.connect(self._on_run)
        self.golden_btn = QPushButton("Load Golden Vehicle")
        self.golden_btn.clicked.connect(self._load_golden)
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self._export_report)
        self.stl_btn = QPushButton("Export CAD/Sim")
        self.stl_btn.clicked.connect(self._export_bundle)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.golden_btn)
        btn_row.addWidget(self.export_btn)
        btn_row.addWidget(self.stl_btn)
        left_layout.addLayout(btn_row)
        left_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)
        splitter.addWidget(scroll)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.status_label = QLabel("Ready")
        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        right_layout.addWidget(self.status_label)
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setFont(QFont("monospace", 10))
        right_layout.addWidget(self.results)
        splitter.addWidget(right)
        splitter.setSizes([460, 820])
        self._load_golden()

    def _spin(
        self,
        value: float,
        minimum: float,
        maximum: float,
        decimals: int = 4,
        step: float = 0.01,
    ) -> QDoubleSpinBox:
        w = QDoubleSpinBox()
        w.setRange(minimum, maximum)
        w.setDecimals(decimals)
        w.setSingleStep(step)
        w.setValue(value)
        return w

    def _build_input_form(self) -> QWidget:
        box = QGroupBox("Design Inputs (SRDS Ch.1)")
        form = QFormLayout(box)

        self.length = self._spin(1.35, 0.1, 20.0, 3, 0.01)
        self.diameter = self._spin(0.1685, 0.01, 2.0, 4, 0.001)
        self.mass = self._spin(24.0, 0.1, 5000.0, 2, 0.1)
        self.water = QComboBox()
        self.water.addItems(["freshwater", "seawater"])
        self.speed = self._spin(1.5, 0.1, 20.0, 3, 0.1)
        self.max_speed = self._spin(2.0, 0.1, 30.0, 3, 0.1)
        self.turn_radius = self._spin(6.0, 0.5, 200.0, 2, 0.5)
        self.turn_time = self._spin(30.0, 0.5, 600.0, 1, 1.0)
        self.material = QComboBox()
        self.material.addItems(list_materials())
        self.material.setCurrentText("PLA")
        self.fin_root_frac = self._spin(0.92, 0.5, 0.99, 3, 0.01)
        self.servo_torque = self._spin(3.481, 0.1, 50.0, 3, 0.1)
        self.shaft_d = self._spin(0.006, 0.001, 0.05, 4, 0.001)
        self.max_span_over_d = self._spin(
            float(self._defaults["geometry_constraints"]["max_span_over_diameter"]),
            0.1,
            2.0,
            3,
            0.05,
        )
        self.airfoil = QComboBox()
        self.airfoil.addItem("(auto)")
        data = repo_root() / "data"
        if data.exists():
            for p in sorted(data.iterdir()):
                if p.is_dir():
                    self.airfoil.addItem(p.name)
        self.opt_cb = QCheckBox("Run NSGA-II optimization (slow)")
        self.sens_cb = QCheckBox("Run ±10% sensitivity")
        self.sens_cb.setChecked(True)

        form.addRow("Length L [m]", self.length)
        form.addRow("Diameter D [m]", self.diameter)
        form.addRow("Mass m [kg]", self.mass)
        form.addRow("Water", self.water)
        form.addRow("Cruise / design speed [m/s]", self.speed)
        form.addRow("Maximum speed [m/s]", self.max_speed)
        form.addRow("Turning radius [m]", self.turn_radius)
        form.addRow("Turn establishment [s]", self.turn_time)
        form.addRow("Material", self.material)
        form.addRow("Servo torque [N·m]", self.servo_torque)
        form.addRow("Shaft diameter [m]", self.shaft_d)
        form.addRow("Fin root LE / L (aft)", self.fin_root_frac)
        form.addRow("Max span / D", self.max_span_over_d)
        form.addRow("Airfoil", self.airfoil)
        form.addRow(self.sens_cb)
        form.addRow(self.opt_cb)
        return box

    def _build_optional_geometry(self) -> QWidget:
        box = QGroupBox("Optional Fin Dimensions (override auto-size)")
        form = QFormLayout(box)
        self.override_dims_cb = QCheckBox("Use fixed fin dimensions")
        self.override_dims_cb.setChecked(False)
        self.override_dims_cb.toggled.connect(self._toggle_dim_overrides)

        self.opt_root_chord = self._spin(0.10, 0.01, 2.0, 4, 0.005)
        self.opt_span = self._spin(0.10, 0.01, 1.0, 4, 0.005)
        self.opt_tip_chord = self._spin(0.05, 0.005, 2.0, 4, 0.005)
        self.opt_tip_enable = QCheckBox("Also fix tip chord")
        self.opt_tip_enable.setChecked(False)
        self.opt_tip_enable.toggled.connect(
            lambda on: self.opt_tip_chord.setEnabled(on and self.override_dims_cb.isChecked())
        )

        form.addRow(self.override_dims_cb)
        form.addRow("Root chord [m]", self.opt_root_chord)
        form.addRow("Span [m]", self.opt_span)
        form.addRow(self.opt_tip_enable, self.opt_tip_chord)
        hint = QLabel(
            "Leave unchecked to auto-size from lift. "
            "When checked, root chord & span are fixed; tip = taper×root unless tip is fixed."
        )
        hint.setWordWrap(True)
        form.addRow(hint)
        self._toggle_dim_overrides(False)
        return box

    def _toggle_dim_overrides(self, enabled: bool) -> None:
        self.opt_root_chord.setEnabled(enabled)
        self.opt_span.setEnabled(enabled)
        self.opt_tip_enable.setEnabled(enabled)
        self.opt_tip_chord.setEnabled(enabled and self.opt_tip_enable.isChecked())

    def _load_golden(self) -> None:
        self.length.setValue(1.35)
        self.diameter.setValue(0.1685)
        self.mass.setValue(24.0)
        self.water.setCurrentText("freshwater")
        self.speed.setValue(1.5)
        self.max_speed.setValue(2.0)
        self.turn_radius.setValue(6.0)
        self.turn_time.setValue(30.0)
        self.material.setCurrentText("PLA")
        self.fin_root_frac.setValue(0.92)
        self.servo_torque.setValue(3.481)
        self.shaft_d.setValue(0.006)
        self.max_span_over_d.setValue(
            float(self._defaults["geometry_constraints"]["max_span_over_diameter"])
        )
        self.override_dims_cb.setChecked(False)
        self.opt_root_chord.setValue(0.10)
        self.opt_span.setValue(0.10)
        self.opt_tip_chord.setValue(0.05)
        self.opt_tip_enable.setChecked(False)
        self.status_label.setText("Golden vehicle loaded (aft X-tail, T=30 s)")

    def _on_run(self) -> None:
        try:
            if self.max_speed.value() < self.speed.value():
                QMessageBox.warning(
                    self, "Input", "Maximum speed must be ≥ design speed."
                )
                return
            vehicle = VehicleModel(
                length=self.length.value(),
                diameter=self.diameter.value(),
                mass=self.mass.value(),
                water=self.water.currentText(),  # type: ignore[arg-type]
                fin_root_le_fraction_of_length=self.fin_root_frac.value(),
            )
            mission = MissionModel(
                design_speed=self.speed.value(),
                turning_radius=self.turn_radius.value(),
                turn_establishment_time=self.turn_time.value(),
                max_speed=self.max_speed.value(),
            )
            servo = ServoSpecification(
                rated_torque=self.servo_torque.value(),
                shaft_diameter=self.shaft_d.value(),
            )
            material = get_material(self.material.currentText())
            defaults = load_defaults()
            defaults["geometry_constraints"]["max_span_over_diameter"] = (
                self.max_span_over_d.value()
            )
            airfoil = self.airfoil.currentText()
            airfoil_name = None if airfoil == "(auto)" else airfoil
            geom_override = None
            if self.override_dims_cb.isChecked():
                tip = (
                    self.opt_tip_chord.value()
                    if self.opt_tip_enable.isChecked()
                    else None
                )
                if tip is not None and tip > self.opt_root_chord.value():
                    QMessageBox.warning(
                        self, "Input", "Tip chord cannot exceed root chord."
                    )
                    return
                geom_override = GeometryOverride(
                    root_chord_m=self.opt_root_chord.value(),
                    span_m=self.opt_span.value(),
                    tip_chord_m=tip,
                )
            self.status_label.setText("Running…")
            QApplication.processEvents()
            result = run_design_pipeline(
                vehicle,
                mission,
                material=material,
                servo=servo,
                defaults=defaults,
                airfoil_name=airfoil_name,
                geometry_override=geom_override,
                run_sensitivity=self.sens_cb.isChecked(),
                run_optimization=self.opt_cb.isChecked(),
            )
            self._last_result = result
            self._show_result(result)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Design failed", str(exc))
            self.status_label.setText("Error")

    def _show_result(self, r: DesignResult) -> None:
        from auv_fin_design.domain.validation.design_diagnosis import diagnose_design

        diagnosis = diagnose_design(r)
        status = "PASSED" if diagnosis.passed else f"FAILED ({diagnosis.failure_count} violation(s))"
        color = "#1b7f3a" if diagnosis.passed else "#b00020"
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color};")
        hv = r.hydro_validation
        g = r.geometry
        lines = [
            *diagnosis.format_lines(),
            "",
            f"Airfoil: {r.airfoil_name}",
            f"Material: {r.material_name}",
            "",
            *format_fin_dimensions_lines(g),
        ]
        cp = r.center_of_pressure
        lines += [
            "",
            "--- Dynamic Center of Pressure (strip Cp integration) ---",
            f"x_cp / MAC from LE→TE: {cp.x_cp_le_frac:.4f}  "
            f"({cp.x_cp_from_le_m:.6f} m = {cp.x_cp_from_le_m*1000:.2f} mm)",
            f"x_cp hinge frame:   {cp.x_cp_hinge_m:.6f} m "
            f"(= {cp.x_cp_hinge_m*1000:.2f} mm; hinge at 0; LE+)",
            f"y_cp: {cp.y_cp_m*1000:.2f} mm",
            f"z_cp from root:     {cp.z_cp_m:.6f} m "
            f"(= {cp.z_cp_m*1000:.2f} mm)",
            f"Hinge arm / moment: {cp.hinge_arm_m*1000:.2f} mm / {cp.hinge_moment_nm:.4f} N·m",
            f"Integrated lift (strips): {cp.total_lift_n:.4f} N",
            f"Verification: {cp.verification.status} — {cp.verification.message}",
            f"  QC estimate x_cp/c={cp.verification.x_cp_c_quarter_chord:.4f}",
            f"  Cm/CL estimate x_cp/c={cp.verification.x_cp_c_cm_cl:.4f}",
            f"Note: {cp.note}",
        ]
        md = r.maneuver_deflection or cp.deflection
        if md is not None:
            lines += [
                "",
                "--- Max Deflection for Maneuver (per fin, α=δ) ---",
                f"CL required: {md.cl_required:.4f}",
                f"delta_required: {md.delta_required_deg:.3f} deg",
                f"delta_max_usable (stall−margin): {md.delta_max_usable_deg:.3f} deg",
                f"delta_margin: {md.delta_margin_deg:.3f} deg",
                f"Sufficient: {'YES' if md.sufficient else 'NO'}",
            ]
        lines += [
            "",
            "--- Shaft Fit at Hinge (25% chord) ---",
            f"Root chord: {r.shaft_fit.root_chord_m:.6f} m "
            f"(= {r.shaft_fit.root_chord_m*1000:.2f} mm)",
            f"Airfoil width at 25%c: {r.shaft_fit.thickness_at_hinge_m*1000:.2f} mm",
            f"Shaft diameter: {r.shaft_fit.shaft_diameter_m*1000:.2f} mm",
            f"Required (≥{r.shaft_fit.clearance_factor:.2f}×shaft): "
            f"{r.shaft_fit.required_thickness_m*1000:.2f} mm",
            f"Radial clearance each side: {r.shaft_fit.radial_clearance_m*1000:.2f} mm",
            f"Fits: {'YES' if r.shaft_fit.fits else 'NO'} — {r.shaft_fit.message}",
            "",
            "--- Control ---",
            f"r_target [rad/s]: {r.control_req.r_target:.5f}",
            f"r_dot [rad/s^2]: {r.control_req.r_dot:.5f}",
            f"M_transient [N·m]: {r.control_req.M_transient:.4f}",
            f"M_steady [N·m]: {r.control_req.M_steady:.4f}",
            f"M_design [N·m]: {r.control_req.M_design:.4f}",
            f"Lift / fin [N]: {r.allocation.lift_per_fin:.4f}",
            f"Lever arm [m]: {r.allocation.lever_arm:.4f} "
            f"(= {r.allocation.lever_arm*1000:.2f} mm)",
            f"Force station x [m]: {getattr(r.allocation, 'force_station_x_m', float('nan')):.4f}",
            "",
            "--- Hydrodynamics ---",
            f"Re_L: {r.hydro.re_length:.3e}",
            f"q [Pa]: {r.hydro.dynamic_pressure:.2f}",
            f"Hull drag [N]: {r.hydro.drag_total_hull:.4f}",
            f"Flow regime: {r.hydro.flow_regime}",
            "",
            "--- Hydro Validation ---",
            f"Actual / required lift [N]: {hv.actual_lift_N:.4f} / {hv.required_lift_N:.4f}",
            f"Lift margin: {hv.lift_margin:.3f}",
            f"Authority margin: {hv.authority_margin:.3f}",
            f"Stall margin [deg]: {hv.stall_margin_deg:.2f}",
            f"Cavitation σ: {hv.cavitation_number:.2f}  risk={hv.cavitation_risk}",
            f"L/D: {hv.lift_to_drag:.2f}",
            f"Validation OK: {hv.overall_ok}",
            "",
            "--- Aero ---",
            f"alpha [deg]: {r.aero.alpha_deg:.3f}",
            f"CL / CD: {r.aero.cl:.4f} / {r.aero.cd_total:.4f}",
            f"Stall alpha [deg]: {r.aero.stall_alpha_deg:.2f}",
            "",
            "--- Structure ---",
            f"FoS cruise / agg / emerg: "
            f"{r.structure_cruise.fos_yield:.2f} / "
            f"{r.structure_aggressive.fos_yield:.2f} / "
            f"{r.structure_emergency.fos_yield:.2f}",
            f"Shear / von Mises [Pa]: "
            f"{r.structure_aggressive.shear_stress:.3e} / "
            f"{r.structure_aggressive.combined_von_mises:.3e}",
            f"Tip deflection [m]: {r.structure_aggressive.tip_deflection:.5f} "
            f"(= {r.structure_aggressive.tip_deflection*1000:.2f} mm)",
            f"Tip twist [deg]: {r.structure_aggressive.tip_twist_deg:.4f}",
            "",
            "--- Servo / Shaft ---",
            f"Servo util: {r.servo_result.utilization:.3f}",
            f"Hinge moment [N·m]: {r.servo_result.hinge_moment:.4f}",
            f"Shaft FoS: {r.servo_result.shaft_fos:.2f}",
            f"Bearing load [N]: {r.servo_result.bearing_radial_load:.3f}",
            f"Actuation time [s]: {r.servo_result.actuation_time_s:.3f}",
            f"Waterproofing: {r.servo_result.waterproofing_note}",
            "",
            "--- Manufacturing ---",
            f"Process: {r.manufacturing.process}",
            f"Orientation: {r.manufacturing.orientation}",
            f"Infill: {r.manufacturing.infill_percent}%",
            f"Printable: {r.manufacturing.printable}",
            *[f"  · {n}" for n in r.manufacturing.notes],
            "",
            "--- Warnings (non-blocking / informational) ---",
            *(r.warnings or ["(none)"]),
        ]
        if r.sensitivity is not None:
            lines += ["", "--- Sensitivity (±10%) ---"]
            for p in r.sensitivity.points:
                lines.append(
                    f"{p.parameter} {p.perturbation:+.0%}: "
                    f"ΔM={p.delta_M_frac:+.2%}  Δspan={p.delta_span_frac:+.2%}  "
                    f"{'OK' if p.passed else 'FAIL'}"
                )
        if r.optimization is not None:
            lines += ["", "--- Optimization ---", r.optimization.message]
            if r.optimization.best_params:
                lines.append(f"Best params: {r.optimization.best_params}")
                lines.append(
                    f"Best drag/mass: {r.optimization.best_drag} / {r.optimization.best_mass}"
                )
        lines += ["", "--- Equation IDs ---", ", ".join(r.equation_ids)]
        self.results.setPlainText("\n".join(lines))

    def _export_report(self) -> None:
        if self._last_result is None:
            QMessageBox.information(self, "Export", "Run a design first.")
            return
        from auv_fin_design.domain.reporting.export import write_all_reports

        paths = write_all_reports(self._last_result, repo_root() / "reports")
        msg = "\n".join(f"{k}: {v}" for k, v in paths.items())
        QMessageBox.information(self, "Export", f"Wrote:\n{msg}")

    def _export_bundle(self) -> None:
        if self._last_result is None:
            QMessageBox.information(self, "Export", "Run a design first.")
            return
        from auv_fin_design.adapters.export_bundle import export_simulation_bundle

        paths = export_simulation_bundle(
            self._last_result, repo_root() / "exports" / "sim_bundle"
        )
        msg = "\n".join(f"{k}: {v}" for k, v in paths.items())
        QMessageBox.information(
            self,
            "Export",
            f"Wrote STL, STEP wire, Fusion params, Gazebo SDF, ROS2 URDF:\n{msg}",
        )


def run_app() -> int:
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("AUV Fin Design Suite")
    win = MainWindow()
    win.show()
    return app.exec()
