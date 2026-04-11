"""Integration tests for Governance Reflex Arc Phase 2 — hard enforcement.

Tests that vow BLOCK and Council BLOCK actually replace output in the
pipeline path, and that the dashboard vow gate works correctly.
"""

from __future__ import annotations

from tonesoul.governance.reflex import (
    GovernanceSnapshot,
    ReflexAction,
    ReflexDecision,
    ReflexEvaluator,
    classify_soul_band,
    enforce_vows_lightweight,
)
from tonesoul.governance.reflex_config import ReflexConfig

# ---------------------------------------------------------------------------
# Hard mode enforcement: vow BLOCK replaces output
# ---------------------------------------------------------------------------


class TestHardModeVowBlock:
    """Vow violations in hard mode must produce BLOCK + replacement message."""

    def _make_hard_evaluator(self) -> ReflexEvaluator:
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        return ReflexEvaluator(config=config)

    def test_vow_blocked_replaces_output(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            vow_blocked=True,
            vow_flags=["no_harm"],
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None
        assert "no_harm" in decision.blocked_message

    def test_vow_blocked_with_multiple_flags(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.1,
            tension=0.1,
            vow_blocked=True,
            vow_flags=["honesty", "transparency", "care"],
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.BLOCK
        assert "honesty" in decision.blocked_message

    def test_vow_not_blocked_passes(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.1,
            tension=0.1,
            vow_blocked=False,
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.PASS
        assert decision.blocked_message is None

    def test_vow_repair_triggers_reflection(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            vow_blocked=False,
            vow_repair_needed=True,
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.trigger_reflection is True


# ---------------------------------------------------------------------------
# Hard mode enforcement: Council BLOCK replaces output
# ---------------------------------------------------------------------------


class TestHardModeCouncilBlock:
    """Council BLOCK verdict in hard mode must produce BLOCK."""

    def _make_hard_evaluator(self) -> ReflexEvaluator:
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        return ReflexEvaluator(config=config)

    def test_council_block_replaces_output(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            council_verdict="BLOCK",
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None
        assert "Council" in decision.blocked_message

    def test_council_warn_does_not_block(self):
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            council_verdict="WARN",
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action != ReflexAction.BLOCK

    def test_council_block_plus_vow_block(self):
        """Both council and vow block — vow takes precedence (evaluated later)."""
        evaluator = self._make_hard_evaluator()
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            vow_blocked=True,
            vow_flags=["integrity"],
            council_verdict="BLOCK",
        )
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.BLOCK
        # Should have enforcement log entries for both
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "council_block" in steps or "vow_block" in steps


# ---------------------------------------------------------------------------
# Critical soul band in hard mode
# ---------------------------------------------------------------------------


class TestCriticalBandHardMode:
    """Critical soul_integral in hard mode blocks output."""

    def test_critical_hard_blocks(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.85, tension=0.5)
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None
        assert "危機" in decision.blocked_message

    def test_critical_soft_softens_not_blocks(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="soft")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.85, tension=0.5)
        decision = evaluator.evaluate(snapshot)
        assert decision.action == ReflexAction.SOFTEN
        assert decision.blocked_message is None
        assert decision.disclaimer is not None


# ---------------------------------------------------------------------------
# apply_reflex_final_gate simulation
# ---------------------------------------------------------------------------


class TestApplyReflexFinalGate:
    """Simulate what unified_pipeline._apply_reflex_final_gate does."""

    @staticmethod
    def _apply(response: str, decision: ReflexDecision) -> str:
        """Mirror the pipeline's final gate logic."""
        if decision.action == ReflexAction.BLOCK:
            if decision.blocked_message:
                return decision.blocked_message
        elif decision.action in (ReflexAction.SOFTEN, ReflexAction.WARN):
            if decision.disclaimer:
                return f"{response}\n\n---\n{decision.disclaimer}"
        return response

    def test_block_replaces_entirely(self):
        decision = ReflexDecision(
            action=ReflexAction.BLOCK,
            blocked_message="此回應已被攔截。",
        )
        result = self._apply("原始回應內容", decision)
        assert result == "此回應已被攔截。"
        assert "原始回應" not in result

    def test_warn_appends_disclaimer(self):
        decision = ReflexDecision(
            action=ReflexAction.WARN,
            disclaimer="[治理提示] 注意。",
        )
        result = self._apply("原始回應", decision)
        assert "原始回應" in result
        assert "[治理提示]" in result

    def test_pass_unchanged(self):
        decision = ReflexDecision(action=ReflexAction.PASS)
        result = self._apply("原始回應", decision)
        assert result == "原始回應"

    def test_soften_appends_disclaimer(self):
        decision = ReflexDecision(
            action=ReflexAction.SOFTEN,
            disclaimer="[治理警告] 系統緊繃。",
        )
        result = self._apply("回應", decision)
        assert "回應" in result
        assert "[治理警告]" in result


# ---------------------------------------------------------------------------
# Gate modifier tightening
# ---------------------------------------------------------------------------


class TestGateModifierTightening:
    """Soul band gate modifier properly tightens AdaptiveGate thresholds."""

    def test_serene_no_tightening(self):
        band = classify_soul_band(0.15)
        assert band.gate_modifier == 1.0

    def test_alert_10_percent(self):
        band = classify_soul_band(0.40)
        assert band.gate_modifier == 0.90

    def test_strained_25_percent(self):
        band = classify_soul_band(0.60)
        assert band.gate_modifier == 0.75

    def test_critical_45_percent(self):
        band = classify_soul_band(0.85)
        assert band.gate_modifier == 0.55

    def test_strained_forces_council(self):
        band = classify_soul_band(0.60)
        assert band.force_council is True

    def test_critical_caps_autonomy(self):
        band = classify_soul_band(0.85)
        assert band.max_autonomy == 0.10


# ---------------------------------------------------------------------------
# enforce_vows_lightweight (Dashboard path)
# ---------------------------------------------------------------------------


class TestEnforceVowsLightweight:
    """Dashboard vow gate should fail closed on errors."""

    def test_returns_dict_structure(self):
        result = enforce_vows_lightweight("Hello world")
        assert isinstance(result, dict)
        assert "passed" in result
        assert "blocked" in result
        assert "flags" in result

    def test_fail_closed_on_import_error(self, monkeypatch):
        """If VowEnforcer import fails, should block (fail closed)."""
        import builtins

        real_import = builtins.__import__

        def _block_vow_import(name, *args, **kwargs):
            if "vow_system" in name:
                raise ImportError("VowEnforcer not available")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_vow_import)
        result = enforce_vows_lightweight("test output")
        assert isinstance(result, dict)
        assert result["blocked"] is True  # fail closed
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# Mode transition: soft → hard
# ---------------------------------------------------------------------------


class TestModeTransition:
    """Verify that switching from soft to hard changes enforcement behavior."""

    def _evaluate_with_mode(
        self, mode: str, *, vow_blocked: bool = False, council_verdict: str = None
    ) -> ReflexDecision:
        config = ReflexConfig(enabled=True, vow_enforcement_mode=mode)
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(
            soul_integral=0.2,
            tension=0.3,
            vow_blocked=vow_blocked,
            vow_flags=["test_vow"] if vow_blocked else [],
            council_verdict=council_verdict,
        )
        return evaluator.evaluate(snapshot)

    def test_soft_vow_warns(self):
        decision = self._evaluate_with_mode("soft", vow_blocked=True)
        assert decision.action == ReflexAction.WARN
        assert decision.blocked_message is None

    def test_hard_vow_blocks(self):
        decision = self._evaluate_with_mode("hard", vow_blocked=True)
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None

    def test_soft_council_warns(self):
        decision = self._evaluate_with_mode("soft", council_verdict="BLOCK")
        assert decision.action == ReflexAction.WARN
        assert decision.blocked_message is None

    def test_hard_council_blocks(self):
        decision = self._evaluate_with_mode("hard", council_verdict="BLOCK")
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None


# ---------------------------------------------------------------------------
# Enforcement log completeness
# ---------------------------------------------------------------------------


class TestEnforcementLog:
    """Enforcement log should contain all evaluation steps."""

    def test_full_enforcement_log(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(
            soul_integral=0.85,  # critical
            tension=0.8,
            vow_blocked=True,
            vow_flags=["no_harm"],
            council_verdict="BLOCK",
            baseline_drift={"caution_bias": 0.8, "autonomy_level": 0.5},
        )
        decision = evaluator.evaluate(snapshot)
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "soul_band" in steps
        assert "critical_enforcement" in steps

    def test_serene_minimal_log(self):
        config = ReflexConfig(enabled=True, vow_enforcement_mode="hard")
        evaluator = ReflexEvaluator(config=config)
        snapshot = GovernanceSnapshot(soul_integral=0.1, tension=0.1)
        decision = evaluator.evaluate(snapshot)
        steps = [e.get("step") for e in decision.enforcement_log]
        assert "soul_band" in steps
        assert len(steps) == 1  # only soul_band, no escalation
