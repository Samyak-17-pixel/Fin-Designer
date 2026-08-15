"""Spanwise strip theory for tapered fins — EQ-COP-003 / EQ-COP-004."""

from __future__ import annotations

import numpy as np

from auv_fin_design.domain.center_of_pressure.constants import (
    DEFAULT_N_STRIPS,
    DEFAULT_Y_CP_M,
    EQ_COP_STRIP_LIFT,
    HINGE_CHORD_FRACTION,
)
from auv_fin_design.domain.center_of_pressure.cp_provider import CenterOfPressureProvider
from auv_fin_design.domain.center_of_pressure.models import StripResult
from auv_fin_design.domain.center_of_pressure.pressure_integrator import integrate_chordwise
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


def local_chord(geometry: CandidateFinGeometry, z_m: float) -> float:
    """Linear taper: c(z) = c_r + (c_t − c_r) (z/b)."""
    b = geometry.span
    eta = 0.0 if b <= 0 else float(np.clip(z_m / b, 0.0, 1.0))
    return geometry.root_chord + (geometry.tip_chord - geometry.root_chord) * eta


def build_strips(
    geometry: CandidateFinGeometry,
    *,
    provider: CenterOfPressureProvider,
    airfoil: str,
    dynamic_pressure: float,
    speed_mps: float,
    nu: float,
    alpha_deg: float,
    n_strips: int = DEFAULT_N_STRIPS,
    hinge_frac: float = HINGE_CHORD_FRACTION,
    epsrel: float = 1.0e-6,
) -> list[StripResult]:
    """Discretize span into strips; integrate local Cp; return strip loads.

    EQ-COP-003: dL = q * c(z) * cn(z) * dz
    Local Re = V * c(z) / ν. Alpha uniform along span in V1 (no twist).
    """
    if n_strips < 2:
        raise ValueError("n_strips must be >= 2")
    b = geometry.span
    edges = np.linspace(0.0, b, n_strips + 1)
    strips: list[StripResult] = []
    for i in range(n_strips):
        z0, z1 = float(edges[i]), float(edges[i + 1])
        z_c = 0.5 * (z0 + z1)
        dz = z1 - z0
        c_loc = local_chord(geometry, z_c)
        re_loc = speed_mps * c_loc / nu if nu > 0 else 1.0e5
        pd = provider.load_pressure_distribution(airfoil, re_loc, alpha_deg)
        chord_int = integrate_chordwise(pd, epsrel=epsrel)
        lift = dynamic_pressure * c_loc * chord_int.cn * dz
        # Moment about LE of strip: q * c^2 * cm_le * dz
        m_le = dynamic_pressure * (c_loc**2) * chord_int.cm_le * dz
        x_from_le = chord_int.x_cp_c * c_loc
        x_hinge = hinge_frac * c_loc - x_from_le  # LE+ hinge frame: hinge at +0? 
        # Hinge frame: LE at +hinge_frac*c, TE negative. CP from LE toward TE:
        # x_hinge = hinge_frac*c - x_from_le  (positive if CP forward of hinge)
        strips.append(
            StripResult(
                strip_index=i,
                z_m=z_c,
                dz_m=dz,
                local_chord_m=c_loc,
                local_reynolds=re_loc,
                local_alpha_deg=alpha_deg,
                cn=chord_int.cn,
                lift_n=lift,
                drag_n=0.0,
                moment_le_nm=m_le,
                cp_x_frac=chord_int.x_cp_c,
                cp_x_hinge_m=x_hinge,
                cp_y_m=DEFAULT_Y_CP_M,
                cp_z_m=z_c,
            )
        )
    _ = EQ_COP_STRIP_LIFT
    return strips
