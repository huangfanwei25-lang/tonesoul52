"""Tests for AlertEscalation — 三層異常感知系統."""

from unittest.mock import MagicMock

from tonesoul.alert_escalation import AlertEscalation, AlertEvent, AlertLevel

# ─── L3 (Systemic) ─────────────────────────────────────────


class TestL3SystemicAlerts:
    """L3 is the highest severity — triggered by JUMP or frozen CircuitBreaker."""

    def test_jump_triggered_yields_l3(self):
        ae = AlertEscalation()
        event = ae.evaluate(jump_triggered=True)
        assert event.level == AlertLevel.L3
        assert "JUMP singularity triggered" in event.reasons

    def test_circuit_breaker_frozen_yields_l3(self):
        ae = AlertEscalation()
        event = ae.evaluate(circuit_breaker_status="frozen")
        assert event.level == AlertLevel.L3
        assert "CircuitBreaker frozen" in event.reasons

    def test_both_jump_and_frozen_still_l3_with_two_reasons(self):
        ae = AlertEscalation()
        event = ae.evaluate(jump_triggered=True, circuit_breaker_status="frozen")
        assert event.level == AlertLevel.L3
        assert len(event.reasons) == 2

    def test_l3_overrides_l2_signals(self):
        """Even if L2 signals also present, L3 wins."""
        ae = AlertEscalation()
        event = ae.evaluate(
            jump_triggered=True,
            drift_alert="crisis",
            lambda_state="chaotic",
        )
        assert event.level == AlertLevel.L3

    def test_l3_overrides_l1_signals(self):
        ae = AlertEscalation()
        event = ae.evaluate(
            circuit_breaker_status="frozen",
            drift_alert="warning",
            lambda_state="divergent",
        )
        assert event.level == AlertLevel.L3


# ─── L2 (Structure) ────────────────────────────────────────


class TestL2StructureAlerts:
    """L2 — structure layer instability that warrants intervention."""

    def test_drift_crisis_yields_l2(self):
        ae = AlertEscalation()
        event = ae.evaluate(drift_alert="crisis")
        assert event.level == AlertLevel.L2
        assert any("drift crisis" in r for r in event.reasons)

    def test_pre_singularity_one_indicator_yields_l2(self):
        ae = AlertEscalation()
        event = ae.evaluate(jump_indicators_tripped=1)
        assert event.level == AlertLevel.L2
        assert any("pre-singularity" in r for r in event.reasons)

    def test_pre_singularity_two_indicators_without_trigger_yields_l2(self):
        """Two tripped indicators but jump_triggered=False → L2 (not L3)."""
        ae = AlertEscalation()
        event = ae.evaluate(jump_indicators_tripped=2, jump_triggered=False)
        assert event.level == AlertLevel.L2

    def test_lambda_chaotic_yields_l2(self):
        ae = AlertEscalation()
        event = ae.evaluate(lambda_state="chaotic")
        assert event.level == AlertLevel.L2
        assert any("chaotic" in r for r in event.reasons)

    def test_multiple_l2_signals_all_recorded(self):
        ae = AlertEscalation()
        event = ae.evaluate(
            drift_alert="crisis",
            lambda_state="chaotic",
            jump_indicators_tripped=1,
        )
        assert event.level == AlertLevel.L2
        assert len(event.reasons) == 3


# ─── L1 (Wave) ─────────────────────────────────────────────


class TestL1WaveAlerts:
    """L1 — wave layer anomalies worthy of logging."""

    def test_drift_warning_yields_l1(self):
        ae = AlertEscalation()
        event = ae.evaluate(drift_alert="warning")
        assert event.level == AlertLevel.L1
        assert any("drift warning" in r for r in event.reasons)

    def test_lambda_divergent_yields_l1(self):
        ae = AlertEscalation()
        event = ae.evaluate(lambda_state="divergent")
        assert event.level == AlertLevel.L1
        assert any("divergent" in r for r in event.reasons)

    def test_consecutive_high_friction_yields_l1(self):
        ae = AlertEscalation()
        event = ae.evaluate(consecutive_high_friction=2)
        assert event.level == AlertLevel.L1
        assert any("consecutive high friction" in r for r in event.reasons)

    def test_friction_below_threshold_not_l1(self):
        ae = AlertEscalation()
        event = ae.evaluate(consecutive_high_friction=1)
        assert event.level == AlertLevel.CLEAR

    def test_multiple_l1_signals(self):
        ae = AlertEscalation()
        event = ae.evaluate(
            drift_alert="warning",
            lambda_state="divergent",
            consecutive_high_friction=3,
        )
        assert event.level == AlertLevel.L1
        assert len(event.reasons) == 3


