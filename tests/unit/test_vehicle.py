"""Unit tests for vehicle model equations."""

from __future__ import annotations

import math

from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel


def test_EQ_VEH_001_to_006_golden():
    v = VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water="freshwater")
    assert abs(v.radius - 0.08425) < 1e-12
    assert abs(v.cross_section_area - math.pi * v.radius**2) < 1e-12
    assert abs(v.wetted_area - math.pi * v.diameter * v.length) < 1e-12
    assert abs(v.volume - math.pi * v.radius**2 * v.length) < 1e-12
    assert abs(v.x_cg - 0.675) < 1e-12
    assert abs(v.Ix - 0.5 * v.mass * v.radius**2) / v.Ix < 0.01
    iz = (1.0 / 12.0) * v.mass * (3 * v.radius**2 + v.length**2)
    assert abs(v.Iz - iz) / iz < 0.01
    assert v.fin_root_le_fraction_of_length == 0.92
    assert v.x_fin_root_le == 0.92 * 1.35


def test_EQ_FLUID_001():
    v = VehicleModel(length=1.0, diameter=0.1, mass=1.0, water="freshwater")
    assert v.fluid.density == 998.2
    assert abs(v.fluid.kinematic_viscosity - 1.004e-6) < 1e-12


def test_EQ_FLUID_002():
    v = VehicleModel(length=1.0, diameter=0.1, mass=1.0, water="seawater")
    assert v.fluid.density == 1025.0
