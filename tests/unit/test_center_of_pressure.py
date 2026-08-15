"""Unit tests for dynamic center-of-pressure module."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from auv_fin_design.domain.center_of_pressure import (
    CoPSolverConfig,
    solve_center_of_pressure,
)
from auv_fin_design.domain.center_of_pressure.exceptions import CoPDataError
from auv_fin_design.domain.center_of_pressure.pressure_integrator import integrate_chordwise
from auv_fin_design.domain.center_of_pressure.models import PressureDistribution
from auv_fin_design.domain.center_of_pressure.xfoil_provider import XfoilProvider
from auv_fin_design.domain.geometry.sizing import build_fin_from_planform
from auv_fin_design.infrastructure.config.loader import repo_root


def _rect_geom(span=0.1, chord=0.1):
    return build_fin_from_planform(
        root_chord=chord, tip_chord=chord, span=span, thickness_ratio=0.15, naca_profile="0015"
    )


def _taper_geom():
    return build_fin_from_planform(
        root_chord=0.12, tip_chord=0.06, span=0.09, thickness_ratio=0.15, naca_profile="0015"
    )


@pytest.fixture
def cfg():
    return CoPSolverConfig(n_strips=20)


def test_rectangular_fin_cop(cfg):
    g = _rect_geom()
    r = solve_center_of_pressure(
        g,
        airfoil="naca0015",
        dynamic_pressure=1000.0,
        speed_mps=1.5,
        nu=1e-6,
        alpha_deg=5.0,
        cm_polar=0.0,
        cl_polar=0.4,
        config=cfg,
    )
    assert r.total_lift_n > 0
    assert 0.0 < r.x_cp_le_frac < 1.0
    assert abs(r.z_cp_m - 0.5 * g.span) / g.span < 0.05  # near mid-span for rectangle
    assert r.verification.status in ("PASS", "WARNING", "FAIL")


def test_tapered_fin_cop(cfg):
    g = _taper_geom()
    r = solve_center_of_pressure(
        g,
        airfoil="naca0015",
        dynamic_pressure=1000.0,
        speed_mps=1.5,
        nu=1e-6,
        alpha_deg=4.0,
        cm_polar=0.0,
        cl_polar=0.35,
        config=cfg,
        lift_required_n=2.0,
        cl_alpha_2d_per_rad=2 * np.pi,
        stall_alpha_deg=12.0,
        stall_margin_deg=5.0,
    )
    assert r.z_cp_m < 0.5 * g.span  # taper shifts load inboard
    assert r.deflection is not None
    assert r.deflection.delta_required_deg > 0


def test_zero_alpha_near_zero_lift(cfg):
    g = _rect_geom()
    r = solve_center_of_pressure(
        g,
        airfoil="naca0012",
        dynamic_pressure=1000.0,
        speed_mps=1.0,
        nu=1e-6,
        alpha_deg=0.0,
        cm_polar=0.0,
        cl_polar=0.0,
        config=cfg,
    )
    assert abs(r.total_lift_n) < 1e-6
    assert abs(r.x_cp_le_frac - 0.25) < 1e-6


def test_high_and_low_reynolds(cfg):
    g = _rect_geom()
    for re_speed in (0.5, 3.0):
        r = solve_center_of_pressure(
            g,
            airfoil="naca0018",
            dynamic_pressure=0.5 * 998 * re_speed**2,
            speed_mps=re_speed,
            nu=1e-6,
            alpha_deg=3.0,
            cm_polar=0.0,
            cl_polar=0.2,
            config=cfg,
        )
        assert r.total_lift_n > 0


def test_near_stall_alpha(cfg):
    g = _rect_geom()
    r = solve_center_of_pressure(
        g,
        airfoil="naca0015",
        dynamic_pressure=1000.0,
        speed_mps=1.5,
        nu=1e-6,
        alpha_deg=14.0,
        cm_polar=-0.02,
        cl_polar=0.8,
        config=cfg,
    )
    assert r.total_lift_n > 0


def test_missing_cp_archive():
    g = _rect_geom()
    with pytest.raises(CoPDataError):
        solve_center_of_pressure(
            g,
            airfoil="naca9999",
            dynamic_pressure=1000.0,
            speed_mps=1.0,
            nu=1e-6,
            alpha_deg=2.0,
            cm_polar=0.0,
            cl_polar=0.1,
            config=CoPSolverConfig(n_strips=8),
        )


def test_provider_interpolation():
    p = XfoilProvider()
    d1 = p.load_pressure_distribution("naca0015", 1.0e5, 2.0)
    d2 = p.load_pressure_distribution("naca0015", 1.5e5, 2.5)
    assert len(d1.x_c) > 10
    assert len(d2.dcp) == len(d2.x_c)


def test_chordwise_integration_flat_plate_like():
    x = np.linspace(1e-4, 1.0, 200)
    alpha = np.radians(5.0)
    dcp = 2.0 * alpha * np.sqrt((1.0 - x) / x)
    pd = PressureDistribution(
        airfoil="test",
        reynolds=1e5,
        alpha_deg=5.0,
        x_c=tuple(float(v) for v in x),
        cp_upper=tuple(float(v) for v in -0.5 * dcp),
        cp_lower=tuple(float(v) for v in 0.5 * dcp),
    )
    integ = integrate_chordwise(pd)
    assert integ.cn > 0
    assert abs(integ.x_cp_c - 0.25) < 0.02


def test_strip_convergence():
    g = _rect_geom()
    lifts = []
    for n in (10, 20, 40):
        r = solve_center_of_pressure(
            g,
            airfoil="naca0015",
            dynamic_pressure=1000.0,
            speed_mps=1.5,
            nu=1e-6,
            alpha_deg=5.0,
            cm_polar=0.0,
            cl_polar=0.4,
            config=CoPSolverConfig(n_strips=n),
        )
        lifts.append(r.total_lift_n)
    assert abs(lifts[-1] - lifts[-2]) / lifts[-1] < 0.05


def test_regression_benchmark():
    path = repo_root() / "benchmarks" / "center_of_pressure_reference.json"
    if not path.exists():
        pytest.skip("benchmark not generated yet")
    ref = json.loads(path.read_text(encoding="utf-8"))
    g = build_fin_from_planform(
        root_chord=ref["inputs"]["root_chord_m"],
        tip_chord=ref["inputs"]["tip_chord_m"],
        span=ref["inputs"]["span_m"],
        thickness_ratio=ref["inputs"]["thickness_ratio"],
        naca_profile="0015",
    )
    r = solve_center_of_pressure(
        g,
        airfoil=ref["inputs"]["airfoil"],
        dynamic_pressure=ref["inputs"]["dynamic_pressure_pa"],
        speed_mps=ref["inputs"]["speed_mps"],
        nu=ref["inputs"]["nu"],
        alpha_deg=ref["inputs"]["alpha_deg"],
        cm_polar=0.0,
        cl_polar=0.4,
        config=CoPSolverConfig(n_strips=ref["inputs"]["n_strips"]),
    )
    tol = ref["tolerance"]
    assert abs(r.x_cp_le_frac - ref["expected"]["x_cp_le_frac"]) < tol["x_cp_le_frac"]
    assert abs(r.z_cp_m - ref["expected"]["z_cp_m"]) / max(ref["expected"]["z_cp_m"], 1e-9) < tol["z_cp_rel"]
    assert abs(r.total_lift_n - ref["expected"]["total_lift_n"]) / max(
        abs(ref["expected"]["total_lift_n"]), 1e-9
    ) < tol["lift_rel"]
