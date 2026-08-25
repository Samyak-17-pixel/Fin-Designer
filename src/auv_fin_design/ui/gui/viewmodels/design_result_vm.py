"""Single source of truth for GUI result display."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from auv_fin_design.domain.reporting.export import design_result_payload

if TYPE_CHECKING:
    from auv_fin_design.application.pipeline import DesignResult


@dataclass(frozen=True)
class DesignResultView:
    """Wraps live DesignResult plus serializable payload for all UI tabs."""

    result: DesignResult
    payload: dict[str, Any]

    @classmethod
    def from_result(cls, result: DesignResult) -> DesignResultView:
        return cls(result=result, payload=design_result_payload(result))

    @property
    def passed(self) -> bool:
        return bool(self.payload["passed"])

    @property
    def failure_count(self) -> int:
        return int(self.payload["diagnosis"].get("failure_count", 0))
