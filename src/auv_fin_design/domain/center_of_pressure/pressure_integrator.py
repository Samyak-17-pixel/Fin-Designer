"""Chordwise pressure integration — EQ-COP-001 / EQ-COP-002."""

from __future__ import annotations

import numpy as np
from scipy.integrate import simpson

from auv_fin_design.domain.center_of_pressure.constants import EQ_COP_CN, EQ_COP_XCP
from auv_fin_design.domain.center_of_pressure.exceptions import CoPIntegrationError
from auv_fin_design.domain.center_of_pressure.models import ChordwiseIntegral, PressureDistribution
from auv_fin_design.domain.center_of_pressure.validators import validate_cp_arrays


def integrate_chordwise(
    pressure: PressureDistribution,
    *,
    epsrel: float = 1.0e-6,
) -> ChordwiseIntegral:
    """Integrate ΔCp along chord for normal force and center of pressure.

    Equations (Equation Register):
      EQ-COP-001: cn = ∫_0^1 ΔCp d(x/c)     [lift-only normal force coeff]
      EQ-COP-002: x_cp/c = ∫ (x/c) ΔCp d(x/c) / cn

    Also cm_le = −∫ (x/c) ΔCp d(x/c)  (pitching moment about LE, 2D coeff).

    Uses SciPy simpson on validated stations (not crude summation).
    epsrel reserved for adaptive refinement hooks; simpson on dense grid is V1.
    """
    _ = epsrel
    x, cu, cl = validate_cp_arrays(pressure.x_c, pressure.cp_upper, pressure.cp_lower)
    dcp = cl - cu
    cn = float(simpson(dcp, x=x))
    moment_integrand = x * dcp
    mx = float(simpson(moment_integrand, x=x))
    if abs(cn) < 1e-12:
        # Near-zero lift → CP undefined; place at aerodynamic center ≈ 0.25
        x_cp_c = 0.25
    else:
        x_cp_c = float(mx / cn)
    if not np.isfinite(cn) or not np.isfinite(x_cp_c):
        raise CoPIntegrationError("Non-finite chordwise integral")
    return ChordwiseIntegral(
        cn=cn,
        cm_le=-mx,
        x_cp_c=x_cp_c,
        equation_ids=(EQ_COP_CN, EQ_COP_XCP),
    )
