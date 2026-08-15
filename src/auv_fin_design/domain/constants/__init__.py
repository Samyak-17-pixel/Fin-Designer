"""Domain constants package."""

from auv_fin_design.domain.constants.fluids import FRESHWATER, SEAWATER, FluidProperties, get_fluid
from auv_fin_design.domain.constants.materials import (
    ABS,
    NYLON,
    PETG,
    PLA,
    MaterialProperties,
    get_material,
    list_materials,
)

__all__ = [
    "FRESHWATER",
    "SEAWATER",
    "FluidProperties",
    "get_fluid",
    "PLA",
    "PETG",
    "ABS",
    "NYLON",
    "MaterialProperties",
    "get_material",
    "list_materials",
]
