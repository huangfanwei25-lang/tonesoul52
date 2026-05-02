"""Tests for tonesoul.governance.reflex — pure helpers and ReflexEvaluator."""

from __future__ import annotations

import pytest

from tonesoul.governance.reflex import (
    _ACTION_SEVERITY,
    ConvictionSignal,
    GovernanceSnapshot,
    ReflexAction,
    ReflexDecision,
    ReflexEvaluator,
    SoulBandLevel,
    classify_soul_band,
    evaluate_conviction_decay,
    evaluate_drift,
)

# ── classify_soul_band ────────────────────────────────────────────────────────


class TestClassifySoulBand:
    def test_serene_below_0_3(self):
        band = classify_soul_band(0.0)
        assert band.level == SoulBandLevel.SERENE

    def test_serene_just_below_0_3(self):
        band = classify_soul_band(0.29)
        assert band.level == SoulBandLevel.SERENE

    def test_alert_at_0_3(self):
        band = classify_soul_band(0.30)
        assert band.level == SoulBandLevel.ALERT

    def test_alert_between_0_3_and_0_55(self):
        band = classify_soul_band(0.45)
        assert band.level == SoulBandLevel.ALERT

    def test_strained_at_0_55(self):
        band = classify_soul_band(0.55)
        assert band.level == SoulBandLevel.STRAINED

    def test_critical_at_0_8(self):
        band = classify_soul_band(0.80)
        assert band.level == SoulBandLevel.CRITICAL

    def test_critical_above_0_8(self):
        band = classify_soul_band(0.95)
        assert band.level == SoulBandLevel.CRITICAL

    def test_clamps_above_one(self):
        band = classify_soul_band(2.0)
        assert band.level == SoulBandLevel.CRITICAL

    def test_clamps_below_zero(self):
        band = classify_soul_band(-1.0)
        assert band.level == SoulBandLevel.SERENE

    def test_serene_gate_modifier_1(self):
        band = classify_soul_band(0.1)
        assert band.gate_modifier == pytest.approx(1.0)

    def test_alert_gate_modifier_0_9(self):
        band = classify_soul_band(0.4)
        assert band.gate_modifier == pytest.approx(0.9)

    def test_strained_force_council(self):
        band = classify_soul_band(0.6)
        assert band.force_council is True

    def test_critical_max_autonomy_0_1(self):
        band = classify_soul_band(0.85)
        assert band.max_autonomy == pytest.approx(0.10)

    def test_custom_thresholds(self):
        # Override strained to start at 0.4
        band = classify_soul_band(
            0.45, thresholds={"alert": 0.20, "strained": 0.40, "critical": 0.80}
        )
        assert band.level == SoulBandLevel.STRAINED

    def test_to_dict_keys(self):
        d = classify_soul_band(0.5).to_dict()
        for key in ("level", "soul_integral", "gate_modifier", "force_council", "max_autonomy"):
            assert key in d


# ── evaluate_drift ────────────────────────────────────────────────────────────


class TestEvaluateDrift:
    def _drift(self, caution=0.5, innovation=0.6, autonomy=0.35) -> dict:
        return {"caution_bias": caution, "innovation_bias": innovation, "autonomy_level": autonomy}

    def test_below_caution_threshold_no_inject(self):
        signal = evaluate_drift(self._drift(caution=0.5))
        assert signal.inject_caution_prompt is False

    def test_above_caution_threshold_injects(self):
        signal = evaluate_drift(self._drift(caution=0.65))
        assert signal.inject_caution_prompt is True

    def test_above_risk_threshold_injects_risk(self):
        signal = evaluate_drift(self._drift(caution=0.80))
        assert signal.inject_risk_prompt is True

    def test_autonomy_capped_when_exceeds_max(self):
        signal = evaluate_drift(self._drift(autonomy=0.5), max_autonomy=0.25)
        assert signal.autonomy_capped is True

    def test_autonomy_not_capped_when_below_max(self):
        signal = evaluate_drift(self._drift(autonomy=0.2), max_autonomy=0.25)
        assert signal.autonomy_capped is False

    def test_no_max_autonomy_never_capped(self):
        signal = evaluate_drift(self._drift(autonomy=1.0), max_autonomy=None)
        assert signal.autonomy_capped is False

    def test_values_preserved(self):
        signal = evaluate_drift(self._drift(caution=0.55, innovation=0.70, autonomy=0.40))
        assert signal.caution_bias == pytest.approx(0.55)
        assert signal.innovation_bias == pytest.approx(0.70)
        assert signal.autonomy_level == pytest.approx(0.40)

    def test_custom_caution_threshold(self):
        signal = evaluate_drift(self._drift(caution=0.5), caution_threshold=0.45)
        assert signal.inject_caution_prompt is True

    def test_empty_drift_uses_defaults(self):
        signal = evaluate_drift({})
        assert 0.0 <= signal.caution_bias <= 1.0


