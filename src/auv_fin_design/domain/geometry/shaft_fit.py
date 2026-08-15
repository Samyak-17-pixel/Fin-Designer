"""Shaft / hinge embedment fit at fixed 25% chord — EQ-GEO-007."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.airfoil.naca import naca4_full_thickness
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


HINGE_CHORD_FRACTION = 0.25


class ShaftFitResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hinge_chord_fraction: float = HINGE_CHORD_FRACTION
    root_chord_m: float
    thickness_at_hinge_m: float = Field(
        ..., description="Full airfoil width at root hinge station [m]"
    )
    shaft_diameter_m: float
    required_thickness_m: float = Field(
        ..., description="shaft_diameter × clearance_factor"
    )
    clearance_factor: float
    radial_clearance_m: float = Field(
        ..., description="(thickness − shaft_d) / 2 each side"
    )
    fits: bool
    message: str
    equation_ids: tuple[str, ...] = ("EQ-GEO-007", "EQ-NACA-001")


def check_shaft_fit_at_hinge(
    geometry: CandidateFinGeometry,
    shaft_diameter_m: float,
    *,
    clearance_factor: float = 1.10,
    hinge_chord_fraction: float = HINGE_CHORD_FRACTION,
) -> ShaftFitResult:
    """Require local root thickness at hinge ≥ clearance_factor × shaft OD.

    Default clearance_factor 1.10 → section ~10% thicker than the shaft
    ("a little more than the shaft diameter").
    """
    if shaft_diameter_m <= 0:
        raise ValueError("shaft_diameter_m must be positive")
    if clearance_factor < 1.0:
        raise ValueError("clearance_factor must be >= 1.0")

    t_hinge = naca4_full_thickness(
        hinge_chord_fraction,
        geometry.thickness_ratio,
        geometry.root_chord,
    )
    required = clearance_factor * shaft_diameter_m
    radial = 0.5 * (t_hinge - shaft_diameter_m)
    fits = t_hinge + 1e-12 >= required
    if fits:
        msg = (
            f"OK: thickness at {hinge_chord_fraction:.0%} chord "
            f"{t_hinge*1000:.2f} mm ≥ {clearance_factor:.2f}×shaft "
            f"({required*1000:.2f} mm); radial clearance {radial*1000:.2f} mm/side"
        )
    else:
        msg = (
            f"FAIL: thickness at {hinge_chord_fraction:.0%} chord "
            f"{t_hinge*1000:.2f} mm < {clearance_factor:.2f}×shaft "
            f"{shaft_diameter_m*1000:.2f} mm (need ≥ {required*1000:.2f} mm)"
        )

    return ShaftFitResult(
        hinge_chord_fraction=hinge_chord_fraction,
        root_chord_m=geometry.root_chord,
        thickness_at_hinge_m=t_hinge,
        shaft_diameter_m=shaft_diameter_m,
        required_thickness_m=required,
        clearance_factor=clearance_factor,
        radial_clearance_m=radial,
        fits=fits,
        message=msg,
    )
