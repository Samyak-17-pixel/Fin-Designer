"""Path and cache utilities for CoP module."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Callable, TypeVar

from auv_fin_design.infrastructure.config.loader import repo_root

T = TypeVar("T")


def default_airfoils_root() -> Path:
    """Resolve data/airfoils under repository root (no hardcoded absolute paths)."""
    return repo_root() / "data" / "airfoils"


def airfoil_dir(airfoils_root: Path, airfoil: str) -> Path:
    name = airfoil.strip().lower().replace(" ", "")
    if not name.startswith("naca") and name.replace("naca", "").isdigit() is False:
        # accept NACA0015 / naca0015 / 0015
        digits = "".join(ch for ch in name if ch.isdigit())
        if len(digits) >= 4:
            name = f"naca{digits[:4]}"
    elif name.startswith("naca") and "naca" in name:
        digits = "".join(ch for ch in name if ch.isdigit())
        if len(digits) >= 4:
            name = f"naca{digits[:4]}"
    return airfoils_root / name


def make_lru_cache(maxsize: int, enabled: bool) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Return lru_cache decorator or identity if caching disabled."""
    if not enabled:
        def identity(fn: Callable[..., T]) -> Callable[..., T]:
            return fn

        return identity
    return lru_cache(maxsize=maxsize)


def parse_re_dirname(name: str) -> float | None:
    """Parse Re100000 → 100000.0"""
    if not name.lower().startswith("re"):
        return None
    try:
        return float(name[2:])
    except ValueError:
        return None


def parse_alpha_filename(name: str) -> float | None:
    """Parse alpha2.00.csv or alpha-2.5.csv → degrees."""
    stem = Path(name).stem.lower()
    if not stem.startswith("alpha"):
        return None
    try:
        return float(stem.replace("alpha", ""))
    except ValueError:
        return None
