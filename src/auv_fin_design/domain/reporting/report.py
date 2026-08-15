"""Simple engineering report writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auv_fin_design.application.pipeline import DesignResult
from auv_fin_design.domain.geometry.sizing import geometry_to_dict


def result_to_dict(result: DesignResult) -> dict[str, Any]:
    return {
        "passed": result.passed,
        "airfoil": result.airfoil_name,
        "vehicle": {
            "length_m": result.vehicle.length,
            "diameter_m": result.vehicle.diameter,
            "mass_kg": result.vehicle.mass,
            "water": result.vehicle.water,
            "fin_root_le_fraction": result.vehicle.fin_root_le_fraction_of_length,
        },
        "mission": {
            "design_speed_mps": result.mission.design_speed,
            "turning_radius_m": result.mission.turning_radius,
            "turn_establishment_s": result.mission.turn_establishment_time,
        },
        "control": {
            "M_design_Nm": result.control_req.M_design,
            "M_transient_Nm": result.control_req.M_transient,
            "M_steady_Nm": result.control_req.M_steady,
            "lift_per_fin_N": result.allocation.lift_per_fin,
            "lever_arm_m": result.allocation.lever_arm,
        },
        "geometry": geometry_to_dict(result.geometry),
        "center_of_pressure": result.center_of_pressure.model_dump(),
        "shaft_fit": result.shaft_fit.model_dump(),
        "aero": {
            "alpha_deg": result.aero.alpha_deg,
            "CL": result.aero.cl,
            "CD": result.aero.cd_total,
            "stall_alpha_deg": result.aero.stall_alpha_deg,
        },
        "structure": {
            "FoS_cruise": result.structure_cruise.fos_yield,
            "FoS_aggressive": result.structure_aggressive.fos_yield,
            "FoS_emergency": result.structure_emergency.fos_yield,
        },
        "servo": {
            "utilization": result.servo_result.utilization,
            "hinge_moment_Nm": result.servo_result.hinge_moment,
        },
        "geometry_violations": result.geometry_violations,
        "warnings": result.warnings,
        "equation_ids": result.equation_ids,
    }


def write_json_report(result: DesignResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return path


def write_markdown_report(result: DesignResult, path: Path) -> Path:
    d = result_to_dict(result)
    g = d["geometry"]
    frame = g["control_surface_frame"]
    lines = [
        "# AUV Fin Design Report",
        "",
        f"**Status:** {'PASSED' if d['passed'] else 'FAILED'}",
        f"**Airfoil:** {d['airfoil']}",
        "",
        "## Control",
        f"- Design moment: {d['control']['M_design_Nm']:.4f} N·m",
        f"- Lift per fin: {d['control']['lift_per_fin_N']:.4f} N",
        f"- Lever arm: {d['control']['lever_arm_m']:.4f} m",
        "",
        "## Final Complete Fin Dimensions",
        f"- NACA Profile: {g['naca_profile']}",
        f"- Surface Area: {g['surface_area_m2']:.6f} m² (= {g['surface_area_mm2']:.1f} mm²)",
        f"- Span: {g['span_m']:.6f} m (= {g['span_mm']:.2f} mm)",
        f"- Root chord: {g['root_chord_m']:.6f} m (= {g['root_chord_mm']:.2f} mm)",
        f"- Tip chord: {g['tip_chord_m']:.6f} m (= {g['tip_chord_mm']:.2f} mm)",
        f"- AR / taper / sweep: {g['aspect_ratio']:.4f} / {g['taper_ratio']:.4f} / {g['sweep_deg']:.2f}°",
        f"- MAC: {g['mac_m']:.6f} m (= {g['mac_mm']:.2f} mm)",
        f"- Root / tip thickness: {g['root_thickness_mm']:.2f} / {g['tip_thickness_mm']:.2f} mm",
        f"- Shaft diameter: {g['shaft_diameter_mm']:.2f} mm",
        f"- Est. mass: {g['mass_est_kg']:.6f} kg",
        "",
        "### Summary (mm)",
        f"- span = {g['span_mm']:.2f} mm",
        f"- root chord = {g['root_chord_mm']:.2f} mm",
        f"- tip chord = {g['tip_chord_mm']:.2f} mm",
        f"- MAC = {g['mac_mm']:.2f} mm",
        "",
        "### Control Surface Geometry (hinge frame)",
        f"- {frame['note']}",
    ]
    for key, label in (
        ("leading_edge_root", "Leading Edge Root"),
        ("trailing_edge_root", "Trailing Edge Root"),
        ("leading_edge_tip", "Leading Edge Tip"),
        ("trailing_edge_tip", "Trailing Edge Tip"),
    ):
        pt = frame.get(key)
        if pt:
            lines.append(
                f"- {label}: X={pt['x_m']:.6f} m ({pt['x_mm']:.2f} mm), "
                f"Z={pt['z_m']:.6f} m ({pt['z_mm']:.2f} mm)"
            )
    cp = d["center_of_pressure"]
    lines += [
        "",
        "## Dynamic Center of Pressure",
        f"- x_cp / MAC (LE→TE): {cp['x_cp_le_frac']:.4f} ({cp['x_cp_from_le_m']*1000:.2f} mm)",
        f"- x_cp hinge frame: {cp['x_cp_hinge_m']*1000:.2f} mm",
        f"- z_cp from root: {cp['z_cp_m']*1000:.2f} mm",
        f"- Hinge moment: {cp['hinge_moment_nm']:.4f} N·m",
        f"- Verification: {cp['verification']['status']} — {cp['verification']['message']}",
        f"- {cp['note']}",
    ]
    if cp.get("deflection"):
        md = cp["deflection"]
        lines += [
            "",
            "## Max Deflection for Maneuver",
            f"- delta_required: {md['delta_required_deg']:.3f} deg",
            f"- delta_max_usable: {md['delta_max_usable_deg']:.3f} deg",
            f"- delta_margin: {md['delta_margin_deg']:.3f} deg",
            f"- Sufficient: {md['sufficient']}",
        ]
    sf = d["shaft_fit"]
    lines += [
        "",
        "## Shaft Fit at Hinge (25% chord)",
        f"- Width at 25%c: {sf['thickness_at_hinge_m']*1000:.2f} mm",
        f"- Shaft OD: {sf['shaft_diameter_m']*1000:.2f} mm",
        f"- Required (≥{sf['clearance_factor']:.2f}×): {sf['required_thickness_m']*1000:.2f} mm",
        f"- Fits: {sf['fits']} — {sf['message']}",
    ]
    lines += [
        "",
        "## Aero",
        f"- α: {d['aero']['alpha_deg']:.3f}°",
        f"- CL / CD: {d['aero']['CL']:.4f} / {d['aero']['CD']:.4f}",
        "",
        "## Structure / Servo",
        f"- FoS (cruise/agg/emerg): {d['structure']['FoS_cruise']:.2f} / "
        f"{d['structure']['FoS_aggressive']:.2f} / {d['structure']['FoS_emergency']:.2f}",
        f"- Servo utilization: {d['servo']['utilization']:.3f}",
        "",
        "## Violations",
        *[f"- {v}" for v in (d["geometry_violations"] or ["(none)"])],
        "",
        "## Warnings",
        *[f"- {w}" for w in (d["warnings"] or ["(none)"])],
        "",
        "## Equation IDs",
        ", ".join(d["equation_ids"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
