"""XFOIL-format Cp file provider (precomputed archives under data/airfoils)."""

from __future__ import annotations

from pathlib import Path

from auv_fin_design.domain.center_of_pressure.cp_interpolator import interpolate_pressure_distribution
from auv_fin_design.domain.center_of_pressure.cp_provider import CenterOfPressureProvider
from auv_fin_design.domain.center_of_pressure.exceptions import CoPDataError
from auv_fin_design.domain.center_of_pressure.models import PressureDistribution
from auv_fin_design.domain.center_of_pressure.utils import airfoil_dir, default_airfoils_root


class XfoilProvider(CenterOfPressureProvider):
    """Load Cp(x) from precomputed XFOIL-compatible CSV archives.

    Purpose: V1 production provider. Does not invoke the XFOIL binary.
    Layout: data/airfoils/<nacaXXXX>/cp/Re<Re>/alpha<deg>.csv
    Validity: Files may be panel-generated bootstrap; replace with true XFOIL dumps in place.
    """

    def __init__(self, airfoils_root: Path | None = None) -> None:
        self._root = Path(airfoils_root) if airfoils_root else default_airfoils_root()

    def load_pressure_distribution(
        self,
        airfoil: str,
        reynolds: float,
        alpha_deg: float,
    ) -> PressureDistribution:
        folder = airfoil_dir(self._root, airfoil)
        cp_root = folder / "cp"
        if not cp_root.is_dir():
            raise CoPDataError(
                f"Missing Cp archive at {cp_root}. Run scripts/generate_cp_dataset.py"
            )
        return interpolate_pressure_distribution(
            airfoil=folder.name,
            reynolds=reynolds,
            alpha_deg=alpha_deg,
            cp_root=cp_root,
        )
