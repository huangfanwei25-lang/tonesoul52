"""Tests for tonesoul.council.swarm_framework — pure helpers and PersonaSwarmFramework."""
from __future__ import annotations

import pytest

from tonesoul.council.swarm_framework import (
    PersonaSwarmFramework,
    SwarmAgentSignal,
    SwarmFrameworkConfig,
    SwarmFrameworkResult,
    _clamp01,
    normalize_swarm_decision,
)


# ── _clamp01 ──────────────────────────────────────────────────────────────────

class TestClamp01:
    def test_normal_value(self):
        assert _clamp01(0.5) == pytest.approx(0.5)

    def test_above_one_clamped(self):
        assert _clamp01(1.5) == pytest.approx(1.0)

    def test_below_zero_clamped(self):
        assert _clamp01(-0.5) == pytest.approx(0.0)

    def test_zero(self):
        assert _clamp01(0.0) == pytest.approx(0.0)

    def test_one(self):
        assert _clamp01(1.0) == pytest.approx(1.0)


# ── normalize_swarm_decision ──────────────────────────────────────────────────

class TestNormalizeSwarmDecision:
    def test_valid_decisions(self):
        for d in ("approve", "block", "revise", "defer"):
            assert normalize_swarm_decision(d) == d

    def test_uppercase_normalized(self):
        assert normalize_swarm_decision("APPROVE") == "approve"

    def test_strips_whitespace(self):
        assert normalize_swarm_decision("  block  ") == "block"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            normalize_swarm_decision("")

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="must be one of"):
            normalize_swarm_decision("maybe")


# ── SwarmAgentSignal.from_dict ────────────────────────────────────────────────

def _signal_dict(**kw):
    defaults = {
        "agent_id": "agent-001",
        "role": "guardian",
        "vote": "approve",
        "confidence": 0.9,
        "safety_score": 0.85,
        "quality_score": 0.8,
        "novelty_score": 0.5,
        "latency_ms": 500.0,
        "token_cost": 100.0,
    }
    defaults.update(kw)
    return defaults


class TestSwarmAgentSignalFromDict:
    def test_valid_dict_creates_signal(self):
        sig = SwarmAgentSignal.from_dict(_signal_dict())
        assert sig.agent_id == "agent-001"
        assert sig.vote == "approve"

    def test_non_dict_raises(self):
        with pytest.raises(TypeError, match="must be an object"):
            SwarmAgentSignal.from_dict("not-a-dict")

    def test_missing_agent_id_raises(self):
        d = _signal_dict()
        del d["agent_id"]
        with pytest.raises(ValueError, match="agent_id"):
            SwarmAgentSignal.from_dict(d)

    def test_invalid_vote_raises(self):
        with pytest.raises(ValueError):
            SwarmAgentSignal.from_dict(_signal_dict(vote="maybe"))

    def test_confidence_clamped(self):
        sig = SwarmAgentSignal.from_dict(_signal_dict(confidence=1.5))
        assert sig.confidence == pytest.approx(1.0)

    def test_role_lowercased(self):
        sig = SwarmAgentSignal.from_dict(_signal_dict(role="GUARDIAN"))
        assert sig.role == "guardian"

    def test_latency_ms_non_negative(self):
        sig = SwarmAgentSignal.from_dict(_signal_dict(latency_ms=-100.0))
        assert sig.latency_ms == pytest.approx(0.0)


# ── SwarmFrameworkResult.to_dict ──────────────────────────────────────────────

class TestSwarmFrameworkResultToDict:
    def test_decision_support_rounded(self):
        result = SwarmFrameworkResult(
            decision="approve",
            decision_support=0.123456789,
            metrics={"swarm_score": 0.5},
            role_distribution={"guardian": 1},
            governance={},
            persona_positioning={},
        )
        d = result.to_dict()
        assert d["decision_support"] == pytest.approx(0.1235, abs=1e-4)

    def test_metrics_rounded(self):
        result = SwarmFrameworkResult(
            decision="block",
            decision_support=0.9,
            metrics={"swarm_score": 0.123456},
            role_distribution={},
            governance={},
            persona_positioning={},
        )
        d = result.to_dict()
        assert d["metrics"]["swarm_score"] == pytest.approx(0.1235, abs=1e-4)


# ── PersonaSwarmFramework static helpers ──────────────────────────────────────