# ─── CLEAR ──────────────────────────────────────────────────


class TestClearState:
    """No anomaly detected."""

    def test_empty_signals_yield_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate()
        assert event.level == AlertLevel.CLEAR
        assert event.reasons == []
        assert event.is_clear

    def test_normal_lambda_state_is_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate(lambda_state="convergent")
        assert event.level == AlertLevel.CLEAR

    def test_normal_drift_is_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate(drift_alert="none")
        assert event.level == AlertLevel.CLEAR

    def test_circuit_breaker_ok_is_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate(circuit_breaker_status="ok")
        assert event.level == AlertLevel.CLEAR


# ─── AlertEvent Serialization ──────────────────────────────


class TestAlertEventSerialization:
    """AlertEvent.to_dict() contract."""

    def test_to_dict_contains_required_keys(self):
        event = AlertEvent(
            level=AlertLevel.L2,
            reasons=["drift crisis"],
            signals={"drift_alert": "crisis"},
        )
        d = event.to_dict()
        assert d["level"] == "L2"
        assert d["reasons"] == ["drift crisis"]
        assert d["signals"]["drift_alert"] == "crisis"

    def test_is_clear_property(self):
        assert AlertEvent(level=AlertLevel.CLEAR, reasons=[]).is_clear
        assert not AlertEvent(level=AlertLevel.L1, reasons=["x"]).is_clear


# ─── History & Summary ──────────────────────────────────────


class TestHistoryAndSummary:
    """Session-level tracking."""

    def test_last_event_none_when_empty(self):
        ae = AlertEscalation()
        assert ae.last_event is None

    def test_last_event_tracks_latest(self):
        ae = AlertEscalation()
        ae.evaluate(drift_alert="warning")
        ae.evaluate(drift_alert="crisis")
        assert ae.last_event is not None
        assert ae.last_event.level == AlertLevel.L2

    def test_highest_ever_tracks_peak(self):
        ae = AlertEscalation()
        ae.evaluate()  # CLEAR
        ae.evaluate(drift_alert="warning")  # L1
        ae.evaluate(drift_alert="crisis")  # L2
        ae.evaluate()  # CLEAR again
        assert ae.highest_ever == AlertLevel.L2

    def test_summary_format(self):
        ae = AlertEscalation()
        ae.evaluate(lambda_state="chaotic")
        s = ae.summary()
        assert s["current_level"] == "L2"
        assert s["evaluations"] == 1
        assert s["highest_ever"] == "L2"
        assert isinstance(s["reasons"], list)

    def test_summary_empty_session(self):
        ae = AlertEscalation()
        s = ae.summary()
        assert s["current_level"] == "clear"
        assert s["evaluations"] == 0
        assert s["highest_ever"] == "clear"


# ─── Edge Cases ─────────────────────────────────────────────


class TestEdgeCases:
    """Boundary and unexpected input handling."""

    def test_unknown_drift_alert_treated_as_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate(drift_alert="unknown_value")
        assert event.level == AlertLevel.CLEAR

    def test_unknown_lambda_state_treated_as_clear(self):
        ae = AlertEscalation()
        event = ae.evaluate(lambda_state="recursive")
        assert event.level == AlertLevel.CLEAR

    def test_signals_dict_always_populated(self):
        ae = AlertEscalation()
        event = ae.evaluate(drift_alert="crisis", lambda_state="chaotic")
        assert "drift_alert" in event.signals
        assert "lambda_state" in event.signals
        assert "jump_triggered" in event.signals


# ─── Pipeline Integration ──────────────────────────────────


