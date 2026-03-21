"""Drift Tracker — Home Vector distance monitoring.

Computes Drift(C_t, H) where C_t is the current operational state and
H is the fixed Home Vector.  When drift exceeds a configurable threshold
the system signals a governance concern.

The 3-dimensional state space (deltaT, deltaS, deltaR) follows the
existing ``DEFAULT_HOME_VECTOR`` convention in ``unified_core.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DriftResult:
    """Result of a drift computation."""

    drift: float = 0.0  # Euclidean distance from H
    per_axis: Optional[Dict[str, float]] = None
    exceeded: bool = False
    threshold: float = 1.0

    def __post_init__(self) -> None:
        if self.per_axis is None:
            self.per_axis = {}


_DEFAULT_HOME = {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}
_DEFAULT_THRESHOLD = 1.0


class DriftTracker:
    """Tracks drift of operational state from a fixed Home Vector H.

    Parameters
    ----------
    home : dict
        Fixed home vector {deltaT, deltaS, deltaR}.
    threshold : float
        Euclidean distance above which drift is considered critical.
    """

    def __init__(
        self,
        home: Optional[Dict[str, float]] = None,
        threshold: float = _DEFAULT_THRESHOLD,
    ) -> None:
        self._home = dict(home or _DEFAULT_HOME)
        self._threshold = max(0.0, float(threshold))
        self._last_result: Optional[DriftResult] = None

    @property
    def home(self) -> Dict[str, float]:
        return dict(self._home)

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def last_result(self) -> Optional[DriftResult]:
        return self._last_result

    def compute(
        self,
        deltaT: float = 0.5,
        deltaS: float = 0.5,
        deltaR: float = 0.5,
    ) -> DriftResult:
        """Compute Euclidean drift from the Home Vector.

        Returns a DriftResult with per-axis deltas and total drift.
        """
        diffs = {
            "deltaT": abs(float(deltaT) - float(self._home.get("deltaT", 0.5))),
            "deltaS": abs(float(deltaS) - float(self._home.get("deltaS", 0.5))),
            "deltaR": abs(float(deltaR) - float(self._home.get("deltaR", 0.5))),
        }
        total = sum(v**2 for v in diffs.values()) ** 0.5
        result = DriftResult(
            drift=round(total, 6),
            per_axis={k: round(v, 6) for k, v in diffs.items()},
            exceeded=total >= self._threshold,
            threshold=self._threshold,
        )
        self._last_result = result
        return result

    def drift_max_for_dcs(
        self,
        deltaT: float = 0.5,
        deltaS: float = 0.5,
        deltaR: float = 0.5,
    ) -> float:
        """Compute drift and return a value suitable for DCS ``drift_max``.

        This rescales the Euclidean distance into the DCS threshold
        domain (default DCS threshold = 4.0, max 3-axis Euclidean = √3 ≈ 1.73).
        """
        result = self.compute(deltaT, deltaS, deltaR)
        # Scale: max possible Euclidean distance is √3 ≈ 1.732
        # DCS default threshold is 4.0
        # Linear map: DCS_drift = (euclidean / √3) × 4.0
        max_euclidean = 3**0.5
        return round((result.drift / max_euclidean) * 4.0, 6) if max_euclidean > 0 else 0.0

    def to_dict(self) -> Dict[str, object]:
        """Serialise for observability."""
        return {
            "home": dict(self._home),
            "threshold": self._threshold,
            "last_drift": self._last_result.drift if self._last_result else None,
            "last_exceeded": self._last_result.exceeded if self._last_result else None,
        }
