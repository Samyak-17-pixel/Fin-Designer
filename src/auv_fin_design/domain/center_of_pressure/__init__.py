"""Dynamic 3D center-of-pressure package (strip theory + Cp integration)."""

from __future__ import annotations

from auv_fin_design.domain.center_of_pressure.cp_solver import CoPSolver, solve_center_of_pressure
from auv_fin_design.domain.center_of_pressure.models import (
    CenterOfPressureResult,
    CoPSolverConfig,
    CoPVerification,
    ManeuverDeflection,
    PressureDistribution,
    StripResult,
)

__all__ = [
    "CenterOfPressureResult",
    "CoPSolver",
    "CoPSolverConfig",
    "CoPVerification",
    "ManeuverDeflection",
    "PressureDistribution",
    "StripResult",
    "solve_center_of_pressure",
]
