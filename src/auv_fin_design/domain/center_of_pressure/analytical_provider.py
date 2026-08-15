"""Stub providers for future CFD / experiment / analytical runtime paths."""

from __future__ import annotations

from auv_fin_design.domain.center_of_pressure.cp_provider import CenterOfPressureProvider
from auv_fin_design.domain.center_of_pressure.exceptions import CoPProviderNotImplementedError
from auv_fin_design.domain.center_of_pressure.models import PressureDistribution


class AnalyticalProvider(CenterOfPressureProvider):
    """Future analytical thin-airfoil Cp provider (not used in V1 runtime)."""

    def load_pressure_distribution(
        self, airfoil: str, reynolds: float, alpha_deg: float
    ) -> PressureDistribution:
        raise CoPProviderNotImplementedError(
            "AnalyticalProvider is a V1 stub; use XfoilProvider with precomputed Cp files"
        )


class CFDProvider(CenterOfPressureProvider):
    """Future CFD Cp provider."""

    def load_pressure_distribution(
        self, airfoil: str, reynolds: float, alpha_deg: float
    ) -> PressureDistribution:
        raise CoPProviderNotImplementedError("CFDProvider not implemented in V1")


class ExperimentalProvider(CenterOfPressureProvider):
    """Future experimental Cp provider."""

    def load_pressure_distribution(
        self, airfoil: str, reynolds: float, alpha_deg: float
    ) -> PressureDistribution:
        raise CoPProviderNotImplementedError("ExperimentalProvider not implemented in V1")
