"""Optional NSGA-II optimization over fin design variables (pymoo)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from auv_fin_design.domain.servo.analysis import ServoSpecification
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel
from auv_fin_design.infrastructure.config.loader import load_defaults


@dataclass
class OptimizationResult:
    available: bool
    message: str
    best_drag: float | None = None
    best_mass: float | None = None
    best_params: dict[str, float] | None = None
    n_evaluations: int = 0


def run_nsga2(
    vehicle: VehicleModel,
    mission: MissionModel,
    *,
    population: int = 40,
    generations: int = 20,
    airfoil_name: str = "NACA0015",
) -> OptimizationResult:
    """Minimize fin drag and mass subject to pipeline feasibility.

    Requires optional dependency: pip install pymoo
    Uses smaller defaults than SRDS (80/120) for interactive use.
    """
    try:
        from pymoo.algorithms.moo.nsga2 import NSGA2
        from pymoo.core.problem import ElementwiseProblem
        from pymoo.optimize import minimize
        from pymoo.operators.crossover.sbx import SBX
        from pymoo.operators.mutation.pm import PM
        from pymoo.operators.sampling.rnd import FloatRandomSampling
    except ImportError:
        return OptimizationResult(
            available=False,
            message='pymoo not installed. Run: pip install -e ".[opt]"',
        )

    # Lazy import to avoid circular dependency with pipeline
    from auv_fin_design.application.pipeline import run_design_pipeline

    defaults = load_defaults()
    servo = ServoSpecification(
        rated_torque=float(defaults["servo"]["rated_torque_nm"]),
        shaft_diameter=float(defaults["servo"]["shaft_diameter_m"]),
    )

    class FinProblem(ElementwiseProblem):
        def __init__(self) -> None:
            super().__init__(
                n_var=2,
                n_obj=2,
                n_ieq_constr=3,
                xl=np.array([0.8, 0.3]),
                xu=np.array([2.5, 1.0]),
            )

        def _evaluate(self, x, out, *args, **kwargs):  # noqa: ANN001, N802
            ar, taper = float(x[0]), float(x[1])
            cfg = load_defaults()
            cfg["sizing"]["aspect_ratio"] = ar
            cfg["sizing"]["taper_ratio"] = taper
            try:
                result = run_design_pipeline(
                    vehicle,
                    mission,
                    servo=servo,
                    defaults=cfg,
                    airfoil_name=airfoil_name,
                    run_sensitivity=False,
                    run_optimization=False,
                )
                drag = result.aero.cd_total * result.hydro.dynamic_pressure * result.geometry.area
                mass = result.geometry.mass_est
                g_span = result.geometry.span - (
                    cfg["geometry_constraints"]["max_span_over_diameter"] * vehicle.diameter
                )
                g_stall = 5.0 - (result.aero.stall_alpha_deg - result.aero.alpha_deg)
                g_pass = 0.0 if result.passed else 1.0
                out["F"] = [drag, mass]
                out["G"] = [g_span, g_stall, g_pass]
            except Exception:  # noqa: BLE001
                out["F"] = [1e6, 1e6]
                out["G"] = [1.0, 1.0, 1.0]

    algorithm = NSGA2(
        pop_size=population,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True,
    )
    res = minimize(FinProblem(), algorithm, ("n_gen", generations), verbose=False, seed=1)
    if res.F is None or len(res.F) == 0:
        return OptimizationResult(
            available=True,
            message="No feasible Pareto points found",
            n_evaluations=population * generations,
        )

    idx = int(np.argmin(res.F[:, 0]))
    return OptimizationResult(
        available=True,
        message="NSGA-II complete",
        best_drag=float(res.F[idx, 0]),
        best_mass=float(res.F[idx, 1]),
        best_params={"aspect_ratio": float(res.X[idx, 0]), "taper_ratio": float(res.X[idx, 1])},
        n_evaluations=population * generations,
    )
