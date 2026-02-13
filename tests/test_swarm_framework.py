from __future__ import annotations

import pytest

from tonesoul.council.swarm_framework import (
    PersonaSwarmFramework,
    SwarmAgentSignal,
    SwarmFrameworkConfig,
)


def _signal(
    *,
    agent_id: str,
    role: str,
    vote: str,
    confidence: float = 0.8,
    safety_score: float = 0.8,
    quality_score: float = 0.8,
    novelty_score: float = 0.5,
    latency_ms: float = 800.0,
    token_cost: float = 300.0,
) -> SwarmAgentSignal:
    return SwarmAgentSignal(
        agent_id=agent_id,
        role=role,
        vote=vote,
        confidence=confidence,
        safety_score=safety_score,
        quality_score=quality_score,
        novelty_score=novelty_score,
        latency_ms=latency_ms,
        token_cost=token_cost,
    )


def _metrics(
    *,
    task_quality: float,
    safety_pass_rate: float,
    consistency_at_session: float,
    disagreement_utility: float,
    diversity_index: float,
    token_latency_cost_index: float = 0.3,
    swarm_score: float = 0.7,
) -> dict[str, float]:
    return {
        "task_quality": task_quality,
        "safety_pass_rate": safety_pass_rate,
        "consistency_at_session": consistency_at_session,
        "disagreement_utility": disagreement_utility,
        "diversity_index": diversity_index,
        "token_latency_cost_index": token_latency_cost_index,
        "swarm_score": swarm_score,
    }


def test_swarm_agent_signal_from_dict_rejects_invalid_payload() -> None:
    with pytest.raises(TypeError):
        SwarmAgentSignal.from_dict("bad-payload")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        SwarmAgentSignal.from_dict(
            {
                "agent_id": "",
                "role": "guardian",
                "vote": "approve",
            }
        )


def test_swarm_agent_signal_from_dict_clamps_numeric_values() -> None:
    signal = SwarmAgentSignal.from_dict(
        {
            "agent_id": "a1",
            "role": "guardian",
            "vote": "approve",
            "confidence": 4.0,
            "safety_score": -3.0,
            "quality_score": 1.6,
            "novelty_score": -1.0,
            "latency_ms": -99,
            "token_cost": -50,
        }
    )
    assert signal.confidence == 1.0
    assert signal.safety_score == 0.0
    assert signal.quality_score == 1.0
    assert signal.novelty_score == 0.0
    assert signal.latency_ms == 0.0
    assert signal.token_cost == 0.0


def test_swarm_agent_signal_from_dict_rejects_unsupported_vote() -> None:
    with pytest.raises(ValueError, match="signal.vote must be one of"):
        SwarmAgentSignal.from_dict(
            {
                "agent_id": "a1",
                "role": "guardian",
                "vote": "maybe",
            }
        )


def test_normalized_entropy_single_role_is_zero_and_uniform_is_high() -> None:
    framework = PersonaSwarmFramework()
    assert framework._normalized_entropy({"guardian": 5}) == 0.0

    entropy_uniform = framework._normalized_entropy(
        {
            "guardian": 1,
            "engineer": 1,
            "philosopher": 1,
        }
    )
    assert 0.99 <= entropy_uniform <= 1.0


def test_cost_index_handles_empty_and_saturated_inputs() -> None:
    framework = PersonaSwarmFramework()
    assert framework._cost_index([]) == 1.0

    saturated = framework._cost_index(
        [
            _signal(
                agent_id="a1",
                role="guardian",
                vote="approve",
                latency_ms=10_000,
                token_cost=10_000,
            )
        ]
    )
    assert saturated == 1.0

    moderate = framework._cost_index(
        [
            _signal(
                agent_id="a2",
                role="engineer",
                vote="approve",
                latency_ms=1200,
                token_cost=600,
            ),
            _signal(
                agent_id="a3",
                role="philosopher",
                vote="approve",
                latency_ms=1800,
                token_cost=1000,
            ),
        ]
    )
    assert 0.0 < moderate < 1.0


def test_disagreement_utility_counts_only_stronger_dissenters() -> None:
    framework = PersonaSwarmFramework()
    signals = [
        _signal(
            agent_id="s1",
            role="guardian",
            vote="approve",
            quality_score=0.55,
            safety_score=0.60,
        ),
        _signal(
            agent_id="s2",
            role="engineer",
            vote="approve",
            quality_score=0.50,
            safety_score=0.60,
        ),
        _signal(
            agent_id="d1",
            role="critic",
            vote="block",
            quality_score=0.90,
            safety_score=0.90,
        ),
        _signal(
            agent_id="d2",
            role="analyst",
            vote="block",
            quality_score=0.45,
            safety_score=0.40,
        ),
    ]

    utility = framework._disagreement_utility(signals, "approve")
    assert utility == 0.5

    no_dissent = framework._disagreement_utility(signals[:2], "approve")
    assert no_dissent == 0.0


