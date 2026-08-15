"""Control allocation — X-tail aft fins — EQ-ALLOC-*."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.control.maneuvering import ControlRequirementModel
from auv_fin_design.domain.vehicle.model import VehicleModel


class ControlAllocationModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    lever_arm: float
    lift_per_fin: float
    n_fins: int
    configuration: str
    clocking_deg: tuple[float, ...]
    yaw_projection_factor: float
    force_station_x_m: float = Field(
        ..., description="Body-x of force application (nose=0) [m]"
    )
    equation_ids: tuple[str, ...] = ()


def root_quarter_chord_station(x_root_le: float, c_root: float) -> float:
    """EQ-ALLOC-003 — legacy QC station (initial guess before dynamic CoP)."""
    return x_root_le + 0.25 * c_root


def lever_arm(x_cg: float, x_force: float) -> float:
    """EQ-ALLOC-002 — |x_force − x_CG|"""
    return abs(x_force - x_cg)


def allocate_x_tail_yaw(
    vehicle: VehicleModel,
    requirement: ControlRequirementModel,
    *,
    root_chord: float,
    force_station_x_m: float | None = None,
) -> ControlAllocationModel:
    """EQ-ALLOC-004 — symmetric X-tail yaw allocation.

    Force station defaults to root quarter-chord; pipeline replaces with dynamic CoP.
    """
    x_force = (
        force_station_x_m
        if force_station_x_m is not None
        else root_quarter_chord_station(vehicle.x_fin_root_le, root_chord)
    )
    ell = lever_arm(vehicle.x_cg, x_force)
    if ell <= 0:
        raise ValueError("Lever arm must be positive; check fin axial station vs CG")

    proj = math.sin(math.radians(45.0))  # 1/sqrt(2)
    n = vehicle.n_fins
    lift = requirement.M_design / (n * ell * proj)

    return ControlAllocationModel(
        lever_arm=ell,
        lift_per_fin=lift,
        n_fins=n,
        configuration=vehicle.configuration,
        clocking_deg=tuple(vehicle.fin_clocking_deg),
        yaw_projection_factor=proj,
        force_station_x_m=x_force,
        equation_ids=(
            "EQ-ALLOC-001",
            "EQ-ALLOC-002",
            "EQ-ALLOC-003",
            "EQ-ALLOC-004",
        ),
    )
