"""Additional integration tests for full SRDS pipeline."""

from __future__ import annotations

from pathlib import Path

from auv_fin_design.adapters.export_bundle import export_simulation_bundle
from auv_fin_design.application.pipeline import load_golden_vehicle, run_design_pipeline
from auv_fin_design.domain.constants.materials import get_material
from auv_fin_design.domain.reporting.export import write_all_reports
from auv_fin_design.infrastructure.config.loader import load_defaults, repo_root


def test_golden_passes_with_default_packaging():
    vehicle, mission = load_golden_vehicle()
    assert mission.max_speed is not None and mission.max_speed >= mission.design_speed
    result = run_design_pipeline(
        vehicle,
        mission,
        material=get_material("PLA"),
        run_sensitivity=False,
        run_optimization=False,
    )
    assert result.hydro_validation.overall_ok
    assert result.manufacturing.printable
    assert result.passed
    assert result.material_name == "PLA"


def test_sensitivity_runs():
    vehicle, mission = load_golden_vehicle()
    result = run_design_pipeline(
        vehicle, mission, run_sensitivity=True, run_optimization=False
    )
    assert result.sensitivity is not None
    assert len(result.sensitivity.points) == 6  # 3 params × ±10%


def test_exports_bundle_and_reports(tmp_path: Path):
    vehicle, mission = load_golden_vehicle()
    result = run_design_pipeline(
        vehicle, mission, run_sensitivity=False, run_optimization=False
    )
    reports = write_all_reports(result, tmp_path / "reports")
    assert reports["json"].exists()
    assert reports["html"].exists()
    paths = export_simulation_bundle(result, tmp_path / "sim")
    assert paths["stl"].exists()
    assert paths["gazebo_sdf"].exists()
    assert paths["ros2_urdf"].exists()
    assert paths["step"].exists()
    assert paths["fusion360"].exists()


def test_material_petg():
    vehicle, mission = load_golden_vehicle()
    result = run_design_pipeline(
        vehicle,
        mission,
        material=get_material("PETG"),
        run_sensitivity=False,
        run_optimization=False,
    )
    assert result.material_name == "PETG"


def test_optional_dimension_override():
    from auv_fin_design.application.pipeline import GeometryOverride

    vehicle, mission = load_golden_vehicle()
    result = run_design_pipeline(
        vehicle,
        mission,
        geometry_override=GeometryOverride(root_chord_m=0.12, span_m=0.08),
        run_sensitivity=False,
        run_optimization=False,
    )
    assert abs(result.geometry.root_chord - 0.12) < 1e-9
    assert abs(result.geometry.span - 0.08) < 1e-9
    assert any("dimension overrides" in w for w in result.warnings)
