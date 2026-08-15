"""NACA 4-digit geometry — EQ-NACA-001 (Abbott & von Doenhoff)."""

from __future__ import annotations

import math
from pathlib import Path


def naca4_thickness_yt(x: float, t: float) -> float:
    """EQ-NACA-001 — half-thickness yt/c for thickness ratio t (e.g. 0.12 for NACA0012)."""
    if x < 0.0 or x > 1.0:
        raise ValueError("x must be in [0, 1] (fraction of chord)")
    if x == 0.0:
        return 0.0
    return 5.0 * t * (
        0.2969 * math.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )


def naca4_full_thickness_ratio(x: float, t: float) -> float:
    """Local section thickness / chord at station x (full width = 2 yt/c)."""
    return 2.0 * naca4_thickness_yt(x, t)


def naca4_full_thickness(x_frac: float, thickness_ratio: float, chord: float) -> float:
    """Local full section thickness [m] at chord fraction x_frac."""
    return naca4_full_thickness_ratio(x_frac, thickness_ratio) * chord


def generate_naca4_coordinates(
    code: str,
    n_points: int = 81,
) -> tuple[list[tuple[float, float]], float]:
    """Generate closed NACA 4-digit section coordinates (x/c, y/c).

    Returns (coords upper+lower TE→LE→TE style, thickness_ratio).
    Symmetric sections only for 00xx in V1.
    """
    code = code.upper().replace("NACA", "").strip()
    if len(code) != 4 or not code.isdigit():
        raise ValueError(f"Unsupported NACA code: {code}")
    t = int(code[2:]) / 100.0
    # Cosine spacing
    betas = [math.pi * i / (n_points - 1) for i in range(n_points)]
    xs = [0.5 * (1.0 - math.cos(b)) for b in betas]
    upper = [(x, naca4_thickness_yt(x, t)) for x in xs]
    lower = [(x, -naca4_thickness_yt(x, t)) for x in reversed(xs[1:])]
    coords = upper + lower
    return coords, t


def write_dat_file(path: Path, name: str, coords: list[tuple[float, float]]) -> None:
    lines = [name]
    for x, y in coords:
        lines.append(f"{x:.6f} {y:.6f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def thickness_ratio_from_code(code: str) -> float:
    code = code.upper().replace("NACA", "").strip()
    # Accept aliases like 0012H
    digits = "".join(ch for ch in code if ch.isdigit())
    if len(digits) < 4:
        raise ValueError(f"Cannot parse thickness from {code}")
    return int(digits[2:4]) / 100.0
