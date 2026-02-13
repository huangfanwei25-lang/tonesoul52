"""Council perspective evolution tracker (experimental)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PerspectiveHistory:
    """Track historical performance for a single perspective."""

    name: str
    total_votes: int = 0
    aligned_with_final: int = 0
    dissent_count: int = 0
    avg_confidence: float = 0.5

    @property
    def alignment_rate(self) -> float:
        if self.total_votes == 0:
            return 0.5
        return self.aligned_with_final / self.total_votes

    def record_vote(self, matched_final: bool, confidence: float = 0.5) -> None:
        self.total_votes += 1
        if matched_final:
            self.aligned_with_final += 1
        else:
            self.dissent_count += 1
        confidence_value = max(0.0, min(1.0, float(confidence)))
        self.avg_confidence = (
            self.avg_confidence * (self.total_votes - 1) + confidence_value
        ) / self.total_votes

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "total_votes": self.total_votes,
            "aligned_with_final": self.aligned_with_final,
            "dissent_count": self.dissent_count,
            "alignment_rate": round(self.alignment_rate, 3),
            "avg_confidence": round(self.avg_confidence, 3),
        }


class CouncilEvolution:
    """Track perspective vote histories and derive soft weight suggestions."""

    DEFAULT_PERSPECTIVES = ("philosopher", "engineer", "guardian")
    MIN_WEIGHT = 0.5
    MAX_WEIGHT = 2.0

    def __init__(self) -> None:
        self._history: Dict[str, PerspectiveHistory] = {}
        self._weights: Dict[str, float] = {}
        for name in self.DEFAULT_PERSPECTIVES:
            self._history[name] = PerspectiveHistory(name=name)
            self._weights[name] = 1.0

    def record_deliberation(
        self,
        perspective_verdicts: Dict[str, str],
        final_verdict: str,
        perspective_confidences: Optional[Dict[str, float]] = None,
    ) -> None:
        confidences = perspective_confidences or {}
        final_norm = str(final_verdict).strip().lower()

        for perspective_name, verdict in perspective_verdicts.items():
            name = str(perspective_name).strip().lower()
            if not name:
                continue
            if name not in self._history:
                self._history[name] = PerspectiveHistory(name=name)
            if name not in self._weights:
                self._weights[name] = 1.0

            verdict_norm = str(verdict).strip().lower()
            matched_final = bool(verdict_norm and verdict_norm == final_norm)
            confidence = confidences.get(perspective_name, confidences.get(name, 0.5))
            self._history[name].record_vote(
                matched_final=matched_final, confidence=float(confidence)
            )

    def evolve_weights(self) -> Dict[str, float]:
        """Reward reliable alignment slightly without penalizing dissent."""
        for name, history in self._history.items():
            if history.total_votes < 3:
                continue
            if history.alignment_rate > 0.6:
                self._weights[name] = min(self.MAX_WEIGHT, self._weights.get(name, 1.0) + 0.05)

        total = sum(self._weights.values())
        count = len(self._weights)
        if total > 0 and count > 0:
            factor = count / total
            normalized: Dict[str, float] = {}
            for name, weight in self._weights.items():
                adjusted = weight * factor
                normalized[name] = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, adjusted))
            self._weights = normalized
        return dict(self._weights)

    def get_weights(self) -> Dict[str, float]:
        return dict(self._weights)

    def get_summary(self) -> Dict[str, object]:
        return {
            "weights": self.get_weights(),
            "history": {name: history.to_dict() for name, history in self._history.items()},
        }
