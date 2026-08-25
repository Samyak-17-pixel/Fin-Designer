"""Tests for GUI view model and payload parity."""

from __future__ import annotations

from auv_fin_design.application.pipeline import load_golden_vehicle, run_design_pipeline
from auv_fin_design.domain.constants.materials import get_material
from auv_fin_design.domain.reporting.export import design_result_payload
from auv_fin_design.infrastructure.config.loader import load_defaults
from auv_fin_design.ui.gui.viewmodels.design_result_vm import DesignResultView


def test_design_result_payload_complete():
    v, m = load_golden_vehicle()
    r = run_design_pipeline(
        v,
        m,
        material=get_material("PLA"),
        defaults=load_defaults(),
        run_sensitivity=True,
        run_optimization=False,
    )
    p = design_result_payload(r)
    assert "yaw_damping" in p["hydrodynamics"]
    assert "control_requirement" in p
    assert "allocation" in p
    assert "cruise" in p["structure"]
    assert p["center_of_pressure"]["strips"]
    view = DesignResultView.from_result(r)
    assert view.payload == p
