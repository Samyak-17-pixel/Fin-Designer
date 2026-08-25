"""Engineering report export — JSON, text, HTML (SRDS 3.13)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from auv_fin_design.domain.geometry.sizing import format_fin_dimensions_lines, geometry_to_dict

if TYPE_CHECKING:
    from auv_fin_design.application.pipeline import DesignResult


def design_result_payload(result: DesignResult) -> dict:
    """Complete serializable view of a design run — shared by GUI, JSON, and reports."""
    from auv_fin_design.domain.validation.design_diagnosis import diagnose_design

    h = result.hydro
    sens = None
    if result.sensitivity is not None:
        sens = {
            "baseline_M_design_Nm": result.sensitivity.baseline_M_design_Nm,
            "baseline_span_m": result.sensitivity.baseline_span_m,
            "points": [p.model_dump() for p in result.sensitivity.points],
            "equation_ids": list(result.sensitivity.equation_ids),
        }
    opt = None
    if result.optimization is not None:
        opt = {
            "available": result.optimization.available,
            "message": result.optimization.message,
            "best_drag": result.optimization.best_drag,
            "best_mass": result.optimization.best_mass,
            "best_params": result.optimization.best_params,
            "n_evaluations": result.optimization.n_evaluations,
        }
    return {
        "passed": result.passed,
        "diagnosis": diagnose_design(result).to_dict(),
        "airfoil": result.airfoil_name,
        "material": result.material_name,
        "inputs": {
            "length_m": result.vehicle.length,
            "diameter_m": result.vehicle.diameter,
            "mass_kg": result.vehicle.mass,
            "water": result.vehicle.water,
            "cg_fraction": result.vehicle.cg_fraction_of_length,
            "cb_fraction": result.vehicle.cb_fraction_of_length,
            "fin_root_le_fraction": result.vehicle.fin_root_le_fraction_of_length,
            "n_fins": result.vehicle.n_fins,
            "configuration": result.vehicle.configuration,
            "fin_clocking_deg": list(result.vehicle.fin_clocking_deg),
            "design_speed_mps": result.mission.design_speed,
            "max_speed_mps": result.mission.max_speed,
            "turning_radius_m": result.mission.turning_radius,
            "turn_establishment_s": result.mission.turn_establishment_time,
        },
        "control_requirement": result.control_req.model_dump(),
        "allocation": result.allocation.model_dump(),
        "hydrodynamics": {
            "speed_mps": h.speed,
            "Re_L": h.re_length,
            "Re_D": h.re_diameter,
            "flow_regime": h.flow_regime,
            "dynamic_pressure_Pa": h.dynamic_pressure,
            "cf_ittc": h.cf_ittc,
            "cd_frontal": h.cd_frontal,
            "drag_friction_N": h.drag_friction,
            "hull_drag_N": h.drag_total_hull,
            "X_udot": h.X_udot,
            "Y_vdot": h.Y_vdot,
            "Z_wdot": h.Z_wdot,
            "K_pdot": h.K_pdot,
            "M_qdot": h.M_qdot,
            "N_rdot": h.N_rdot,
            "yaw_damping": h.yaw_damping.model_dump(),
            "design_yaw_rate_rad_s": h.design_yaw_rate_rad_s,
            "design_lateral_speed_mps": h.design_lateral_speed_mps,
            "wake_fraction": h.wake_fraction,
            "cd_cross": h.cd_cross,
            "equation_ids": list(h.equation_ids),
        },
        "hydro_validation": result.hydro_validation.model_dump(),
        "geometry": geometry_to_dict(result.geometry),
        "center_of_pressure": result.center_of_pressure.model_dump(),
        "shaft_fit": result.shaft_fit.model_dump(),
        "aero": {
            "alpha_deg": result.aero.alpha_deg,
            "alpha_rad": result.aero.alpha_rad,
            "CL": result.aero.cl,
            "CL_alpha_2d": result.aero.cl_alpha_2d,
            "CL_alpha_3d": result.aero.cl_alpha_3d,
            "CL_max_2d": result.aero.cl_max_2d,
            "CD_profile": result.aero.cd_profile,
            "CD_induced": result.aero.cd_induced,
            "CD": result.aero.cd_total,
            "Cm": result.aero.cm,
            "stall_alpha_deg": result.aero.stall_alpha_deg,
            "stalled": result.aero.stalled,
            "equation_ids": list(result.aero.equation_ids),
        },
        "structure": {
            "cruise": result.structure_cruise.model_dump(),
            "aggressive": result.structure_aggressive.model_dump(),
            "emergency": result.structure_emergency.model_dump(),
        },
        "servo": result.servo_result.model_dump(),
        "manufacturing": result.manufacturing.model_dump(),
        "sensitivity": sens,
        "optimization": opt,
        "iteration_history": result.iteration_history,
        "geometry_violations": result.geometry_violations,
        "warnings": result.warnings,
        "equation_ids": result.equation_ids,
    }


def _payload(result: DesignResult) -> dict:
    """Alias for backward compatibility within this module."""
    return design_result_payload(result)


def write_json_report(result: DesignResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_payload(result), indent=2), encoding="utf-8")
    return path


def _geometry_text_lines(result: DesignResult) -> list[str]:
    lines = ["", *format_fin_dimensions_lines(result.geometry)]
    cp = result.center_of_pressure
    lines += [
        "",
        "DYNAMIC CENTER OF PRESSURE (strip Cp integration)",
        "-" * 40,
        f"x_cp / MAC from LE→TE: {cp.x_cp_le_frac:.4f} "
        f"({cp.x_cp_from_le_m:.6f} m = {cp.x_cp_from_le_m*1000:.2f} mm)",
        f"x_cp hinge frame: {cp.x_cp_hinge_m:.6f} m (= {cp.x_cp_hinge_m*1000:.2f} mm)",
        f"y_cp: {cp.y_cp_m*1000:.2f} mm",
        f"z_cp from root: {cp.z_cp_m:.6f} m (= {cp.z_cp_m*1000:.2f} mm)",
        f"Hinge arm / moment: {cp.hinge_arm_m*1000:.2f} mm / {cp.hinge_moment_nm:.4f} N·m",
        f"Verification: {cp.verification.status} — {cp.verification.message}",
        f"Note: {cp.note}",
    ]
    if cp.deflection is not None:
        md = cp.deflection
        lines += [
            "",
            "MAX DEFLECTION FOR MANEUVER (per fin)",
            "-" * 40,
            f"delta_required: {md.delta_required_deg:.3f} deg",
            f"delta_max_usable: {md.delta_max_usable_deg:.3f} deg",
            f"delta_margin: {md.delta_margin_deg:.3f} deg",
            f"Sufficient: {md.sufficient}",
        ]
    sf = result.shaft_fit
    lines += [
        "",
        "SHAFT FIT AT HINGE (25% chord)",
        "-" * 40,
        f"Airfoil width at 25%c: {sf.thickness_at_hinge_m*1000:.2f} mm",
        f"Shaft diameter: {sf.shaft_diameter_m*1000:.2f} mm",
        f"Required (≥{sf.clearance_factor:.2f}×): {sf.required_thickness_m*1000:.2f} mm",
        f"Radial clearance/side: {sf.radial_clearance_m*1000:.2f} mm",
        f"Fits: {sf.fits} — {sf.message}",
    ]
    return lines


def write_text_report(result: DesignResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    from auv_fin_design.domain.validation.design_diagnosis import diagnose_design

    hv = result.hydro_validation
    diagnosis = diagnose_design(result)
    lines = [
        "AUV Fin Design Engineering Report",
        "=" * 40,
        *diagnosis.format_lines(),
        "",
        f"Passed: {result.passed}",
        f"Airfoil: {result.airfoil_name}",
        f"Material: {result.material_name}",
        f"M_design: {result.control_req.M_design:.4f} N·m",
        f"Lift/fin: {result.allocation.lift_per_fin:.4f} N",
        *_geometry_text_lines(result),
        "",
        f"alpha: {result.aero.alpha_deg:.3f} deg",
        f"CL: {result.aero.cl:.4f}  CD: {result.aero.cd_total:.4f}",
        f"Authority margin: {hv.authority_margin:.3f}",
        f"Lift margin: {hv.lift_margin:.3f}",
        f"Cavitation σ: {hv.cavitation_number:.2f}",
        f"FoS aggressive: {result.structure_aggressive.fos_yield:.2f}",
        f"Servo util: {result.servo_result.utilization:.3f}",
        f"Shaft FoS: {result.servo_result.shaft_fos:.2f}",
        f"Process: {result.manufacturing.process} / {result.manufacturing.material}",
        "",
        "Warnings:",
        *(result.warnings or ["(none)"]),
        "",
        "Equation IDs:",
        ", ".join(result.equation_ids),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_html_report(result: DesignResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    from auv_fin_design.domain.validation.design_diagnosis import diagnose_design

    diagnosis = diagnose_design(result)
    status = "PASSED" if diagnosis.passed else f"FAILED ({diagnosis.failure_count} violations)"
    color = "#1b7f3a" if diagnosis.passed else "#b00020"
    g = result.geometry
    corners = ""
    if g.leading_edge_root:
        corners = f"""
