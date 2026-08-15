"""Dynamic CoP solver — orchestrates strip theory, integration, verification."""

from __future__ import annotations

import math
from pathlib import Path

from auv_fin_design.domain.center_of_pressure.constants import (
    DEFAULT_Y_CP_M,
    EQ_COP_DELTA,
    EQ_COP_HINGE,
    EQ_COP_VERIFY,
    EQ_COP_ZCP,
)
from auv_fin_design.domain.center_of_pressure.cp_provider import CenterOfPressureProvider
from auv_fin_design.domain.center_of_pressure.finite_wing_correction import helmbold_lift_slope
from auv_fin_design.domain.center_of_pressure.models import (
    CenterOfPressureResult,
    CoPSolverConfig,
    CoPVerification,
    ManeuverDeflection,
)
from auv_fin_design.domain.center_of_pressure.strip_theory import build_strips
from auv_fin_design.domain.center_of_pressure.utils import default_airfoils_root
from auv_fin_design.domain.center_of_pressure.xfoil_provider import XfoilProvider
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


def _verification(
    x_cp_c: float,
    cm: float,
    cl: float,
    *,
    warn_tol: float,
    fail_tol: float,
    cm_from_integration: float | None = None,
    cn_from_integration: float | None = None,
) -> CoPVerification:
    """EQ-COP-006 — compare integrated x_cp/c to QC and Cm/CL estimates."""
    qc = 0.25
    if (
        cm_from_integration is not None
        and cn_from_integration is not None
        and abs(cn_from_integration) > 1e-9
    ):
        cm_c4 = cm_from_integration + 0.25 * cn_from_integration
        cm_cl = 0.25 - cm_c4 / cn_from_integration
    elif abs(cl) < 1e-9:
        cm_cl = 0.25
    else:
        cm_cl = 0.25 - cm / cl
    err_qc = abs(x_cp_c - qc) / max(abs(qc), 1e-6)
    err_cm = abs(x_cp_c - cm_cl) / max(abs(cm_cl), 1e-6)
    worst = err_cm
    if worst > fail_tol:
        status = "FAIL"
    elif worst > warn_tol or err_qc > warn_tol:
        status = "WARNING"
    else:
        status = "PASS"
    msg = (
        f"x_cp/c integrated={x_cp_c:.4f}, QC=0.25, Cm/CL={cm_cl:.4f}; "
        f"rel_err QC={err_qc:.3%}, Cm/CL={err_cm:.3%} → {status}"
    )
    return CoPVerification(
        x_cp_c_integrated=x_cp_c,
        x_cp_c_quarter_chord=qc,
        x_cp_c_cm_cl=cm_cl,
        rel_err_vs_qc=err_qc,
        rel_err_vs_cm_cl=err_cm,
        status=status,
        message=msg,
        equation_ids=(EQ_COP_VERIFY,),
    )


def compute_maneuver_deflection(
    *,
    lift_required_n: float,
    dynamic_pressure: float,
    area_m2: float,
    cl_alpha_2d_per_rad: float,
    aspect_ratio: float,
    stall_alpha_deg: float,
    stall_margin_deg: float,
) -> ManeuverDeflection:
    """EQ-COP-007 — required fin deflection for maneuver lift (α=δ V1)."""
    a3d = helmbold_lift_slope(cl_alpha_2d_per_rad, aspect_ratio)
    cl_req = lift_required_n / max(dynamic_pressure * area_m2, 1e-12)
    delta_req = 0.0 if a3d <= 0 else math.degrees(cl_req / a3d)
    delta_max = max(0.0, stall_alpha_deg - stall_margin_deg)
    margin = delta_max - delta_req
    return ManeuverDeflection(
        cl_required=cl_req,
        cl_alpha_3d_per_rad=a3d,
        delta_required_deg=delta_req,
        delta_max_usable_deg=delta_max,
        delta_margin_deg=margin,
        sufficient=margin >= -0.1,
        equation_ids=(EQ_COP_DELTA,),
    )


