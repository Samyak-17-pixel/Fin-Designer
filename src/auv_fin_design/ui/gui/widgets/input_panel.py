"""Design input form — grouped, collapsible, live validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from auv_fin_design.application.pipeline import GeometryOverride
from auv_fin_design.domain.constants.materials import get_material, list_materials
from auv_fin_design.domain.servo.analysis import ServoSpecification
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel
from auv_fin_design.infrastructure.config.loader import load_defaults, repo_root
from auv_fin_design.ui.gui.widgets.common import CollapsibleGroup


@dataclass
class DesignInputs:
    vehicle: VehicleModel
    mission: MissionModel
    material: Any
    servo: ServoSpecification
    defaults: dict[str, Any]
    airfoil_name: str | None
    geometry_override: GeometryOverride | None
    run_sensitivity: bool
    run_optimization: bool


class InputPanel(QWidget):
    """Grouped inputs with live validation hints."""

    validation_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._defaults = load_defaults()
        layout = QVBoxLayout(self)
        self.hint_label = QLabel("")
        self.hint_label.setObjectName("InputHint")
        self.hint_label.setWordWrap(True)
        layout.addWidget(self._build_vehicle())
        layout.addWidget(self._build_mission())
        layout.addWidget(self._build_servo())
        layout.addWidget(self._build_fin())
        layout.addWidget(self._build_advanced())
        layout.addWidget(self._build_optional_geometry())
        layout.addWidget(self.hint_label)
        layout.addStretch(1)

        for w in (
            self.length,
            self.diameter,
            self.mass,
            self.speed,
            self.max_speed,
            self.turn_radius,
            self.turn_time,
            self.servo_torque,
            self.shaft_d,
        ):
            w.valueChanged.connect(self._refresh_hints)
        self.water.currentTextChanged.connect(lambda _: self._refresh_hints())
        self._refresh_hints()

    def _spin(
        self,
        value: float,
        minimum: float,
        maximum: float,
        decimals: int = 4,
        step: float = 0.01,
        tip: str = "",
    ) -> QDoubleSpinBox:
        w = QDoubleSpinBox()
        w.setRange(minimum, maximum)
        w.setDecimals(decimals)
        w.setSingleStep(step)
        w.setValue(value)
        if tip:
            w.setToolTip(tip)
        return w

    def _build_vehicle(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Vehicle")
        form = QFormLayout()
        self.length = self._spin(1.35, 0.1, 20.0, 3, 0.01, "Hull length L [m]")
        self.diameter = self._spin(0.1685, 0.01, 2.0, 4, 0.001, "Hull diameter D [m]")
        self.mass = self._spin(24.0, 0.1, 5000.0, 2, 0.1, "Vehicle mass [kg]")
        self.water = QComboBox()
        self.water.addItems(["freshwater", "seawater"])
        self.water.setToolTip("Fluid for density and cavitation checks")
        form.addRow("Length L [m]", self.length)
        form.addRow("Diameter D [m]", self.diameter)
        form.addRow("Mass m [kg]", self.mass)
        form.addRow("Water", self.water)
        box.add_layout(form)
        return box

    def _build_mission(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Mission")
        form = QFormLayout()
        self.speed = self._spin(1.5, 0.1, 20.0, 3, 0.1, "Design / cruise speed [m/s]")
        self.max_speed = self._spin(2.0, 0.1, 30.0, 3, 0.1, "Must be ≥ design speed")
        self.turn_radius = self._spin(6.0, 0.5, 200.0, 2, 0.5, "Desired turn radius [m]")
        self.turn_time = self._spin(30.0, 0.5, 600.0, 1, 1.0, "Turn establishment time [s]")
        form.addRow("Design speed [m/s]", self.speed)
        form.addRow("Max speed [m/s]", self.max_speed)
        form.addRow("Turn radius [m]", self.turn_radius)
        form.addRow("Turn establish [s]", self.turn_time)
        box.add_layout(form)
        return box

    def _build_servo(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Servo & Shaft")
        form = QFormLayout()
        self.servo_torque = self._spin(3.481, 0.1, 50.0, 3, 0.1, "Rated continuous torque [N·m]")
        self.shaft_d = self._spin(0.006, 0.001, 0.05, 4, 0.001, "Shaft outer diameter [m]")
        form.addRow("Servo torque [N·m]", self.servo_torque)
        form.addRow("Shaft diameter [m]", self.shaft_d)
        box.add_layout(form)
        return box

    def _build_fin(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Fin & Material")
        form = QFormLayout()
        self.material = QComboBox()
        self.material.addItems(list_materials())
        self.material.setCurrentText("PLA")
        self.fin_root_frac = self._spin(0.92, 0.5, 0.99, 3, 0.01, "Aft fin root LE station / L")
        self.max_span_over_d = self._spin(
            float(self._defaults["geometry_constraints"]["max_span_over_diameter"]),
            0.1,
            2.0,
            3,
            0.05,
            "Packaging limit on span / diameter",
        )
        self.airfoil = QComboBox()
        self.airfoil.addItem("(auto)")
        data = repo_root() / "data"
        if data.exists():
            for p in sorted(data.iterdir()):
                if p.is_dir():
                    self.airfoil.addItem(p.name)
        form.addRow("Material", self.material)
        form.addRow("Fin root LE / L", self.fin_root_frac)
        form.addRow("Max span / D", self.max_span_over_d)
        form.addRow("Airfoil", self.airfoil)
        box.add_layout(form)
        return box

    def _build_advanced(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Analysis Options")
        box.setChecked(False)
        self.sens_cb = QCheckBox("Run ±10% sensitivity sweep")
        self.sens_cb.setChecked(True)
        self.opt_cb = QCheckBox("Run NSGA-II optimization (slow — needs pymoo)")
        box.add_widget(self.sens_cb)
        box.add_widget(self.opt_cb)
        return box

    def _build_optional_geometry(self) -> CollapsibleGroup:
        box = CollapsibleGroup("Fixed Fin Dimensions (override)")
        box.setChecked(False)
        form = QFormLayout()
        self.override_dims_cb = QCheckBox("Use fixed root chord & span")
        self.override_dims_cb.toggled.connect(self._toggle_dim_overrides)
        self.opt_root_chord = self._spin(0.10, 0.01, 2.0, 4, 0.005)
        self.opt_span = self._spin(0.10, 0.01, 1.0, 4, 0.005)
        self.opt_tip_chord = self._spin(0.05, 0.005, 2.0, 4, 0.005)
        self.opt_tip_enable = QCheckBox("Also fix tip chord")
        self.opt_tip_enable.toggled.connect(
            lambda on: self.opt_tip_chord.setEnabled(on and self.override_dims_cb.isChecked())
        )
        form.addRow(self.override_dims_cb)
        form.addRow("Root chord [m]", self.opt_root_chord)
        form.addRow("Span [m]", self.opt_span)
        form.addRow(self.opt_tip_enable, self.opt_tip_chord)
        hint = QLabel("Leave off to auto-size from required lift.")
        hint.setWordWrap(True)
        form.addRow(hint)
        box.add_layout(form)
        self._toggle_dim_overrides(False)
        return box

    def _toggle_dim_overrides(self, enabled: bool) -> None:
        self.opt_root_chord.setEnabled(enabled)
        self.opt_span.setEnabled(enabled)
        self.opt_tip_enable.setEnabled(enabled)
        self.opt_tip_chord.setEnabled(enabled and self.opt_tip_enable.isChecked())
        self._refresh_hints()

    def _refresh_hints(self) -> None:
        msgs: list[str] = []
        L, D = self.length.value(), self.diameter.value()
        msgs.append(f"Slenderness L/D = {L / D:.1f}")
        r_yaw = self.speed.value() / self.turn_radius.value()
        msgs.append(f"Design yaw rate r = V/R = {r_yaw:.4f} rad/s")
        if self.max_speed.value() < self.speed.value():
            self.hint_label.setObjectName("InputHintError")
            self.hint_label.setText("⚠ Max speed must be ≥ design speed.")
            self.validation_changed.emit("Max speed must be ≥ design speed.")
            return
        if self.override_dims_cb.isChecked() and self.opt_tip_enable.isChecked():
            if self.opt_tip_chord.value() > self.opt_root_chord.value():
                self.hint_label.setObjectName("InputHintError")
                self.hint_label.setText("⚠ Tip chord cannot exceed root chord.")
                self.validation_changed.emit("Tip chord cannot exceed root chord.")
                return
        self.hint_label.setObjectName("InputHint")
        self.hint_label.setText("  ·  ".join(msgs))
        self.validation_changed.emit("")

    def load_golden(self) -> None:
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
        self._refresh_hints()

    def validate(self) -> str | None:
        if self.max_speed.value() < self.speed.value():
            return "Maximum speed must be ≥ design speed."
        if self.override_dims_cb.isChecked() and self.opt_tip_enable.isChecked():
            if self.opt_tip_chord.value() > self.opt_root_chord.value():
                return "Tip chord cannot exceed root chord."
        return None

    def gather(self) -> DesignInputs:
        defaults = load_defaults()
        defaults["geometry_constraints"]["max_span_over_diameter"] = self.max_span_over_d.value()
        airfoil = self.airfoil.currentText()
        geom_override = None
        if self.override_dims_cb.isChecked():
            tip = self.opt_tip_chord.value() if self.opt_tip_enable.isChecked() else None
            geom_override = GeometryOverride(
                root_chord_m=self.opt_root_chord.value(),
                span_m=self.opt_span.value(),
                tip_chord_m=tip,
            )
        return DesignInputs(
            vehicle=VehicleModel(
                length=self.length.value(),
                diameter=self.diameter.value(),
                mass=self.mass.value(),
                water=self.water.currentText(),  # type: ignore[arg-type]
                fin_root_le_fraction_of_length=self.fin_root_frac.value(),
            ),
            mission=MissionModel(
                design_speed=self.speed.value(),
                turning_radius=self.turn_radius.value(),
                turn_establishment_time=self.turn_time.value(),
                max_speed=self.max_speed.value(),
            ),
            material=get_material(self.material.currentText()),
            servo=ServoSpecification(
                rated_torque=self.servo_torque.value(),
                shaft_diameter=self.shaft_d.value(),
            ),
            defaults=defaults,
            airfoil_name=None if airfoil == "(auto)" else airfoil,
            geometry_override=geom_override,
            run_sensitivity=self.sens_cb.isChecked(),
            run_optimization=self.opt_cb.isChecked(),
        )
