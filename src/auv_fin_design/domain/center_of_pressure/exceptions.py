"""Engineering exceptions for the CoP module."""

from __future__ import annotations


class CoPError(Exception):
    """Base CoP engineering error."""


class CoPDataError(CoPError):
    """Missing or unreadable Cp / airfoil data."""


class CoPInterpolationError(CoPError):
    """Failed Re / alpha / chord interpolation."""


class CoPIntegrationError(CoPError):
    """Numerical integration failure or non-physical result."""


class CoPValidationError(CoPError):
    """Invalid geometry, coordinates, or configuration."""


class CoPProviderNotImplementedError(CoPError, NotImplementedError):
    """Provider stub not available in this version."""
