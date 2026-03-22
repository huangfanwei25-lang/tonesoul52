"""AlertEscalation — 三層異常感知系統 (L1 / L2 / L3).

Aggregates signals from DriftMonitor, LambdaObserver, CircuitBreaker,
and JumpMonitor into a graduated alert hierarchy:

  L1 (Wave)      — anomaly logging, no action change
  L2 (Structure)  — freeze structural updates, annotate warning
  L3 (Systemic)   — Seabed-grade degradation (Guardian-only, minimal output)

Spec reference: TONESOUL_THEORY Section VII (L1-L3 Alerts).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AlertLevel(str, Enum):
    """Three-tier alert classification per spec."""

    CLEAR = "clear"
    L1 = "L1"  # Wave layer instability
    L2 = "L2"  # Structure layer drift / near-freeze
    L3 = "L3"  # Systemic failure → Seabed Lockdown


@dataclass
class AlertEvent:
    """Immutable record of a single escalation evaluation."""

    level: AlertLevel
    reasons: List[str]
    signals: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_clear(self) -> bool:
        return self.level == AlertLevel.CLEAR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "reasons": list(self.reasons),
            "signals": dict(self.signals),
        }


class AlertEscalation:
    """Centralized anomaly orchestrator.

    Collects heterogeneous safety signals and classifies them into
    the highest applicable alert level.  Does NOT take action itself —
    the caller (UnifiedPipeline) decides what to do with the result.

    Signal mapping
    ──────────────
    L3 triggers (any one is sufficient):
      • jump_triggered == True
      • circuit_breaker_status == "frozen"

    L2 triggers (any one is sufficient):
      • drift_alert == "crisis"
      • jump_indicators_tripped >= 1  (pre-singularity)
      • lambda_state == "chaotic"

    L1 triggers (any one is sufficient):
      • drift_alert == "warning"
      • lambda_state == "divergent"
      • consecutive_high_friction >= 2
    """

    def __init__(self) -> None:
        self._history: List[AlertEvent] = []

    def evaluate(
        self,
        *,
        drift_alert: Optional[str] = None,
        lambda_state: Optional[str] = None,
        circuit_breaker_status: Optional[str] = None,
        jump_triggered: bool = False,
        jump_indicators_tripped: int = 0,
        consecutive_high_friction: int = 0,
    ) -> AlertEvent:
        """Evaluate all signals and return the highest-severity AlertEvent."""

        _rank = {AlertLevel.CLEAR: 0, AlertLevel.L1: 1, AlertLevel.L2: 2, AlertLevel.L3: 3}

        reasons: List[str] = []
        signals: Dict[str, Any] = {
            "drift_alert": drift_alert,
            "lambda_state": lambda_state,
            "circuit_breaker_status": circuit_breaker_status,
            "jump_triggered": jump_triggered,
            "jump_indicators_tripped": jump_indicators_tripped,
            "consecutive_high_friction": consecutive_high_friction,
        }

        level = AlertLevel.CLEAR

        # --- L3 checks (highest severity) ---
        if jump_triggered:
            reasons.append("JUMP singularity triggered")
            level = AlertLevel.L3
        if circuit_breaker_status == "frozen":
            reasons.append("CircuitBreaker frozen")
            level = AlertLevel.L3

        # --- L2 checks (only if not already L3) ---
        if _rank[level] < _rank[AlertLevel.L2]:
            if drift_alert == "crisis":
                reasons.append("drift crisis (structure layer)")
                level = AlertLevel.L2
            if jump_indicators_tripped >= 1 and not jump_triggered:
                reasons.append(f"pre-singularity ({jump_indicators_tripped} indicator(s))")
                level = AlertLevel.L2
            if lambda_state == "chaotic":
                reasons.append("lambda state chaotic (wave energy surge)")
                level = AlertLevel.L2

        # --- L1 checks (only if still CLEAR) ---
        if level == AlertLevel.CLEAR:
            if drift_alert == "warning":
                reasons.append("drift warning (approaching threshold)")
                level = AlertLevel.L1
            if lambda_state == "divergent":
                reasons.append("lambda state divergent (oscillation)")
                level = AlertLevel.L1
            if consecutive_high_friction >= 2:
                reasons.append(f"consecutive high friction ({consecutive_high_friction})")
                level = AlertLevel.L1

        event = AlertEvent(level=level, reasons=reasons, signals=signals)
        self._history.append(event)
        return event

    @property
    def last_event(self) -> Optional[AlertEvent]:
        return self._history[-1] if self._history else None

    @property
    def highest_ever(self) -> AlertLevel:
        """Return the highest alert level seen in this session."""
        if not self._history:
            return AlertLevel.CLEAR
        order = {AlertLevel.CLEAR: 0, AlertLevel.L1: 1, AlertLevel.L2: 2, AlertLevel.L3: 3}
        return max((e.level for e in self._history), key=lambda lv: order[lv])

    def summary(self) -> Dict[str, Any]:
        """Compact summary for dispatch_trace."""
        last = self.last_event
        return {
            "current_level": last.level.value if last else "clear",
            "reasons": last.reasons if last else [],
            "evaluations": len(self._history),
            "highest_ever": self.highest_ever.value,
        }
