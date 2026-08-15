"""Input validation for CoP data and configuration."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from auv_fin_design.domain.center_of_pressure.exceptions import CoPValidationError


def validate_airfoil_name(name: str) -> str:
    """Normalize and validate airfoil folder name."""
    cleaned = name.strip().lower().replace(" ", "")
    if not cleaned:
        raise CoPValidationError("Airfoil name is empty")
    return cleaned.replace("naca", "naca") if cleaned.startswith("naca") else f"naca{cleaned}" if cleaned.isdigit() else cleaned


def validate_cp_arrays(
    x_c: Sequence[float],
    cp_upper: Sequence[float],
    cp_lower: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Validate Cp arrays: finite, same length, x in [0,1], strictly increasing after unique."""
    x = np.asarray(x_c, dtype=float)
    cu = np.asarray(cp_upper, dtype=float)
    cl = np.asarray(cp_lower, dtype=float)
    if x.size < 3:
        raise CoPValidationError("Cp distribution needs at least 3 points")
    if not (x.size == cu.size == cl.size):
        raise CoPValidationError("x_c, Cp_upper, Cp_lower length mismatch")
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(cu)) and np.all(np.isfinite(cl))):
        raise CoPValidationError("NaN/Inf in Cp distribution")
    # Deduplicate x (keep first)
    _, idx = np.unique(x, return_index=True)
    idx = np.sort(idx)
    x, cu, cl = x[idx], cu[idx], cl[idx]
    if x.size < 3:
        raise CoPValidationError("Too few unique x stations after deduplication")
    if np.any(np.diff(x) <= 0):
        raise CoPValidationError("x_c must be strictly monotonic increasing")
    if x[0] < -1e-6 or x[-1] > 1.0 + 1e-6:
        raise CoPValidationError("x_c must lie in [0, 1]")
    x = np.clip(x, 0.0, 1.0)
    return x, cu, cl


def validate_positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise CoPValidationError(f"{name} must be finite and > 0, got {value}")
    return value
