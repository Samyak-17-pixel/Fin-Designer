"""Constants for dynamic CoP solver — no magic numbers in algorithms."""

from __future__ import annotations

# Mechanical hinge / shaft station (frozen V1); CoP is free.
HINGE_CHORD_FRACTION = 0.25

# Strip theory defaults
DEFAULT_N_STRIPS = 100

# Numerical integration
DEFAULT_INTEGRATION_EPSREL = 1.0e-6
DEFAULT_INTEGRATION_LIMIT = 200

# Verification relative error on x_cp/c
DEFAULT_VERIFY_REL_TOL_WARN = 0.05
DEFAULT_VERIFY_REL_TOL_FAIL = 0.15

# Provider / cache
DEFAULT_PROVIDER = "xfoil_file"
DEFAULT_CACHE_ENABLED = True
DEFAULT_CACHE_SIZE = 256

# Alpha grid naming in Cp archives
ALPHA_FILENAME_DECIMALS = 2

# Body / control-surface frame: y ≈ 0 for lift-only mid-plane integration
DEFAULT_Y_CP_M = 0.0

# Equation IDs (Equation Register)
EQ_COP_CN = "EQ-COP-001"
EQ_COP_XCP = "EQ-COP-002"
EQ_COP_STRIP_LIFT = "EQ-COP-003"
EQ_COP_ZCP = "EQ-COP-004"
EQ_COP_HINGE = "EQ-COP-005"
EQ_COP_VERIFY = "EQ-COP-006"
EQ_COP_DELTA = "EQ-COP-007"
