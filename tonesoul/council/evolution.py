"""Council perspective evolution tracker (experimental).

Tracks how each perspective (Guardian / Analyst / Critic / Advocate / Axiomatic) votes
relative to the final verdict, and slowly adjusts weights to reward
reliable alignment without penalizing healthy dissent.

State is persisted to ``memory/council_evolution.json`` so that
weights survive across process restarts.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Persistence path (relative to project root)
_DEFAULT_STATE_PATH = Path("memory") / "council_evolution.json"


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

    DEFAULT_PERSPECTIVES = ("guardian", "analyst", "critic", "advocate", "axiomatic")
    MIN_WEIGHT = 0.5
    MAX_WEIGHT = 2.0
    SUPPRESSION_WEIGHT_THRESHOLD = 0.95
    SUPPRESSION_DISSENT_FLOOR = 2
    SUPPRESSION_ALIGNMENT_CEILING = 0.5

    def __init__(self, state_path: Path | str | None = None) -> None:
        self._state_path = Path(state_path) if state_path else _DEFAULT_STATE_PATH
        self._history: Dict[str, PerspectiveHistory] = {}
        self._weights: Dict[str, float] = {}
        for name in self.DEFAULT_PERSPECTIVES:
            self._history[name] = PerspectiveHistory(name=name)
            self._weights[name] = 1.0
        self._load_state()

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
        self._save_state()
        return dict(self._weights)

    def get_weights(self) -> Dict[str, float]:
        return dict(self._weights)

    def _build_suppression_observability(self) -> Dict[str, object]:
        suppressed: list[Dict[str, object]] = []
        for name, history in self._history.items():
            weight = float(self._weights.get(name, 1.0))
            dissent_rate = (
                round(history.dissent_count / history.total_votes, 3)
                if history.total_votes
                else 0.0
            )
            if (
                history.total_votes >= 3
                and history.dissent_count >= self.SUPPRESSION_DISSENT_FLOOR
                and history.alignment_rate <= self.SUPPRESSION_ALIGNMENT_CEILING
                and weight < self.SUPPRESSION_WEIGHT_THRESHOLD
            ):
                suppressed.append(
                    {
                        "perspective": name,
                        "weight": round(weight, 3),
                        "baseline_weight": 1.0,
                        "alignment_rate": round(history.alignment_rate, 3),
                        "dissent_rate": dissent_rate,
                        "avg_confidence": round(history.avg_confidence, 3),
                        "reason": "weight_below_baseline_with_repeated_dissent",
                    }
                )

        if suppressed:
            summary_text = (
                "Repeated dissenting perspectives now sit below baseline weight; "
                "treat agreement-heavy council outcomes as potentially conformity-biased."
            )
        else:
            summary_text = "No repeated dissenting perspective currently falls below the suppression threshold."
        return {
            "flag": bool(suppressed),
            "suppressed_perspectives": suppressed,
            "summary_text": summary_text,
        }

    def get_summary(self) -> Dict[str, object]:
        return {
            "weights": self.get_weights(),
            "history": {name: history.to_dict() for name, history in self._history.items()},
            "suppression_observability": self._build_suppression_observability(),
        }

    # ------------------------------------------------------------------ #
    #  Persistence
    # ------------------------------------------------------------------ #

    def _load_state(self) -> None:
        """Restore weights and vote counts from disk (if available)."""
        if not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
            saved_weights = raw.get("weights", {})
            saved_history = raw.get("history", {})
            for name, w in saved_weights.items():
                self._weights[name] = float(w)
            for name, h in saved_history.items():
                if name not in self._history:
                    self._history[name] = PerspectiveHistory(name=name)
                self._history[name].total_votes = int(h.get("total_votes", 0))
                self._history[name].aligned_with_final = int(h.get("aligned_with_final", 0))
                self._history[name].dissent_count = int(h.get("dissent_count", 0))
                self._history[name].avg_confidence = float(h.get("avg_confidence", 0.5))
            logger.debug("Council evolution state loaded from %s", self._state_path)
        except Exception as exc:
            logger.warning("Failed to load council evolution state: %s", exc)

    def _save_state(self) -> None:
        """Persist current weights and vote counts to disk."""
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            payload = self.get_summary()
            self._state_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.debug("Council evolution state saved to %s", self._state_path)
        except Exception as exc:
            logger.warning("Failed to save council evolution state: %s", exc)