# ── evaluate_conviction_decay ─────────────────────────────────────────────────


class TestEvaluateConvictionDecay:
    def test_empty_vows_no_decay(self):
        signal = evaluate_conviction_decay([])
        assert signal.trigger_self_assessment is False
        assert signal.min_conviction == pytest.approx(1.0)

    def test_none_vows_no_decay(self):
        signal = evaluate_conviction_decay(None)
        assert signal.trigger_self_assessment is False

    def test_decaying_vow_triggers_assessment(self):
        vows = [{"id": "v1", "conviction": 0.3, "trajectory": "decaying"}]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is True
        assert len(signal.decaying_vows) == 1

    def test_low_conviction_non_decaying_not_triggered(self):
        vows = [{"id": "v1", "conviction": 0.3, "trajectory": "stable"}]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is False

    def test_high_conviction_not_triggered(self):
        vows = [{"id": "v1", "conviction": 0.9, "trajectory": "decaying"}]
        signal = evaluate_conviction_decay(vows)
        assert signal.trigger_self_assessment is False

    def test_min_conviction_tracked(self):
        vows = [
            {"id": "v1", "conviction": 0.8, "trajectory": "stable"},
            {"id": "v2", "conviction": 0.5, "trajectory": "stable"},
        ]
        signal = evaluate_conviction_decay(vows)
        assert signal.min_conviction == pytest.approx(0.5)

    def test_custom_threshold(self):
        vows = [{"id": "v1", "conviction": 0.6, "trajectory": "decaying"}]
        signal = evaluate_conviction_decay(vows, decay_threshold=0.7)
        assert signal.trigger_self_assessment is True

    def test_object_with_vows_attribute(self):
        class _VowState:
            vows = [{"id": "v1", "conviction": 0.3, "trajectory": "decaying"}]

        signal = evaluate_conviction_decay(_VowState())
        assert signal.trigger_self_assessment is True

    def test_to_dict_keys(self):
        vows = [{"id": "v1", "conviction": 0.8, "trajectory": "stable"}]
        signal = evaluate_conviction_decay(vows)
        d = signal.to_dict()
        for k in ("decaying_vows", "min_conviction", "trigger_self_assessment"):
            assert k in d


# ── ReflexDecision.to_dict ────────────────────────────────────────────────────


class TestReflexDecisionToDict:
    def test_required_keys(self):
        d = ReflexDecision().to_dict()
        assert "action" in d
        assert "gate_modifier" in d
        assert "trigger_reflection" in d

    def test_action_is_string(self):
        d = ReflexDecision(action=ReflexAction.WARN).to_dict()
        assert d["action"] == "warn"

    def test_disclaimer_included_when_set(self):
        d = ReflexDecision(disclaimer="warning").to_dict()
        assert d["disclaimer"] == "warning"

    def test_blocked_message_included(self):
        d = ReflexDecision(blocked_message="blocked").to_dict()
        assert d["blocked_message"] == "blocked"

    def test_soul_band_included_when_set(self):
        band = classify_soul_band(0.4)
        d = ReflexDecision(soul_band=band).to_dict()
        assert "soul_band" in d

    def test_enforcement_log_included_when_nonempty(self):
        d = ReflexDecision(enforcement_log=[{"step": "test"}]).to_dict()
        assert "enforcement_log" in d


# ── _ACTION_SEVERITY ordering ─────────────────────────────────────────────────


