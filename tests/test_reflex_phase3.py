"""Tests for Governance Reflex Arc Phase 3 — Drift reactions + auto-reflection."""

from __future__ import annotations

from tonesoul.governance.reflex import (
    ConvictionSignal,
    GovernanceSnapshot,
    ReflexAction,
    ReflexEvaluator,
    classify_soul_band,
    evaluate_conviction_decay,
    evaluate_drift,
)
from tonesoul.governance.reflex_config import ReflexConfig

# ---------------------------------------------------------------------------
# Conviction Decay
# ---------------------------------------------------------------------------


class TestConvictionDecay:
    """Conviction decay detection and self-assessment trigger."""

    def test_no_vows_returns_empty(self):
        signal = evaluate_conviction_decay(None)
        assert signal.trigger_self_assessment is False
        assert signal.min_conviction == 1.0

    def test_healthy_vows_no_trigger(self):
        vows = [
            {"vow_id": "truth", "conviction": 0.9, "trajectory": "stable"},
            {"vow_id": "care", "conviction": 0.8, "trajectory": "rising"},
        ]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is False
        assert signal.min_conviction == 0.8

    def test_decaying_below_threshold_triggers(self):
        vows = [
            {"vow_id": "truth", "conviction": 0.35, "trajectory": "decaying"},
            {"vow_id": "care", "conviction": 0.8, "trajectory": "stable"},
        ]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is True
        assert len(signal.decaying_vows) == 1
        assert signal.decaying_vows[0]["vow_id"] == "truth"
        assert signal.min_conviction == 0.35

    def test_low_conviction_stable_trajectory_no_trigger(self):
        """Low conviction alone isn't enough — trajectory must be 'decaying'."""
        vows = [
            {"vow_id": "truth", "conviction": 0.3, "trajectory": "stable"},
        ]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is False

    def test_custom_threshold(self):
        vows = [
            {"vow_id": "truth", "conviction": 0.5, "trajectory": "decaying"},
        ]
        signal = evaluate_conviction_decay(vows, decay_threshold=0.6)
        assert signal.trigger_self_assessment is True

    def test_to_dict(self):
        signal = ConvictionSignal(
            decaying_vows=[{"vow_id": "x", "conviction": 0.3, "trajectory": "decaying"}],
            min_conviction=0.3,
            trigger_self_assessment=True,
        )
        d = signal.to_dict()
        assert d["trigger_self_assessment"] is True
        assert d["min_conviction"] == 0.3


# ---------------------------------------------------------------------------
# Drift Reactions
# ---------------------------------------------------------------------------


class TestDriftReactions:
    """Drift signals correctly influence reflex decisions."""

    def test_high_caution_injects_prompt(self):
        signal = evaluate_drift({"caution_bias": 0.65, "autonomy_level": 0.3})
        assert signal.inject_caution_prompt is True
        assert signal.inject_risk_prompt is False

    def test_very_high_caution_injects_risk(self):
        signal = evaluate_drift({"caution_bias": 0.80, "autonomy_level": 0.3})
        assert signal.inject_caution_prompt is True
        assert signal.inject_risk_prompt is True

    def test_autonomy_capped_by_soul_band(self):
        signal = evaluate_drift(
            {"caution_bias": 0.5, "autonomy_level": 0.5},
            max_autonomy=0.25,
        )
        assert signal.autonomy_capped is True

    def test_normal_drift_no_flags(self):
        signal = evaluate_drift({"caution_bias": 0.4, "autonomy_level": 0.3})
        assert signal.inject_caution_prompt is False
        assert signal.inject_risk_prompt is False
        assert signal.autonomy_capped is False


# ---------------------------------------------------------------------------
# Evaluator: conviction decay triggers reflection
# ---------------------------------------------------------------------------


class TestConvictionDecayInEvaluator:
    """Conviction decay flows through to ReflexDecision."""

    def test_decaying_conviction_triggers_reflection(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.2,
            conviction_signal=ConvictionSignal(
                decaying_vows=[{"vow_id": "truth", "conviction": 0.3, "trajectory": "decaying"}],
                min_conviction=0.3,
                trigger_self_assessment=True,
            ),
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.trigger_reflection is True
        assert decision.action == ReflexAction.WARN
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "conviction_decay" in steps

    def test_no_conviction_signal_no_trigger(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.1, tension=0.1)
        decision = evaluator.evaluate(snapshot)
        assert decision.trigger_reflection is False


# ---------------------------------------------------------------------------
# Autonomy Gate (autonomous_cycle path)
# ---------------------------------------------------------------------------


class TestAutonomyGate:
    """Soul band caps block autonomous operations."""

    def test_strained_band_caps_autonomy(self):
        band = classify_soul_band(0.60)
        assert band.max_autonomy == 0.25

    def test_critical_band_strict_cap(self):
        band = classify_soul_band(0.85)
        assert band.max_autonomy == 0.10

    def test_serene_no_cap(self):
        band = classify_soul_band(0.15)
        assert band.max_autonomy is None


# ---------------------------------------------------------------------------
# Tension + soul_integral combined trigger
# ---------------------------------------------------------------------------


class TestTensionReflectionTrigger:
    """High tension + high soul_integral forces reflection."""

    def test_both_high_triggers(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.60, tension=0.75)
        decision = evaluator.evaluate(snapshot)
        assert decision.trigger_reflection is True
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "tension_reflection_trigger" in steps

    def test_high_tension_low_integral_no_trigger(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.20, tension=0.80)
        decision = evaluator.evaluate(snapshot)
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "tension_reflection_trigger" not in steps

    def test_high_integral_low_tension_no_trigger(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.70, tension=0.30)
        decision = evaluator.evaluate(snapshot)
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "tension_reflection_trigger" not in steps
