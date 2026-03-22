"""JUMP Engine — Singularity Detection & Seabed Lockdown.

Implements Vol-5 §2 monitoring:
  1. Reasoning convergence: ΔU / ΔInput → 0
  2. Responsibility chain integrity: echo-trace completeness
  3. Self-reference ratio: r = ‖C_t − C_{t−1}‖ / ‖Input_t‖

When any two of the three indicators exceed their thresholds, the system
enters **Seabed Lockdown** — restricting actions to Verify / Cite / Inquire.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class LockdownStatus(str, Enum):
    NORMAL = "normal"
    LOCKDOWN = "lockdown"


@dataclass
class JumpSignal:
    """Result of a singularity check."""

    triggered: bool = False
    reasoning_convergence: float = 1.0  # ΔU/ΔInput, lower = more converged
    chain_integrity: float = 1.0  # 0.0-1.0, lower = less complete
    self_reference_ratio: float = 0.0  # higher = more self-referential
    indicators_tripped: int = 0
    reason: str = ""


@dataclass
class _OutputRecord:
    """Lightweight record of a pipeline output for convergence tracking."""

    tension_total: float = 0.0
    has_echo_trace: bool = True
    center_delta_norm: float = 0.0
    input_norm: float = 1.0
    timestamp: str = ""


class JumpMonitor:
    """Tracks singularity indicators over a sliding window.

    Parameters
    ----------
    window_size : int
        Number of recent outputs to consider (default: 10).
    convergence_threshold : float
        When ΔU/ΔInput falls below this, reasoning convergence trips (default: 0.05).
    chain_threshold : float
        When echo-trace integrity falls below this, chain integrity trips (default: 0.3).
    self_ref_threshold : float
        When self-reference ratio exceeds this, self-reference trips (default: 0.8).
    min_indicators : int
        How many indicators must trip to trigger JUMP (default: 2).
    """

    def __init__(
        self,
        window_size: int = 10,
        convergence_threshold: float = 0.05,
        chain_threshold: float = 0.3,
        self_ref_threshold: float = 0.8,
        min_indicators: int = 2,
    ) -> None:
        self._window: deque[_OutputRecord] = deque(maxlen=max(2, window_size))
        self._convergence_threshold = convergence_threshold
        self._chain_threshold = chain_threshold
        self._self_ref_threshold = self_ref_threshold
        self._min_indicators = min_indicators
        self._status = LockdownStatus.NORMAL
        self._lockdown_reason: str = ""
        self._lockdown_at: Optional[str] = None

    # --- Public API ---

    @property
    def status(self) -> LockdownStatus:
        return self._status

    @property
    def lockdown_reason(self) -> str:
        return self._lockdown_reason

    def record_output(
        self,
        tension_total: float = 0.0,
        has_echo_trace: bool = True,
        center_delta_norm: float = 0.0,
        input_norm: float = 1.0,
    ) -> None:
        """Record a pipeline output for subsequent singularity checks."""
        self._window.append(
            _OutputRecord(
                tension_total=tension_total,
                has_echo_trace=has_echo_trace,
                center_delta_norm=center_delta_norm,
                input_norm=max(1e-12, input_norm),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )

    def check_singularity(self) -> JumpSignal:
        """Evaluate the three singularity indicators over recent outputs.

        Returns a JumpSignal indicating whether JUMP should be triggered.
        """
        if len(self._window) < 2:
            return JumpSignal()

        rc = self._measure_reasoning_convergence()
        ci = self._measure_chain_integrity()
        sr = self._measure_self_reference_ratio()

        tripped = 0
        reasons: List[str] = []

        if rc < self._convergence_threshold:
            tripped += 1
            reasons.append(f"reasoning_convergence={rc:.4f}")
        if ci < self._chain_threshold:
            tripped += 1
            reasons.append(f"chain_integrity={ci:.4f}")
        if sr > self._self_ref_threshold:
            tripped += 1
            reasons.append(f"self_reference_ratio={sr:.4f}")

        triggered = tripped >= self._min_indicators
        reason = "; ".join(reasons) if reasons else ""

        if triggered and self._status != LockdownStatus.LOCKDOWN:
            self._status = LockdownStatus.LOCKDOWN
            self._lockdown_reason = reason
            self._lockdown_at = datetime.now(timezone.utc).isoformat()

        return JumpSignal(
            triggered=triggered,
            reasoning_convergence=rc,
            chain_integrity=ci,
            self_reference_ratio=sr,
            indicators_tripped=tripped,
            reason=reason,
        )

    def exit_lockdown(self) -> bool:
        """Exit Seabed Lockdown. Requires explicit call (human approval path)."""
        if self._status != LockdownStatus.LOCKDOWN:
            return False
        self._status = LockdownStatus.NORMAL
        self._lockdown_reason = ""
        self._lockdown_at = None
        self._window.clear()
        return True

    def to_dict(self) -> Dict[str, object]:
        """Serialise current state for observability."""
        return {
            "status": self._status.value,
            "lockdown_reason": self._lockdown_reason,
            "lockdown_at": self._lockdown_at,
            "window_size": len(self._window),
        }

    # --- Internal Metrics ---

    def _measure_reasoning_convergence(self) -> float:
        """Compute ΔU/ΔInput — marginal improvement ratio.

        Uses the tension_total as a proxy for U (utility).
        Returns a value in [0, ∞). Values near 0 indicate convergence.
        """
        records = list(self._window)
        if len(records) < 2:
            return 1.0
        deltas = [
            abs(records[i].tension_total - records[i - 1].tension_total)
            for i in range(1, len(records))
        ]
        mean_delta = sum(deltas) / len(deltas)
        return mean_delta

    def _measure_chain_integrity(self) -> float:
        """Compute echo-trace completeness over the window.

        Returns proportion of recent outputs that have a complete
        responsibility chain (echo trace).  1.0 = all complete.
        """
        records = list(self._window)
        if not records:
            return 1.0
        complete = sum(1 for r in records if r.has_echo_trace)
        return complete / len(records)

    def _measure_self_reference_ratio(self) -> float:
        """Compute average self-reference ratio: ‖C_t − C_{t−1}‖ / ‖Input_t‖.

        Higher values indicate the system is primarily updating its
        internal state from its own past rather than from external input.
        """
        records = list(self._window)
        if not records:
            return 0.0
        ratios = [r.center_delta_norm / r.input_norm for r in records]
        return sum(ratios) / len(ratios)
