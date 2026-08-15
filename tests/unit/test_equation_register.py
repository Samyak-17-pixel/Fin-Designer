"""Equation register presence and schema smoke test."""

from __future__ import annotations

from auv_fin_design.infrastructure.config.loader import load_equation_register


def test_equation_register_loads():
    reg = load_equation_register()
    assert "equations" in reg
    ids = {e["id"] for e in reg["equations"]}
    required = {
        "EQ-FLUID-001",
        "EQ-VEH-003",
        "EQ-HYD-015",
        "EQ-MAN-007",
        "EQ-ALLOC-004",
        "EQ-AERO-001",
        "EQ-GEO-001",
        "EQ-STR-001",
    }
    assert required.issubset(ids)
    for e in reg["equations"]:
        assert "status" in e
        assert "reference" in e
        assert "implementation_module" in e
