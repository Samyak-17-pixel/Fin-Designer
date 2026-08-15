"""Immutable models for dynamic center-of-pressure analysis."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from auv_fin_design.domain.center_of_pressure.constants import (
    DEFAULT_CACHE_ENABLED,
    DEFAULT_INTEGRATION_EPSREL,
    DEFAULT_N_STRIPS,
    DEFAULT_PROVIDER,
    DEFAULT_VERIFY_REL_TOL_FAIL,
    DEFAULT_VERIFY_REL_TOL_WARN,
    HINGE_CHORD_FRACTION,
)


class CoPSolverConfig(BaseModel):
    """Runtime configuration for the CoP solver.

    Units: SI unless noted. Loaded from configs/defaults.yaml center_of_pressure.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: Literal["xfoil_file", "analytical", "cfd", "experimental"] = DEFAULT_PROVIDER
    n_strips: int = Field(DEFAULT_N_STRIPS, ge=4, le=2000)
    integration_epsrel: float = Field(DEFAULT_INTEGRATION_EPSREL, gt=0, le=1e-2)
    verify_rel_tol_warn: float = Field(DEFAULT_VERIFY_REL_TOL_WARN, gt=0)
    verify_rel_tol_fail: float = Field(DEFAULT_VERIFY_REL_TOL_FAIL, gt=0)
    cache_enabled: bool = DEFAULT_CACHE_ENABLED
    hinge_chord_fraction: float = Field(HINGE_CHORD_FRACTION, gt=0, lt=1)
    airfoils_root: str | None = None  # None → data/airfoils under repo root


class PressureDistribution(BaseModel):
    """Sectional pressure coefficient distribution Cp(x/c).

    Purpose: Provider output for chordwise integration.
    Units: x_c [-], Cp_upper/lower [-], dCp = Cp_lower - Cp_upper (lift-positive convention).
    Reference: Abbott & von Doenhoff; XFOIL Cp convention.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    airfoil: str
    reynolds: float = Field(..., gt=0)
    alpha_deg: float
    x_c: tuple[float, ...]
    cp_upper: tuple[float, ...]
    cp_lower: tuple[float, ...]
    source: str = "xfoil_file"

    @property
    def dcp(self) -> tuple[float, ...]:
        """ΔCp = Cp_lower − Cp_upper (positive for positive lift on +α)."""
        return tuple(lo - up for lo, up in zip(self.cp_lower, self.cp_upper, strict=True))


class ChordwiseIntegral(BaseModel):
    """Result of integrating ΔCp along the chord (EQ-COP-001/002)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cn: float = Field(..., description="Normal-force coefficient [-]")
    cm_le: float = Field(..., description="Pitching moment about LE [-]")
    x_cp_c: float = Field(..., description="x_cp / c from LE toward TE [-]")
    equation_ids: tuple[str, ...] = ()


class StripResult(BaseModel):
    """Per-strip aerodynamic result (strip theory).

    Frame: control-surface — X chordwise (LE+ from hinge), Z spanwise from root.
    Units: SI (N, N·m, m, deg).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    strip_index: int
    z_m: float = Field(..., description="Strip center span station from root [m]")
    dz_m: float
    local_chord_m: float
    local_reynolds: float
    local_alpha_deg: float
    cn: float
    lift_n: float
    drag_n: float = 0.0  # lift-only CoP; profile drag optional later
    moment_le_nm: float
    cp_x_frac: float = Field(..., description="x_cp/c on local chord from LE [-]")
    cp_x_hinge_m: float = Field(..., description="Chordwise CP in hinge frame [m]")
    cp_y_m: float = 0.0
    cp_z_m: float = Field(..., description="Spanwise CP of strip (= z_m) [m]")


class CoPVerification(BaseModel):
    """Cross-check integrated CoP vs QC and Cm/CL estimates (EQ-COP-006)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    x_cp_c_integrated: float
    x_cp_c_quarter_chord: float = 0.25
    x_cp_c_cm_cl: float
    rel_err_vs_qc: float
    rel_err_vs_cm_cl: float
    status: Literal["PASS", "WARNING", "FAIL"]
    message: str
    equation_ids: tuple[str, ...] = ("EQ-COP-006",)


class ManeuverDeflection(BaseModel):
    """Required and usable fin deflection for the design maneuver (EQ-COP-007).

    V1: alpha = delta. Per-fin value for X-tail yaw (symmetric).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    cl_required: float
    cl_alpha_3d_per_rad: float
    delta_required_deg: float
    delta_max_usable_deg: float
    delta_margin_deg: float
    sufficient: bool
    note: str = "V1: geometric alpha = fin deflection"
    equation_ids: tuple[str, ...] = ("EQ-COP-007",)


class CenterOfPressureResult(BaseModel):
    """Full-fin dynamic CoP result for pipeline consumption.

    Purpose: Replace fixed QC force application for aero loads while hinge stays at 25%c.
    Units: SI. Body/control-surface: x hinge-frame chordwise, y thickness, z span.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_lift_n: float
    total_drag_n: float
    total_pitching_moment_le_nm: float
    x_cp_le_frac: float = Field(..., description="Effective x_cp/MAC from LE [-]")
    x_cp_from_le_m: float
    x_cp_hinge_m: float
    y_cp_m: float = 0.0
    z_cp_m: float
    hinge_arm_m: float = Field(..., description="Chordwise lever from hinge to CoP [m]")
    hinge_moment_nm: float
    servo_torque_nm: float
    strips: tuple[StripResult, ...] = ()
    verification: CoPVerification
    deflection: ManeuverDeflection | None = None
    # Legacy-compatible aliases for GUI that expected CenterOfPressure
    hinge_fixed_at_qc: bool = True
    note: str = (
        "Dynamic CoP from strip Cp integration; shaft/hinge fixed at 25% chord."
    )
    equation_ids: tuple[str, ...] = (
        "EQ-COP-001",
        "EQ-COP-002",
        "EQ-COP-003",
        "EQ-COP-004",
        "EQ-COP-005",
        "EQ-COP-006",
    )

    # Compatibility with older CenterOfPressure field names
    @property
    def x_cp_le_frac_compat(self) -> float:
        return self.x_cp_le_frac
