"""Finite-wing corrections — Helmbold + induced drag — EQ-AERO-001..005."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict

from auv_fin_design.domain.airfoil.database import AirfoilPolar


class FiniteWingPerformance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cl_alpha_2d: float
    cl_alpha_3d: float
    alpha_rad: float
    alpha_deg: float
    cl: float
    cl_max_2d: float
    stall_alpha_deg: float
    cd_profile: float
    cd_induced: float
    cd_total: float
    cm: float
    stalled: bool
    equation_ids: tuple[str, ...] = (
        "EQ-AERO-001",
        "EQ-AERO-002",
        "EQ-AERO-003",
        "EQ-AERO-004",
        "EQ-AERO-005",
    )


def helmbold_cl_alpha(cl_alpha_2d: float, aspect_ratio: float) -> float:
    """EQ-AERO-001 — Helmbold low-AR lift-curve slope [1/rad]."""
    if aspect_ratio <= 0:
        raise ValueError("aspect_ratio must be positive")
    a0 = cl_alpha_2d
    term = a0 / (math.pi * aspect_ratio)
    return a0 / (math.sqrt(1.0 + term**2) + term)


def evaluate_finite_wing(
    polar: AirfoilPolar,
    *,
    aspect_ratio: float,
    alpha_deg: float,
    oswald_e: float = 0.80,
) -> FiniteWingPerformance:
    """Build 3D performance: Helmbold CL, XFOIL Cd/Cm, induced drag."""
    a0 = polar.cl_alpha_per_rad()
    a3d = helmbold_cl_alpha(a0, aspect_ratio)
    alpha_rad = math.radians(alpha_deg)
    cl = a3d * alpha_rad  # EQ-AERO-002
    cl_max, stall_a = polar.first_local_cl_max()
    stalled = False
    if cl > cl_max:
        cl = cl_max
        stalled = True
    if abs(alpha_deg) > abs(stall_a) and alpha_deg > 0:
        stalled = True
        cl = min(cl, cl_max)

    # Profile Cd and Cm from XFOIL at geometric alpha (= deflection V1)
    pt = polar.interpolate_at_alpha(alpha_deg)
    cd_i = cl**2 / (math.pi * oswald_e * aspect_ratio)  # EQ-AERO-004
    cd = pt.cd + cd_i  # EQ-AERO-005

    return FiniteWingPerformance(
        cl_alpha_2d=a0,
        cl_alpha_3d=a3d,
        alpha_rad=alpha_rad,
        alpha_deg=alpha_deg,
        cl=cl,
        cl_max_2d=cl_max,
        stall_alpha_deg=stall_a,
        cd_profile=pt.cd,
        cd_induced=cd_i,
        cd_total=cd,
        cm=pt.cm,
        stalled=stalled,
    )


def alpha_for_required_cl(
    polar: AirfoilPolar,
    *,
    aspect_ratio: float,
    cl_required: float,
    oswald_e: float = 0.80,
) -> FiniteWingPerformance:
    """Invert Helmbold linear model for required CL; then evaluate full polar drag."""
    a0 = polar.cl_alpha_per_rad()
    a3d = helmbold_cl_alpha(a0, aspect_ratio)
    cl_max, stall_a = polar.first_local_cl_max()
    if cl_required > cl_max:
        # Cannot achieve — return stalled at stall alpha with cl_max
        return evaluate_finite_wing(polar, aspect_ratio=aspect_ratio, alpha_deg=stall_a, oswald_e=oswald_e)
    alpha_rad = cl_required / a3d
    alpha_deg = math.degrees(alpha_rad)
    return evaluate_finite_wing(polar, aspect_ratio=aspect_ratio, alpha_deg=alpha_deg, oswald_e=oswald_e)
