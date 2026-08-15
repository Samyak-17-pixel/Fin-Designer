"""Tests for design diagnosis (violations + corrections)."""

from __future__ import annotations

from auv_fin_design.application.pipeline import load_golden_vehicle, run_design_pipeline
from auv_fin_design.domain.constants.materials import get_material
from auv_fin_design.domain.validation.design_diagnosis import diagnose_design
from auv_fin_design.infrastructure.config.loader import load_defaults


def test_diagnosis_pass_golden() -> None:
    v, m = load_golden_vehicle()
    d = load_defaults()
    r = run_design_pipeline(
        v, m, material=get_material("PLA"), defaults=d, run_sensitivity=False
    )
    diag = diagnose_design(r)
    assert diag.passed is r.passed
    if r.passed:
        assert diag.failure_count == 0
        text = "\n".join(diag.format_lines())
        assert "PASSED" in text


def test_diagnosis_lists_violations_when_span_tight() -> None:
    v, m = load_golden_vehicle()
    d = load_defaults()
    d["geometry_constraints"]["max_span_over_diameter"] = 0.30
    r = run_design_pipeline(
        v, m, material=get_material("PLA"), defaults=d, run_sensitivity=False
    )
    diag = diagnose_design(r)
    assert not diag.passed
    assert diag.failure_count >= 1
    cats = {i.category for i in diag.issues}
    assert any("Geometry" in c or "Hydro" in c or "Maneuver" in c for c in cats)
    text = "\n".join(diag.format_lines())
    assert "ALL VIOLATIONS" in text
    assert "SUGGESTED CORRECTIONS" in text
    assert any(i.corrections for i in diag.issues)
