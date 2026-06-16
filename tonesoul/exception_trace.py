"""Lightweight exception observer for suppressed runtime failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

__ts_layer__ = "observability"
__ts_purpose__ = "Exception trace: structured exception capture for governance fault observability."


@dataclass
class SuppressedError:
    """A single suppressed exception record.

    ``tier`` classifies the fail-soft semantics (see DESIGN.md "Fail-Soft Has Tiers"):
    - ``"optional"`` — degradable subsystem; failure tolerated but made VISIBLE (default).
    - ``"telemetry"`` — best-effort/high-volume; failure ignorable but COUNTED.
    ``"required"`` failures do not appear here — they fail closed (raise) instead of
    being suppressed.
    """

    component: str
    operation: str
    error_type: str
    message: str
    tier: str = "optional"


class ExceptionTrace:
    """Session-scoped collector for suppressed exceptions."""

    def __init__(self) -> None:
        self._errors: List[SuppressedError] = []

    def record(
        self,
        component: str,
        operation: str,
        error: Exception,
        tier: str = "optional",
    ) -> None:
        """Record a suppressed exception without changing control flow.

        ``tier`` is the fail-soft class: ``"optional"`` (degraded, visible — default)
        or ``"telemetry"`` (best-effort, counted). ``"required"`` failures should fail
        closed (raise) rather than be recorded here.
        """

        self._errors.append(
            SuppressedError(
                component=component,
                operation=operation,
                error_type=type(error).__name__,
                message=str(error)[:200],
                tier=tier,
            )
        )

    @property
    def has_errors(self) -> bool:
        return bool(self._errors)

    @property
    def count(self) -> int:
        return len(self._errors)

    def summary(self) -> Dict[str, Any]:
        """Return a structured payload suitable for dispatch traces."""

        if not self._errors:
            return {"suppressed_count": 0}
        tiers: Dict[str, int] = {}
        for error in self._errors:
            tiers[error.tier] = tiers.get(error.tier, 0) + 1
        return {
            "suppressed_count": len(self._errors),
            "tiers": tiers,
            "errors": [
                {
                    "component": error.component,
                    "operation": error.operation,
                    "error_type": error.error_type,
                    "message": error.message,
                    "tier": error.tier,
                }
                for error in self._errors
            ],
        }
