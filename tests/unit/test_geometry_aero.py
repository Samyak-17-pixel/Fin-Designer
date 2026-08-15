"""Geometry and Helmbold tests."""

from __future__ import annotations

import math

from auv_fin_design.domain.airfoil.center_of_pressure import center_of_pressure
from auv_fin_design.domain.airfoil.finite_wing import helmbold_cl_alpha
from auv_fin_design.domain.geometry.sizing import (
    mean_aerodynamic_chord,
    size_fin,
    trapezoid_chords,
)


def test_EQ_GEO_trapezoid():
    S, AR, lam = 0.01, 1.8, 0.5
    b = math.sqrt(S * AR)
    cr, ct = trapezoid_chords(S, b, lam)
    assert abs(ct / cr - lam) < 1e-12
    assert abs(0.5 * (cr + ct) * b - S) / S < 1e-9
    mac = mean_aerodynamic_chord(cr, lam)
    expected = (2 / 3) * cr * (1 + lam + lam**2) / (1 + lam)
    assert abs(mac - expected) / expected < 1e-12


def test_EQ_AERO_001_helmbold():
    a0 = 2 * math.pi
    ar = 1.8
    a3d = helmbold_cl_alpha(a0, ar)
    term = a0 / (math.pi * ar)
    expected = a0 / (math.sqrt(1 + term**2) + term)
    assert abs(a3d - expected) / expected < 1e-12
    # Must be less than 2D slope
    assert a3d < a0
    # Helmbold > slender-wing pi*AR/2 for this AR? Not required — just positive
    assert a3d > 0


def test_size_fin_cl():
    g = size_fin(10.0, 1000.0, cl=0.5, aspect_ratio=1.8, taper_ratio=0.5, thickness_ratio=0.12)
    assert abs(g.area - 10.0 / (1000.0 * 0.5)) < 1e-12


def test_EQ_AERO_008_center_of_pressure():
    g = size_fin(10.0, 1000.0, cl=0.5, aspect_ratio=1.8, taper_ratio=0.5, thickness_ratio=0.12)
    # Cm = 0 → CP at quarter-chord / hinge
    cp0 = center_of_pressure(cl=0.5, cm=0.0, mac=g.mac, geometry=g)
    assert abs(cp0.x_cp_le_frac - 0.25) < 1e-12
    assert abs(cp0.x_cp_hinge_m) < 1e-12
    # Negative Cm, positive CL → CP aft of QC (negative X in hinge frame)
    cp = center_of_pressure(cl=0.5, cm=-0.05, mac=g.mac, geometry=g)
    assert abs(cp.x_cp_le_frac - (0.25 - (-0.05) / 0.5)) < 1e-12
    assert abs(cp.x_cp_hinge_m - ((-0.05) / 0.5) * g.mac) < 1e-12
    # Trapezoid planform centroid
    z_exp = g.span * (2 * g.tip_chord + g.root_chord) / (3 * (g.root_chord + g.tip_chord))
    assert abs(cp.z_cp_m - z_exp) < 1e-12
    assert cp.hinge_fixed_at_qc


def test_build_fin_from_planform_and_override():
    from auv_fin_design.domain.geometry.sizing import (
        apply_dimension_overrides,
        build_fin_from_planform,
    )

    g = build_fin_from_planform(
        root_chord=0.10, span=0.20, taper_ratio=0.5, thickness_ratio=0.15
    )
    assert abs(g.tip_chord - 0.05) < 1e-12
    assert abs(g.area - 0.5 * (0.10 + 0.05) * 0.20) < 1e-12
    g2 = apply_dimension_overrides(g, root_chord=0.12, span=0.18)
    assert abs(g2.root_chord - 0.12) < 1e-12
    assert abs(g2.span - 0.18) < 1e-12
    assert abs(g2.tip_chord - 0.06) < 1e-12  # keeps taper 0.5


def test_EQ_GEO_007_shaft_fit_at_hinge():
    from auv_fin_design.domain.airfoil.naca import naca4_full_thickness
    from auv_fin_design.domain.geometry.shaft_fit import check_shaft_fit_at_hinge

    g = size_fin(10.0, 1000.0, cl=0.5, aspect_ratio=1.8, taper_ratio=0.5, thickness_ratio=0.15)
    t25 = naca4_full_thickness(0.25, 0.15, g.root_chord)
    ok = check_shaft_fit_at_hinge(g, shaft_diameter_m=0.006, clearance_factor=1.10)
    assert ok.fits
    assert abs(ok.thickness_at_hinge_m - t25) < 1e-12
    # Oversized shaft must fail
    fail = check_shaft_fit_at_hinge(g, shaft_diameter_m=t25, clearance_factor=1.10)
    assert not fail.fits