class TestStaticHelpers:
    def setup_method(self):
        self.fw = PersonaSwarmFramework()

    def test_role_distribution(self):
        sigs = [
            SwarmAgentSignal.from_dict(_signal_dict(role="guardian")),
            SwarmAgentSignal.from_dict(_signal_dict(agent_id="a2", role="guardian")),
            SwarmAgentSignal.from_dict(_signal_dict(agent_id="a3", role="analyst")),
        ]
        dist = PersonaSwarmFramework._role_distribution(sigs)
        assert dist["guardian"] == 2
        assert dist["analyst"] == 1

    def test_weighted_vote_scores(self):
        sigs = [SwarmAgentSignal.from_dict(_signal_dict(vote="approve"))]
        scores = PersonaSwarmFramework._weighted_vote_scores(sigs)
        assert "approve" in scores
        assert scores["approve"] > 0

    def test_normalized_entropy_zero_on_single(self):
        assert PersonaSwarmFramework._normalized_entropy({"a": 1}) == 0.0

    def test_normalized_entropy_high_on_uniform(self):
        e = PersonaSwarmFramework._normalized_entropy({"a": 1, "b": 1, "c": 1, "d": 1})
        assert e == pytest.approx(1.0)

    def test_mean_empty(self):
        assert PersonaSwarmFramework._mean([]) == pytest.approx(0.0)

    def test_mean_values(self):
        assert PersonaSwarmFramework._mean([0.4, 0.6]) == pytest.approx(0.5)

    def test_is_guardian_role(self):
        assert PersonaSwarmFramework._is_guardian_role("guardian") is True
        assert PersonaSwarmFramework._is_guardian_role("guardian:strict") is True
        assert PersonaSwarmFramework._is_guardian_role("analyst") is False

    def test_support_ratio_empty(self):
        assert PersonaSwarmFramework._support_ratio({}, "approve") == pytest.approx(0.0)

    def test_support_ratio_correct(self):
        scores = {"approve": 3.0, "block": 1.0}
        assert PersonaSwarmFramework._support_ratio(scores, "approve") == pytest.approx(0.75)


# ── PersonaSwarmFramework.evaluate ────────────────────────────────────────────

def _make_signal(agent_id="a1", role="analyst", vote="approve", **kw):
    return SwarmAgentSignal.from_dict(_signal_dict(agent_id=agent_id, role=role, vote=vote, **kw))


class TestPersonaSwarmFrameworkEvaluate:
    def setup_method(self):
        self.fw = PersonaSwarmFramework()

    def test_empty_signals_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            self.fw.evaluate([])

    def test_majority_approve_wins(self):
        signals = [
            _make_signal("a1", vote="approve"),
            _make_signal("a2", vote="approve"),
            _make_signal("a3", vote="block"),
        ]
        result = self.fw.evaluate(signals)
        assert result.decision == "approve"

    def test_explicit_final_decision_honored(self):
        signals = [
            _make_signal("a1", vote="approve"),
            _make_signal("a2", vote="approve"),
        ]
        result = self.fw.evaluate(signals, final_decision="revise")
        assert result.decision == "revise"

    def test_result_has_all_required_keys(self):
        result = self.fw.evaluate([_make_signal()])
        d = result.to_dict()
        assert "decision" in d
        assert "decision_support" in d
        assert "metrics" in d
        assert "role_distribution" in d
        assert "governance" in d
        assert "persona_positioning" in d

    def test_metrics_include_swarm_score(self):
        result = self.fw.evaluate([_make_signal()])
        assert "swarm_score" in result.metrics
        assert 0.0 <= result.metrics["swarm_score"] <= 1.0

    def test_guardian_fail_fast_triggers_block(self):
        signals = [
            _make_signal("guardian-1", role="guardian", vote="block",
                         confidence=0.9, safety_score=0.9),
            _make_signal("a2", vote="approve"),
        ]
        result = self.fw.evaluate(signals)
        assert result.decision == "block"
        assert result.governance["guardian_fail_fast_triggered"] is True

    def test_guardian_fail_fast_disabled(self):
        config = SwarmFrameworkConfig(guardian_fail_fast_enabled=False)
        fw = PersonaSwarmFramework(config=config)
        signals = [
            _make_signal("guardian-1", role="guardian", vote="block",
                         confidence=0.9, safety_score=0.9),
            _make_signal("a2", vote="approve"),
            _make_signal("a3", vote="approve"),
        ]
        result = fw.evaluate(signals)
        # Without fail-fast, majority vote (approve) should win
        assert result.decision == "approve"

    def test_decision_support_in_range(self):
        result = self.fw.evaluate([_make_signal()])
        assert 0.0 <= result.decision_support <= 1.0

    def test_cost_index_computed(self):
        signals = [_make_signal(latency_ms=1000.0, token_cost=500.0)]
        result = self.fw.evaluate(signals)
        assert "token_latency_cost_index" in result.metrics

    def test_persona_positioning_has_archetype(self):
        result = self.fw.evaluate([_make_signal()])
        assert "archetype" in result.persona_positioning

    def test_unanimous_block_all_block(self):
        signals = [
            _make_signal("a1", vote="block"),
            _make_signal("a2", vote="block"),
        ]
        result = self.fw.evaluate(signals)
        assert result.decision == "block"
