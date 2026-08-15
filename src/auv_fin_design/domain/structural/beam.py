"""Structural cantilever beam analysis — EQ-STR-*."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict

from auv_fin_design.domain.constants.materials import MaterialProperties
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


class StructuralResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    load_case: str
    lift: float
    root_shear: float
    root_moment: float
    root_torque: float
    I_root: float
    J_root: float
    bending_stress: float
    shear_stress: float
    torsional_stress: float
    combined_von_mises: float
    tip_deflection: float
    tip_twist_deg: float
    fos_yield: float
    tip_deflection_ok: bool
    fos_ok: bool
    required_fos: float
    failure_modes: tuple[str, ...] = ()
    equation_ids: tuple[str, ...] = ()


def elliptical_section_I(chord: float, thickness: float) -> float:
    """EQ-STR-004 — Ixx = pi * c * t^3 / 64 for solid ellipse."""
    return math.pi * chord * thickness**3 / 64.0


def elliptical_section_J(chord: float, thickness: float) -> float:
    """Polar moment approx for solid ellipse: J ≈ π a b (a²+b²)/4 with a=c/2, b=t/2."""
    a = chord / 2.0
    b = thickness / 2.0
    return math.pi * a * b * (a**2 + b**2) / 4.0


def analyze_fin_structure(
    geom: CandidateFinGeometry,
    material: MaterialProperties,
    lift: float,
    *,
    load_case: str,
    required_fos: float,
    tip_deflection_limit_span_frac: float = 0.05,
    drag: float = 0.0,
    hinge_moment: float = 0.0,
) -> StructuralResult:
    """EQ-STR-002…007 plus shear, torsion, combined stress."""
    v_root = lift
    m_root = lift * geom.span / 2.0
    torque = abs(hinge_moment) if hinge_moment else abs(drag) * (geom.mac * 0.25)
    i_root = elliptical_section_I(geom.root_chord, geom.root_thickness)
    j_root = elliptical_section_J(geom.root_chord, geom.root_thickness)
    if i_root <= 0 or j_root <= 0:
        raise ValueError("Invalid section inertia")

    sigma = m_root * (geom.root_thickness / 2.0) / i_root
    # Average shear on elliptical area A = π c t / 4
    area_sect = math.pi * geom.root_chord * geom.root_thickness / 4.0
    tau_shear = (1.5 * v_root / area_sect) if area_sect > 0 else 0.0
    tau_torsion = torque * (max(geom.root_chord, geom.root_thickness) / 2.0) / j_root
    # von Mises with combined shear
    tau_tot = tau_shear + tau_torsion
    von = math.sqrt(sigma**2 + 3.0 * tau_tot**2)

    w = lift / geom.span
    delta = w * geom.span**4 / (8.0 * material.youngs_modulus * i_root)
    # Twist θ = T L / (G J)
    twist_rad = torque * geom.span / (material.shear_modulus * j_root)
    twist_deg = math.degrees(twist_rad)

    fos = material.yield_strength / von if von > 0 else float("inf")
    tip_ok = delta <= tip_deflection_limit_span_frac * geom.span
    fos_ok = fos >= required_fos

    modes: list[str] = []
    if not fos_ok:
        modes.append("Yield / combined stress")
    if not tip_ok:
        modes.append("Excessive tip deflection")
    if twist_deg > 5.0:
        modes.append("Excessive tip twist")

    return StructuralResult(
        load_case=load_case,
        lift=lift,
        root_shear=v_root,
        root_moment=m_root,
        root_torque=torque,
        I_root=i_root,
        J_root=j_root,
        bending_stress=sigma,
        shear_stress=tau_shear,
        torsional_stress=tau_torsion,
        combined_von_mises=von,
        tip_deflection=delta,
        tip_twist_deg=twist_deg,
        fos_yield=fos,
        tip_deflection_ok=tip_ok,
        fos_ok=fos_ok,
        required_fos=required_fos,
        failure_modes=tuple(modes),
        equation_ids=(
            "EQ-STR-002",
            "EQ-STR-003",
            "EQ-STR-004",
            "EQ-STR-005",
            "EQ-STR-006",
            "EQ-STR-007",
        ),
    )
