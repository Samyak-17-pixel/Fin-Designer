"""Manufacturing recommendations — SRDS 3.11 / Software Outputs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry
from auv_fin_design.domain.constants.materials import MaterialProperties


class ManufacturingRecommendations(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    process: str
    material: str
    layer_height_mm: float
    wall_loops: int
    infill_percent: float
    orientation: str
    min_feature_mm: float
    post_process: tuple[str, ...]
    notes: tuple[str, ...]
    printable: bool


def recommend_manufacturing(
    geom: CandidateFinGeometry,
    material: MaterialProperties,
    *,
    min_wall_m: float = 0.0012,
    min_te_m: float = 0.0008,
) -> ManufacturingRecommendations:
    tip_t_mm = geom.tip_thickness * 1000.0
    notes: list[str] = []
    printable = True
    if geom.tip_thickness < min_wall_m:
        printable = False
        notes.append(f"Tip thickness {tip_t_mm:.2f} mm below min wall {min_wall_m*1000:.1f} mm")
    if geom.tip_chord * 0.02 < min_te_m:
        notes.append("Consider thickening trailing edge for FDM printability")
    if geom.aspect_ratio < 1.0:
        notes.append("Low AR fin: print with span vertical for better layer bonding on root")
    notes.append("Sand leading edge after print; seal with epoxy for water use")
    notes.append("Insert stainless shaft sleeve before bonding fin to shaft")

    return ManufacturingRecommendations(
        process="FDM 3D printing",
        material=material.name,
        layer_height_mm=0.2,
        wall_loops=4,
        infill_percent=40.0 if geom.span < 0.12 else 30.0,
        orientation="Span along Z (build vertical); root on build plate",
        min_feature_mm=min(tip_t_mm, geom.tip_chord * 1000.0 * 0.02),
        post_process=(
            "Support removal",
            "Sand LE/TE",
            "Epoxy seal coat",
            "Shaft sleeve bond",
        ),
        notes=tuple(notes),
        printable=printable,
    )
