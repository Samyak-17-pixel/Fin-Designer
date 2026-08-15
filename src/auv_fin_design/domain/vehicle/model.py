"""Vehicle mathematical model — Chapter 3.1 / EQ-VEH-*."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from auv_fin_design.domain.constants.fluids import FluidProperties, WaterType, get_fluid

ConfigurationType = Literal["X", "+"]


class VehicleModel(BaseModel):
    """Immutable torpedo AUV vehicle model (SI units)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    length: float = Field(..., gt=0, description="Hull length L [m]")
    diameter: float = Field(..., gt=0, description="Hull diameter D [m]")
    mass: float = Field(..., gt=0, description="Vehicle mass m [kg]")
    water: WaterType = "freshwater"
    cg_fraction_of_length: float = Field(0.5, ge=0.0, le=1.0)
    cb_fraction_of_length: float = Field(0.5, ge=0.0, le=1.0)
    # Aft fin root leading-edge station as fraction of length from nose
    fin_root_le_fraction_of_length: float = Field(
        0.92, ge=0.5, le=1.0, description="Aft fin root LE station / L"
    )
    n_fins: int = Field(4, ge=1)
    configuration: ConfigurationType = "X"
    fin_clocking_deg: tuple[float, ...] = (45.0, 135.0, 225.0, 315.0)
    # Optional inertia override (kg·m^2); None → solid cylinder EQ-VEH-005
    Ix_override: float | None = None
    Iy_override: float | None = None
    Iz_override: float | None = None

    equation_ids: tuple[str, ...] = (
        "EQ-VEH-001",
        "EQ-VEH-002",
        "EQ-VEH-003",
        "EQ-VEH-004",
        "EQ-VEH-005",
        "EQ-VEH-006",
    )

    @model_validator(mode="after")
    def _check_clocking(self) -> VehicleModel:
        if self.configuration == "X" and self.n_fins != 4:
            raise ValueError("X configuration requires exactly 4 fins in V1")
        if len(self.fin_clocking_deg) != self.n_fins:
            raise ValueError("fin_clocking_deg length must equal n_fins")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def radius(self) -> float:
        """EQ-VEH-001"""
        return self.diameter / 2.0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cross_section_area(self) -> float:
        """EQ-VEH-002"""
        return math.pi * self.radius**2

    @computed_field  # type: ignore[prop-decorator]
    @property
    def frontal_area(self) -> float:
        return self.cross_section_area

    @computed_field  # type: ignore[prop-decorator]
    @property
    def wetted_area(self) -> float:
        """EQ-VEH-003 — cylinder only, ignores nose/tail."""
        return math.pi * self.diameter * self.length

    @computed_field  # type: ignore[prop-decorator]
    @property
    def volume(self) -> float:
        """EQ-VEH-004"""
        return math.pi * self.radius**2 * self.length

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fluid(self) -> FluidProperties:
        return get_fluid(self.water)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def x_cg(self) -> float:
        """EQ-VEH-006 — from nose."""
        return self.cg_fraction_of_length * self.length

    @computed_field  # type: ignore[prop-decorator]
    @property
    def x_cb(self) -> float:
        return self.cb_fraction_of_length * self.length

    @computed_field  # type: ignore[prop-decorator]
    @property
    def x_fin_root_le(self) -> float:
        """Root leading-edge axial station from nose [m]. Aft placement."""
        return self.fin_root_le_fraction_of_length * self.length

    @computed_field  # type: ignore[prop-decorator]
    @property
    def Ix(self) -> float:
        """EQ-VEH-005 roll inertia."""
        if self.Ix_override is not None:
            return self.Ix_override
        return 0.5 * self.mass * self.radius**2

    @computed_field  # type: ignore[prop-decorator]
    @property
    def Iy(self) -> float:
        if self.Iy_override is not None:
            return self.Iy_override
        return (1.0 / 12.0) * self.mass * (3.0 * self.radius**2 + self.length**2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def Iz(self) -> float:
        if self.Iz_override is not None:
            return self.Iz_override
        return (1.0 / 12.0) * self.mass * (3.0 * self.radius**2 + self.length**2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def slenderness(self) -> float:
        return self.length / self.diameter

    def displaced_mass(self) -> float:
        return self.fluid.density * self.volume


class MissionModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    design_speed: float = Field(..., gt=0, description="Design / cruise speed [m/s]")
    turning_radius: float = Field(..., gt=0, description="Desired turning radius [m]")
    turn_establishment_time: float = Field(..., gt=0, description="Time to establish turn [s]")
    max_speed: float | None = Field(None, gt=0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def speed(self) -> float:
        return self.design_speed