def test_evaluate_aggregates_metrics_and_role_distribution() -> None:
    framework = PersonaSwarmFramework()
    signals = [
        _signal(
            agent_id="a1",
            role="guardian",
            vote="approve",
            confidence=0.9,
            safety_score=0.95,
            quality_score=0.85,
            latency_ms=900,
            token_cost=350,
        ),
        _signal(
            agent_id="a2",
            role="engineer",
            vote="approve",
            confidence=0.8,
            safety_score=0.85,
            quality_score=0.88,
            latency_ms=1200,
            token_cost=500,
        ),
        _signal(
            agent_id="a3",
            role="philosopher",
            vote="block",
            confidence=0.6,
            safety_score=0.75,
            quality_score=0.82,
            latency_ms=1500,
            token_cost=650,
        ),
    ]

    result = framework.evaluate(signals)
    assert result.decision == "approve"
    assert result.decision_support > 0.5
    assert result.role_distribution == {"guardian": 1, "engineer": 1, "philosopher": 1}
    assert result.metrics["task_quality"] > 0.8
    assert result.metrics["safety_pass_rate"] == 1.0
    assert result.metrics["swarm_score"] > 0.0
    assert result.governance["guardian_fail_fast_triggered"] is False
    assert result.to_dict()["metrics"]["swarm_score"] == round(result.metrics["swarm_score"], 4)


def test_evaluate_respects_final_decision_override() -> None:
    framework = PersonaSwarmFramework()
    signals = [
        _signal(agent_id="a1", role="guardian", vote="approve"),
        _signal(agent_id="a2", role="engineer", vote="approve"),
        _signal(agent_id="a3", role="philosopher", vote="block"),
    ]

    result = framework.evaluate(signals, final_decision="block")
    assert result.decision == "block"
    assert 0.0 <= result.decision_support <= 1.0


def test_evaluate_rejects_unsupported_final_decision() -> None:
    framework = PersonaSwarmFramework()
    signals = [
        _signal(agent_id="a1", role="guardian", vote="approve"),
        _signal(agent_id="a2", role="engineer", vote="block"),
    ]
    with pytest.raises(ValueError, match="final_decision must be one of"):
        framework.evaluate(signals, final_decision="escalate")


def test_guardian_fail_fast_overrides_requested_decision() -> None:
    framework = PersonaSwarmFramework()
    signals = [
        _signal(
            agent_id="g1",
            role="guardian",
            vote="block",
            confidence=0.92,
            safety_score=0.91,
        ),
        _signal(agent_id="e1", role="engineer", vote="approve", confidence=0.95),
    ]
    result = framework.evaluate(signals, final_decision="approve")

    assert result.decision == "block"
    assert result.governance["guardian_fail_fast_triggered"] is True
    assert result.governance["final_decision_overridden"] is True
    assert result.governance["guardian_blocking_agent_ids"] == ["g1"]
    assert result.metrics["guardian_fail_fast_triggered"] == 1.0


def test_guardian_fail_fast_can_be_disabled() -> None:
    config = SwarmFrameworkConfig(guardian_fail_fast_enabled=False)
    framework = PersonaSwarmFramework(config=config)
    signals = [
        _signal(
            agent_id="g1",
            role="guardian",
            vote="block",
            confidence=0.92,
            safety_score=0.91,
        ),
        _signal(agent_id="e1", role="engineer", vote="approve", confidence=0.95),
    ]
    result = framework.evaluate(signals, final_decision="approve")

    assert result.decision == "approve"
    assert result.governance["guardian_fail_fast_triggered"] is False
    assert result.metrics["guardian_fail_fast_triggered"] == 0.0


def test_persona_positioning_supports_all_archetypes() -> None:
    framework = PersonaSwarmFramework()

    sentinel = framework._persona_positioning(
        _metrics(
            task_quality=0.5,
            safety_pass_rate=0.50,
            consistency_at_session=0.5,
            disagreement_utility=0.2,
            diversity_index=0.3,
        ),
        decision_support=0.8,
    )
    assert sentinel["archetype"] == "sentinel_recovery"

    critical = framework._persona_positioning(
        _metrics(
            task_quality=0.75,
            safety_pass_rate=0.8,
            consistency_at_session=0.6,
            disagreement_utility=0.70,
            diversity_index=0.60,
        ),
        decision_support=0.8,
    )
    assert critical["archetype"] == "critical_discovery"

    reliable = framework._persona_positioning(
        _metrics(
            task_quality=0.80,
            safety_pass_rate=0.85,
            consistency_at_session=0.82,
            disagreement_utility=0.2,
            diversity_index=0.2,
        ),
        decision_support=0.9,
    )
    assert reliable["archetype"] == "reliable_executor"

    adaptive = framework._persona_positioning(
        _metrics(
            task_quality=0.70,
            safety_pass_rate=0.8,
            consistency_at_session=0.65,
            disagreement_utility=0.2,
            diversity_index=0.3,
        ),
        decision_support=0.6,
    )
    assert adaptive["archetype"] == "adaptive_integrator"
