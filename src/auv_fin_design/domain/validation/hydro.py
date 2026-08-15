"""Hydrodynamic validation module — SRDS Chapter 3.7."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from auv_fin_design.domain.airfoil.finite_wing import FiniteWingPerformance
from auv_fin_design.domain.control.allocation import ControlAllocationModel
from auv_fin_design.domain.control.maneuvering import ControlRequirementModel
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry
from auv_fin_design.domain.hydrodynamics.estimator import HydrodynamicModel


class HydrodynamicValidationModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    actual_lift_N: float
    required_lift_N: float
    lift_margin: float  # (actual - required) / required
    actual_drag_N: float
    available_control_moment_Nm: float
    required_control_moment_Nm: float
    authority_margin: float
    stall_margin_deg: float
    stall_ok: bool
    deflection_deg: float
    max_deflection_deg: float
    deflection_ok: bool
    cavitation_number: float
    cavitation_risk: bool
    lift_to_drag: float
    control_authority_ok: bool
    lift_ok: bool
    overall_ok: bool
    messages: tuple[str, ...] = ()
    equation_ids: tuple[str, ...] = ("EQ-HYD-VAL-001", "EQ-HYD-VAL-002", "EQ-HYD-VAL-003")


def validate_hydrodynamics(
    *,
    hydro: HydrodynamicModel,
    aero: FiniteWingPerformance,
    geometry: CandidateFinGeometry,
    allocation: ControlAllocationModel,
    control_req: ControlRequirementModel,
    max_deflection_deg: float = 45.0,
    stall_margin_required_deg: float = 5.0,
    vapor_pressure_pa: float = 2339.0,  # water ~20 C
    depth_m: float = 1.0,
    gravity: float = 9.80665,
    density: float = 998.2,
) -> HydrodynamicValidationModel:
    """Validate fin hydro performance against control and stall requirements."""
    q = hydro.dynamic_pressure
    actual_lift = q * geometry.area * aero.cl
    actual_drag = q * geometry.area * aero.cd_total
    required_lift = allocation.lift_per_fin
    lift_margin = (actual_lift - required_lift) / required_lift if required_lift > 0 else 0.0

    # Available yaw moment from achieved lift (same projection as allocation)
    available_moment = (
        allocation.n_fins
        * actual_lift
        * allocation.lever_arm
        * allocation.yaw_projection_factor
    )
    authority_margin = (
        (available_moment - control_req.M_design) / control_req.M_design
        if control_req.M_design > 0
        else 0.0
    )

    stall_margin = aero.stall_alpha_deg - aero.alpha_deg
    stall_ok = (not aero.stalled) and stall_margin >= stall_margin_required_deg - 0.1
    deflection_ok = abs(aero.alpha_deg) <= max_deflection_deg + 1e-9

    # Cavitation number σ = (p∞ - pv) / q ; p∞ = patm + ρgh
    p_inf = 101325.0 + density * gravity * depth_m
    sigma = (p_inf - vapor_pressure_pa) / q if q > 0 else float("inf")
    cavitation_risk = sigma < 1.5  # conservative preliminary threshold

    lift_ok = lift_margin >= -0.01  # allow 1% numerical tolerance
    authority_ok = authority_margin >= -0.01
    messages: list[str] = []
    if not lift_ok:
        messages.append(f"Insufficient lift: margin={lift_margin:.3f}")
    if not authority_ok:
        messages.append(f"Insufficient control authority: margin={authority_margin:.3f}")
    if not stall_ok:
        messages.append(f"Stall margin {stall_margin:.2f}° below required {stall_margin_required_deg}°")
    if not deflection_ok:
        messages.append(f"Deflection {aero.alpha_deg:.2f}° exceeds max {max_deflection_deg}°")
    if cavitation_risk:
        messages.append(f"Cavitation risk: σ={sigma:.2f} < 1.5")

    overall = lift_ok and authority_ok and stall_ok and deflection_ok and not cavitation_risk
    return HydrodynamicValidationModel(
        actual_lift_N=actual_lift,
        required_lift_N=required_lift,
        lift_margin=lift_margin,
        actual_drag_N=actual_drag,
        available_control_moment_Nm=available_moment,
        required_control_moment_Nm=control_req.M_design,
        authority_margin=authority_margin,
        stall_margin_deg=stall_margin,
        stall_ok=stall_ok,
        deflection_deg=aero.alpha_deg,
        max_deflection_deg=max_deflection_deg,
        deflection_ok=deflection_ok,
        cavitation_number=sigma,
        cavitation_risk=cavitation_risk,
        lift_to_drag=aero.cl / aero.cd_total if aero.cd_total > 0 else 0.0,
        control_authority_ok=authority_ok,
        lift_ok=lift_ok,
        overall_ok=overall,
        messages=tuple(messages),
    )
