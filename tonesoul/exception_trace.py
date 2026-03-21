"""Lightweight exception observer for suppressed runtime failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SuppressedError:
    """A single suppressed exception record."""

    component: str
    operation: str
    error_type: str
    message: str


class ExceptionTrace:
    """Session-scoped collector for suppressed exceptions."""

    def __init__(self) -> None:
        self._errors: List[SuppressedError] = []

    def record(self, component: str, operation: str, error: Exception) -> None:
        """Record a suppressed exception without changing control flow."""

        self._errors.append(
            SuppressedError(
                component=component,
                operation=operation,
                error_type=type(error).__name__,
                message=str(error)[:200],
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
        return {
            "suppressed_count": len(self._errors),
            "errors": [
                {
                    "component": error.component,
                    "operation": error.operation,
                    "error_type": error.error_type,
                    "message": error.message,
                }
                for error in self._errors
            ],
        }
