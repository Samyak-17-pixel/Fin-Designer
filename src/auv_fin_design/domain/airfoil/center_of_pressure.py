"""Center of pressure — EQ-AERO-008 (from Cm about quarter-chord)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


class CenterOfPressure(BaseModel):
    """Aerodynamic center of pressure for the sized fin at the design operating point.

    Chordwise CP uses XFOIL Cm (about c/4) and 3D CL:
        x_cp/c |_LE→TE = 0.25 − Cm/CL

    Shaft / hinge is fixed at 25% chord (V1); CP generally differs from the hinge
    unless Cm ≈ 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    x_cp_le_frac: float = Field(
        ...,
        description="Fraction of MAC from LE toward TE (standard aero)",
    )
    x_cp_from_le_m: float = Field(..., description="Distance from LE toward TE [m] on MAC")
    x_cp_hinge_m: float = Field(
        ...,
        description="Chordwise position in hinge frame [m]; LE+, TE−; hinge at 0",
    )
    z_cp_m: float = Field(
        ...,
        description="Spanwise CP from root [m] (planform area centroid, uniform load)",
    )
    hinge_fixed_at_qc: bool = True
    note: str = (
        "Shaft/hinge is fixed at 25% chord by design convention; "
        "corner coordinates scale with chord/span; CP is computed from Cm/CL."
    )
    equation_ids: tuple[str, ...] = ("EQ-AERO-008",)


def center_of_pressure(
    *,
    cl: float,
    cm: float,
    mac: float,
    geometry: CandidateFinGeometry,
) -> CenterOfPressure:
    """EQ-AERO-008 — CP from quarter-chord pitching moment.

    With Cm referenced to c/4 (XFOIL / Abbott convention):
        x_cp/c (LE→TE) = 0.25 − Cm/CL
    In the control-surface hinge frame (LE +, hinge at 0):
        x_cp_hinge = (Cm/CL) * MAC
    Spanwise: planform area centroid of the trapezoid (uniform load V1).
    """
    if abs(cl) < 1e-9:
        # No meaningful CP; fall back to aerodynamic center ≈ quarter-chord
        x_le_frac = 0.25
        x_hinge = 0.0
    else:
        x_le_frac = 0.25 - cm / cl
        x_hinge = (cm / cl) * mac

    # Trapezoid centroid from root (chords c_r at root, c_t at tip)
    c_r, c_t, b = geometry.root_chord, geometry.tip_chord, geometry.span
    z_cp = b * (2.0 * c_t + c_r) / (3.0 * (c_r + c_t))

    return CenterOfPressure(
        x_cp_le_frac=x_le_frac,
        x_cp_from_le_m=x_le_frac * mac,
        x_cp_hinge_m=x_hinge,
        z_cp_m=z_cp,
    )
