"""
Unit tests for the Governance Reflex Arc (Phase 1).

Tests:
  - SoulBand classification at all four levels
  - Gate modifier boundaries
  - ReflexEvaluator in soft vs hard mode
  - Drift signal evaluation
  - Vow enforcement decisions
  - Council BLOCK handling
  - Lightweight vow gate
  - ReflexConfig loading
"""

from __future__ import annotations

import json

from tonesoul.governance.reflex import (
    GovernanceSnapshot,
    ReflexAction,
    ReflexDecision,
    ReflexEvaluator,
    SoulBandLevel,
    classify_soul_band,
    enforce_vows_lightweight,
    evaluate_drift,
)
from tonesoul.governance.reflex_config import ReflexConfig, load_reflex_config

# ---------------------------------------------------------------------------
# SoulBand Classification
# ---------------------------------------------------------------------------


class TestSoulBandClassification:
    """Soul integral → band level mapping."""

    def test_serene_low(self):
        band = classify_soul_band(0.0)
        assert band.level == SoulBandLevel.SERENE
        assert band.gate_modifier == 1.0
        assert band.force_council is False
        assert band.max_autonomy is None

    def test_serene_upper_boundary(self):
        band = classify_soul_band(0.29)
        assert band.level == SoulBandLevel.SERENE

    def test_alert_lower_boundary(self):
        band = classify_soul_band(0.30)
        assert band.level == SoulBandLevel.ALERT
        assert band.gate_modifier == 0.90
        assert band.force_council is False

    def test_alert_mid(self):
        band = classify_soul_band(0.45)
        assert band.level == SoulBandLevel.ALERT

    def test_strained_lower_boundary(self):
        band = classify_soul_band(0.55)
        assert band.level == SoulBandLevel.STRAINED
        assert band.gate_modifier == 0.75
        assert band.force_council is True
        assert band.max_autonomy == 0.25

    def test_strained_mid(self):
        band = classify_soul_band(0.70)
        assert band.level == SoulBandLevel.STRAINED

    def test_critical_lower_boundary(self):
        band = classify_soul_band(0.80)
        assert band.level == SoulBandLevel.CRITICAL
        assert band.gate_modifier == 0.55
        assert band.force_council is True
        assert band.max_autonomy == 0.10

    def test_critical_max(self):
        band = classify_soul_band(1.0)
        assert band.level == SoulBandLevel.CRITICAL

    def test_clamp_negative(self):
        band = classify_soul_band(-0.5)
        assert band.level == SoulBandLevel.SERENE
        assert band.soul_integral == 0.0

    def test_clamp_above_one(self):
        band = classify_soul_band(1.5)
        assert band.level == SoulBandLevel.CRITICAL
        assert band.soul_integral == 1.0

    def test_custom_thresholds(self):
        band = classify_soul_band(
            0.50,
            thresholds={"alert": 0.20, "strained": 0.40, "critical": 0.60},
        )
        assert band.level == SoulBandLevel.STRAINED

    def test_to_dict(self):
        band = classify_soul_band(0.45)
        d = band.to_dict()
        assert d["level"] == "alert"
        assert "gate_modifier" in d
        assert "soul_integral" in d


# ---------------------------------------------------------------------------
# Drift Evaluation
# ---------------------------------------------------------------------------


class TestDriftEvaluation:
    """Baseline drift → actionable signals."""

    def test_default_drift_no_flags(self):
        signal = evaluate_drift({"caution_bias": 0.5, "autonomy_level": 0.35})
        assert signal.inject_caution_prompt is False
        assert signal.inject_risk_prompt is False
        assert signal.autonomy_capped is False

    def test_caution_above_threshold(self):
        signal = evaluate_drift({"caution_bias": 0.65, "autonomy_level": 0.35})
        assert signal.inject_caution_prompt is True
        assert signal.inject_risk_prompt is False

    def test_risk_above_threshold(self):
        signal = evaluate_drift({"caution_bias": 0.80, "autonomy_level": 0.35})
        assert signal.inject_caution_prompt is True
        assert signal.inject_risk_prompt is True

    def test_autonomy_capped(self):
        signal = evaluate_drift(
            {"caution_bias": 0.5, "autonomy_level": 0.50},
            max_autonomy=0.25,
        )
        assert signal.autonomy_capped is True

    def test_autonomy_not_capped_when_below(self):
        signal = evaluate_drift(
            {"caution_bias": 0.5, "autonomy_level": 0.20},
            max_autonomy=0.25,
        )
        assert signal.autonomy_capped is False

    def test_to_dict(self):
        signal = evaluate_drift({"caution_bias": 0.7, "autonomy_level": 0.35})
        d = signal.to_dict()
        assert "inject_caution_prompt" in d
        assert d["inject_caution_prompt"] is True


