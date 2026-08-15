"""Abstract CenterOfPressureProvider — swappable Cp data source."""

from __future__ import annotations

from abc import ABC, abstractmethod

from auv_fin_design.domain.center_of_pressure.models import PressureDistribution


class CenterOfPressureProvider(ABC):
    """Load sectional Cp(x) for airfoil, Reynolds number, and angle of attack.

    Purpose: Decouple CoP solver from data origin (XFOIL archive, CFD, experiment).
    Inputs: airfoil name, Re [-], alpha [deg].
    Outputs: PressureDistribution (x/c, Cp_upper, Cp_lower).
    Validity: Provider-specific; missing data → CoPDataError.
    """

    @abstractmethod
    def load_pressure_distribution(
        self,
        airfoil: str,
        reynolds: float,
        alpha_deg: float,
    ) -> PressureDistribution:
        """Return Cp(x) at the requested (or interpolated) operating point."""
        raise NotImplementedError
