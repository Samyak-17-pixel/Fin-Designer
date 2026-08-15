"""Servo / shaft / hinge analysis — EQ-AERO-007, EQ-SRV-*."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field


class ServoSpecification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rated_torque: float = Field(..., gt=0, description="N·m")
    shaft_diameter: float = Field(..., gt=0, description="m")
    max_rotation_deg: float = Field(45.0, gt=0)
    efficiency: float = Field(1.0, gt=0, le=1.0)
    max_speed_deg_s: float = Field(60.0, gt=0, description="No-load angular speed")


class ServoResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hinge_moment: float
    torque_required: float
    utilization: float
    continuous_ok: bool
    peak_ok: bool
    shaft_shear_stress: float
    shaft_fos: float
    shaft_ok: bool
    bearing_radial_load: float
    bearing_ok: bool
    actuation_time_s: float
    speed_ok: bool
    waterproofing_note: str
    failure_modes: tuple[str, ...] = ()
    equation_ids: tuple[str, ...] = ()


def hinge_moment(q: float, area: float, mac: float, cm: float) -> float:
    """EQ-AERO-007 — H = q S c Cm."""
    return q * area * mac * cm


def analyze_servo(
    *,
    q: float,
    area: float,
    mac: float,
    cm: float,
    servo: ServoSpecification,
    lift: float = 0.0,
    util_continuous_limit: float = 0.70,
    util_peak_limit: float = 0.90,
    peak_case: bool = False,
    shaft_allowable_pa: float = 150e6,  # stainless sleeve typical
    required_deflection_deg: float = 0.0,
    hinge_moment_override: float | None = None,
) -> ServoResult:
    h = (
        float(hinge_moment_override)
        if hinge_moment_override is not None
        else hinge_moment(q, area, mac, cm)
    )
    t_req = abs(h) / servo.efficiency
    util = t_req / servo.rated_torque
    continuous_ok = util <= util_continuous_limit
    peak_ok = util <= util_peak_limit

    # Shaft torsion τ = 16 T / (π d³)
    d = servo.shaft_diameter
    tau = 16.0 * t_req / (math.pi * d**3) if d > 0 else float("inf")
    shaft_fos = shaft_allowable_pa / tau if tau > 0 else float("inf")
    shaft_ok = shaft_fos >= 2.0

    # Bearing radial ≈ resultant hydrodynamic force at root
    bearing_load = math.hypot(lift, abs(h) / max(mac * 0.25, 1e-6) * 0.0) + lift
    bearing_ok = bearing_load < 500.0  # N — soft V1 check for hobby bearings

    # Time to slew to required deflection
    act_time = abs(required_deflection_deg) / servo.max_speed_deg_s if servo.max_speed_deg_s > 0 else 0.0
    speed_ok = act_time <= 2.0 or required_deflection_deg == 0.0

    modes: list[str] = []
    if not continuous_ok:
        modes.append("Servo continuous torque exceeded")
    if not shaft_ok:
        modes.append("Shaft shear FoS < 2")
    if not bearing_ok:
        modes.append("Bearing radial load high")
    if not speed_ok:
        modes.append("Actuation too slow for maneuver")

    return ServoResult(
        hinge_moment=h,
        torque_required=t_req,
        utilization=util,
        continuous_ok=continuous_ok,
        peak_ok=peak_ok,
        shaft_shear_stress=tau,
        shaft_fos=shaft_fos,
        shaft_ok=shaft_ok,
        bearing_radial_load=bearing_load,
        bearing_ok=bearing_ok,
        actuation_time_s=act_time,
        speed_ok=speed_ok,
        waterproofing_note="Use IP67 servo or oil-compensated housing; shaft O-ring seal required",
        failure_modes=tuple(modes),
        equation_ids=("EQ-AERO-007", "EQ-SRV-001", "EQ-SRV-002", "EQ-SRV-003"),
    )