# ---------------------------------------------------------------------------
# GovernanceSnapshot
# ---------------------------------------------------------------------------


class TestGovernanceSnapshot:
    """Building snapshots from various inputs."""

    def test_defaults(self):
        snap = GovernanceSnapshot()
        assert snap.soul_integral == 0.0
        assert snap.tension == 0.0
        assert snap.vow_blocked is False
        assert snap.council_verdict is None

    def test_from_posture_like_object(self):
        class FakePosture:
            soul_integral = 0.65
            baseline_drift = {"caution_bias": 0.7, "autonomy_level": 0.3}

        snap = GovernanceSnapshot.from_posture(
            FakePosture(),
            tension=0.5,
            vow_blocked=True,
            vow_flags=["BLOCKED by vow_truth"],
            council_verdict="BLOCK",
        )
        assert snap.soul_integral == 0.65
        assert snap.tension == 0.5
        assert snap.vow_blocked is True
        assert snap.council_verdict == "BLOCK"
        assert "BLOCKED by vow_truth" in snap.vow_flags


# ---------------------------------------------------------------------------
# ReflexEvaluator
# ---------------------------------------------------------------------------


class TestReflexEvaluatorSoftMode:
    """Soft enforcement — warnings only."""

    def _make_evaluator(self, **overrides):
        overrides.setdefault("vow_enforcement_mode", "soft")
        config = ReflexConfig(**overrides)
        return ReflexEvaluator(config=config)

    def test_serene_pass(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.1, tension=0.2)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.PASS
        assert decision.gate_modifier == 1.0
        assert decision.disclaimer is None
        assert decision.blocked_message is None

    def test_alert_with_tension_warns(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.40, tension=0.45)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.WARN
        assert decision.disclaimer is not None
        assert "警覺" in decision.disclaimer
        assert decision.gate_modifier == 0.90

    def test_alert_without_tension_passes(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.40, tension=0.2)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.PASS
        assert decision.gate_modifier == 0.90

    def test_strained_softens(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.65, tension=0.5)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.SOFTEN
        assert decision.gate_modifier == 0.75
        assert decision.trigger_reflection is True
        assert decision.soul_band.force_council is True

    def test_critical_softens_not_blocks(self):
        """In soft mode, critical doesn't block."""
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.90, tension=0.6)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.SOFTEN
        assert decision.gate_modifier == 0.55
        assert decision.blocked_message is None

    def test_vow_blocked_soft_warns(self):
        """Soft mode: vow BLOCK → WARN, not actual block."""
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(
            soul_integral=0.1,
            vow_blocked=True,
            vow_flags=["BLOCKED by vow_truth: Truthfulness"],
        )
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.WARN
        assert decision.blocked_message is None
        assert "誓言警告" in decision.disclaimer

    def test_council_block_soft_warns(self):
        """Soft mode: council BLOCK → WARN."""
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.1, council_verdict="BLOCK")
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.WARN
        assert decision.blocked_message is None

    def test_tension_reflection_trigger(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.60, tension=0.75)
        decision = ev.evaluate(snap)
        assert decision.trigger_reflection is True

    def test_custom_band_thresholds_are_used(self):
        ev = self._make_evaluator(
            soul_band_thresholds={"alert": 0.10, "strained": 0.20, "critical": 0.30}
        )
        snap = GovernanceSnapshot(soul_integral=0.25, tension=0.30)
        decision = ev.evaluate(snap)
        assert decision.soul_band is not None
        assert decision.soul_band.level == SoulBandLevel.STRAINED
        assert decision.gate_modifier == 0.75

    def test_custom_drift_thresholds_are_used(self):
        ev = self._make_evaluator(
            caution_prompt_threshold=0.70,
            risk_prompt_threshold=0.90,
        )
        snap = GovernanceSnapshot(
            soul_integral=0.10,
            baseline_drift={"caution_bias": 0.65, "autonomy_level": 0.35},
        )
        decision = ev.evaluate(snap)
        steps = [e["step"] for e in decision.enforcement_log]
        assert "drift_caution_inject" not in steps
        assert "drift_risk_inject" not in steps

    def test_custom_reflection_thresholds_are_used(self):
        ev = self._make_evaluator(
            tension_reflection_threshold=0.40,
            soul_integral_reflection_threshold=0.20,
        )
        snap = GovernanceSnapshot(soul_integral=0.25, tension=0.45)
        decision = ev.evaluate(snap)
        assert decision.trigger_reflection is True

    def test_disabled_always_passes(self):
        ev = self._make_evaluator(enabled=False)
        snap = GovernanceSnapshot(soul_integral=0.99, tension=0.99, vow_blocked=True)
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.PASS
        assert decision.gate_modifier == 1.0