<table>
<tr><th>Corner</th><th>X [m]</th><th>Z [m]</th></tr>
<tr><td>Leading Edge Root</td><td>{g.leading_edge_root.x:.6f}</td><td>{g.leading_edge_root.z:.6f}</td></tr>
<tr><td>Trailing Edge Root</td><td>{g.trailing_edge_root.x:.6f}</td><td>{g.trailing_edge_root.z:.6f}</td></tr>
<tr><td>Leading Edge Tip</td><td>{g.leading_edge_tip.x:.6f}</td><td>{g.leading_edge_tip.z:.6f}</td></tr>
<tr><td>Trailing Edge Tip</td><td>{g.trailing_edge_tip.x:.6f}</td><td>{g.trailing_edge_tip.z:.6f}</td></tr>
</table>
<p><em>Control-surface frame: origin at root hinge (25% chord). X chordwise (LE+), Z spanwise.</em></p>
"""
    sens_rows = ""
    if result.sensitivity:
        for p in result.sensitivity.points:
            sens_rows += (
                f"<tr><td>{p.parameter}</td><td>{p.perturbation:+.0%}</td>"
                f"<td>{p.delta_M_frac:+.2%}</td><td>{p.delta_span_frac:+.2%}</td>"
                f"<td>{'OK' if p.passed else 'FAIL'}</td></tr>"
            )

    viol_html = ""
    if diagnosis.issues:
        viol_items = "".join(
            f"<li><strong>[{i.category}]</strong> {i.message}"
            f"<ul>{''.join(f'<li>{c}</li>' for c in i.corrections)}</ul></li>"
            for i in diagnosis.issues
        )
        all_corr = list(dict.fromkeys(c for i in diagnosis.issues for c in i.corrections))
        corr_items = "".join(f"<li>{c}</li>" for c in all_corr)
        viol_html = f"""
