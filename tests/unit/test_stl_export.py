"""STL export smoke test."""

from __future__ import annotations

from pathlib import Path

from auv_fin_design.domain.geometry.sizing import size_fin
from auv_fin_design.domain.manufacturing.stl_export import export_fin_stl


def test_export_fin_stl(tmp_path: Path):
    geom = size_fin(5.0, 1000.0, cl=0.4, aspect_ratio=1.5, taper_ratio=0.5, thickness_ratio=0.15)
    path = export_fin_stl(geom, tmp_path / "fin.stl", naca_code="0015")
    text = path.read_text(encoding="utf-8")
    assert text.startswith("solid")
    assert "facet normal" in text
    assert text.strip().endswith("endsolid auv_fin")
