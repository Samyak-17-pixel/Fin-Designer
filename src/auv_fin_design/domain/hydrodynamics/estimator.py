"""Hydrodynamic estimator — Chapter 3.2 / EQ-HYD-*."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.hydrodynamics.yaw_damping import (
    YawDampingCoefficients,
    estimate_yaw_damping_coefficients,
)
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel

FlowRegime = Literal["laminar", "transitional", "turbulent"]


class HydrodynamicModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    speed: float
    re_length: float
    re_diameter: float
    flow_regime: FlowRegime
    dynamic_pressure: float
    cf_ittc: float
    cd_frontal: float
    drag_friction: float
    drag_total_hull: float
    X_udot: float
    Y_vdot: float
    Z_wdot: float
    K_pdot: float
    M_qdot: float
    N_rdot: float
    yaw_damping: YawDampingCoefficients
    design_yaw_rate_rad_s: float = Field(
        ..., description="Operating yaw rate V/R used for coefficient calibration"
    )
    design_lateral_speed_mps: float = Field(
        0.0, description="Sway velocity v at design evaluation (zero sideslip V1)"
    )
    wake_fraction: float = 0.0
    cd_cross: float = 1.0
    equation_ids: tuple[str, ...] = ()


def classify_flow_regime(re_l: float) -> FlowRegime:
    """EQ-HYD-003"""
    if re_l < 5.0e5:
        return "laminar"
    if re_l <= 3.0e6:
        return "transitional"
    return "turbulent"


def ittc_1957_cf(re_l: float) -> float:
    """EQ-HYD-005 — ITTC-1957 friction line."""
    if re_l <= 1.0e5:
        # Avoid singular/nonphysical log argument for very low Re; clamp for V1
        re_l = 1.0e5
    return 0.075 / (math.log10(re_l) - 2.0) ** 2


def hoerner_streamlined_cd_frontal(cf: float, sw: float, af: float, d: float, l: float) -> float:
    """EQ-HYD-008 — Hoerner streamlined body Cd on frontal area."""
    slenderness_inv = d / l
    form = 1.0 + 1.5 * slenderness_inv**1.5 + 7.0 * slenderness_inv**3
    return cf * (sw / af) * form


def estimate_hydrodynamics(
    vehicle: VehicleModel,
    mission: MissionModel,
    *,
    operating_yaw_rate: float | None = None,
    crossflow_cd: float = 1.0,
    axial_added_mass_factor: float = 0.1,
    yaw_damping_cfg: dict[str, float] | None = None,
) -> HydrodynamicModel:
    """Build HydrodynamicModel from vehicle + mission.

    Equations: EQ-HYD-001 … EQ-HYD-017.
    """
    fluid = vehicle.fluid
    v = mission.speed
    rho = fluid.density
    nu = fluid.kinematic_viscosity
    L = vehicle.length
    D = vehicle.diameter
    R = vehicle.radius

    re_l = v * L / nu  # EQ-HYD-001
    re_d = v * D / nu  # EQ-HYD-002
    regime = classify_flow_regime(re_l)
    q = 0.5 * rho * v**2  # EQ-HYD-004

    cf = ittc_1957_cf(re_l)
    cd_af = hoerner_streamlined_cd_frontal(
        cf, vehicle.wetted_area, vehicle.frontal_area, D, L
    )
    df = q * cf * vehicle.wetted_area  # EQ-HYD-006 (friction component)
    dh = q * cd_af * vehicle.frontal_area  # EQ-HYD-009

    # Added mass EQ-HYD-010..013
    y_vdot = rho * math.pi * R**2 * L
    x_udot = axial_added_mass_factor * rho * vehicle.volume
    n_rdot = rho * math.pi * R**2 * L**3 / 12.0

    # Fossen polynomial yaw damping EQ-HYD-018 (coefficients EQ-HYD-015/019)
    yaw_coeffs, r_op, v_design = estimate_yaw_damping_coefficients(
        rho=rho,
        diameter_m=D,
        length_m=L,
        design_speed_mps=v,
        turning_radius_m=mission.turning_radius,
        crossflow_cd=crossflow_cd,
        x_cg_m=vehicle.x_cg,
        yaw_cfg=yaw_damping_cfg,
    )
    if operating_yaw_rate is not None:
        r_op = operating_yaw_rate

    return HydrodynamicModel(
        speed=v,
        re_length=re_l,
        re_diameter=re_d,
        flow_regime=regime,
        dynamic_pressure=q,
        cf_ittc=cf,
        cd_frontal=cd_af,
        drag_friction=df,
        drag_total_hull=dh,
        X_udot=x_udot,
        Y_vdot=y_vdot,
        Z_wdot=y_vdot,
        K_pdot=0.0,
        M_qdot=n_rdot,
        N_rdot=n_rdot,
        yaw_damping=yaw_coeffs,
        design_yaw_rate_rad_s=r_op,
        design_lateral_speed_mps=v_design,
        wake_fraction=0.0,
        cd_cross=crossflow_cd,
        equation_ids=(
            "EQ-HYD-001",
            "EQ-HYD-002",
            "EQ-HYD-003",
            "EQ-HYD-004",
            "EQ-HYD-005",
            "EQ-HYD-006",
            "EQ-HYD-008",
            "EQ-HYD-009",
            "EQ-HYD-010",
            "EQ-HYD-011",
            "EQ-HYD-012",
            "EQ-HYD-013",
            "EQ-HYD-014",
            "EQ-HYD-015",
            "EQ-HYD-017",
            "EQ-HYD-018",
            "EQ-HYD-019",
            "EQ-HYD-020",
        ),
    )
