"""Airfoil polar database with log-Re interpolation — EQ-AERO-006."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class PolarPoint:
    alpha_deg: float
    cl: float
    cd: float
    cdp: float
    cm: float


@dataclass(frozen=True)
class AirfoilPolar:
    airfoil: str
    reynolds: float
    alpha_deg: NDArray[np.floating]
    cl: NDArray[np.floating]
    cd: NDArray[np.floating]
    cdp: NDArray[np.floating]
    cm: NDArray[np.floating]
    max_cl_cd: float | None = None
    max_cl_cd_alpha: float | None = None

    def interpolate_at_alpha(self, alpha_deg: float) -> PolarPoint:
        a = self.alpha_deg
        if alpha_deg <= float(a[0]):
            i = 0
            return PolarPoint(float(a[0]), float(self.cl[0]), float(self.cd[0]), float(self.cdp[0]), float(self.cm[0]))
        if alpha_deg >= float(a[-1]):
            return PolarPoint(float(a[-1]), float(self.cl[-1]), float(self.cd[-1]), float(self.cdp[-1]), float(self.cm[-1]))
        cl = float(np.interp(alpha_deg, a, self.cl))
        cd = float(np.interp(alpha_deg, a, self.cd))
        cdp = float(np.interp(alpha_deg, a, self.cdp))
        cm = float(np.interp(alpha_deg, a, self.cm))
        return PolarPoint(alpha_deg, cl, cd, cdp, cm)

    def cl_alpha_per_rad(self, alpha_lo: float = -2.0, alpha_hi: float = 4.0) -> float:
        """Estimate 2D lift-curve slope [1/rad] from linear polar region."""
        mask = (self.alpha_deg >= alpha_lo) & (self.alpha_deg <= alpha_hi)
        if np.count_nonzero(mask) < 3:
            mask = (self.alpha_deg >= -4.0) & (self.alpha_deg <= 6.0)
        x = np.deg2rad(self.alpha_deg[mask])
        y = self.cl[mask]
        # Linear fit cl = a * alpha + b
        a, _b = np.polyfit(x, y, 1)
        return float(a)

    def first_local_cl_max(self, smooth_window: int = 3) -> tuple[float, float]:
        """Return (CL_max, alpha_deg) of first local maximum for alpha>0 — EQ-AERO-003."""
        cl = self.cl.astype(float).copy()
        if smooth_window >= 3:
            kernel = np.ones(smooth_window) / smooth_window
            cl = np.convolve(cl, kernel, mode="same")
        # Search alpha > 0
        pos = self.alpha_deg > 0
        idxs = np.where(pos)[0]
        for i in idxs[1:-1]:
            if cl[i] >= cl[i - 1] and cl[i] >= cl[i + 1] and cl[i] > 0:
                return float(cl[i]), float(self.alpha_deg[i])
        # Fallback: global max on positive alpha
        if len(idxs):
            j = idxs[np.argmax(cl[idxs])]
            return float(self.cl[j]), float(self.alpha_deg[j])
        j = int(np.argmax(self.cl))
        return float(self.cl[j]), float(self.alpha_deg[j])


def parse_airfoiltools_csv(path: Path) -> AirfoilPolar:
    """Parse AirfoilTools / XFOIL CSV polar."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    airfoil = path.stem
    reynolds = 0.0
    max_cl_cd = None
    max_cl_cd_alpha = None
    data_start = 0
    for i, line in enumerate(lines):
        if line.lower().startswith("airfoil,"):
            airfoil = line.split(",", 1)[1].strip()
        elif line.lower().startswith("reynolds number,"):
            reynolds = float(line.split(",", 1)[1].strip())
        elif line.lower().startswith("max cl/cd,"):
            try:
                max_cl_cd = float(line.split(",", 1)[1].strip())
            except ValueError:
                pass
        elif line.lower().startswith("max cl/cd alpha,"):
            try:
                max_cl_cd_alpha = float(line.split(",", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("Alpha,"):
            data_start = i + 1
            break
    rows = []
    for line in lines[data_start:]:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 5:
            continue
        try:
            rows.append([float(parts[j]) for j in range(5)])
        except ValueError:
            continue
    arr = np.asarray(rows, dtype=float)
    if arr.size == 0:
        raise ValueError(f"No polar data in {path}")
    # Infer Re from filename if missing
    if reynolds <= 0:
        m = re.search(r"(\d{4,8})", path.stem)
        if m:
            reynolds = float(m.group(1))
    return AirfoilPolar(
        airfoil=airfoil,
        reynolds=reynolds,
        alpha_deg=arr[:, 0],
        cl=arr[:, 1],
        cd=arr[:, 2],
        cdp=arr[:, 3],
        cm=arr[:, 4],
        max_cl_cd=max_cl_cd,
        max_cl_cd_alpha=max_cl_cd_alpha,
    )


@dataclass
class AirfoilEntry:
    name: str
    folder: Path
    thickness_ratio: float
    polars: list[AirfoilPolar]

    def polar_at_re(self, re: float) -> AirfoilPolar:
        """Log-Re interpolate between nearest polars — EQ-AERO-006."""
        if not self.polars:
            raise ValueError(f"No polars for {self.name}")
        polars = sorted(self.polars, key=lambda p: p.reynolds)
        res = [p.reynolds for p in polars]
        if re <= res[0]:
            return polars[0]
        if re >= res[-1]:
            return polars[-1]
        # Find bracket
        for i in range(len(res) - 1):
            if res[i] <= re <= res[i + 1]:
                p1, p2 = polars[i], polars[i + 1]
                w = (math.log(re) - math.log(res[i])) / (math.log(res[i + 1]) - math.log(res[i]))
                return _blend_polars(p1, p2, w, re)
        return polars[-1]


def _blend_polars(p1: AirfoilPolar, p2: AirfoilPolar, w: float, re: float) -> AirfoilPolar:
    """Blend on common alpha grid."""
    a_min = max(float(p1.alpha_deg[0]), float(p2.alpha_deg[0]))
    a_max = min(float(p1.alpha_deg[-1]), float(p2.alpha_deg[-1]))
    grid = np.linspace(a_min, a_max, 161)
    cl = (1 - w) * np.interp(grid, p1.alpha_deg, p1.cl) + w * np.interp(grid, p2.alpha_deg, p2.cl)
    cd = (1 - w) * np.interp(grid, p1.alpha_deg, p1.cd) + w * np.interp(grid, p2.alpha_deg, p2.cd)
    cdp = (1 - w) * np.interp(grid, p1.alpha_deg, p1.cdp) + w * np.interp(grid, p2.alpha_deg, p2.cdp)
    cm = (1 - w) * np.interp(grid, p1.alpha_deg, p1.cm) + w * np.interp(grid, p2.alpha_deg, p2.cm)
    return AirfoilPolar(
        airfoil=p1.airfoil,
        reynolds=re,
        alpha_deg=grid,
        cl=cl,
        cd=cd,
        cdp=cdp,
        cm=cm,
    )


class AirfoilDatabase:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.entries: dict[str, AirfoilEntry] = {}
        self._load()

    def _load(self) -> None:
        from auv_fin_design.domain.airfoil.naca import thickness_ratio_from_code

        if not self.root.exists():
            return
        for folder in sorted(self.root.iterdir()):
            if not folder.is_dir():
                continue
            name = folder.name.upper()
            polars = []
            for csv in sorted(folder.glob("*.csv")):
                polars.append(parse_airfoiltools_csv(csv))
            if not polars:
                continue
            try:
                t = thickness_ratio_from_code(name)
            except ValueError:
                t = 0.12
            self.entries[name] = AirfoilEntry(name=name, folder=folder, thickness_ratio=t, polars=polars)

    def names(self) -> list[str]:
        return sorted(self.entries.keys())

    def get(self, name: str) -> AirfoilEntry:
        key = name.upper()
        if key in self.entries:
            return self.entries[key]
        # Accept "0012" or "NACA0012"
        digits = "".join(ch for ch in key if ch.isdigit())[:4]
        for k, entry in self.entries.items():
            if "".join(ch for ch in k if ch.isdigit())[:4] == digits:
                return entry
        raise KeyError(name)
