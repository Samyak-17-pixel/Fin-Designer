"""CLI entrypoints for analysis and GUI launch."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="AUV Fin Design Suite")
    parser.add_argument("--golden", action="store_true", help="Run golden vehicle design (JSON)")
    parser.add_argument("--gui", action="store_true", help="Launch desktop GUI")
    parser.add_argument("--airfoil", type=str, default=None, help="Force airfoil folder name")
    parser.add_argument("--material", type=str, default="PLA", help="Material name")
    parser.add_argument(
        "--max-span-over-d",
        type=float,
        default=None,
        help="Override max span / diameter packaging limit",
    )
    parser.add_argument("--optimize", action="store_true", help="Run NSGA-II after design")
    parser.add_argument("--no-sensitivity", action="store_true", help="Skip sensitivity sweep")
    parser.add_argument("--export-all", action="store_true", help="Write reports + CAD/sim bundle")
    args = parser.parse_args()

    if args.gui:
        from auv_fin_design.ui.app import main as gui_main

        gui_main()
        return

    from auv_fin_design.adapters.export_bundle import export_simulation_bundle
    from auv_fin_design.application.pipeline import (
        load_golden_servo,
        load_golden_vehicle,
        run_design_pipeline,
    )
    from auv_fin_design.domain.constants.materials import get_material
    from auv_fin_design.domain.geometry.sizing import geometry_to_dict
    from auv_fin_design.domain.reporting.export import write_all_reports
    from auv_fin_design.domain.validation.design_diagnosis import diagnose_design
    from auv_fin_design.infrastructure.config.loader import load_defaults, repo_root

    vehicle, mission = load_golden_vehicle()
    defaults = load_defaults()
    if args.max_span_over_d is not None:
        defaults["geometry_constraints"]["max_span_over_diameter"] = args.max_span_over_d
    result = run_design_pipeline(
        vehicle,
        mission,
        material=get_material(args.material),
        servo=load_golden_servo(),
        airfoil_name=args.airfoil,
        defaults=defaults,
        run_sensitivity=not args.no_sensitivity,
        run_optimization=args.optimize,
    )
    out = {
        "passed": result.passed,
        "diagnosis": diagnose_design(result).to_dict(),
        "airfoil": result.airfoil_name,
        "material": result.material_name,
        "geometry": geometry_to_dict(result.geometry),
        "center_of_pressure": result.center_of_pressure.model_dump(),
        "shaft_fit": result.shaft_fit.model_dump(),
        "M_design_Nm": result.control_req.M_design,
        "lift_per_fin_N": result.allocation.lift_per_fin,
        "alpha_deg": result.aero.alpha_deg,
        "CL": result.aero.cl,
        "CD": result.aero.cd_total,
        "authority_margin": result.hydro_validation.authority_margin,
        "FoS_aggressive": result.structure_aggressive.fos_yield,
        "servo_util": result.servo_result.utilization,
        "geometry_violations": result.geometry_violations,
        "warnings": result.warnings,
    }
    print(json.dumps(out, indent=2))
    if args.export_all:
        write_all_reports(result, repo_root() / "reports")
        export_simulation_bundle(result, repo_root() / "exports" / "sim_bundle")
        print("Wrote reports/ and exports/sim_bundle/", file=sys.stderr)
    sys.exit(0 if result.passed else 2)


if __name__ == "__main__":
    main()
