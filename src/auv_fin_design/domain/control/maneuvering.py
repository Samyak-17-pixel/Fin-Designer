"""Maneuvering / required control authority — EQ-MAN-*."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.hydrodynamics.estimator import HydrodynamicModel
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


class ControlRequirementModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    r_target: float
    r_dot: float
    M_inertial: float
    M_added: float
    M_damping_transient: float
    M_damping_steady: float
    M_transient: float
    M_steady: float
    M_raw_governing: float
    control_margin: float
    M_design: float
    equation_ids: tuple[str, ...] = ()


def compute_control_requirement(
    vehicle: VehicleModel,
    hydro: HydrodynamicModel,
    mission: MissionModel,
    *,
    control_margin: float = 0.25,
) -> ControlRequirementModel:
    """EQ-MAN-001 … EQ-MAN-007.

    Transient: r = r_target, r_dot = r_target/T (establish turn with full rate + accel).
    Steady: r = r_target, r_dot = 0.
    Design moment = max(|transient|, |steady|) * (1 + margin).
    """
    r_target = mission.speed / mission.turning_radius  # EQ-MAN-001
    r_dot = r_target / mission.turn_establishment_time  # EQ-MAN-002

    m_i = vehicle.Iz * r_dot  # EQ-MAN-003
    m_a = hydro.N_rdot * r_dot  # EQ-MAN-004

    def damping(r: float) -> float:
        # EQ-MAN-005 — signed moment opposing yaw (N coeffs are negative)
        return hydro.N_r * r + hydro.N_r_abs_r * abs(r) * r

    m_d_trans = damping(r_target)
    m_d_steady = damping(r_target)

    # Required control moment counters inertia+added+damping.
    # With negative damping coeffs, damping() is negative for r>0; fins must overcome
    # the magnitude of resistance. Use moment balance for required fin moment magnitude:
    # M_control + M_damping = M_I + M_A  during transient? 
    # SRDS: M_req = M_I + M_A + M_D where M_D is hydrodynamic resistance magnitude.
    # Damping coefficients are negative (resistive). The resistive moment magnitude is -M_D
    # when M_D = N_r*r + N_|r|r*|r|*r < 0.
    m_damp_trans_resist = -m_d_trans  # positive resistance
    m_damp_steady_resist = -m_d_steady

    m_transient = m_i + m_a + m_damp_trans_resist  # EQ-MAN-006
    m_steady = m_damp_steady_resist  # no angular accel

    m_raw = max(abs(m_transient), abs(m_steady))
    m_design = m_raw * (1.0 + control_margin)  # EQ-MAN-007

    return ControlRequirementModel(
        r_target=r_target,
        r_dot=r_dot,
        M_inertial=m_i,
        M_added=m_a,
        M_damping_transient=m_damp_trans_resist,
        M_damping_steady=m_damp_steady_resist,
        M_transient=m_transient,
        M_steady=m_steady,
        M_raw_governing=m_raw,
        control_margin=control_margin,
        M_design=m_design,
        equation_ids=(
            "EQ-MAN-001",
            "EQ-MAN-002",
            "EQ-MAN-003",
            "EQ-MAN-004",
            "EQ-MAN-005",
            "EQ-MAN-006",
            "EQ-MAN-007",
        ),
    )


def estimate_minimum_turn_radius(vehicle: VehicleModel, speed: float) -> float:
    """Heuristic feasibility: Rt should exceed ~2L for gentle AUV turns (warning only)."""
    return 2.0 * vehicle.length
