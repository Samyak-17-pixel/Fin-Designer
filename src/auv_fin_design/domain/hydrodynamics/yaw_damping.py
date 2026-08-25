"""Fossen-style polynomial yaw hydrodynamic moment — EQ-HYD-018 / EQ-MAN-005."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class YawDampingCoefficients(BaseModel):
    """Yaw damping polynomial coefficients (Fossen 3-DOF surge-sway-yaw subset).

    Moment [N·m]:
      N = N_r*r + N_v*v + N_rrr*r³ + N_vvr*v²*r + N_vrr*v*r² + N_vvv*v³

    Term types:
      - **Linear:** N_r·r, N_v·v  (odd in r / v — correct damping sign structure)
      - **Cubic (total degree 3):** N_rrr·r³, N_vvv·v³, N_vvr·v²r, N_vrr·vr²
      - No standalone r² term (even → unphysical for rotational damping)

    Units:
      N_r   [N·m·s/rad]
      N_v   [N·m·s/m]
      N_rrr [N·m·s²/rad²]
      N_vvr [N·m·s/m²]
      N_vrr [N·m·s²/(m·rad)]
      N_vvv [N·m·s²/m²]
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    N_r: float = Field(0.0, description="Linear yaw damping")
    N_v: float = Field(0.0, description="Linear sway–yaw coupling")
    N_rrr: float = Field(..., description="Cubic yaw damping")
    N_vvr: float = Field(0.0, description="v²r coupling (degree 3)")
    N_vrr: float = Field(0.0, description="vr² coupling (degree 3)")
    N_vvv: float = Field(0.0, description="Cubic sway damping")


def yaw_hydrodynamic_moment(
    v_sway_mps: float,
    r_yaw_rad_s: float,
    coeffs: YawDampingCoefficients,
) -> float:
    """EQ-MAN-005 — hydrodynamic yaw resistive moment [N·m]."""
    c = coeffs
    return (
        c.N_r * r_yaw_rad_s
        + c.N_v * v_sway_mps
        + c.N_rrr * r_yaw_rad_s**3
        + c.N_vvr * v_sway_mps**2 * r_yaw_rad_s
        + c.N_vrr * v_sway_mps * r_yaw_rad_s**2
        + c.N_vvv * v_sway_mps**3
    )


def crossflow_yaw_reference(
    rho: float,
    diameter_m: float,
    length_m: float,
    *,
    cd_cross: float = 1.0,
) -> float:
    """Hoerner cross-flow strip integral (EQ-HYD-015).

    Returns N_cross [N·m·s²/rad²] scale so |N_cross|·r² matches |r|·r resistive moment.
    """
    return abs((1.0 / 32.0) * rho * cd_cross * diameter_m * length_m**4)


def bootstrap_yaw_damping_from_crossflow(
    n_rrr: float,
    *,
    r_ref_rad_s: float,
    v_ref_mps: float,
    x_cg_m: float,
    length_m: float,
    rho: float,
    diameter_m: float,
    cd_cross: float,
) -> dict[str, float]:
    """Analytical bootstrap for all polynomial terms when tank data are unavailable.

    EQ-HYD-020 — anchored on Hoerner N_rrr, scaled to reference kinematics (V_ref, r_ref).

    Sources:
      N_rrr  — Hoerner cross-flow on hull (primary)
      N_r    — slope of N_rrr·r³ at r_ref: d/dr(N_rrr r³) = 3 N_rrr r_ref²
      N_v    — cross-flow sway–yaw + CG offset: N_rrr r_ref²/V_ref − ρ Cd D L (x_cg − L/2)
      N_vvv  — cubic sway: N_rrr r_ref² / V_ref²
      N_vvr  — mixed: 2 N_rrr r_ref / V_ref
      N_vrr  — mixed (degree 3): N_rrr / V_ref

    Replace any value with tank/CFD measurements in configs/defaults.yaml → yaw_damping.
    """
    r_ref = max(abs(r_ref_rad_s), 1e-9)
    v_ref = max(abs(v_ref_mps), 1e-6)

    n_v_geom = -rho * cd_cross * diameter_m * length_m * (x_cg_m - 0.5 * length_m)

    return {
        "N_r": 3.0 * n_rrr * r_ref**2,
        "N_v": n_rrr * r_ref**2 / v_ref + n_v_geom,
        "N_rrr": n_rrr,
        "N_vvr": 2.0 * n_rrr * r_ref / v_ref,
        "N_vrr": n_rrr / v_ref,
        "N_vvv": n_rrr * r_ref**2 / v_ref**2,
    }


def _cfg_float(cfg: dict, key: str, default: float) -> float:
    return float(cfg[key]) if key in cfg else default


def estimate_yaw_damping_coefficients(
    *,
    rho: float,
    diameter_m: float,
    length_m: float,
    design_speed_mps: float,
    turning_radius_m: float,
    crossflow_cd: float = 1.0,
    x_cg_m: float | None = None,
    yaw_cfg: dict[str, float] | None = None,
) -> tuple[YawDampingCoefficients, float, float]:
    """Build full yaw damping polynomial coefficients.

    With ``estimate_all_terms: true`` (default) and no tank data:
      all six coefficients are bootstrapped from Hoerner cross-flow + (V_ref, r_ref).

    Override any single coefficient in ``yaw_damping`` config; omitted keys use bootstrap.
    """
    cfg = yaw_cfg or {}
    r_ref = design_speed_mps / turning_radius_m
    v_design = float(cfg.get("lateral_speed_mps", 0.0))
    v_ref = float(cfg.get("reference_speed_mps", design_speed_mps))
    estimate_all = bool(cfg.get("estimate_all_terms", True))
    n_rrr_scale = float(cfg.get("N_rrr_scale", 1.0))
    x_cg = length_m * 0.5 if x_cg_m is None else x_cg_m

    n_cross = crossflow_yaw_reference(
        rho, diameter_m, length_m, cd_cross=crossflow_cd
    )

    if "N_rrr" in cfg:
        n_rrr = float(cfg["N_rrr"])
    else:
        n_rrr = -n_rrr_scale * n_cross / max(abs(r_ref), 1e-9)

    if estimate_all:
        defaults = bootstrap_yaw_damping_from_crossflow(
            n_rrr,
            r_ref_rad_s=r_ref,
            v_ref_mps=v_ref,
            x_cg_m=x_cg,
            length_m=length_m,
            rho=rho,
            diameter_m=diameter_m,
            cd_cross=crossflow_cd,
        )
    else:
        defaults = {
            "N_r": 0.0,
            "N_v": 0.0,
            "N_rrr": n_rrr,
            "N_vvr": 0.0,
            "N_vrr": 0.0,
            "N_vvv": 0.0,
        }

    coeffs = YawDampingCoefficients(
        N_r=_cfg_float(cfg, "N_r", defaults["N_r"]),
        N_v=_cfg_float(cfg, "N_v", defaults["N_v"]),
        N_rrr=n_rrr,
        N_vvr=_cfg_float(cfg, "N_vvr", defaults["N_vvr"]),
        N_vrr=_cfg_float(cfg, "N_vrr", defaults["N_vrr"]),
        N_vvv=_cfg_float(cfg, "N_vvv", defaults["N_vvv"]),
    )
    return coeffs, r_ref, v_design