<div class="card" style="border-left:4px solid {color}">
<h2>Design Diagnosis</h2>
<p><strong>{status}</strong></p>
<h3>All violations</h3>
<ol>{viol_items}</ol>
<h3>Suggested corrections</h3>
<ol>{corr_items}</ol>
</div>
"""
    else:
        viol_html = f"""
<div class="card" style="border-left:4px solid {color}">
<h2>Design Diagnosis</h2>
<p><strong>PASSED</strong> — all engineering checks satisfied.</p>
</div>
"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>AUV Fin Design Report</title>
<style>
body{{font-family:system-ui,sans-serif;margin:2rem;background:#f7f7f7;color:#222}}
h1{{color:{color}}} table{{border-collapse:collapse;background:#fff;margin:1rem 0}}
td,th{{border:1px solid #ccc;padding:.4rem .7rem;text-align:left}}
.card{{background:#fff;padding:1rem 1.25rem;border-radius:8px;margin-bottom:1rem;
box-shadow:0 1px 3px rgba(0,0,0,.08)}}
</style></head><body>
<h1>{status}</h1>
{viol_html}
<div class="card">
<h2>Summary</h2>
<ul>
<li>Airfoil: {result.airfoil_name}</li>
<li>Material: {result.material_name}</li>
<li>M_design: {result.control_req.M_design:.4f} N·m</li>
<li>α / CL / CD: {result.aero.alpha_deg:.2f}° / {result.aero.cl:.4f} / {result.aero.cd_total:.4f}</li>
<li>FoS (cruise/agg/emerg): {result.structure_cruise.fos_yield:.1f} /
{result.structure_aggressive.fos_yield:.1f} / {result.structure_emergency.fos_yield:.1f}</li>
<li>Servo util / shaft FoS: {result.servo_result.utilization:.3f} / {result.servo_result.shaft_fos:.1f}</li>
</ul>
</div>
<div class="card">
<h2>Final Complete Fin Dimensions</h2>
<ul>
<li>NACA Profile: {g.naca_profile}</li>
<li>Surface Area: {g.area:.6f} m² (= {g.area*1e6:.1f} mm²)</li>
<li>Span: {g.span:.6f} m (= {g.span*1000:.2f} mm)</li>
<li>Root Chord: {g.root_chord:.6f} m (= {g.root_chord*1000:.2f} mm)</li>
<li>Tip Chord: {g.tip_chord:.6f} m (= {g.tip_chord*1000:.2f} mm)</li>
<li>MAC: {g.mac:.6f} m (= {g.mac*1000:.2f} mm)</li>
<li>Aspect Ratio: {g.aspect_ratio:.4f}</li>
<li>Taper Ratio: {g.taper_ratio:.4f}</li>
<li>Sweep: {g.sweep_deg:.2f}°</li>
<li>Thickness Ratio (t/c): {g.thickness_ratio:.4f}</li>
<li>Root / Tip Max Thickness: {g.root_thickness*1000:.2f} / {g.tip_thickness*1000:.2f} mm</li>
<li>Shaft Diameter (root max width): {g.shaft_diameter*1000:.2f} mm</li>
<li>Est. Volume / Mass: {g.volume_est:.6e} m³ / {g.mass_est:.6f} kg</li>
</ul>
<p><strong>Summary (mm):</strong>
span = {g.span*1000:.2f} mm,
root chord = {g.root_chord*1000:.2f} mm,
tip chord = {g.tip_chord*1000:.2f} mm,
MAC = {g.mac*1000:.2f} mm</p>
{corners}
</div>
<div class="card">
<h2>Center of Pressure</h2>
<ul>
<li>x_cp / MAC (LE→TE): {result.center_of_pressure.x_cp_le_frac:.4f} ({result.center_of_pressure.x_cp_from_le_m*1000:.2f} mm)</li>
<li>x_cp hinge frame: {result.center_of_pressure.x_cp_hinge_m*1000:.2f} mm (shaft fixed at 25%c)</li>
<li>z_cp from root: {result.center_of_pressure.z_cp_m*1000:.2f} mm</li>
<li>Hinge moment: {result.center_of_pressure.hinge_moment_nm:.4f} N·m</li>
<li>Verification: {result.center_of_pressure.verification.status}</li>
</ul>
<p>{result.center_of_pressure.verification.message}</p>
<p><em>{result.center_of_pressure.note}</em></p>
{"<p><strong>Deflection:</strong> required %.3f° / usable %.3f° (margin %.3f°)</p>" % (result.center_of_pressure.deflection.delta_required_deg, result.center_of_pressure.deflection.delta_max_usable_deg, result.center_of_pressure.deflection.delta_margin_deg) if result.center_of_pressure.deflection else ""}
</div>
<div class="card">
<h2>Shaft Fit at Hinge (25% chord)</h2>
<ul>
<li>Airfoil width at 25%c: {result.shaft_fit.thickness_at_hinge_m*1000:.2f} mm</li>
<li>Shaft diameter: {result.shaft_fit.shaft_diameter_m*1000:.2f} mm</li>
<li>Required (≥{result.shaft_fit.clearance_factor:.2f}×): {result.shaft_fit.required_thickness_m*1000:.2f} mm</li>
<li>Radial clearance/side: {result.shaft_fit.radial_clearance_m*1000:.2f} mm</li>
<li>Fits: {"YES" if result.shaft_fit.fits else "NO"}</li>
</ul>
<p>{result.shaft_fit.message}</p>
</div>
<div class="card">
<h2>Hydrodynamic Validation</h2>
<ul>
<li>Lift margin: {result.hydro_validation.lift_margin:.3f}</li>
<li>Authority margin: {result.hydro_validation.authority_margin:.3f}</li>
<li>Stall margin: {result.hydro_validation.stall_margin_deg:.2f}°</li>
<li>Cavitation σ: {result.hydro_validation.cavitation_number:.2f}</li>
<li>L/D: {result.hydro_validation.lift_to_drag:.2f}</li>
</ul>
</div>
<div class="card">
<h2>Manufacturing</h2>
<ul>
<li>Process: {result.manufacturing.process}</li>
<li>Orientation: {result.manufacturing.orientation}</li>
<li>Infill: {result.manufacturing.infill_percent}%</li>
<li>Printable: {result.manufacturing.printable}</li>
</ul>
<p>{"<br/>".join(result.manufacturing.notes)}</p>
</div>
<div class="card">
<h2>Sensitivity (±10%)</h2>
<table><tr><th>Parameter</th><th>Δ</th><th>ΔM</th><th>Δspan</th><th>Pass</th></tr>
{sens_rows or "<tr><td colspan='5'>Not run</td></tr>"}
</table>
</div>
<div class="card">
<h2>Traceability</h2>
<p>{", ".join(result.equation_ids)}</p>
</div>
</body></html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def write_all_reports(result: DesignResult, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "json": write_json_report(result, out_dir / "engineering_report.json"),
        "txt": write_text_report(result, out_dir / "engineering_report.txt"),
        "html": write_html_report(result, out_dir / "engineering_report.html"),
    }
