"""End-to-end engineering design pipeline (SRDS workflow)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import math

from auv_fin_design.domain.airfoil.database import AirfoilDatabase
from auv_fin_design.domain.airfoil.finite_wing import (
    alpha_for_required_cl,
    helmbold_cl_alpha,
)
from auv_fin_design.domain.center_of_pressure import (
    CenterOfPressureResult,
    CoPSolverConfig,
    solve_center_of_pressure,
)
from auv_fin_design.domain.constants.materials import MaterialProperties, get_material
from auv_fin_design.domain.control.allocation import allocate_x_tail_yaw
from auv_fin_design.domain.control.maneuvering import compute_control_requirement
from auv_fin_design.domain.geometry.sizing import (
    CandidateFinGeometry,
    apply_dimension_overrides,
    check_geometry_constraints,
    size_fin,
)
from auv_fin_design.domain.geometry.shaft_fit import ShaftFitResult, check_shaft_fit_at_hinge
from auv_fin_design.domain.hydrodynamics.estimator import estimate_hydrodynamics
from auv_fin_design.domain.manufacturing.recommendations import (
    ManufacturingRecommendations,
    recommend_manufacturing,
)
from auv_fin_design.domain.servo.analysis import ServoSpecification, analyze_servo
from auv_fin_design.domain.structural.beam import StructuralResult, analyze_fin_structure
from auv_fin_design.domain.validation.hydro import (
    HydrodynamicValidationModel,
    validate_hydrodynamics,
)
from auv_fin_design.domain.validation.sensitivity import SensitivityReport
from auv_fin_design.domain.vehicle.model import MissionModel, VehicleModel
from auv_fin_design.infrastructure.config.loader import load_defaults, repo_root


@dataclass
class GeometryOverride:
    """Optional user-fixed fin planform dimensions (leave None to auto-size)."""

    root_chord_m: float | None = None
    span_m: float | None = None
    tip_chord_m: float | None = None
    taper_ratio: float | None = None


@dataclass
class DesignResult:
    vehicle: VehicleModel
    mission: MissionModel
    material_name: str
    hydro: Any
    control_req: Any
    allocation: Any
    geometry: CandidateFinGeometry
    airfoil_name: str
    aero: Any
    center_of_pressure: CenterOfPressureResult
    shaft_fit: ShaftFitResult
    hydro_validation: HydrodynamicValidationModel
    structure_cruise: StructuralResult
    structure_aggressive: StructuralResult
    structure_emergency: StructuralResult
    servo_result: Any
    manufacturing: ManufacturingRecommendations
    geometry_violations: list[str]
    maneuver_deflection: Any | None = None
    sensitivity: SensitivityReport | None = None
    optimization: Any | None = None
    iteration_history: list[dict[str, float]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    equation_ids: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True only when diagnose_design finds no blocking violations."""
        from auv_fin_design.domain.validation.design_diagnosis import diagnose_design

        return diagnose_design(self).passed


