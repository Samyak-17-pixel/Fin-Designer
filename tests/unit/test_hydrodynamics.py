"""Hydrodynamic equation tests."""

from __future__ import annotations

import math

from auv_fin_design.domain.hydrodynamics.estimator import (
    classify_flow_regime,
    estimate_hydrodynamics,
    ittc_1957_cf,
)
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


def test_EQ_HYD_003_regime():
    assert classify_flow_regime(1e5) == "laminar"
    assert classify_flow_regime(1e6) == "transitional"
    assert classify_flow_regime(5e6) == "turbulent"


def test_EQ_HYD_005_ittc():
    cf = ittc_1957_cf(1.0e6)
    expected = 0.075 / (math.log10(1.0e6) - 2.0) ** 2
    assert abs(cf - expected) / expected < 1e-9


def test_EQ_HYD_golden_added_mass_and_damping():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    m = MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=30.0)
    h = estimate_hydrodynamics(v, m)
    rho = v.fluid.density
    R = v.radius
    L = v.length
    y = rho * math.pi * R**2 * L
    n = rho * math.pi * R**2 * L**3 / 12.0
    assert abs(h.Y_vdot - y) / y < 0.01
    assert abs(h.N_rdot - n) / n < 0.01
    nrr = -(1.0 / 32.0) * rho * 1.0 * v.diameter * L**4
    assert abs(h.N_r_abs_r - nrr) / abs(nrr) < 0.01
    r_op = 1.5 / 6.0
    assert abs(h.N_r - 2 * nrr * abs(r_op)) / abs(h.N_r) < 0.01
    assert h.wake_fraction == 0.0
