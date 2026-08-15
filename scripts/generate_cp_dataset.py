#!/usr/bin/env python3
"""Generate precomputed Cp archives for data/airfoils (XFOIL-replaceable).

Uses a simple vortex-panel method on NACA 4-digit sections (inviscid).
Cp is duplicated across Re folders so log-Re interpolation is defined;
replace files in place with true XFOIL dumps when available.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from auv_fin_design.domain.airfoil.naca import generate_naca4_coordinates, naca4_thickness_yt
from auv_fin_design.infrastructure.config.loader import repo_root


def vortex_panel_cp(code: str, alpha_deg: float, n_panels: int = 80) -> pd.DataFrame:
    """Symmetric NACA: thin-airfoil ΔCp + thickness Cp perturbation → upper/lower.

    Purpose: Bootstrap Cp datasets without an XFOIL binary.
    Limitations: Inviscid; not a substitute for viscous XFOIL near stall.
    """
    alpha = math.radians(alpha_deg)
    t = int("".join(ch for ch in code if ch.isdigit())[2:4]) / 100.0
    # Cosine-spaced x from LE to TE
    beta = np.linspace(0.0, math.pi, n_panels)
    x = 0.5 * (1.0 - np.cos(beta))
    x = np.clip(x, 1e-6, 1.0 - 1e-9)
    # Flat-plate thin-airfoil loading (Glauert): ΔCp = 2 α √((1-x)/x)
    dcp_alpha = 2.0 * alpha * np.sqrt((1.0 - x) / x)
    # Thickness: approximate surface speed perturbation ~ proportional to yt slope
    yt = np.array([naca4_thickness_yt(float(xi), t) for xi in x])
    # Small thickness Cp ≈ ± (dyt/dx related); use simple closed form from NACA
    # Cp_thickness ~ -2*(dy/dx contribution) — use finite difference of yt
    dyt = np.gradient(yt, x)
    cp_t = -2.0 * dyt  # crude thickness pressure
    cp_upper = -0.5 * dcp_alpha + cp_t
    cp_lower = 0.5 * dcp_alpha + cp_t
    return pd.DataFrame({"x_c": x, "Cp_upper": cp_upper, "Cp_lower": cp_lower})


def setup_airfoil(name: str, legacy_dir: Path, out_root: Path) -> Path:
    digits = "".join(ch for ch in name if ch.isdigit())[:4]
    folder = out_root / f"naca{digits}"
    folder.mkdir(parents=True, exist_ok=True)
    cp_root = folder / "cp"
    polars = folder / "polars"
    polars.mkdir(exist_ok=True)
    # geometry
    coords, t = generate_naca4_coordinates(digits, n_points=81)
    geo = folder / "geometry.dat"
    lines = [f"NACA {digits}"]
    for x, y in coords:
        lines.append(f"{x:.6f} {y:.6f}")
    geo.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # copy polars from legacy
    if legacy_dir.is_dir():
        for f in legacy_dir.glob("xf-*.csv"):
            shutil.copy2(f, polars / f.name)
        legacy_coords = legacy_dir / "coordinates.dat"
        if legacy_coords.exists() and not (folder / "coordinates.dat").exists():
            shutil.copy2(legacy_coords, folder / "coordinates.dat")
    meta = {
        "name": f"naca{digits}",
        "thickness_ratio": t,
        "cp_source": "vortex_panel_bootstrap_v1",
        "note": "Replace cp/ with true XFOIL dumps when available; layout unchanged.",
    }
    (folder / "metadata.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")
    return folder


def generate(
    airfoils: list[str] | None = None,
    reynolds: list[float] | None = None,
    alphas: list[float] | None = None,
) -> None:
    root = repo_root()
    out = root / "data" / "airfoils"
    out.mkdir(parents=True, exist_ok=True)
    airfoils = airfoils or ["0012", "0015", "0018"]
    reynolds = reynolds or [5.0e4, 1.0e5, 2.0e5, 5.0e5, 1.0e6]
    alphas = alphas or list(np.linspace(-4.0, 16.0, 21))  # 1 deg steps-ish
    # denser near typical design
    alphas = sorted(set(float(a) for a in alphas) | set(np.arange(0.0, 12.1, 1.0)))

    for code in airfoils:
        legacy = root / "data" / f"NACA{code}"
        folder = setup_airfoil(code, legacy, out)
        for re in reynolds:
            re_dir = folder / "cp" / f"Re{int(re)}"
            re_dir.mkdir(parents=True, exist_ok=True)
            for a in alphas:
                df = vortex_panel_cp(code, a)
                # Format alpha filename: alpha2.00.csv / alpha-2.00.csv
                fname = f"alpha{a:.2f}.csv"
                df.to_csv(re_dir / fname, index=False)
        print(f"Wrote {folder}")


if __name__ == "__main__":
    generate()