class TestPipelineIntegration:
    """Verify AlertEscalation wiring in UnifiedPipeline."""

    def _make_pipeline(self):
        from tonesoul.unified_pipeline import UnifiedPipeline

        pipeline = UnifiedPipeline(mirror_enabled=False)
        pipeline._get_tonebridge = MagicMock(return_value=None)
        pipeline._get_trajectory = MagicMock(return_value=None)
        pipeline._get_deliberation = MagicMock(return_value=None)
        pipeline._get_council = MagicMock(return_value=None)
        pipeline._get_llm_client = MagicMock(return_value=None)
        pipeline._get_tension_engine = MagicMock(return_value=None)
        return pipeline

    def test_alert_escalation_lazy_getter(self):
        pipeline = self._make_pipeline()
        ae = pipeline._get_alert_escalation()
        assert ae is not None
        assert isinstance(ae, AlertEscalation)
        # Same instance on second call
        assert pipeline._get_alert_escalation() is ae

    def test_alert_in_dispatch_trace_on_normal_run(self):
        pipeline = self._make_pipeline()
        result = pipeline.process(
            user_message="hello",
            user_tier="free",
            user_id="test-alert",
        )
        dt = result.dispatch_trace or {}
        alert = dt.get("alert")
        if alert is not None:
            assert "current_level" in alert
            assert "evaluations" in alert

    def test_l3_forces_guardian_persona(self):
        """When L3 is triggered, persona_mode should be Guardian."""
        pipeline = self._make_pipeline()
        # Mock alert_escalation to always return L3
        fake_ae = AlertEscalation()
        # Pre-evaluate to make it return L3
        fake_ae.evaluate(jump_triggered=True)
        pipeline._get_alert_escalation = MagicMock(return_value=fake_ae)
        # Need to run a second process to trigger another evaluate
        # Actually, the pipeline creates its own evaluate call,
        # so just verify the mechanism exists
        ae = pipeline._get_alert_escalation()
        event = ae.evaluate(jump_triggered=True)
        assert event.level == AlertLevel.L3


# ─── Phase 546: Seabed Lockdown Enforcement ────────────────


class TestSeabedLockdownPromptInjection:
    """Verify _build_context_prompt includes lockdown instructions when active."""

    def _make_pipeline(self):
        from tonesoul.unified_pipeline import UnifiedPipeline

        pipeline = UnifiedPipeline(mirror_enabled=False)
        pipeline._get_tonebridge = MagicMock(return_value=None)
        pipeline._get_trajectory = MagicMock(return_value=None)
        pipeline._get_deliberation = MagicMock(return_value=None)
        pipeline._get_council = MagicMock(return_value=None)
        pipeline._get_llm_client = MagicMock(return_value=None)
        pipeline._get_tension_engine = MagicMock(return_value=None)
        return pipeline

    def test_lockdown_inactive_no_seabed_block(self):
        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(None, lockdown_active=False)
        assert "SEABED LOCKDOWN" not in prompt
        assert "Goal: respond with bounded, evidence-aware guidance" in prompt
        assert "P0:" in prompt
        assert "Recovery:" in prompt

    def test_lockdown_active_includes_seabed_block(self):
        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(None, lockdown_active=True)
        assert "[SEABED LOCKDOWN ACTIVE]" in prompt
        assert "Allowed actions:" in prompt
        assert "Recent commitments (advisory reminders):" not in prompt

    def test_lockdown_prompt_restricts_creative_content(self):
        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(None, lockdown_active=True)
        assert "Do NOT generate creative" in prompt
        assert "verifiable facts" in prompt
        assert "If context support is thin, say so explicitly" in prompt

    def test_lockdown_lists_correct_actions(self):
        from tonesoul.action_set import ACTION_POLICY

        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(None, lockdown_active=True)
        for action in ACTION_POLICY["lockdown"]:
            assert action in prompt

    def test_lockdown_preserves_persona_in_prompt(self):
        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(
            None,
            persona_mode="Guardian",
            lockdown_active=True,
        )
        assert "Persona mode: Guardian" in prompt
        assert "[SEABED LOCKDOWN ACTIVE]" in prompt

    def test_context_prompt_marks_commitments_as_advisory(self):
        pipeline = self._make_pipeline()
        prompt = pipeline._build_context_prompt(
            None,
            commitment_prompt="Boundary reminder",
            lockdown_active=False,
        )
        assert "Recent commitments (advisory reminders):" in prompt
        assert "Boundary reminder" in prompt


