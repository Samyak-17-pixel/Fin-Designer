"""Golden vehicle integration / regression benchmark."""

from __future__ import annotations

from auv_fin_design.application.pipeline import (
    load_golden_servo,
    load_golden_vehicle,
    run_design_pipeline,
)
from auv_fin_design.domain.airfoil.database import AirfoilDatabase
from auv_fin_design.infrastructure.config.loader import repo_root


def test_golden_vehicle_pipeline_runs():
    vehicle, mission = load_golden_vehicle()
    db = AirfoilDatabase(repo_root() / "data")
    assert len(db.names()) >= 1
    result = run_design_pipeline(
        vehicle,
        mission,
        airfoil_db=db,
        servo=load_golden_servo(),
        run_sensitivity=False,
        run_optimization=False,
    )
    assert result.control_req.M_design > 0
    assert result.allocation.lift_per_fin > 0
    assert result.geometry.span > 0
    assert result.geometry.area > 0
    assert result.aero.cl > 0
    assert result.allocation.lever_arm > 0.3
    assert result.hydro_validation is not None
    result2 = run_design_pipeline(
        vehicle,
        mission,
        airfoil_db=db,
        airfoil_name=result.airfoil_name,
        servo=load_golden_servo(),
        run_sensitivity=False,
        run_optimization=False,
    )
    assert abs(result2.geometry.area - result.geometry.area) / result.geometry.area < 0.001
    assert abs(result2.control_req.M_design - result.control_req.M_design) / result.control_req.M_design < 0.01


def test_airfoil_log_re_interpolation():
    db = AirfoilDatabase(repo_root() / "data")
    entry = db.get("NACA0012")
    p = entry.polar_at_re(160_000)
    assert 100_000 < p.reynolds < 200_000 or abs(p.reynolds - 160_000) < 1.0
    # blended polar should have data
    assert len(p.alpha_deg) > 10
