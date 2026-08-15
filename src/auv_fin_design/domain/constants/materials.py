"""Material constants — EQ-STR-001 and V1 material library."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MaterialProperties:
    name: str
    density: float  # kg/m^3
    youngs_modulus: float  # Pa
    poisson_ratio: float
    yield_strength: float  # Pa
    ultimate_strength: float  # Pa
    shear_modulus: float  # Pa
    equation_ids: tuple[str, ...]


PLA = MaterialProperties(
    name="PLA",
    density=1240.0,
    youngs_modulus=3.2e9,
    poisson_ratio=0.36,
    yield_strength=60.0e6,
    ultimate_strength=65.0e6,
    shear_modulus=1.18e9,
    equation_ids=("EQ-STR-001",),
)

PETG = MaterialProperties(
    name="PETG",
    density=1270.0,
    youngs_modulus=2.1e9,
    poisson_ratio=0.38,
    yield_strength=50.0e6,
    ultimate_strength=53.0e6,
    shear_modulus=0.76e9,
    equation_ids=("EQ-STR-001",),
)

ABS = MaterialProperties(
    name="ABS",
    density=1040.0,
    youngs_modulus=2.3e9,
    poisson_ratio=0.35,
    yield_strength=40.0e6,
    ultimate_strength=45.0e6,
    shear_modulus=0.85e9,
    equation_ids=("EQ-STR-001",),
)

NYLON = MaterialProperties(
    name="Nylon",
    density=1140.0,
    youngs_modulus=1.8e9,
    poisson_ratio=0.39,
    yield_strength=55.0e6,
    ultimate_strength=70.0e6,
    shear_modulus=0.65e9,
    equation_ids=("EQ-STR-001",),
)

_MATERIALS = {
    "PLA": PLA,
    "PETG": PETG,
    "ABS": ABS,
    "NYLON": NYLON,
}


def list_materials() -> list[str]:
    return sorted(_MATERIALS.keys())


def get_material(name: str) -> MaterialProperties:
    key = name.strip().upper()
    if key not in _MATERIALS:
        raise ValueError(f"Unknown material: {name!r}. Available: {list_materials()}")
    return _MATERIALS[key]