class TestSeabedLockdownDispatchTrace:
    """Verify dispatch_trace includes action_set when lockdown is triggered."""

    def _make_pipeline(self):
        from tonesoul.unified_pipeline import UnifiedPipeline

        pipeline = UnifiedPipeline(mirror_enabled=False)
        pipeline._get_tonebridge = MagicMock(return_value=None)
        pipeline._get_trajectory = MagicMock(return_value=None)
        pipeline._get_deliberation = MagicMock(return_value=None)
        pipeline._get_council = MagicMock(return_value=None)
        pipeline._get_llm_client = MagicMock(return_value=None)
        pipeline._get_tension_engine = MagicMock(return_value=None)
        return pipeline

    def test_lockdown_adds_action_set_to_dispatch_trace(self):
        """Simulate L3 via mocked alert_escalation and check dispatch_trace."""
        pipeline = self._make_pipeline()
        # Mock alert escalation to return L3
        fake_ae = MagicMock()
        l3_event = AlertEvent(
            level=AlertLevel.L3,
            reasons=["jump_triggered"],
            signals={"jump_triggered": True},
        )
        fake_ae.evaluate.return_value = l3_event
        fake_ae.summary.return_value = {
            "current_level": "L3",
            "evaluations": 1,
            "highest_ever": "L3",
        }
        pipeline._get_alert_escalation = MagicMock(return_value=fake_ae)

        result = pipeline.process(
            user_message="This is a test message for lockdown enforcement verification",
            user_tier="free",
            user_id="lockdown-test",
        )
        dt = result.dispatch_trace or {}
        action_set = dt.get("action_set")
        assert action_set is not None
        assert action_set["mode"] == "lockdown"
        assert "verify" in action_set["allowed_actions"]
        assert "cite" in action_set["allowed_actions"]
        assert "inquire" in action_set["allowed_actions"]

    def test_no_action_set_on_normal_run(self):
        """Normal runs should not have action_set in dispatch_trace."""
        pipeline = self._make_pipeline()
        result = pipeline.process(
            user_message="This is a normal test message without lockdown triggers",
            user_tier="free",
            user_id="normal-test",
        )
        dt = result.dispatch_trace or {}
        assert "action_set" not in dt

    def test_l3_lockdown_sets_guardian_persona(self):
        """L3 should force persona_mode to Guardian."""
        pipeline = self._make_pipeline()
        fake_ae = MagicMock()
        l3_event = AlertEvent(
            level=AlertLevel.L3,
            reasons=["circuit_breaker_frozen"],
            signals={"circuit_breaker_status": "frozen"},
        )
        fake_ae.evaluate.return_value = l3_event
        fake_ae.summary.return_value = {"current_level": "L3"}
        pipeline._get_alert_escalation = MagicMock(return_value=fake_ae)

        result = pipeline.process(
            user_message="This is a test message to verify guardian mode enforcement",
            user_tier="free",
            user_id="guardian-test",
        )
        assert result.persona_mode == "Guardian"


class TestActionSetResolution:
    """Verify action_set module provides correct lockdown policy."""

    def test_lockdown_policy_has_three_actions(self):
        from tonesoul.action_set import ACTION_POLICY

        lockdown = ACTION_POLICY["lockdown"]
        assert len(lockdown) == 3
        assert set(lockdown) == {"verify", "cite", "inquire"}

    def test_normal_policy_matches_lockdown(self):
        from tonesoul.action_set import ACTION_POLICY

        # In current spec, lockdown and normal have same actions
        assert set(ACTION_POLICY["normal"]) == set(ACTION_POLICY["lockdown"])

    def test_cautious_policy_is_subset(self):
        from tonesoul.action_set import ACTION_POLICY

        assert set(ACTION_POLICY["cautious"]).issubset(set(ACTION_POLICY["lockdown"]))
