"""
VowInventory — Commitment Conviction Tracker
語魂誓言信念追蹤器

Maintains a running ledger of how well each active vow has been honored
across interactions. Analogous to a position conviction ledger in equity
research: every check against a vow updates its conviction score and
trajectory, so the system can ask "which commitments am I drifting from?"

Financial parallel:
  Vow           ← investment thesis
  conviction_score ← running Sharpe ratio of the thesis
  trajectory    ← analyst's view update (strengthen / stable / decaying)
  needs_attention ← thesis under review flag
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# How many recent checks define the "recent window" for trajectory
RECENT_WINDOW = 10

# Violation penalty multiplier — breaking a vow costs more than keeping it earns
VIOLATION_PENALTY = 2.0

# Trajectory thresholds (fraction of recent passes)
TRAJECTORY_STRONG = 0.85
TRAJECTORY_STABLE = 0.65

# Minimum checks to classify trajectory
MIN_CHECKS_FOR_TRAJECTORY = 3


TrajectoryType = Literal["strengthening", "stable", "decaying", "untested"]


@dataclass
class VowCheckRecord:
    """A single test of a vow at a specific point in time."""

    vow_id: str
    passed: bool
    score: float
    threshold: float
    context_label: Optional[str] = None
    checked_at: str = field(default_factory=_utc_iso)
    violation_reason: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "vow_id": self.vow_id,
            "passed": self.passed,
            "score": self.score,
            "threshold": self.threshold,
            "context_label": self.context_label,
            "checked_at": self.checked_at,
            "violation_reason": self.violation_reason,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "VowCheckRecord":
        return cls(
            vow_id=d["vow_id"],
            passed=d["passed"],
            score=d["score"],
            threshold=d["threshold"],
            context_label=d.get("context_label"),
            checked_at=d.get("checked_at", _utc_iso()),
            violation_reason=d.get("violation_reason"),
        )


@dataclass
class VowConvictionState:
    """
    The running conviction state for a single vow.

    conviction_score formula (analogous to a risk-adjusted return):
      raw = passes - (violations * VIOLATION_PENALTY)
      conviction_score = max(0.0, min(1.0, raw / max(1, total_tests)))

    Trajectory is computed over the recent window only, so short-term drift
    is detectable even if the long-term record is strong.
    """

    vow_id: str
    vow_title: str
    first_committed_at: str
    last_tested_at: Optional[str]
    total_tests: int
    passes: int
    violations: int
    uncertain: int  # tests where score was within 10% of threshold
    conviction_score: float
    trajectory: TrajectoryType
    needs_attention: bool
    last_violation_reason: Optional[str]
    # recent check history (capped at RECENT_WINDOW * 3 for audit trail)
    recent_checks: List[VowCheckRecord] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "vow_id": self.vow_id,
            "vow_title": self.vow_title,
            "first_committed_at": self.first_committed_at,
            "last_tested_at": self.last_tested_at,
            "total_tests": self.total_tests,
            "passes": self.passes,
            "violations": self.violations,
            "uncertain": self.uncertain,
            "conviction_score": round(self.conviction_score, 4),
            "trajectory": self.trajectory,
            "needs_attention": self.needs_attention,
            "last_violation_reason": self.last_violation_reason,
            "recent_checks": [r.to_dict() for r in self.recent_checks],
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "VowConvictionState":
        return cls(
            vow_id=d["vow_id"],
            vow_title=d.get("vow_title", ""),
            first_committed_at=d["first_committed_at"],
            last_tested_at=d.get("last_tested_at"),
            total_tests=d.get("total_tests", 0),
            passes=d.get("passes", 0),
            violations=d.get("violations", 0),
            uncertain=d.get("uncertain", 0),
            conviction_score=d.get("conviction_score", 0.0),
            trajectory=d.get("trajectory", "untested"),
            needs_attention=d.get("needs_attention", False),
            last_violation_reason=d.get("last_violation_reason"),
            recent_checks=[VowCheckRecord.from_dict(r) for r in d.get("recent_checks", [])],
        )


def _compute_conviction(passes: int, violations: int, total_tests: int) -> float:
    if total_tests == 0:
        return 0.0
    raw = passes - (violations * VIOLATION_PENALTY)
    return max(0.0, min(1.0, raw / total_tests))


def _compute_trajectory(
    recent_checks: List[VowCheckRecord],
    total_tests: int,
) -> TrajectoryType:
    if total_tests < MIN_CHECKS_FOR_TRAJECTORY:
        return "untested"
    window = recent_checks[-RECENT_WINDOW:]
    if not window:
        return "untested"
    pass_rate = sum(1 for r in window if r.passed) / len(window)
    if pass_rate >= TRAJECTORY_STRONG:
        return "strengthening"
    elif pass_rate >= TRAJECTORY_STABLE:
        return "stable"
    else:
        return "decaying"


class VowInventory:
    """
    Running ledger of vow conviction states across all interactions.

    Usage:
        inventory = VowInventory()
        inventory.record_check("ΣVow_001", passed=True, score=0.97, threshold=0.95)
        state = inventory.get_state("ΣVow_001")
        print(state.trajectory)  # "untested" until MIN_CHECKS_FOR_TRAJECTORY checks
    """

    def __init__(self) -> None:
        self._states: Dict[str, VowConvictionState] = {}

    # ── Public API ──────────────────────────────────────────────────────────

    def record_check(
        self,
        vow_id: str,
        passed: bool,
        score: float,
        threshold: float,
        vow_title: str = "",
        context_label: Optional[str] = None,
        violation_reason: Optional[str] = None,
    ) -> VowConvictionState:
        """Record the result of a single vow check and return updated state."""
        now = _utc_iso()
        check = VowCheckRecord(
            vow_id=vow_id,
            passed=passed,
            score=score,
            threshold=threshold,
            context_label=context_label,
            checked_at=now,
            violation_reason=violation_reason if not passed else None,
        )

        if vow_id not in self._states:
            self._states[vow_id] = VowConvictionState(
                vow_id=vow_id,
                vow_title=vow_title,
                first_committed_at=now,
                last_tested_at=None,
                total_tests=0,
                passes=0,
                violations=0,
                uncertain=0,
                conviction_score=0.0,
                trajectory="untested",
                needs_attention=False,
                last_violation_reason=None,
                recent_checks=[],
            )

        state = self._states[vow_id]

        # Update title if provided (registry may supply it lazily)
        if vow_title and not state.vow_title:
            state.vow_title = vow_title

        # Record the check
        state.recent_checks.append(check)
        # Cap audit trail at 3× recent window to bound memory
        max_history = RECENT_WINDOW * 3
        if len(state.recent_checks) > max_history:
            state.recent_checks = state.recent_checks[-max_history:]

        # Update counters
        state.total_tests += 1
        state.last_tested_at = now
        if passed:
            state.passes += 1
        else:
            state.violations += 1
            state.last_violation_reason = violation_reason

        # Detect near-threshold "uncertain" checks (within 10% of threshold)
        margin = abs(score - threshold)
        if margin / max(threshold, 1e-9) < 0.10:
            state.uncertain += 1

        # Recompute derived metrics
        state.conviction_score = _compute_conviction(
            state.passes, state.violations, state.total_tests
        )
        state.trajectory = _compute_trajectory(state.recent_checks, state.total_tests)
        state.needs_attention = self._should_flag(state)

        return state

    def get_state(self, vow_id: str) -> Optional[VowConvictionState]:
        return self._states.get(vow_id)

    def all_states(self) -> List[VowConvictionState]:
        return list(self._states.values())

    def attention_needed(self) -> List[VowConvictionState]:
        """Return vows that need human/system review."""
        return [s for s in self._states.values() if s.needs_attention]

    def conviction_summary(self) -> Dict:
        """Compact summary suitable for governance brief fields."""
        states = self.all_states()
        if not states:
            return {"total_vows": 0, "mean_conviction": 0.0, "attention_needed": 0}
        mean_conviction = sum(s.conviction_score for s in states) / len(states)
        return {
            "total_vows": len(states),
            "mean_conviction": round(mean_conviction, 4),
            "strengthening": sum(1 for s in states if s.trajectory == "strengthening"),
            "stable": sum(1 for s in states if s.trajectory == "stable"),
            "decaying": sum(1 for s in states if s.trajectory == "decaying"),
            "untested": sum(1 for s in states if s.trajectory == "untested"),
            "attention_needed": sum(1 for s in states if s.needs_attention),
        }

    def to_artifact(self) -> Dict:
        """Full artifact for docs/status/ emission."""
        return {
            "generated_at": _utc_iso(),
            "summary": self.conviction_summary(),
            "states": [s.to_dict() for s in self.all_states()],
        }

    # ── Persistence ─────────────────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_artifact(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "VowInventory":
        inventory = cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for state_dict in data.get("states", []):
            state = VowConvictionState.from_dict(state_dict)
            inventory._states[state.vow_id] = state
        return inventory

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _should_flag(state: VowConvictionState) -> bool:
        """A vow needs attention when conviction is low or trajectory is decaying."""
        if state.trajectory == "decaying":
            return True
        if state.conviction_score < 0.5 and state.total_tests >= MIN_CHECKS_FOR_TRAJECTORY:
            return True
        return False
