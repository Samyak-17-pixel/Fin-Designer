"""Simple STL export of a solid NACA fin (no CadQuery required)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from auv_fin_design.domain.airfoil.naca import generate_naca4_coordinates
from auv_fin_design.domain.geometry.sizing import CandidateFinGeometry


def _section_xy(code: str, chord: float, n: int = 41) -> np.ndarray:
    coords, _ = generate_naca4_coordinates(code, n_points=n)
    # coords are closed TE→around; use unique upper+lower from generator
    arr = np.asarray(coords, dtype=float)
    # Keep first n points as upper (LE to TE) then lower already appended
    return arr * np.array([chord, chord])


def export_fin_stl(
    geom: CandidateFinGeometry,
    path: Path,
    *,
    naca_code: str = "0018",
    n_chord: int = 41,
) -> Path:
    """Loft root→tip NACA sections and write binary-ish ASCII STL."""
    root = _section_xy(naca_code, geom.root_chord, n_chord)
    tip = _section_xy(naca_code, geom.tip_chord, n_chord)
    # Align LE at x=0 for both; span along z
    z0, z1 = 0.0, geom.span
    # Build triangle strip between corresponding points
    # Use same index count
    n = min(len(root), len(tip))
    root = root[:n]
    tip = tip[:n]
    facets: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for i in range(n - 1):
        r0 = np.array([root[i, 0], root[i, 1], z0])
        r1 = np.array([root[i + 1, 0], root[i + 1, 1], z0])
        t0 = np.array([tip[i, 0], tip[i, 1], z1])
        t1 = np.array([tip[i + 1, 0], tip[i + 1, 1], z1])
        facets.append((r0, r1, t0))
        facets.append((r1, t1, t0))
    # Cap root and tip approximately with fan from centroid
    for section, z in ((root, z0), (tip, z1)):
        c = np.array([section[:, 0].mean(), section[:, 1].mean(), z])
        for i in range(n - 1):
            p0 = np.array([section[i, 0], section[i, 1], z])
            p1 = np.array([section[i + 1, 0], section[i + 1, 1], z])
            facets.append((c, p0, p1))

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["solid auv_fin"]
    for a, b, c in facets:
        nrm = np.cross(b - a, c - a)
        nn = np.linalg.norm(nrm)
        if nn > 0:
            nrm = nrm / nn
        else:
            nrm = np.array([0.0, 0.0, 1.0])
        lines.append(f"  facet normal {nrm[0]:.6e} {nrm[1]:.6e} {nrm[2]:.6e}")
        lines.append("    outer loop")
        for p in (a, b, c):
            lines.append(f"      vertex {p[0]:.6e} {p[1]:.6e} {p[2]:.6e}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append("endsolid auv_fin")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