def _rank_airfoils(
    db: AirfoilDatabase,
    re_mac: float,
    *,
    weights: dict[str, float],
) -> list[tuple[str, float]]:
    scores: list[tuple[str, float]] = []
    for name, entry in db.entries.items():
        polar = entry.polar_at_re(re_mac)
        cl_max, _ = polar.first_local_cl_max()
        pt = polar.interpolate_at_alpha(5.0)
        lift_score = min(max(cl_max / 1.2, 0.0), 1.0)
        drag_score = min(max(1.0 - pt.cd / 0.05, 0.0), 1.0)
        thick_score = min(max((entry.thickness_ratio - 0.08) / (0.20 - 0.08), 0.0), 1.0)
        moment_score = min(max(1.0 - abs(pt.cm) / 0.15, 0.0), 1.0)
        servo_score = moment_score
        mfg_score = thick_score
        s = (
            weights["lift_capability"] * lift_score
            + weights["profile_drag"] * drag_score
            + weights["thickness"] * thick_score
            + weights["pitching_moment"] * moment_score
            + weights["servo_demand"] * servo_score
            + weights["manufacturability"] * mfg_score
        )
        scores.append((name, s))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def run_design_pipeline(
    vehicle: VehicleModel,
    mission: MissionModel,
    *,
    material: MaterialProperties | None = None,
    servo: ServoSpecification | None = None,
    airfoil_db: AirfoilDatabase | None = None,
    defaults: dict[str, Any] | None = None,
    airfoil_name: str | None = None,
    geometry_override: GeometryOverride | None = None,
    run_sensitivity: bool = True,
    run_optimization: bool = False,
) -> DesignResult:
    """Execute full SRDS engineering workflow."""
    cfg = defaults or load_defaults()
    material = material or get_material("PLA")
    servo = servo or ServoSpecification(
        rated_torque=float(cfg["servo"]["rated_torque_nm"]),
        shaft_diameter=float(cfg["servo"]["shaft_diameter_m"]),
        max_rotation_deg=float(cfg["servo"]["max_rotation_deg"]),
        efficiency=float(cfg["servo"]["efficiency"]),
        max_speed_deg_s=float(cfg["servo"].get("max_speed_deg_s", 60.0)),
    )
    if airfoil_db is None:
        airfoil_db = AirfoilDatabase(repo_root() / "data")

    # Use max of design and max speed for critical aero checks later
    design_speed = mission.design_speed
    max_speed = mission.max_speed if mission.max_speed is not None else design_speed

    hydro = estimate_hydrodynamics(
        vehicle,
        mission,
        crossflow_cd=float(cfg["hydrodynamics"]["crossflow_cd"]),
        axial_added_mass_factor=float(cfg["hydrodynamics"]["axial_added_mass_factor"]),
        yaw_damping_cfg=cfg["hydrodynamics"].get("yaw_damping"),
    )
    control_req = compute_control_requirement(
        vehicle,
        hydro,
        mission,
        control_margin=float(cfg["maneuvering"]["control_margin"]),
    )

    sizing_cfg = cfg["sizing"]
    c_root_guess = 0.08
    alloc = allocate_x_tail_yaw(vehicle, control_req, root_chord=c_root_guess)

    cl = float(sizing_cfg["cl_initial"])
    ar = float(sizing_cfg["aspect_ratio"])
    taper = float(sizing_cfg["taper_ratio"])
    sweep = float(sizing_cfg["sweep_deg"])
    e = float(sizing_cfg["oswald_e"])
    tol = float(sizing_cfg["area_convergence_tol"])
    max_iter = int(sizing_cfg["max_airfoil_iterations"])

    t_ratio = 0.12
    naca_code = "0012"
    geom = size_fin(
        alloc.lift_per_fin,
        hydro.dynamic_pressure,
        cl=cl,
        aspect_ratio=ar,
        taper_ratio=taper,
        sweep_deg=sweep,
        thickness_ratio=t_ratio,
        material_density=material.density,
        naca_profile=naca_code,
    )
    alloc = allocate_x_tail_yaw(vehicle, control_req, root_chord=geom.root_chord)
    geom = size_fin(
        alloc.lift_per_fin,
        hydro.dynamic_pressure,
        cl=cl,
        aspect_ratio=ar,
        taper_ratio=taper,
        sweep_deg=sweep,
        thickness_ratio=t_ratio,
        material_density=material.density,
        naca_profile=naca_code,
    )

    override = geometry_override or GeometryOverride()
    fixed_dims = (
        override.root_chord_m is not None
        or override.span_m is not None
        or override.tip_chord_m is not None
    )
    if fixed_dims:
        geom = apply_dimension_overrides(
            geom,
            root_chord=override.root_chord_m,
            span=override.span_m,
            tip_chord=override.tip_chord_m,
            taper_ratio=override.taper_ratio if override.taper_ratio is not None else taper,
            sweep_deg=sweep,
            thickness_ratio=t_ratio,
            material_density=material.density,
            naca_profile=naca_code,
        )
        ar = geom.aspect_ratio
        taper = geom.taper_ratio

    nu = vehicle.fluid.kinematic_viscosity
    re_mac = design_speed * geom.mac / nu
    weights = cfg["airfoil_ranking_weights"]
    ranked = _rank_airfoils(airfoil_db, re_mac, weights=weights)
    if not ranked:
        raise RuntimeError("Airfoil database is empty — add polar CSV folders under data/")

    chosen = airfoil_name.upper() if airfoil_name else ranked[0][0]
    entry = airfoil_db.get(chosen)
    t_ratio = entry.thickness_ratio
    naca_code = chosen.replace("NACA", "").replace("naca", "").strip() or "0015"

    history: list[dict[str, float]] = []
    warnings: list[str] = []
    aero = None
    stall_margin = float(sizing_cfg["stall_margin_deg"])
    gcfg = cfg["geometry_constraints"]
    max_span = float(gcfg["max_span_over_diameter"]) * vehicle.diameter
    min_ar = 0.8
    if fixed_dims:
        geom = apply_dimension_overrides(
            geom,
            root_chord=geom.root_chord,
            span=geom.span,
            tip_chord=geom.tip_chord,
            sweep_deg=sweep,
            thickness_ratio=t_ratio,
            material_density=material.density,
            naca_profile=naca_code,
        )
        warnings.append(
            "Using optional fin dimension overrides: "
            + ", ".join(
                p
                for p in (
                    f"root_chord={override.root_chord_m:.4f} m"
                    if override.root_chord_m is not None
                    else "",
                    f"span={override.span_m:.4f} m"
                    if override.span_m is not None
                    else "",
                    f"tip_chord={override.tip_chord_m:.4f} m"
                    if override.tip_chord_m is not None
                    else "",
                )
                if p
            )
        )

    for _ in range(max_iter):
        alloc = allocate_x_tail_yaw(vehicle, control_req, root_chord=geom.root_chord)
        re_mac = design_speed * geom.mac / nu
        polar = entry.polar_at_re(re_mac)
        a0 = polar.cl_alpha_per_rad()
        a3d = helmbold_cl_alpha(a0, ar)
        cl_max, stall_a = polar.first_local_cl_max()

        alpha_design = max(1.0, stall_a - stall_margin)
        cl_margin = a3d * math.radians(alpha_design)
        cl_use = max(0.05, min(cl_margin, 0.9 * cl_max))

        cl_req = alloc.lift_per_fin / (hydro.dynamic_pressure * geom.area)
        if cl_req > cl_use + 1e-6:
            warnings.append(
                f"Resizing area: required CL={cl_req:.3f} > usable CL={cl_use:.3f} "
                f"(stall margin {stall_margin}°)"
            )

        if fixed_dims:
            # Keep user dimensions; only refresh thickness/airfoil-dependent fields
            new_geom = apply_dimension_overrides(
                geom,
                root_chord=geom.root_chord,
                span=geom.span,
                tip_chord=geom.tip_chord,
                sweep_deg=sweep,
                thickness_ratio=t_ratio,
                material_density=material.density,
                naca_profile=naca_code,
            )
            if cl_req > cl_use + 1e-6:
                warnings.append(
                    "Fixed dimensions may be undersized for required lift "
                    f"(CL_req={cl_req:.3f} > CL_use={cl_use:.3f})"
                )
        else:
            new_geom = size_fin(
                alloc.lift_per_fin,
                hydro.dynamic_pressure,
                cl=cl_use,
                aspect_ratio=ar,
                taper_ratio=taper,
                sweep_deg=sweep,
                thickness_ratio=t_ratio,
                material_density=material.density,
                naca_profile=naca_code,
            )

            if new_geom.span > max_span:
                ar_fit = max(min_ar, (max_span**2) / new_geom.area)
                if ar_fit < ar - 1e-6:
                    warnings.append(
                        f"Span {new_geom.span:.4f} m > max {max_span:.4f} m; "
                        f"reducing AR {ar:.3f} → {ar_fit:.3f}"
                    )
                    ar = ar_fit
                    new_geom = size_fin(
                        alloc.lift_per_fin,
                        hydro.dynamic_pressure,
                        cl=cl_use,
                        aspect_ratio=ar,
                        taper_ratio=taper,
                        sweep_deg=sweep,
                        thickness_ratio=t_ratio,
                        material_density=material.density,
                        naca_profile=naca_code,
                    )
                if new_geom.span > max_span * 1.001:
                    warnings.append(
                        f"Cannot meet lift and span constraint simultaneously "
                        f"(span={new_geom.span:.4f} m, max={max_span:.4f} m)"
                    )

        aero = alpha_for_required_cl(
            polar, aspect_ratio=ar, cl_required=cl_use, oswald_e=e
        )
        area_change = abs(new_geom.area - geom.area) / geom.area
        history.append(
            {
                "area": new_geom.area,
                "ar": ar,
                "cl_req": cl_req,
                "cl_use": cl_use,
                "alpha_deg": aero.alpha_deg,
                "re_mac": re_mac,
            }
        )
        geom = new_geom
        if fixed_dims or area_change < tol:
            break
    else:
        warnings.append("Airfoil/geometry iteration hit max iterations")

    assert aero is not None

    alloc = allocate_x_tail_yaw(vehicle, control_req, root_chord=geom.root_chord)
    cl_final = alloc.lift_per_fin / (hydro.dynamic_pressure * geom.area)
    polar = entry.polar_at_re(design_speed * geom.mac / nu)
    aero = alpha_for_required_cl(polar, aspect_ratio=ar, cl_required=cl_final, oswald_e=e)
    if aero.stall_alpha_deg - aero.alpha_deg < stall_margin - 1e-6:
        warnings.append(
            f"Final stall margin {aero.stall_alpha_deg - aero.alpha_deg:.2f}° < {stall_margin}°"
        )

    # Max-speed check (SRDS input): higher q increases loads — re-evaluate FoS at max speed ratio
    speed_ratio = (max_speed / design_speed) ** 2 if design_speed > 0 else 1.0
    if speed_ratio > 1.01:
        warnings.append(
            f"Max speed {max_speed:.2f} m/s → load scale {speed_ratio:.2f}× vs design speed"
        )

    lift_design = alloc.lift_per_fin
    drag_design = hydro.dynamic_pressure * geom.area * aero.cd_total
    emerg_factor = float(cfg["maneuvering"]["emergency_load_factor"])
    str_cfg = cfg["structure"]

    # Dynamic CoP (strip Cp integration) — EQ-COP-*
    cop_cfg_raw = cfg.get("center_of_pressure", {})
    cop_config = CoPSolverConfig(
        provider=cop_cfg_raw.get("provider", "xfoil_file"),
        n_strips=int(cop_cfg_raw.get("n_strips", 40)),
        integration_epsrel=float(cop_cfg_raw.get("integration_epsrel", 1e-6)),
        verify_rel_tol_warn=float(cop_cfg_raw.get("verify_rel_tol_warn", 0.05)),
        verify_rel_tol_fail=float(cop_cfg_raw.get("verify_rel_tol_fail", 0.15)),
        cache_enabled=bool(cop_cfg_raw.get("cache_enabled", True)),
        hinge_chord_fraction=float(cop_cfg_raw.get("hinge_chord_fraction", 0.25)),
    )
    # Use fewer strips in default path for speed; config may request 100
    airfoil_key = chosen.lower().replace("naca", "naca") if "naca" in chosen.lower() else f"naca{''.join(ch for ch in chosen if ch.isdigit())[:4]}"
    if not airfoil_key.startswith("naca"):
        digits = "".join(ch for ch in chosen if ch.isdigit())
        airfoil_key = f"naca{digits[:4]}" if len(digits) >= 4 else chosen.lower()

    polar_final = entry.polar_at_re(design_speed * geom.mac / nu)
    a0_final = polar_final.cl_alpha_per_rad()

    cp = solve_center_of_pressure(
        geom,
        airfoil=airfoil_key,
        dynamic_pressure=hydro.dynamic_pressure,
        speed_mps=design_speed,
        nu=nu,
        alpha_deg=aero.alpha_deg,
        cm_polar=aero.cm,
        cl_polar=aero.cl,
        config=cop_config,
        lift_required_n=lift_design,
        cl_alpha_2d_per_rad=a0_final,
        stall_alpha_deg=aero.stall_alpha_deg,
        stall_margin_deg=stall_margin,
        servo_efficiency=float(cfg["servo"]["efficiency"]),
    )
    warnings.append(f"CoP verification: {cp.verification.message}")
    if cp.deflection is not None and not cp.deflection.sufficient:
        warnings.append(
            f"Required deflection {cp.deflection.delta_required_deg:.2f}° exceeds "
            f"usable {cp.deflection.delta_max_usable_deg:.2f}°"
        )

    # Re-allocate using body-x of dynamic CoP (one iteration)
    x_force = vehicle.x_fin_root_le + cp.x_cp_from_le_m
    alloc = allocate_x_tail_yaw(
        vehicle, control_req, root_chord=geom.root_chord, force_station_x_m=x_force
    )
    lift_design = alloc.lift_per_fin
    # Refresh aero at updated CL
    cl_final = lift_design / (hydro.dynamic_pressure * geom.area)
    aero = alpha_for_required_cl(polar_final, aspect_ratio=ar, cl_required=cl_final, oswald_e=e)
    drag_design = hydro.dynamic_pressure * geom.area * aero.cd_total
    cp = solve_center_of_pressure(
        geom,
        airfoil=airfoil_key,
        dynamic_pressure=hydro.dynamic_pressure,
        speed_mps=design_speed,
        nu=nu,
        alpha_deg=aero.alpha_deg,
        cm_polar=aero.cm,
        cl_polar=aero.cl,
        config=cop_config,
        lift_required_n=lift_design,
        cl_alpha_2d_per_rad=a0_final,
        stall_alpha_deg=aero.stall_alpha_deg,
        stall_margin_deg=stall_margin,
        servo_efficiency=float(cfg["servo"]["efficiency"]),
    )

    hydro_val = validate_hydrodynamics(
        hydro=hydro,
        aero=aero,
        geometry=geom,
        allocation=alloc,
        control_req=control_req,
        max_deflection_deg=float(servo.max_rotation_deg),
        stall_margin_required_deg=stall_margin,
        density=vehicle.fluid.density,
        gravity=vehicle.fluid.gravity,
    )
    if hydro_val.messages:
        warnings.extend(hydro_val.messages)

    servo_res = analyze_servo(
        q=hydro.dynamic_pressure,
        area=geom.area,
        mac=geom.mac,
        cm=aero.cm,
        servo=servo,
        lift=lift_design,
        util_continuous_limit=float(cfg["servo"]["util_continuous_limit"]),
        util_peak_limit=float(cfg["servo"]["util_peak_limit"]),
        required_deflection_deg=abs(
            cp.deflection.delta_required_deg if cp.deflection else aero.alpha_deg
        ),
        hinge_moment_override=cp.hinge_moment_nm,
    )

    st_cruise = analyze_fin_structure(
        geom,
        material,
        lift_design * 0.5,
        load_case="cruise",
        required_fos=float(str_cfg["fos_cruise"]),
        tip_deflection_limit_span_frac=float(str_cfg["tip_deflection_limit_span_frac"]),
        drag=drag_design * 0.5,
        hinge_moment=servo_res.hinge_moment * 0.5,
    )
    st_agg = analyze_fin_structure(
        geom,
        material,
        lift_design * speed_ratio,
        load_case="aggressive",
        required_fos=float(str_cfg["fos_aggressive"]),
        tip_deflection_limit_span_frac=float(str_cfg["tip_deflection_limit_span_frac"]),
        drag=drag_design * speed_ratio,
        hinge_moment=servo_res.hinge_moment * speed_ratio,
    )
    st_em = analyze_fin_structure(
        geom,
        material,
        lift_design * emerg_factor * speed_ratio,
        load_case="emergency",
        required_fos=float(str_cfg["fos_emergency"]),
        tip_deflection_limit_span_frac=float(str_cfg["tip_deflection_limit_span_frac"]),
        drag=drag_design * emerg_factor * speed_ratio,
        hinge_moment=servo_res.hinge_moment * emerg_factor * speed_ratio,
    )

    mfg = recommend_manufacturing(
        geom,
        material,
        min_wall_m=float(gcfg["min_wall_thickness_m"]),
        min_te_m=float(gcfg["min_te_thickness_m"]),
    )

    violations = check_geometry_constraints(
        geom,
        vehicle.diameter,
        max_span_over_diameter=float(gcfg["max_span_over_diameter"]),
        min_tip_chord_m=float(gcfg["min_tip_chord_m"]),
        min_te_thickness_m=float(gcfg["min_te_thickness_m"]),
        min_wall_thickness_m=float(gcfg["min_wall_thickness_m"]),
    )

    shaft_fit = check_shaft_fit_at_hinge(
        geom,
        servo.shaft_diameter,
        clearance_factor=float(gcfg.get("shaft_clearance_factor", 1.10)),
    )
    if not shaft_fit.fits:
        violations.append(shaft_fit.message)

    eq_ids: list[str] = []
    for obj in (hydro, control_req, alloc, geom, aero, cp, shaft_fit, hydro_val, st_agg, servo_res):
        ids = getattr(obj, "equation_ids", ())
        eq_ids.extend(list(ids))

    result = DesignResult(
        vehicle=vehicle,
        mission=mission,
        material_name=material.name,
        hydro=hydro,
        control_req=control_req,
        allocation=alloc,
        geometry=geom,
        airfoil_name=chosen,
        aero=aero,
        center_of_pressure=cp,
        shaft_fit=shaft_fit,
        hydro_validation=hydro_val,
        structure_cruise=st_cruise,
        structure_aggressive=st_agg,
        structure_emergency=st_em,
        servo_result=servo_res,
        manufacturing=mfg,
        geometry_violations=violations,
        maneuver_deflection=cp.deflection,
        iteration_history=history,
        warnings=list(dict.fromkeys(warnings)),
        equation_ids=sorted(set(eq_ids)),
    )

    if run_sensitivity:
        from auv_fin_design.domain.validation.sensitivity import run_sensitivity as _sens

        result.sensitivity = _sens(
            vehicle,
            mission,
            material=material,
            servo=servo,
            defaults=cfg,
            airfoil_name=chosen,
        )

    if run_optimization:
        from auv_fin_design.domain.optimization.nsga2 import run_nsga2

        opt_cfg = cfg.get("optimization", {})
        result.optimization = run_nsga2(
            vehicle,
            mission,
            population=int(opt_cfg.get("population", 40)),
            generations=int(opt_cfg.get("generations", 20)),
            airfoil_name=chosen,
        )

    return result


def load_golden_vehicle() -> tuple[VehicleModel, MissionModel]:
    from auv_fin_design.infrastructure.config.loader import load_yaml

    path = repo_root() / "benchmarks" / "golden_vehicle" / "golden_vehicle.yaml"
    data = load_yaml(path)
    v = data["vehicle"]
    m = data["mission"]
    vehicle = VehicleModel(
        length=float(v["length_m"]),
        diameter=float(v["diameter_m"]),
        mass=float(v["mass_kg"]),
        water=v["water"],
        cg_fraction_of_length=float(v["cg_fraction_of_length"]),
        fin_root_le_fraction_of_length=float(v["fin_root_le_fraction_of_length"]),
        n_fins=int(data["fins"]["count"]),
        configuration=data["fins"]["configuration"],
        fin_clocking_deg=tuple(float(x) for x in data["fins"]["clocking_deg"]),
    )
    mission = MissionModel(
        design_speed=float(m["design_speed_mps"]),
        turning_radius=float(m["turning_radius_m"]),
        turn_establishment_time=float(m["turn_establishment_s"]),
        max_speed=float(m.get("max_speed_mps", m["design_speed_mps"] * 1.25)),
    )
    return vehicle, mission
