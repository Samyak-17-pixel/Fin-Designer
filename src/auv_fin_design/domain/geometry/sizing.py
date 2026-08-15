"""Initial fin sizing — EQ-GEO-*."""

from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field, computed_field


class FinCornerPoint(BaseModel):
    """Corner of the fin planform in the control-surface frame.

    Origin at the hinge (25% chord from LE at the root).
    X = chordwise (LE positive / forward of hinge, TE negative / aft of hinge)
    Z = spanwise (root = 0, tip = +span)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    x: float
    z: float


class CandidateFinGeometry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    area: float = Field(..., gt=0)
    aspect_ratio: float = Field(..., gt=0)
    taper_ratio: float = Field(..., gt=0, le=1.0)
    sweep_deg: float = 0.0
    span: float = Field(..., gt=0)
    root_chord: float = Field(..., gt=0)
    tip_chord: float = Field(..., gt=0)
    mac: float = Field(..., gt=0)
    thickness_ratio: float = Field(..., gt=0)
    root_thickness: float = Field(..., gt=0)
    tip_thickness: float = Field(..., gt=0)
    volume_est: float = Field(..., ge=0)
    mass_est: float = Field(..., ge=0)
    # Shaft diameter = max width of airfoil section at root (t/c * c_root)
    shaft_diameter: float = Field(..., gt=0)
    naca_profile: str = "0015"
    leading_edge_root: FinCornerPoint | None = None
    trailing_edge_root: FinCornerPoint | None = None
    leading_edge_tip: FinCornerPoint | None = None
    trailing_edge_tip: FinCornerPoint | None = None
    equation_ids: tuple[str, ...] = ()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mean_chord(self) -> float:
        return self.area / self.span


def trapezoid_chords(area: float, span: float, taper: float) -> tuple[float, float]:
    """EQ-GEO-003"""
    c_r = 2.0 * area / (span * (1.0 + taper))
    c_t = taper * c_r
    return c_r, c_t


def mean_aerodynamic_chord(root_chord: float, taper: float) -> float:
    """EQ-GEO-004"""
    lam = taper
    return (2.0 / 3.0) * root_chord * (1.0 + lam + lam**2) / (1.0 + lam)


def fin_corner_points(
    root_chord: float,
    tip_chord: float,
    span: float,
    sweep_deg: float = 0.0,
) -> tuple[FinCornerPoint, FinCornerPoint, FinCornerPoint, FinCornerPoint]:
    """Corner coordinates in the control-surface frame (origin at root hinge = 25% chord).

    X chordwise: LE positive (forward of hinge), TE negative (aft of hinge).
    Z spanwise: root = 0, tip = +span.
    """
    sweep_rad = math.radians(sweep_deg)
    le_tip_from_le_root = span * math.tan(sweep_rad)
    le_root_x = 0.25 * root_chord
    te_root_x = -0.75 * root_chord
    le_tip_x = 0.25 * tip_chord + le_tip_from_le_root
    te_tip_x = -0.75 * tip_chord + le_tip_from_le_root
    return (
        FinCornerPoint(x=le_root_x, z=0.0),
        FinCornerPoint(x=te_root_x, z=0.0),
        FinCornerPoint(x=le_tip_x, z=span),
        FinCornerPoint(x=te_tip_x, z=span),
    )


def _naca_profile_code(naca_profile: str, thickness_ratio: float) -> str:
    cleaned = naca_profile.replace("NACA", "").replace("naca", "").strip()
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    if len(digits) >= 4:
        return digits[:4]
    if len(digits) == 2:
        return f"00{digits}"
    return f"00{int(round(thickness_ratio * 100)):02d}"


def size_fin(
    lift_required: float,
    dynamic_pressure: float,
    *,
    cl: float,
    aspect_ratio: float,
    taper_ratio: float,
    sweep_deg: float = 0.0,
    thickness_ratio: float = 0.12,
    material_density: float = 1240.0,
    naca_profile: str = "0015",
) -> CandidateFinGeometry:
    """EQ-GEO-001 … EQ-GEO-004 plus corner coordinates and shaft diameter."""
    if dynamic_pressure <= 0 or cl <= 0:
        raise ValueError("dynamic_pressure and cl must be positive")
    area = lift_required / (dynamic_pressure * cl)  # EQ-GEO-001
    span = math.sqrt(area * aspect_ratio)  # EQ-GEO-002
    c_r, c_t = trapezoid_chords(area, span, taper_ratio)
    return build_fin_from_planform(
        root_chord=c_r,
        tip_chord=c_t,
        span=span,
        sweep_deg=sweep_deg,
        thickness_ratio=thickness_ratio,
        material_density=material_density,
        naca_profile=naca_profile,
        equation_ids=("EQ-GEO-001", "EQ-GEO-002", "EQ-GEO-003", "EQ-GEO-004"),
    )


def build_fin_from_planform(
    *,
    root_chord: float,
    span: float,
    tip_chord: float | None = None,
    taper_ratio: float = 0.5,
    sweep_deg: float = 0.0,
    thickness_ratio: float = 0.12,
    material_density: float = 1240.0,
    naca_profile: str = "0015",
    equation_ids: tuple[str, ...] = ("EQ-GEO-003", "EQ-GEO-004"),
) -> CandidateFinGeometry:
    """Build geometry from explicit planform dimensions (optional user overrides)."""
    if root_chord <= 0 or span <= 0:
        raise ValueError("root_chord and span must be positive")
    c_t = tip_chord if tip_chord is not None else taper_ratio * root_chord
    if c_t <= 0:
        raise ValueError("tip_chord must be positive")
    if c_t > root_chord + 1e-12:
        raise ValueError("tip_chord cannot exceed root_chord")
    lam = c_t / root_chord
    area = 0.5 * (root_chord + c_t) * span
    ar = (span**2) / area
    mac = mean_aerodynamic_chord(root_chord, lam)
    t_r = thickness_ratio * root_chord
    t_t = thickness_ratio * c_t
    a_root = math.pi * root_chord * t_r / 4.0
    a_tip = math.pi * c_t * t_t / 4.0
    volume = 0.5 * (a_root + a_tip) * span
    mass = volume * material_density
    le_root, te_root, le_tip, te_tip = fin_corner_points(
        root_chord, c_t, span, sweep_deg
    )
    return CandidateFinGeometry(
        area=area,
        aspect_ratio=ar,
        taper_ratio=lam,
        sweep_deg=sweep_deg,
        span=span,
        root_chord=root_chord,
        tip_chord=c_t,
        mac=mac,
        thickness_ratio=thickness_ratio,
        root_thickness=t_r,
        tip_thickness=t_t,
        volume_est=volume,
        mass_est=mass,
        shaft_diameter=t_r,
        naca_profile=_naca_profile_code(naca_profile, thickness_ratio),
        leading_edge_root=le_root,
        trailing_edge_root=te_root,
        leading_edge_tip=le_tip,
        trailing_edge_tip=te_tip,
        equation_ids=equation_ids,
    )


def apply_dimension_overrides(
    geom: CandidateFinGeometry,
    *,
    root_chord: float | None = None,
    span: float | None = None,
    tip_chord: float | None = None,
    taper_ratio: float | None = None,
    sweep_deg: float | None = None,
    thickness_ratio: float | None = None,
    material_density: float = 1240.0,
    naca_profile: str | None = None,
) -> CandidateFinGeometry:
    """Replace selected planform dimensions; unspecified values keep current geom."""
    if root_chord is None and span is None and tip_chord is None:
        return geom
    cr = root_chord if root_chord is not None else geom.root_chord
    b = span if span is not None else geom.span
    if tip_chord is not None:
        ct: float | None = tip_chord
        lam = taper_ratio if taper_ratio is not None else geom.taper_ratio
    else:
        lam = taper_ratio if taper_ratio is not None else geom.taper_ratio
        ct = None
    return build_fin_from_planform(
        root_chord=cr,
        span=b,
        tip_chord=ct,
        taper_ratio=lam,
        sweep_deg=sweep_deg if sweep_deg is not None else geom.sweep_deg,
        thickness_ratio=thickness_ratio
        if thickness_ratio is not None
        else geom.thickness_ratio,
        material_density=material_density,
        naca_profile=naca_profile or geom.naca_profile,
        equation_ids=geom.equation_ids + ("EQ-GEO-OVERRIDE",),
    )


def geometry_to_dict(geom: CandidateFinGeometry) -> dict:
    """Complete fin dimensions for GUI / reports / CLI (control-surface frame)."""

    def _pt(p: FinCornerPoint | None) -> dict[str, float] | None:
        if p is None:
            return None
        return {
            "x_m": p.x,
            "z_m": p.z,
            "x_mm": p.x * 1000.0,
            "z_mm": p.z * 1000.0,
        }

    return {
        "naca_profile": geom.naca_profile,
        "surface_area_m2": geom.area,
        "surface_area_mm2": geom.area * 1.0e6,
        "span_m": geom.span,
        "span_mm": geom.span * 1000.0,
        "root_chord_m": geom.root_chord,
        "root_chord_mm": geom.root_chord * 1000.0,
        "tip_chord_m": geom.tip_chord,
        "tip_chord_mm": geom.tip_chord * 1000.0,
        "aspect_ratio": geom.aspect_ratio,
        "taper_ratio": geom.taper_ratio,
        "sweep_deg": geom.sweep_deg,
        "mac_m": geom.mac,
        "mac_mm": geom.mac * 1000.0,
        "thickness_ratio": geom.thickness_ratio,
        "root_thickness_m": geom.root_thickness,
        "root_thickness_mm": geom.root_thickness * 1000.0,
        "tip_thickness_m": geom.tip_thickness,
        "tip_thickness_mm": geom.tip_thickness * 1000.0,
        "shaft_diameter_m": geom.shaft_diameter,
        "shaft_diameter_mm": geom.shaft_diameter * 1000.0,
        "volume_est_m3": geom.volume_est,
        "mass_est_kg": geom.mass_est,
        "control_surface_frame": {
            "note": (
                "Origin FIXED at root hinge = 25% chord (V1). "
                "Shaft does not move with aerodynamics; corners scale with chord/span. "
                "X chordwise (LE+), Z spanwise."
            ),
            "hinge_fixed_at_quarter_chord": True,
            "leading_edge_root": _pt(geom.leading_edge_root),
            "trailing_edge_root": _pt(geom.trailing_edge_root),
            "leading_edge_tip": _pt(geom.leading_edge_tip),
            "trailing_edge_tip": _pt(geom.trailing_edge_tip),
        },
    }


def format_fin_dimensions_lines(geom: CandidateFinGeometry) -> list[str]:
    """Human-readable final dimensions in metres and millimetres."""

    def mm(x: float) -> str:
        return f"{x * 1000.0:.2f} mm"

    def m_mm(x: float) -> str:
        return f"{x:.6f} m  (= {mm(x)})"

    lines = [
        "=== FINAL COMPLETE FIN DIMENSIONS ===",
        f"NACA Profile: {geom.naca_profile}",
        f"Surface Area: {geom.area:.6f} m²  (= {geom.area * 1e6:.1f} mm²)",
        f"Span: {m_mm(geom.span)}",
        f"Root Chord: {m_mm(geom.root_chord)}",
        f"Tip Chord: {m_mm(geom.tip_chord)}",
        f"MAC: {m_mm(geom.mac)}",
        f"Aspect Ratio: {geom.aspect_ratio:.4f}",
        f"Taper Ratio: {geom.taper_ratio:.4f}",
        f"Sweep: {geom.sweep_deg:.2f} deg",
        f"Thickness Ratio (t/c): {geom.thickness_ratio:.4f}",
        f"Root Max Thickness: {m_mm(geom.root_thickness)}",
        f"Tip Max Thickness: {m_mm(geom.tip_thickness)}",
        f"Shaft Diameter (root max width): {m_mm(geom.shaft_diameter)}",
        f"Est. Volume: {geom.volume_est:.6e} m³",
        f"Est. Mass: {geom.mass_est:.6f} kg",
        "",
        "--- Summary (mm) ---",
        f"span = {mm(geom.span)}",
        f"root chord = {mm(geom.root_chord)}",
        f"tip chord = {mm(geom.tip_chord)}",
        f"MAC = {mm(geom.mac)}",
        f"root max thickness = {mm(geom.root_thickness)}",
        f"tip max thickness = {mm(geom.tip_thickness)}",
        f"shaft diameter (max width) = {mm(geom.shaft_diameter)}",
    ]
    if geom.leading_edge_root:
        lines += [
            "",
            "--- Control Surface Geometry (hinge frame) ---",
            "Shaft/hinge FIXED at 25% chord (V1). X chordwise (LE+), Z spanwise.",
            (
                f"Leading Edge Root:     X={geom.leading_edge_root.x:.6f} m "
                f"({geom.leading_edge_root.x*1000:.2f} mm)   "
                f"Z={geom.leading_edge_root.z:.6f} m ({geom.leading_edge_root.z*1000:.2f} mm)"
            ),
            (
                f"Trailing Edge Root:    X={geom.trailing_edge_root.x:.6f} m "
                f"({geom.trailing_edge_root.x*1000:.2f} mm)   "
                f"Z={geom.trailing_edge_root.z:.6f} m ({geom.trailing_edge_root.z*1000:.2f} mm)"
            ),
            (
                f"Leading Edge Tip:      X={geom.leading_edge_tip.x:.6f} m "
                f"({geom.leading_edge_tip.x*1000:.2f} mm)   "
                f"Z={geom.leading_edge_tip.z:.6f} m ({geom.leading_edge_tip.z*1000:.2f} mm)"
            ),
            (
                f"Trailing Edge Tip:     X={geom.trailing_edge_tip.x:.6f} m "
                f"({geom.trailing_edge_tip.x*1000:.2f} mm)   "
                f"Z={geom.trailing_edge_tip.z:.6f} m ({geom.trailing_edge_tip.z*1000:.2f} mm)"
            ),
        ]
    return lines


def check_geometry_constraints(
    geom: CandidateFinGeometry,
    hull_diameter: float,
    *,
    max_span_over_diameter: float = 0.45,
    min_tip_chord_m: float = 0.015,
    min_te_thickness_m: float = 0.0008,
    min_wall_thickness_m: float = 0.0012,
) -> list[str]:
    """EQ-GEO-006 and packaging rules. Returns list of violation messages."""
    violations: list[str] = []
    max_span = max_span_over_diameter * hull_diameter
    if geom.span > max_span:
        violations.append(
            f"Span {geom.span:.4f} m exceeds max {max_span:.4f} m "
            f"({max_span_over_diameter}*D)"
        )
    if geom.tip_chord < min_tip_chord_m:
        violations.append(f"Tip chord {geom.tip_chord:.4f} m < min {min_tip_chord_m} m")
    if geom.tip_thickness < min_wall_thickness_m:
        violations.append(
            f"Tip thickness {geom.tip_thickness:.4f} m < min wall {min_wall_thickness_m} m"
        )
    return violations
