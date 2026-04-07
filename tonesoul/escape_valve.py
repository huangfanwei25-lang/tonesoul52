"""Escape Valve: circuit breaker for constraint loops.

This module prevents infinite rejections when multiple audit layers
(Council, BenevolenceFilter, 7D) repeatedly block outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class EscapeReason(str, Enum):
    """Reasons for triggering the Escape Valve."""

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    SAME_FAILURE_REPEATED = "same_failure_repeated"
    MANUAL_OVERRIDE = "manual_override"


@dataclass
class EscapeValveConfig:
    """Configuration for the Escape Valve."""

    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    uncertainty_allowed: bool = True
    same_failure_threshold: int = 2


@dataclass
class EscapeValveResult:
    """Result of an Escape Valve evaluation."""

    triggered: bool
    reason: Optional[EscapeReason] = None
    retry_count: int = 0
    failure_history: list[str] = field(default_factory=list)
    final_output: Optional[str] = None
    uncertainty_tag: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/serialization."""
        return {
            "triggered": self.triggered,
            "reason": self.reason.value if self.reason else None,
            "retry_count": self.retry_count,
            "failure_history": self.failure_history,
            "final_output": self.final_output,
            "uncertainty_tag": self.uncertainty_tag,
            "timestamp": self.timestamp.isoformat(),
        }


class EscapeValve:
    """Circuit breaker for constraint loops."""

    def __init__(self, config: Optional[EscapeValveConfig] = None):
        self.config = config or EscapeValveConfig()
        self._failure_history: list[str] = []
        self._circuit_open: bool = False
        self._consecutive_failures: int = 0

    def reset(self) -> None:
        """Reset failure history, consecutive counts, and circuit breaker."""
        self._failure_history = []
        self._consecutive_failures = 0
        self._circuit_open = False

    def record_failure(self, reason: str) -> None:
        """Record one failure."""
        self._failure_history.append(reason)
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.config.circuit_breaker_threshold:
            self._circuit_open = True

    def record_success(self) -> None:
        """Record success and clear consecutive-failure pressure."""
        self._consecutive_failures = 0

    def evaluate(self, proposed_output: Optional[str] = None) -> EscapeValveResult:
        """Evaluate whether the escape valve should trigger."""
        if self._circuit_open:
            return self._create_escape_result(
                reason=EscapeReason.CIRCUIT_BREAKER_OPEN,
                proposed_output=proposed_output,
            )

        if len(self._failure_history) >= self.config.max_retries:
            return self._create_escape_result(
                reason=EscapeReason.MAX_RETRIES_EXCEEDED,
                proposed_output=proposed_output,
            )

        if self._has_repeated_failure():
            return self._create_escape_result(
                reason=EscapeReason.SAME_FAILURE_REPEATED,
                proposed_output=proposed_output,
            )

        return EscapeValveResult(
            triggered=False,
            retry_count=len(self._failure_history),
            failure_history=self._failure_history.copy(),
        )

    def _has_repeated_failure(self) -> bool:
        if len(self._failure_history) < self.config.same_failure_threshold:
            return False
        recent = self._failure_history[-self.config.same_failure_threshold :]
        return len(set(recent)) == 1

    def _create_escape_result(
        self,
        reason: EscapeReason,
        proposed_output: Optional[str],
    ) -> EscapeValveResult:
        return EscapeValveResult(
            triggered=True,
            reason=reason,
            retry_count=len(self._failure_history),
            failure_history=self._failure_history.copy(),
            final_output=self._format_uncertainty_output(proposed_output, reason),
            uncertainty_tag=True,
        )

    def _format_uncertainty_output(
        self,
        proposed_output: Optional[str],
        reason: EscapeReason,
    ) -> str:
        """Format output with uncertainty tag."""
        if not self.config.uncertainty_allowed:
            return "[BLOCKED] Unable to produce compliant output."

        base_output = proposed_output or "Unable to provide a fully reliable answer."
        recent_failures = self._failure_history[-3:]
        failure_summary = "; ".join(dict.fromkeys(recent_failures)) if recent_failures else "none"

        return (
            f"[UNCERTAINTY] {base_output}\n\n"
            "---\n"
            f"Escape valve reason: {reason.value}\n"
            f"Recent failures: {failure_summary}\n"
            f"Total failures: {len(self._failure_history)}"
        )

    @property
    def is_circuit_open(self) -> bool:
        return self._circuit_open

    @property
    def failure_count(self) -> int:
        return len(self._failure_history)