class TestActionSeverity:
    def test_pass_lowest(self):
        assert _ACTION_SEVERITY[ReflexAction.PASS] == 0

    def test_block_highest(self):
        assert _ACTION_SEVERITY[ReflexAction.BLOCK] > _ACTION_SEVERITY[ReflexAction.SOFTEN]

    def test_warn_less_than_soften(self):
        assert _ACTION_SEVERITY[ReflexAction.WARN] < _ACTION_SEVERITY[ReflexAction.SOFTEN]


# ── GovernanceSnapshot.from_posture ───────────────────────────────────────────


class TestGovernanceSnapshotFromPosture:
    def _posture(self, si=0.2, drift=None, vows=None):
        class _P:
            soul_integral = si
            baseline_drift = drift or {
                "caution_bias": 0.5,
                "innovation_bias": 0.6,
                "autonomy_level": 0.35,
            }

        if vows is not None:
            _P.vows = vows
        return _P()

    def test_soul_integral_extracted(self):
        snap = GovernanceSnapshot.from_posture(self._posture(si=0.4))
        assert snap.soul_integral == pytest.approx(0.4)

    def test_drift_extracted(self):
        p = self._posture(
            drift={"caution_bias": 0.7, "innovation_bias": 0.5, "autonomy_level": 0.3}
        )
        snap = GovernanceSnapshot.from_posture(p)
        assert snap.baseline_drift["caution_bias"] == pytest.approx(0.7)

    def test_tension_set(self):
        snap = GovernanceSnapshot.from_posture(self._posture(), tension=0.8)
        assert snap.tension == pytest.approx(0.8)

    def test_council_verdict_uppercased(self):
        snap = GovernanceSnapshot.from_posture(self._posture(), council_verdict="block")
        assert snap.council_verdict == "BLOCK"

    def test_no_council_verdict_none(self):
        snap = GovernanceSnapshot.from_posture(self._posture())
        assert snap.council_verdict is None

    def test_vow_flags_set(self):
        snap = GovernanceSnapshot.from_posture(self._posture(), vow_flags=["flag1"])
        assert "flag1" in snap.vow_flags

    def test_conviction_extracted_from_vows(self):
        vows = [{"id": "v1", "conviction": 0.3, "trajectory": "decaying"}]
        snap = GovernanceSnapshot.from_posture(self._posture(vows=vows))
        assert snap.conviction_signal is not None
        assert snap.conviction_signal.trigger_self_assessment is True


# ── ReflexEvaluator.evaluate ──────────────────────────────────────────────────


def _snap(
    si=0.1,
    tension=0.0,
    vow_blocked=False,
    vow_repair=False,
    vow_flags=None,
    council_verdict=None,
    conviction=None,
):
    return GovernanceSnapshot(
        soul_integral=si,
        baseline_drift={"caution_bias": 0.5, "innovation_bias": 0.6, "autonomy_level": 0.35},
        tension=tension,
        vow_blocked=vow_blocked,
        vow_repair_needed=vow_repair,
        vow_flags=vow_flags or [],
        council_verdict=council_verdict,
        conviction_signal=conviction,
    )


class TestReflexEvaluatorDisabled:
    def test_disabled_returns_pass(self):
        class _Cfg:
            enabled = False

        ev = ReflexEvaluator(config=_Cfg())
        decision = ev.evaluate(_snap())
        assert decision.action == ReflexAction.PASS
        assert decision.gate_modifier == pytest.approx(1.0)


class TestReflexEvaluatorSerene:
    def setup_method(self):
        self.ev = ReflexEvaluator()

    def test_serene_low_tension_pass(self):
        decision = self.ev.evaluate(_snap(si=0.1, tension=0.2))
        assert decision.action == ReflexAction.PASS

    def test_serene_gate_modifier_1(self):
        decision = self.ev.evaluate(_snap(si=0.1))
        assert decision.gate_modifier == pytest.approx(1.0)


