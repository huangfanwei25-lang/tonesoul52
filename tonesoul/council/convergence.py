"""Convergence verification for council deliberation.

When perspectives have wildly different confidence values, the council
has reached a verdict but not actually converged on shared understanding.
This module measures that gap and recommends whether to continue deliberating.

Convergence ≠ consensus.
  Consensus: everyone voted the same way.
  Convergence: everyone's uncertainty about the decision has settled.
  A unanimous APPROVE with one perspective at 0.55 and another at 0.95
  is not converged — the high-confidence perspective may be overriding
  unresolved doubt rather than resolving it.

The convergence score is 1 - normalized_variance across vote confidences.
A score ≥ CONVERGENCE_THRESHOLD means the council's uncertainty has settled
enough that another deliberation round would not change the outcome.

Design rule: this module is advisory only. It never retries or mutates
council state. The calling code decides whether to act on the recommendation.
Maximum deliberation rounds must be enforced by the caller to avoid loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

from .types import PerspectiveType, PerspectiveVote, VoteDecision

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Convergence checker: measure whether council perspectives have settled "
    "into stable agreement and recommend additional deliberation if not."
)

CONVERGENCE_THRESHOLD: float = 0.75  # score above this → converged
HIGH_VARIANCE_THRESHOLD: float = 0.04  # variance above this → unstable
MAX_RECOMMENDED_ROUNDS: int = 2  # never recommend more than this


@dataclass
class ConvergenceResult:
    """Result of a convergence check across a set of perspective votes."""

    converged: bool
    score: float  # 0.0 (chaos) → 1.0 (fully settled)
    variance: float  # variance of confidence values
    mean_confidence: float
    recommendation: str  # plain-language note for logging
    suggested_focus: List[str] = field(default_factory=list)  # perspectives to re-engage
    additional_rounds_recommended: int = 0

    def to_dict(self):
        return {
            "converged": self.converged,
            "score": round(self.score, 4),
            "variance": round(self.variance, 4),
            "mean_confidence": round(self.mean_confidence, 4),
            "recommendation": self.recommendation,
            "suggested_focus": self.suggested_focus,
            "additional_rounds_recommended": self.additional_rounds_recommended,
        }


# ── Internal helpers ──────────────────────────────────────────────────────────


def _perspective_label(value: Union[PerspectiveType, str]) -> str:
    if isinstance(value, PerspectiveType):
        return value.value
    return str(value)


def _compute_variance(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _outlier_perspectives(
    votes: List[PerspectiveVote],
    mean: float,
    *,
    threshold: float = 0.2,
) -> List[str]:
    """Return perspectives whose confidence deviates significantly from the mean."""
    outliers = []
    for vote in votes:
        if abs(vote.confidence - mean) > threshold:
            outliers.append(_perspective_label(vote.perspective))
    return outliers


# ── Public API ────────────────────────────────────────────────────────────────


def convergence_score(votes: List[PerspectiveVote]) -> float:
    """Compute convergence score (0.0 → 1.0) from a list of perspective votes.

    High score = perspectives have settled; confidence values are tightly clustered.
    Low score = wide spread; the council is uncertain even if it has a majority.
    """
    if not votes:
        return 1.0  # vacuously converged
    if len(votes) == 1:
        return votes[0].confidence

    confidences = [v.confidence for v in votes]
    var = _compute_variance(confidences)
    # Normalize: max theoretical variance for [0,1] values is 0.25
    normalized_variance = min(1.0, var / 0.25)
    return round(1.0 - normalized_variance, 4)


def check_convergence(
    votes: List[PerspectiveVote],
    *,
    threshold: float = CONVERGENCE_THRESHOLD,
) -> ConvergenceResult:
    """Evaluate whether this set of votes represents a converged deliberation.

    Returns a ConvergenceResult with:
      - whether the council has converged
      - which perspectives are outliers (if any)
      - how many additional rounds might help (0, 1, or 2)
    """
    if not votes:
        return ConvergenceResult(
            converged=True,
            score=1.0,
            variance=0.0,
            mean_confidence=0.0,
            recommendation="No votes — vacuously converged.",
        )

    confidences = [v.confidence for v in votes]
    mean = sum(confidences) / len(confidences)
    variance = _compute_variance(confidences)
    score = convergence_score(votes)
    converged = score >= threshold

    # Objecting perspectives always prevent convergence
    objectors = [
        _perspective_label(v.perspective) for v in votes if v.decision == VoteDecision.OBJECT
    ]
    if objectors:
        converged = False

    outliers = _outlier_perspectives(votes, mean)
    focus = objectors if objectors else outliers

    if converged:
        recommendation = (
            f"Converged (score={score:.3f}). "
            f"Mean confidence {mean:.2f}, variance {variance:.4f}."
        )
        rounds = 0
    elif variance > HIGH_VARIANCE_THRESHOLD * 4:
        recommendation = (
            f"High divergence (score={score:.3f}, variance={variance:.4f}). "
            f"Perspectives disagree significantly — consider re-examining framing."
        )
        rounds = min(MAX_RECOMMENDED_ROUNDS, 2)
    else:
        recommendation = (
            f"Partial convergence (score={score:.3f}). "
            f"Additional deliberation may stabilize confidence."
        )
        rounds = 1

    return ConvergenceResult(
        converged=converged,
        score=score,
        variance=variance,
        mean_confidence=round(mean, 4),
        recommendation=recommendation,
        suggested_focus=focus,
        additional_rounds_recommended=rounds,
    )


def should_continue_deliberating(
    result: ConvergenceResult,
    current_round: int,
    *,
    max_rounds: int = MAX_RECOMMENDED_ROUNDS,
) -> bool:
    """Return True if another deliberation round is warranted.

    Always returns False once max_rounds is reached, preventing infinite loops.
    This is the hard stop that callers must respect.
    """
    if current_round >= max_rounds:
        return False
    return not result.converged and result.additional_rounds_recommended > 0
