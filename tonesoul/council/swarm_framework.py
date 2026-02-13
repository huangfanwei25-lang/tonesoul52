"""Persona Swarm Framework.

Experimental multi-persona framework that complements the existing
tri-persona council mode with a swarm-style aggregation layer.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

SWARM_DECISIONS = frozenset({"approve", "block", "revise", "defer"})


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalize_swarm_decision(decision: str, *, field_name: str = "decision") -> str:
    value = str(decision).strip().lower()
    if not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    if value not in SWARM_DECISIONS:
        allowed = ", ".join(sorted(SWARM_DECISIONS))
        raise ValueError(f"{field_name} must be one of: {allowed}")
    return value


@dataclass(frozen=True)
class SwarmAgentSignal:
    """Single persona/agent signal used by the swarm evaluator."""

    agent_id: str
    role: str
    vote: str
    confidence: float
    safety_score: float
    quality_score: float
    novelty_score: float
    latency_ms: float
    token_cost: float

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SwarmAgentSignal":
        if not isinstance(payload, dict):
            raise TypeError("signal payload must be an object")

        def _get_text(key: str) -> str:
            value = payload.get(key, "")
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"signal.{key} must be a non-empty string")
            return value.strip()

        return cls(
            agent_id=_get_text("agent_id"),
            role=_get_text("role").lower(),
            vote=normalize_swarm_decision(_get_text("vote"), field_name="signal.vote"),
            confidence=_clamp01(payload.get("confidence", 0.5)),
            safety_score=_clamp01(payload.get("safety_score", 0.5)),
            quality_score=_clamp01(payload.get("quality_score", 0.5)),
            novelty_score=_clamp01(payload.get("novelty_score", 0.5)),
            latency_ms=max(0.0, float(payload.get("latency_ms", 0.0))),
            token_cost=max(0.0, float(payload.get("token_cost", 0.0))),
        )


@dataclass(frozen=True)
class SwarmFrameworkConfig:
    min_safety_gate: float = 0.70
    quality_weight: float = 0.40
    safety_weight: float = 0.30
    consistency_weight: float = 0.20
    cost_weight: float = 0.10
    baseline_latency_ms: float = 3000.0
    baseline_token_cost: float = 2000.0
    guardian_fail_fast_enabled: bool = True
    guardian_fail_fast_min_confidence: float = 0.75
    guardian_fail_fast_min_safety: float = 0.75
    allow_final_decision_override_on_fail_fast: bool = False


@dataclass(frozen=True)
class SwarmFrameworkResult:
    decision: str
    decision_support: float
    metrics: Dict[str, float]
    role_distribution: Dict[str, int]
    governance: Dict[str, Any]
    persona_positioning: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "decision_support": round(self.decision_support, 4),
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "role_distribution": dict(self.role_distribution),
            "governance": dict(self.governance),
            "persona_positioning": dict(self.persona_positioning),
        }


class PersonaSwarmFramework:
    """Swarm evaluator with positioning output."""

    def __init__(self, config: SwarmFrameworkConfig | None = None) -> None:
        self.config = config or SwarmFrameworkConfig()

    @staticmethod
    def _role_distribution(signals: Sequence[SwarmAgentSignal]) -> Dict[str, int]:
        counter = Counter(signal.role for signal in signals)
        return dict(counter)

    @staticmethod
    def _weighted_vote_scores(signals: Sequence[SwarmAgentSignal]) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for signal in signals:
            reliability_weight = 0.5 + 0.5 * signal.safety_score
            vote_weight = max(0.05, signal.confidence) * reliability_weight
            scores[signal.vote] = scores.get(signal.vote, 0.0) + vote_weight
        return scores

    @staticmethod
    def _normalized_entropy(counter: Dict[str, int]) -> float:
        total = sum(counter.values())
        if total <= 1:
            return 0.0
        probabilities = [count / total for count in counter.values() if count > 0]
        if len(probabilities) <= 1:
            return 0.0
        entropy = -sum(p * math.log(p) for p in probabilities)
        return _clamp01(entropy / math.log(len(probabilities)))

    def _cost_index(self, signals: Sequence[SwarmAgentSignal]) -> float:
        if not signals:
            return 1.0
        avg_latency = sum(signal.latency_ms for signal in signals) / len(signals)
        avg_token_cost = sum(signal.token_cost for signal in signals) / len(signals)
        latency_norm = min(1.0, avg_latency / max(1.0, self.config.baseline_latency_ms))
        token_norm = min(1.0, avg_token_cost / max(1.0, self.config.baseline_token_cost))
        return _clamp01(0.6 * latency_norm + 0.4 * token_norm)

    @staticmethod
    def _mean(values: Iterable[float]) -> float:
        bucket = list(values)
        if not bucket:
            return 0.0
        return sum(bucket) / len(bucket)

    def _disagreement_utility(
        self,
        signals: Sequence[SwarmAgentSignal],
        final_decision: str,
    ) -> float:
        dissenters = [signal for signal in signals if signal.vote != final_decision]
        supporters = [signal for signal in signals if signal.vote == final_decision]
        if not dissenters or not supporters:
            return 0.0

        supporter_baseline = self._mean(
            ((signal.quality_score + signal.safety_score) / 2.0) for signal in supporters
        )
        improved = [
            signal
            for signal in dissenters
            if ((signal.quality_score + signal.safety_score) / 2.0) > supporter_baseline
        ]
        return _clamp01(len(improved) / len(dissenters))

    @staticmethod
    def _support_ratio(vote_scores: Dict[str, float], decision: str) -> float:
        total = sum(vote_scores.values())
        if total <= 0:
            return 0.0
        return _clamp01(vote_scores.get(decision, 0.0) / total)

    @staticmethod
    def _is_guardian_role(role: str) -> bool:
        value = str(role).strip().lower()
        return value == "guardian" or value.startswith("guardian:")

    def _guardian_fail_fast(self, signals: Sequence[SwarmAgentSignal]) -> tuple[bool, list[str]]:
        if not self.config.guardian_fail_fast_enabled:
            return False, []

        blocking_guardians = [
            signal.agent_id
            for signal in signals
            if self._is_guardian_role(signal.role)
            and signal.vote == "block"
            and signal.confidence >= self.config.guardian_fail_fast_min_confidence
            and signal.safety_score >= self.config.guardian_fail_fast_min_safety
        ]
        return bool(blocking_guardians), blocking_guardians

    def _persona_positioning(
        self, metrics: Dict[str, float], decision_support: float
    ) -> Dict[str, Any]:
        safety = metrics["safety_pass_rate"]
        quality = metrics["task_quality"]
        consistency = metrics["consistency_at_session"]
        diversity = metrics["diversity_index"]
        disagreement = metrics["disagreement_utility"]

        if safety < 0.65:
            return {
                "archetype": "sentinel_recovery",
                "suggested_identity": "guardian-first stabilizer",
                "confidence_band": "high" if decision_support >= 0.75 else "medium",
                "statement": (
                    "Swarm identity should prioritize containment and reliability before exploration."
                ),
            }
        if disagreement >= 0.55 and diversity >= 0.45:
            return {
                "archetype": "critical_discovery",
                "suggested_identity": "explorer-critic collective",
                "confidence_band": "high" if decision_support >= 0.75 else "medium",
                "statement": (
                    "Swarm identity is a constructive challenger: preserve dissent to unlock better plans."
                ),
            }
        if quality >= 0.75 and consistency >= 0.75 and safety >= 0.80:
            return {
                "archetype": "reliable_executor",
                "suggested_identity": "trusted integrator",
                "confidence_band": "high" if decision_support >= 0.75 else "medium",
                "statement": "Swarm identity is execution-focused with high trust and low volatility.",
            }
        return {
            "archetype": "adaptive_integrator",
            "suggested_identity": "balanced orchestration layer",
            "confidence_band": "high" if decision_support >= 0.75 else "medium",
            "statement": "Swarm identity is adaptive: trade off creativity, safety, and speed per context.",
        }

    def evaluate(
        self,
        signals: Sequence[SwarmAgentSignal],
        *,
        final_decision: str | None = None,
    ) -> SwarmFrameworkResult:
        if not signals:
            raise ValueError("signals must not be empty")

        vote_scores = self._weighted_vote_scores(signals)
        if not vote_scores:
            raise ValueError("unable to compute vote scores")

        requested_decision = (
            normalize_swarm_decision(final_decision, field_name="final_decision")
            if isinstance(final_decision, str)
            else ""
        )
        guardian_fail_fast_triggered, guardian_blocking_agent_ids = self._guardian_fail_fast(
            signals
        )

        decision = requested_decision
        if guardian_fail_fast_triggered and (
            not requested_decision or not self.config.allow_final_decision_override_on_fail_fast
        ):
            decision = "block"

        if not decision:
            decision = max(vote_scores.items(), key=lambda item: (item[1], item[0]))[0]

        role_distribution = self._role_distribution(signals)
        decision_support = self._support_ratio(vote_scores, decision)

        task_quality = _clamp01(self._mean(signal.quality_score for signal in signals))
        safety_pass_rate = _clamp01(
            self._mean(
                float(signal.safety_score >= self.config.min_safety_gate) for signal in signals
            )
        )
        consistency_at_session = _clamp01(decision_support)
        disagreement_utility = self._disagreement_utility(signals, decision)
        diversity_index = self._normalized_entropy(role_distribution)
        cost_index = self._cost_index(signals)

        swarm_score = _clamp01(
            self.config.quality_weight * task_quality
            + self.config.safety_weight * safety_pass_rate
            + self.config.consistency_weight * consistency_at_session
            + self.config.cost_weight * (1.0 - cost_index)
        )

        metrics = {
            "task_quality": task_quality,
            "safety_pass_rate": safety_pass_rate,
            "consistency_at_session": consistency_at_session,
            "disagreement_utility": disagreement_utility,
            "diversity_index": diversity_index,
            "token_latency_cost_index": cost_index,
            "swarm_score": swarm_score,
            "guardian_fail_fast_triggered": 1.0 if guardian_fail_fast_triggered else 0.0,
        }
        positioning = self._persona_positioning(metrics, decision_support)
        governance = {
            "guardian_fail_fast_triggered": guardian_fail_fast_triggered,
            "guardian_blocking_agent_ids": guardian_blocking_agent_ids,
            "requested_decision": requested_decision or None,
            "final_decision_overridden": bool(
                guardian_fail_fast_triggered
                and requested_decision
                and requested_decision != decision
                and not self.config.allow_final_decision_override_on_fail_fast
            ),
        }

        return SwarmFrameworkResult(
            decision=decision,
            decision_support=decision_support,
            metrics=metrics,
            role_distribution=role_distribution,
            governance=governance,
            persona_positioning=positioning,
        )
