"""SciPy interpolation of Cp distributions over Re, alpha, and x/c."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from auv_fin_design.domain.center_of_pressure.constants import DEFAULT_CACHE_SIZE
from auv_fin_design.domain.center_of_pressure.exceptions import (
    CoPDataError,
    CoPInterpolationError,
)
from auv_fin_design.domain.center_of_pressure.models import PressureDistribution
from auv_fin_design.domain.center_of_pressure.utils import parse_alpha_filename, parse_re_dirname
from auv_fin_design.domain.center_of_pressure.validators import validate_cp_arrays


def _read_cp_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    df = pd.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    def col(*names: str) -> str:
        for n in names:
            if n in cols:
                return cols[n]
        raise CoPDataError(f"Missing columns {names} in {path}")

    x = df[col("x_c", "x/c", "x")].to_numpy(dtype=float)
    if "dcp" in cols or "delta_cp" in cols:
        dcp = df[col("dcp", "delta_cp")].to_numpy(dtype=float)
        # Split symmetrically if only ΔCp stored
        cu = -0.5 * dcp
        cl = 0.5 * dcp
    else:
        cu = df[col("cp_upper", "cpu", "cp_u")].to_numpy(dtype=float)
        cl = df[col("cp_lower", "cpl", "cp_l")].to_numpy(dtype=float)
    return validate_cp_arrays(x, cu, cl)


@lru_cache(maxsize=DEFAULT_CACHE_SIZE)
def _index_airfoil_cp(airfoil_cp_root: str) -> tuple[tuple[float, ...], tuple[tuple[float, str], ...]]:
    """Index Re folders and alpha files. Returns (Re_list, flat list of (Re, alpha, path))."""
    root = Path(airfoil_cp_root)
    if not root.is_dir():
        raise CoPDataError(f"Cp directory missing: {root}")
    records: list[tuple[float, float, str]] = []
    res: list[float] = []
    for re_dir in sorted(root.iterdir()):
        if not re_dir.is_dir():
            continue
        re_val = parse_re_dirname(re_dir.name)
        if re_val is None:
            continue
        res.append(re_val)
        for f in sorted(re_dir.glob("alpha*.csv")):
            a = parse_alpha_filename(f.name)
            if a is None:
                continue
            records.append((re_val, a, str(f)))
    if not records:
        raise CoPDataError(f"No Cp CSV files under {root}")
    re_unique = tuple(sorted(set(res)))
    return re_unique, tuple((r, a, p) for r, a, p in records)


def interpolate_pressure_distribution(
    airfoil: str,
    reynolds: float,
    alpha_deg: float,
    cp_root: Path,
    *,
    x_grid: np.ndarray | None = None,
) -> PressureDistribution:
    """Build continuous Cp(x) by bilinear blend in (log Re, alpha) then x-interp.

    Purpose: EQ-AERO-006 style log-Re + linear-alpha blend of archived Cp.
    Limitations: Requires at least one bounding Re and alpha in the archive.
    """
    re_list, records = _index_airfoil_cp(str(cp_root.resolve()))
    re_arr = np.asarray(re_list, dtype=float)
    # Clamp Re to available range
    re_use = float(np.clip(reynolds, re_arr.min(), re_arr.max()))
    # Find bracketing Re
    if re_use <= re_arr[0]:
        re1 = re2 = float(re_arr[0])
        w_re = 0.0
    elif re_use >= re_arr[-1]:
        re1 = re2 = float(re_arr[-1])
        w_re = 0.0
    else:
        i = int(np.searchsorted(re_arr, re_use) - 1)
        re1, re2 = float(re_arr[i]), float(re_arr[i + 1])
        w_re = (math_log(re_use) - math_log(re1)) / (math_log(re2) - math_log(re1))

    def at_re(re_val: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        alphas = sorted({a for r, a, _ in records if abs(r - re_val) < 1e-6})
        if not alphas:
            raise CoPInterpolationError(f"No alphas for Re={re_val}")
        a_arr = np.asarray(alphas, dtype=float)
        a_use = float(np.clip(alpha_deg, a_arr.min(), a_arr.max()))
        if a_use <= a_arr[0]:
            path = _path_for(records, re_val, float(a_arr[0]))
            return _read_cp_csv(Path(path))
        if a_use >= a_arr[-1]:
            path = _path_for(records, re_val, float(a_arr[-1]))
            return _read_cp_csv(Path(path))
        j = int(np.searchsorted(a_arr, a_use) - 1)
        a1, a2 = float(a_arr[j]), float(a_arr[j + 1])
        w = (a_use - a1) / (a2 - a1)
        x1, u1, l1 = _read_cp_csv(Path(_path_for(records, re_val, a1)))
        x2, u2, l2 = _read_cp_csv(Path(_path_for(records, re_val, a2)))
        grid = x_grid if x_grid is not None else np.unique(np.concatenate([x1, x2]))
        u = (1 - w) * interp1d(x1, u1, kind="linear", fill_value="extrapolate")(grid)
        l = (1 - w) * interp1d(x1, l1, kind="linear", fill_value="extrapolate")(grid)
        u += w * interp1d(x2, u2, kind="linear", fill_value="extrapolate")(grid)
        l += w * interp1d(x2, l2, kind="linear", fill_value="extrapolate")(grid)
        return grid, u, l

    x1, u1, l1 = at_re(re1)
    if abs(re2 - re1) < 1e-12:
        x, u, l = x1, u1, l1
    else:
        x2, u2, l2 = at_re(re2)
        grid = x_grid if x_grid is not None else np.unique(np.concatenate([x1, x2]))
        u = (1 - w_re) * interp1d(x1, u1, kind="linear", fill_value="extrapolate")(grid)
        l = (1 - w_re) * interp1d(x1, l1, kind="linear", fill_value="extrapolate")(grid)
        u += w_re * interp1d(x2, u2, kind="linear", fill_value="extrapolate")(grid)
        l += w_re * interp1d(x2, l2, kind="linear", fill_value="extrapolate")(grid)
        x = grid

    x, u, l = validate_cp_arrays(x, u, l)
    return PressureDistribution(
        airfoil=airfoil,
        reynolds=reynolds,
        alpha_deg=alpha_deg,
        x_c=tuple(float(v) for v in x),
        cp_upper=tuple(float(v) for v in u),
        cp_lower=tuple(float(v) for v in l),
        source="xfoil_file",
    )


def _path_for(records: tuple, re_val: float, alpha: float) -> str:
    for r, a, p in records:
        if abs(r - re_val) < 1e-6 and abs(a - alpha) < 1e-6:
            return p
    raise CoPInterpolationError(f"No file for Re={re_val} alpha={alpha}")


def math_log(x: float) -> float:
    return float(np.log(x))
