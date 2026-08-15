"""Fluid property constants — EQ-FLUID-001, EQ-FLUID-002."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WaterType = Literal["freshwater", "seawater"]


@dataclass(frozen=True, slots=True)
class FluidProperties:
    """Immutable fluid properties. Equations: EQ-FLUID-001 / EQ-FLUID-002."""

    name: WaterType
    density: float  # kg/m^3
    dynamic_viscosity: float  # Pa·s
    kinematic_viscosity: float  # m^2/s
    gravity: float  # m/s^2
    temperature_C: float
    equation_ids: tuple[str, ...]


FRESHWATER = FluidProperties(
    name="freshwater",
    density=998.2,
    dynamic_viscosity=1.002e-3,
    kinematic_viscosity=1.004e-6,
    gravity=9.80665,
    temperature_C=20.0,
    equation_ids=("EQ-FLUID-001",),
)

SEAWATER = FluidProperties(
    name="seawater",
    density=1025.0,
    dynamic_viscosity=1.08e-3,
    kinematic_viscosity=1.05e-6,
    gravity=9.80665,
    temperature_C=20.0,
    equation_ids=("EQ-FLUID-002",),
)


def get_fluid(water: WaterType) -> FluidProperties:
    if water == "freshwater":
        return FRESHWATER
    if water == "seawater":
        return SEAWATER
    raise ValueError(f"Unknown water type: {water!r}")