class TestReflexEvaluatorHardMode:
    """Phase 2 preview: hard enforcement — blocks when triggered."""

    def _make_evaluator(self):
        config = ReflexConfig(vow_enforcement_mode="hard")
        return ReflexEvaluator(config=config)

    def test_vow_blocked_hard_blocks(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(
            soul_integral=0.1,
            vow_blocked=True,
            vow_flags=["BLOCKED by vow_truth: Truthfulness"],
        )
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None
        assert "誓言守護" in decision.blocked_message

    def test_council_block_hard_blocks(self):
        ev = self._make_evaluator()
        snap = GovernanceSnapshot(soul_integral=0.1, council_verdict="BLOCK")
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None
        assert "Council" in decision.blocked_message

    def test_council_block_respects_config_switch(self):
        config = ReflexConfig(
            vow_enforcement_mode="hard",
            council_block_enforcement=False,
        )
        ev = ReflexEvaluator(config=config)
        snap = GovernanceSnapshot(soul_integral=0.1, council_verdict="BLOCK")
        decision = ev.evaluate(snap)
        assert decision.action == ReflexAction.PASS
        steps = [e["step"] for e in decision.enforcement_log]
        assert "council_block_ignored_by_config" in steps


# ---------------------------------------------------------------------------
# ReflexDecision
# ---------------------------------------------------------------------------


class TestReflexDecision:
    def test_to_dict_minimal(self):
        d = ReflexDecision().to_dict()
        assert d["action"] == "pass"
        assert d["gate_modifier"] == 1.0
        assert "disclaimer" not in d
        assert "blocked_message" not in d

    def test_to_dict_full(self):
        band = classify_soul_band(0.70)
        d = ReflexDecision(
            action=ReflexAction.SOFTEN,
            gate_modifier=0.75,
            soul_band=band,
            disclaimer="test",
            blocked_message="blocked",
            enforcement_log=[{"step": "test"}],
        ).to_dict()
        assert d["action"] == "soften"
        assert d["soul_band"]["level"] == "strained"
        assert d["disclaimer"] == "test"
        assert d["blocked_message"] == "blocked"
        assert len(d["enforcement_log"]) == 1


# ---------------------------------------------------------------------------
# Enforcement Log
# ---------------------------------------------------------------------------


class TestEnforcementLog:
    """Verify that enforcement log captures key steps."""

    def test_serene_logs_soul_band_only(self):
        ev = ReflexEvaluator(config=ReflexConfig())
        snap = GovernanceSnapshot(soul_integral=0.1, tension=0.1)
        decision = ev.evaluate(snap)
        steps = [e["step"] for e in decision.enforcement_log]
        assert "soul_band" in steps

    def test_strained_logs_enforcement(self):
        ev = ReflexEvaluator(config=ReflexConfig())
        snap = GovernanceSnapshot(soul_integral=0.65, tension=0.5)
        decision = ev.evaluate(snap)
        steps = [e["step"] for e in decision.enforcement_log]
        assert "soul_band" in steps
        assert "strained_enforcement" in steps

    def test_vow_block_logged(self):
        ev = ReflexEvaluator(config=ReflexConfig(vow_enforcement_mode="hard"))
        snap = GovernanceSnapshot(vow_blocked=True, vow_flags=["test"])
        decision = ev.evaluate(snap)
        steps = [e["step"] for e in decision.enforcement_log]
        assert "vow_block" in steps


# ---------------------------------------------------------------------------
# ReflexConfig
# ---------------------------------------------------------------------------


class TestReflexConfig:
    def test_defaults(self):
        cfg = ReflexConfig()
        assert cfg.enabled is True
        assert cfg.vow_enforcement_mode == "hard"
        assert cfg.council_block_enforcement is True
        assert cfg.soul_band_thresholds["alert"] == 0.30

    def test_from_dict(self):
        cfg = ReflexConfig.from_dict(
            {
                "enabled": False,
                "vow_enforcement_mode": "hard",
                "soul_band_thresholds": {"alert": 0.25, "strained": 0.50, "critical": 0.75},
            }
        )
        assert cfg.enabled is False
        assert cfg.vow_enforcement_mode == "hard"
        assert cfg.soul_band_thresholds["alert"] == 0.25

    def test_to_dict_roundtrip(self):
        cfg = ReflexConfig()
        d = cfg.to_dict()
        cfg2 = ReflexConfig.from_dict(d)
        assert cfg2.enabled == cfg.enabled
        assert cfg2.vow_enforcement_mode == cfg.vow_enforcement_mode

    def test_load_from_file(self, tmp_path):
        config_data = {
            "enabled": True,
            "vow_enforcement_mode": "hard",
            "soul_band_thresholds": {"alert": 0.20, "strained": 0.40, "critical": 0.60},
        }
        config_file = tmp_path / "reflex_config.json"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")
        cfg = load_reflex_config(repo_root=tmp_path)
        assert cfg.vow_enforcement_mode == "hard"
        assert cfg.soul_band_thresholds["alert"] == 0.20

    def test_load_missing_file_returns_defaults(self, tmp_path):
        cfg = load_reflex_config(repo_root=tmp_path)
        assert cfg.enabled is True
        assert cfg.vow_enforcement_mode == "hard"

    def test_load_malformed_file_returns_defaults(self, tmp_path):
        (tmp_path / "reflex_config.json").write_text("not json!", encoding="utf-8")
        cfg = load_reflex_config(repo_root=tmp_path)
        assert cfg.enabled is True


# ---------------------------------------------------------------------------
# Lightweight Vow Gate
# ---------------------------------------------------------------------------


class TestEnforceVowsLightweight:
    """Quick vow check for dashboard path."""

    def test_normal_output_passes(self):
        result = enforce_vows_lightweight("I think this is approximately correct.")
        assert result["passed"] is True or result["blocked"] is False
        assert result["replacement"] is None

    def test_empty_output_blocks(self):
        result = enforce_vows_lightweight("")
        assert result["blocked"] is True


# ---------------------------------------------------------------------------
# AdaptiveGate integration
# ---------------------------------------------------------------------------


class TestAdaptiveGateModifier:
    """Verify _action_from_tension respects gate_modifier."""

    def test_default_modifier_unchanged(self):
        from tonesoul.adaptive_gate import AdaptiveGate, GateAction

        assert AdaptiveGate._action_from_tension(0.85) == GateAction.BLOCK
        assert AdaptiveGate._action_from_tension(0.60) == GateAction.REVIEW
        assert AdaptiveGate._action_from_tension(0.40) == GateAction.WARN
        assert AdaptiveGate._action_from_tension(0.30) == GateAction.PASS

    def test_tightened_modifier(self):
        from tonesoul.adaptive_gate import AdaptiveGate, GateAction

        # With modifier 0.75: BLOCK at 0.85*0.75=0.6375, REVIEW at 0.60*0.75=0.45
        assert AdaptiveGate._action_from_tension(0.65, gate_modifier=0.75) == GateAction.BLOCK
        assert AdaptiveGate._action_from_tension(0.50, gate_modifier=0.75) == GateAction.REVIEW
        assert AdaptiveGate._action_from_tension(0.35, gate_modifier=0.75) == GateAction.WARN

    def test_modifier_floor(self):
        from tonesoul.adaptive_gate import AdaptiveGate

        # Modifier below 0.55 is clamped to 0.55
        result_low = AdaptiveGate._action_from_tension(0.50, gate_modifier=0.10)
        result_floor = AdaptiveGate._action_from_tension(0.50, gate_modifier=0.55)
        assert result_low == result_floor


# ---------------------------------------------------------------------------
# GovernanceKernel force_convene
# ---------------------------------------------------------------------------


class TestKernelForceConvene:
    """Verify should_convene_council respects force_convene."""

    def test_force_convene_overrides_low_tension(self):
        from tonesoul.governance.kernel import GovernanceKernel

        kernel = GovernanceKernel()
        convene, reason = kernel.should_convene_council(tension=0.1, force_convene=True)
        assert convene is True
        assert "reflex" in reason.lower()

    def test_no_force_low_tension_no_convene(self):
        from tonesoul.governance.kernel import GovernanceKernel

        kernel = GovernanceKernel()
        convene, _ = kernel.should_convene_council(tension=0.1)
        assert convene is False
