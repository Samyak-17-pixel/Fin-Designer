"""Yaw damping polynomial tests."""

from __future__ import annotations

import math

from auv_fin_design.domain.hydrodynamics.estimator import estimate_hydrodynamics
from auv_fin_design.domain.hydrodynamics.yaw_damping import (
    bootstrap_yaw_damping_from_crossflow,
    crossflow_yaw_reference,
    estimate_yaw_damping_coefficients,
    yaw_hydrodynamic_moment,
)
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


def test_yaw_polynomial_matches_crossflow_at_design_r():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    m = MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=30.0)
    h = estimate_hydrodynamics(v, m)
    r_op = 1.5 / 6.0
    n_cross = crossflow_yaw_reference(
        v.fluid.density, v.diameter, v.length, cd_cross=1.0
    )
    # Full polynomial at r_op, v=0: N_r*r + N_rrr*r³
    c = h.yaw_damping
    m_expected = c.N_r * r_op + c.N_rrr * r_op**3
    m_new = yaw_hydrodynamic_moment(
        h.design_lateral_speed_mps, r_op, h.yaw_damping
    )
    assert abs(m_new - m_expected) / abs(m_expected) < 0.01


def test_bootstrap_yaw_damping_all_terms():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    m = MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=30.0)
    h = estimate_hydrodynamics(v, m)
    c = h.yaw_damping
    assert c.N_rrr != 0.0
    assert c.N_r != 0.0
    assert c.N_vvr != 0.0
    assert c.N_vrr != 0.0
    assert c.N_vvv != 0.0
    # CG at mid-length → geometric N_v contribution is zero; bootstrap N_v still non-zero
    assert c.N_v != 0.0


def test_bootstrap_matches_helper():
    rho = 998.2
    d, L = 0.1685, 1.35
    r_ref, v_ref = 0.25, 1.5
    n_cross = crossflow_yaw_reference(rho, d, L)
    n_rrr = -n_cross / r_ref
    boot = bootstrap_yaw_damping_from_crossflow(
        n_rrr,
        r_ref_rad_s=r_ref,
        v_ref_mps=v_ref,
        x_cg_m=0.5 * L,
        length_m=L,
        rho=rho,
        diameter_m=d,
        cd_cross=1.0,
    )
    coeffs, _, _ = estimate_yaw_damping_coefficients(
        rho=rho,
        diameter_m=d,
        length_m=L,
        design_speed_mps=v_ref,
        turning_radius_m=v_ref / r_ref,
        x_cg_m=0.5 * L,
        yaw_cfg={"estimate_all_terms": True},
    )
    for key in ("N_r", "N_v", "N_vvr", "N_vrr", "N_vvv"):
        assert abs(getattr(coeffs, key) - boot[key]) / max(abs(boot[key]), 1e-30) < 1e-9


def test_yaw_polynomial_v_terms():
    from auv_fin_design.domain.hydrodynamics.yaw_damping import YawDampingCoefficients

    c = YawDampingCoefficients(
        N_r=1.0,
        N_v=2.0,
        N_rrr=-0.5,
        N_vvr=0.1,
        N_vrr=0.2,
        N_vvv=0.05,
    )
    v, r = 0.3, 0.25
    expected = (
        c.N_r * r
        + c.N_v * v
        + c.N_rrr * r**3
        + c.N_vvr * v**2 * r
        + c.N_vrr * v * r**2
        + c.N_vvv * v**3
    )
    assert abs(yaw_hydrodynamic_moment(v, r, c) - expected) < 1e-12


def test_cg_offset_adds_N_v():
    rho = 998.2
    d, L = 0.1685, 1.35
    coeffs_mid, _, _ = estimate_yaw_damping_coefficients(
        rho=rho,
        diameter_m=d,
        length_m=L,
        design_speed_mps=1.5,
        turning_radius_m=6.0,
        x_cg_m=0.5 * L,
    )
    coeffs_aft, _, _ = estimate_yaw_damping_coefficients(
        rho=rho,
        diameter_m=d,
        length_m=L,
        design_speed_mps=1.5,
        turning_radius_m=6.0,
        x_cg_m=0.55 * L,
    )
    assert coeffs_aft.N_v != coeffs_mid.N_v
