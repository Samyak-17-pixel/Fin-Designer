"""Helmbold finite-wing correction wrapper — independent of CoP solver."""

from __future__ import annotations

from auv_fin_design.domain.airfoil.finite_wing import helmbold_cl_alpha


def helmbold_lift_slope(cl_alpha_2d_per_rad: float, aspect_ratio: float) -> float:
    """EQ-AERO-001 — Helmbold low-AR lift-curve slope [1/rad].

    Purpose: Convert 2D polar slope to 3D before strip α / CL usage.
    Reference: Helmbold (1942); existing domain.airfoil.finite_wing.
    """
    return helmbold_cl_alpha(cl_alpha_2d_per_rad, aspect_ratio)
