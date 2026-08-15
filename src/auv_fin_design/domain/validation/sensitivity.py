"""Sensitivity analysis — SRDS §2.14 / 3.3.12 / 3.10.10."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict

from auv_fin_design.domain.constants.materials import MaterialProperties
from auv_fin_design.domain.servo.analysis import ServoSpecification
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


class SensitivityPoint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    parameter: str
    perturbation: float
    M_design_Nm: float
    span_m: float
    area_m2: float
    CD: float
    passed: bool
    delta_M_frac: float
    delta_span_frac: float


class SensitivityReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    baseline_M_design_Nm: float
    baseline_span_m: float
    points: tuple[SensitivityPoint, ...]
    equation_ids: tuple[str, ...] = ("EQ-SENS-001",)


def run_sensitivity(
    vehicle: VehicleModel,
    mission: MissionModel,
    *,
    material: MaterialProperties | None = None,
    servo: ServoSpecification | None = None,
    defaults: dict[str, Any] | None = None,
    airfoil_name: str | None = None,
    perturbations: tuple[float, ...] = (-0.10, 0.10),
) -> SensitivityReport:
    """±10% sweeps on mass, speed, turning radius (SRDS freeze)."""
    from auv_fin_design.application.pipeline import run_design_pipeline

    base = run_design_pipeline(
        vehicle,
        mission,
        material=material,
        servo=servo,
        defaults=defaults,
        airfoil_name=airfoil_name,
        run_sensitivity=False,
        run_optimization=False,
    )
    points: list[SensitivityPoint] = []

    sweeps: list[tuple[str, Callable[[float], tuple[VehicleModel, MissionModel]]]] = [
        (
            "mass",
            lambda frac: (
                vehicle.model_copy(update={"mass": vehicle.mass * (1.0 + frac)}),
                mission,
            ),
        ),
        (
            "design_speed",
            lambda frac: (
                vehicle,
                mission.model_copy(update={"design_speed": mission.design_speed * (1.0 + frac)}),
            ),
        ),
        (
            "turning_radius",
            lambda frac: (
                vehicle,
                mission.model_copy(
                    update={"turning_radius": mission.turning_radius * (1.0 + frac)}
                ),
            ),
        ),
    ]

    for name, builder in sweeps:
        for frac in perturbations:
            v2, m2 = builder(frac)
            r = run_design_pipeline(
                v2,
                m2,
                material=material,
                servo=servo,
                defaults=deepcopy(defaults) if defaults else None,
                airfoil_name=airfoil_name,
                run_sensitivity=False,
                run_optimization=False,
            )
            points.append(
                SensitivityPoint(
                    parameter=name,
                    perturbation=frac,
                    M_design_Nm=r.control_req.M_design,
                    span_m=r.geometry.span,
                    area_m2=r.geometry.area,
                    CD=r.aero.cd_total,
                    passed=r.passed,
                    delta_M_frac=(r.control_req.M_design - base.control_req.M_design)
                    / base.control_req.M_design,
                    delta_span_frac=(r.geometry.span - base.geometry.span)
                    / max(base.geometry.span, 1e-12),
                )
            )

    return SensitivityReport(
        baseline_M_design_Nm=base.control_req.M_design,
        baseline_span_m=base.geometry.span,
        points=tuple(points),
    )
