"""Configuration loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULTS_PATH = _REPO_ROOT / "configs" / "defaults.yaml"


def repo_root() -> Path:
    return _REPO_ROOT


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_defaults(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or _DEFAULTS_PATH)


def load_equation_register() -> dict[str, Any]:
    path = _REPO_ROOT / "docs" / "equations" / "equation_register.yaml"
    return load_yaml(path)