class CoPSolver:
    """Production dynamic CoP solver (strip theory + Cp archives)."""

    def __init__(
        self,
        config: CoPSolverConfig | None = None,
        provider: CenterOfPressureProvider | None = None,
    ) -> None:
        self.config = config or CoPSolverConfig()
        root = (
            Path(self.config.airfoils_root)
            if self.config.airfoils_root
            else default_airfoils_root()
        )
        self.provider = provider or XfoilProvider(root)

    def solve(
        self,
        geometry: CandidateFinGeometry,
        *,
        airfoil: str,
        dynamic_pressure: float,
        speed_mps: float,
        nu: float,
        alpha_deg: float,
        cm_polar: float,
        cl_polar: float,
        lift_required_n: float | None = None,
        cl_alpha_2d_per_rad: float | None = None,
        stall_alpha_deg: float | None = None,
        stall_margin_deg: float = 5.0,
        servo_efficiency: float = 1.0,
    ) -> CenterOfPressureResult:
        """Compute 3D CoP, hinge moment, optional maneuver deflection."""
        cfg = self.config
        strips = build_strips(
            geometry,
            provider=self.provider,
            airfoil=airfoil,
            dynamic_pressure=dynamic_pressure,
            speed_mps=speed_mps,
            nu=nu,
            alpha_deg=alpha_deg,
            n_strips=cfg.n_strips,
            hinge_frac=cfg.hinge_chord_fraction,
            epsrel=cfg.integration_epsrel,
        )
        lifts = [s.lift_n for s in strips]
        L = float(sum(lifts))
        m_le_tot = float(sum(s.moment_le_nm for s in strips))
        cn_eff = L / max(dynamic_pressure * geometry.area, 1e-12)
        cm_le_eff = m_le_tot / max(dynamic_pressure * geometry.area * geometry.mac, 1e-12)
        if abs(L) < 1e-12:
            z_cp = 0.5 * geometry.span
            x_from_le = 0.25 * geometry.mac
            x_hinge = 0.0
            x_frac = 0.25
        else:
            z_cp = float(sum(s.lift_n * s.z_m for s in strips) / L)
            mx_le = sum(s.lift_n * (s.cp_x_frac * s.local_chord_m) for s in strips)
            x_from_le = float(mx_le / L)
            x_frac = x_from_le / max(geometry.mac, 1e-12)
            x_hinge = cfg.hinge_chord_fraction * geometry.mac - x_from_le

        hinge_moment = float(sum(s.lift_n * (-s.cp_x_hinge_m) for s in strips))
        hinge_arm = abs(x_hinge)
        servo_torque = abs(hinge_moment) / max(servo_efficiency, 1e-6)

        ver = _verification(
            x_frac,
            cm_polar,
            cl_polar,
            warn_tol=cfg.verify_rel_tol_warn,
            fail_tol=cfg.verify_rel_tol_fail,
            cm_from_integration=cm_le_eff,
            cn_from_integration=cn_eff,
        )

        deflection = None
        if (
            lift_required_n is not None
            and cl_alpha_2d_per_rad is not None
            and stall_alpha_deg is not None
        ):
            deflection = compute_maneuver_deflection(
                lift_required_n=lift_required_n,
                dynamic_pressure=dynamic_pressure,
                area_m2=geometry.area,
                cl_alpha_2d_per_rad=cl_alpha_2d_per_rad,
                aspect_ratio=geometry.aspect_ratio,
                stall_alpha_deg=stall_alpha_deg,
                stall_margin_deg=stall_margin_deg,
            )

        _ = (EQ_COP_ZCP, EQ_COP_HINGE)
        return CenterOfPressureResult(
            total_lift_n=L,
            total_drag_n=float(sum(s.drag_n for s in strips)),
            total_pitching_moment_le_nm=m_le_tot,
            x_cp_le_frac=x_frac,
            x_cp_from_le_m=x_from_le,
            x_cp_hinge_m=x_hinge,
            y_cp_m=DEFAULT_Y_CP_M,
            z_cp_m=z_cp,
            hinge_arm_m=hinge_arm,
            hinge_moment_nm=hinge_moment,
            servo_torque_nm=servo_torque,
            strips=tuple(strips),
            verification=ver,
            deflection=deflection,
        )


def solve_center_of_pressure(
    geometry: CandidateFinGeometry,
    *,
    airfoil: str,
    dynamic_pressure: float,
    speed_mps: float,
    nu: float,
    alpha_deg: float,
    cm_polar: float,
    cl_polar: float,
    config: CoPSolverConfig | None = None,
    provider: CenterOfPressureProvider | None = None,
    **kwargs,
) -> CenterOfPressureResult:
    """Convenience entry point for the design pipeline."""
    return CoPSolver(config=config, provider=provider).solve(
        geometry,
        airfoil=airfoil,
        dynamic_pressure=dynamic_pressure,
        speed_mps=speed_mps,
        nu=nu,
        alpha_deg=alpha_deg,
        cm_polar=cm_polar,
        cl_polar=cl_polar,
        **kwargs,
    )
