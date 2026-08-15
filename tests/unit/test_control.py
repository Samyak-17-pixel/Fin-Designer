"""Maneuvering and allocation tests."""

from __future__ import annotations

import math

from auv_fin_design.domain.control.allocation import allocate_x_tail_yaw
from auv_fin_design.domain.control.maneuvering import compute_control_requirement
from auv_fin_design.domain.hydrodynamics.estimator import estimate_hydrodynamics
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


def test_EQ_MAN_golden():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    m = MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=30.0)
    h = estimate_hydrodynamics(v, m)
    req = compute_control_requirement(v, h, m, control_margin=0.25)
    r = 1.5 / 6.0
    assert abs(req.r_target - r) / r < 0.01
    assert abs(req.r_dot - r / 30.0) / req.r_dot < 0.01
    assert req.M_design == req.M_raw_governing * 1.25
    assert req.M_design > 0


def test_EQ_ALLOC_x_tail():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    m = MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=30.0)
    h = estimate_hydrodynamics(v, m)
    req = compute_control_requirement(v, h, m)
    c_r = 0.08
    alloc = allocate_x_tail_yaw(v, req, root_chord=c_r)
    x_qc = v.x_fin_root_le + 0.25 * c_r
    ell = abs(x_qc - v.x_cg)
    assert abs(alloc.lever_arm - ell) / ell < 0.001
    proj = math.sin(math.radians(45))
    lift = req.M_design / (4 * ell * proj)
    assert abs(alloc.lift_per_fin - lift) / lift < 0.001