class TestReflexEvaluatorAlert:
    def setup_method(self):
        self.ev = ReflexEvaluator()

    def test_alert_with_tension_warns(self):
        decision = self.ev.evaluate(_snap(si=0.4, tension=0.5))
        assert decision.action == ReflexAction.WARN
        assert decision.disclaimer is not None

    def test_alert_without_tension_passes(self):
        decision = self.ev.evaluate(_snap(si=0.4, tension=0.2))
        assert decision.action == ReflexAction.PASS

    def test_alert_gate_modifier_0_9(self):
        decision = self.ev.evaluate(_snap(si=0.4))
        assert decision.gate_modifier == pytest.approx(0.9)


class TestReflexEvaluatorStrained:
    def setup_method(self):
        self.ev = ReflexEvaluator()

    def test_strained_softens(self):
        decision = self.ev.evaluate(_snap(si=0.6))
        assert decision.action == ReflexAction.SOFTEN

    def test_strained_triggers_reflection(self):
        decision = self.ev.evaluate(_snap(si=0.6))
        assert decision.trigger_reflection is True

    def test_strained_gate_modifier_0_75(self):
        decision = self.ev.evaluate(_snap(si=0.6))
        assert decision.gate_modifier == pytest.approx(0.75)


class TestReflexEvaluatorCritical:
    def test_critical_soft_mode_soften(self):
        ev = ReflexEvaluator()
        decision = ev.evaluate(_snap(si=0.85))
        assert decision.action == ReflexAction.SOFTEN

    def test_critical_hard_mode_blocks(self):
        class _Cfg:
            enabled = True
            vow_enforcement_mode = "hard"

        ev = ReflexEvaluator(config=_Cfg())
        decision = ev.evaluate(_snap(si=0.85))
        assert decision.action == ReflexAction.BLOCK
        assert decision.blocked_message is not None


class TestReflexEvaluatorVows:
    def test_vow_blocked_soft_warns(self):
        ev = ReflexEvaluator()
        decision = ev.evaluate(_snap(si=0.1, vow_blocked=True, vow_flags=["flag1"]))
        assert decision.action == ReflexAction.WARN

    def test_vow_blocked_hard_blocks(self):
        class _Cfg:
            enabled = True
            vow_enforcement_mode = "hard"

        ev = ReflexEvaluator(config=_Cfg())
        decision = ev.evaluate(_snap(si=0.1, vow_blocked=True, vow_flags=["flag1"]))
        assert decision.action == ReflexAction.BLOCK

    def test_vow_repair_needed_triggers_reflection(self):
        ev = ReflexEvaluator()
        decision = ev.evaluate(_snap(si=0.1, vow_repair=True))
        assert decision.trigger_reflection is True


class TestReflexEvaluatorCouncil:
    def test_council_block_soft_warns(self):
        ev = ReflexEvaluator()
        decision = ev.evaluate(_snap(si=0.1, council_verdict="BLOCK"))
        assert decision.action == ReflexAction.WARN

    def test_council_block_hard_blocks(self):
        class _Cfg:
            enabled = True
            vow_enforcement_mode = "hard"

        ev = ReflexEvaluator(config=_Cfg())
        decision = ev.evaluate(_snap(si=0.1, council_verdict="BLOCK"))
        assert decision.action == ReflexAction.BLOCK


class TestReflexEvaluatorConviction:
    def test_conviction_decay_triggers_reflection(self):
        ev = ReflexEvaluator()
        conv = ConvictionSignal(
            decaying_vows=[{"vow_id": "v1", "conviction": 0.3, "trajectory": "decaying"}],
            min_conviction=0.3,
            trigger_self_assessment=True,
        )
        decision = ev.evaluate(_snap(si=0.1, conviction=conv))
        assert decision.trigger_reflection is True
        assert decision.action == ReflexAction.WARN

    def test_no_conviction_no_trigger(self):
        ev = ReflexEvaluator()
        decision = ev.evaluate(_snap(si=0.1, conviction=None))
        assert decision.trigger_reflection is False


class TestReflexEvaluatorTensionReflection:
    def test_high_tension_and_si_triggers_reflection(self):
        ev = ReflexEvaluator()
        # tension > 0.70 and si > 0.55 both together
        decision = ev.evaluate(_snap(si=0.6, tension=0.8))
        assert decision.trigger_reflection is True
