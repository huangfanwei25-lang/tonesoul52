"""
Phase 544: Drift Monitor — Structure Layer semantic anchor.

Tracks the system's "context center" C_t via Exponential Moving Average (EMA)
and computes drift from the Home vector H.  When drift exceeds a threshold the
monitor emits an alert level that governance can act on.

Formula (from TONESOUL_THEORY spec):
    C_t = ema_alpha * observation + (1 - ema_alpha) * C_prev
    Drift(C_t, H) = 1 - cos(C_t, H)        (range 0-2, practically 0-1)
    If Drift > theta_warning  → WARNING
    If Drift > theta_crisis   → CRISIS
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class DriftAlert(Enum):
    NONE = "none"
    WARNING = "warning"
    CRISIS = "crisis"


@dataclass
class DriftSnapshot:
    """Immutable snapshot of drift state at a point in time."""

    center: Dict[str, float]
    home: Dict[str, float]
    drift: float
    alert: DriftAlert
    step: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "center": dict(self.center),
            "home": dict(self.home),
            "drift": round(self.drift, 6),
            "alert": self.alert.value,
            "step": self.step,
        }


@dataclass
class DriftActionRecommendation:
    """Bounded action guidance derived from the latest drift alert."""

    alert: DriftAlert
    action: str
    note: str
    current_drift: float
    step: int
    log_required: bool = True
    increase_caution: bool = False
    session_pause_recommended: bool = False
    human_check_in_recommended: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "alert": self.alert.value,
            "action": self.action,
            "note": self.note,
            "current_drift": round(self.current_drift, 6),
            "step": self.step,
            "log_required": self.log_required,
            "increase_caution": self.increase_caution,
            "session_pause_recommended": self.session_pause_recommended,
            "human_check_in_recommended": self.human_check_in_recommended,
        }


_DEFAULT_HOME = {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}
_DIMS = ("deltaT", "deltaS", "deltaR")


class DriftMonitor:
    """Session-level drift monitor in 3-dim persona space.

    Parameters
    ----------
    home_vector : dict
        Fixed anchor vector {"deltaT", "deltaS", "deltaR"}.
    ema_alpha : float
        Weight for new observations (default 0.3 → smooth 5-turn EMA).
    theta_warning : float
        Drift threshold for WARNING (default 0.35).
    theta_crisis : float
        Drift threshold for CRISIS (default 0.60).
    """

    def __init__(
        self,
        *,
        home_vector: Optional[Dict[str, float]] = None,
        ema_alpha: float = 0.3,
        theta_warning: float = 0.35,
        theta_crisis: float = 0.60,
    ) -> None:
        self.home = dict(home_vector or _DEFAULT_HOME)
        self.ema_alpha = max(0.01, min(1.0, ema_alpha))
        self.theta_warning = theta_warning
        self.theta_crisis = theta_crisis

        self._center: Optional[Dict[str, float]] = None
        self._step: int = 0
        self._history: List[DriftSnapshot] = []
        self._last_recommendation: Optional[DriftActionRecommendation] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def observe(
        self,
        observation: Dict[str, float],
    ) -> DriftSnapshot:
        """Feed a new persona-space observation and return drift snapshot.

        *observation* should contain at least ``deltaT``, ``deltaS``, ``deltaR``.
        """
        obs = {d: float(observation.get(d, 0.5)) for d in _DIMS}

        if self._center is None:
            self._center = dict(obs)
        else:
            alpha = self.ema_alpha
            self._center = {d: alpha * obs[d] + (1.0 - alpha) * self._center[d] for d in _DIMS}

        self._step += 1
        drift = self._cosine_drift(self._center, self.home)
        alert = self._classify(drift)

        snap = DriftSnapshot(
            center=dict(self._center),
            home=dict(self.home),
            drift=drift,
            alert=alert,
            step=self._step,
        )
        self._history.append(snap)
        self._last_recommendation = self._build_recommendation(snap)
        return snap

    @property
    def current_drift(self) -> float:
        if not self._history:
            return 0.0
        return self._history[-1].drift

    @property
    def current_alert(self) -> DriftAlert:
        if not self._history:
            return DriftAlert.NONE
        return self._history[-1].alert

    @property
    def step_count(self) -> int:
        return self._step

    @property
    def last_recommendation(self) -> Optional[DriftActionRecommendation]:
        return self._last_recommendation

    def summary(self) -> Dict[str, object]:
        """Compact summary for governance surfaces."""
        if not self._history:
            return {
                "drift": 0.0,
                "alert": DriftAlert.NONE.value,
                "steps": 0,
                "max_drift": 0.0,
                "home": dict(self.home),
            }
        drifts = [s.drift for s in self._history]
        return {
            "drift": round(self._history[-1].drift, 6),
            "alert": self._history[-1].alert.value,
            "steps": self._step,
            "max_drift": round(max(drifts), 6),
            "mean_drift": round(sum(drifts) / len(drifts), 6),
            "home": dict(self.home),
            "recommended_action": (
                self._last_recommendation.to_dict() if self._last_recommendation else None
            ),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _cosine_drift(center: Dict[str, float], home: Dict[str, float]) -> float:
        """Drift = 1 - cos(C_t, H) in 3-dim persona space."""
        dot = sum(center[d] * home[d] for d in _DIMS)
        mag_c = math.sqrt(sum(center[d] ** 2 for d in _DIMS))
        mag_h = math.sqrt(sum(home[d] ** 2 for d in _DIMS))
        if mag_c == 0.0 or mag_h == 0.0:
            return 1.0
        cosine = dot / (mag_c * mag_h)
        cosine = max(-1.0, min(1.0, cosine))
        return 1.0 - cosine

    def _classify(self, drift: float) -> DriftAlert:
        if drift >= self.theta_crisis:
            return DriftAlert.CRISIS
        if drift >= self.theta_warning:
            return DriftAlert.WARNING
        return DriftAlert.NONE

    def _build_recommendation(
        self,
        snapshot: DriftSnapshot,
    ) -> Optional[DriftActionRecommendation]:
        if snapshot.alert == DriftAlert.WARNING:
            return DriftActionRecommendation(
                alert=snapshot.alert,
                action="increase_caution",
                note=("Drift warning: continue with extra caution and keep the response bounded."),
                current_drift=snapshot.drift,
                step=snapshot.step,
                increase_caution=True,
            )
        if snapshot.alert == DriftAlert.CRISIS:
            return DriftActionRecommendation(
                alert=snapshot.alert,
                action="recommend_session_pause",
                note=(
                    "Drift crisis: recommend pausing the session or asking for a human "
                    "check-in before further expansion."
                ),
                current_drift=snapshot.drift,
                step=snapshot.step,
                increase_caution=True,
                session_pause_recommended=True,
                human_check_in_recommended=True,
            )
        return None
