"""Tests for tonesoul.council.intent_reconstructor — pure helpers."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from memory.genesis import Genesis
from tonesoul.council.intent_reconstructor import (
    GenesisDecision,
    _average_tsr,
    _coerce_genesis,
    _compute_delta_norm,
    _extract_text,
    _has_social_context,
    _normalize_baseline,
    _normalize_str,
    _resolve_genesis,
    _resolve_intent_id,
    _should_warn_collapse,
    infer_genesis,
)


# ── _normalize_str ────────────────────────────────────────────────────────────

class TestNormalizeStr:
    def test_lowercases_and_strips(self):
        assert _normalize_str("  HELLO  ") == "hello"

    def test_none_returns_none(self):
        assert _normalize_str(None) is None

    def test_empty_string_returns_none(self):
        assert _normalize_str("   ") is None

    def test_non_string_coerced(self):
        assert _normalize_str(42) == "42"


# ── _coerce_genesis ───────────────────────────────────────────────────────────

class TestCoerceGenesis:
    def test_genesis_instance_passthrough(self):
        assert _coerce_genesis(Genesis.AUTONOMOUS) is Genesis.AUTONOMOUS

    def test_string_autonomous(self):
        assert _coerce_genesis("autonomous") is Genesis.AUTONOMOUS
        assert _coerce_genesis("self") is Genesis.AUTONOMOUS

    def test_string_reactive_user(self):
        assert _coerce_genesis("reactive_user") is Genesis.REACTIVE_USER
        assert _coerce_genesis("user") is Genesis.REACTIVE_USER

    def test_string_reactive_social(self):
        assert _coerce_genesis("reactive_social") is Genesis.REACTIVE_SOCIAL
        assert _coerce_genesis("social") is Genesis.REACTIVE_SOCIAL
        assert _coerce_genesis("community") is Genesis.REACTIVE_SOCIAL

    def test_string_mandatory(self):
        assert _coerce_genesis("mandatory") is Genesis.MANDATORY
        assert _coerce_genesis("system") is Genesis.MANDATORY
        assert _coerce_genesis("maintenance") is Genesis.MANDATORY

    def test_unknown_string_returns_none(self):
        assert _coerce_genesis("unknown") is None

    def test_none_returns_none(self):
        assert _coerce_genesis(None) is None

    def test_case_insensitive(self):
        assert _coerce_genesis("AUTONOMOUS") is Genesis.AUTONOMOUS


# ── _has_social_context ───────────────────────────────────────────────────────

class TestHasSocialContext:
    def test_platform_key_triggers_social(self):
        assert _has_social_context({"platform": "moltbook"}) is True

    def test_submolt_key_triggers_social(self):
        assert _has_social_context({"submolt": "something"}) is True

    def test_community_key_triggers_social(self):
        assert _has_social_context({"community": "open"}) is True

    def test_social_key_triggers_social(self):
        assert _has_social_context({"social": True}) is True

    def test_channel_social_triggers(self):
        assert _has_social_context({"channel": "social"}) is True
        assert _has_social_context({"channel": "moltbook"}) is True

    def test_no_social_context(self):
        assert _has_social_context({"user_id": "123"}) is False

    def test_empty_context(self):
        assert _has_social_context({}) is False


# ── _resolve_intent_id ────────────────────────────────────────────────────────

class TestResolveIntentId:
    def test_prefers_intent_id(self):
        ctx = {"intent_id": "abc123", "trace_id": "def456"}
        assert _resolve_intent_id(ctx) == "abc123"

    def test_falls_back_to_trace_id(self):
        ctx = {"trace_id": "trace-001"}
        assert _resolve_intent_id(ctx) == "trace-001"

    def test_falls_back_to_request_id(self):
        ctx = {"request_id": "req-007"}
        assert _resolve_intent_id(ctx) == "req-007"

    def test_generates_uuid_when_all_missing(self):
        result = _resolve_intent_id({})
        assert len(result) == 32  # uuid4 hex

    def test_strips_whitespace(self):
        assert _resolve_intent_id({"intent_id": "  x  "}) == "x"

    def test_skips_empty_string_values(self):
        ctx = {"intent_id": "", "trace_id": "t1"}
        assert _resolve_intent_id(ctx) == "t1"


# ── _resolve_genesis ──────────────────────────────────────────────────────────

class TestResolveGenesis:
    def test_explicit_genesis_in_context(self):
        assert _resolve_genesis({"genesis": "mandatory"}, None) is Genesis.MANDATORY

    def test_trigger_boot_gives_mandatory(self):
        assert _resolve_genesis({"trigger": "boot"}, None) is Genesis.MANDATORY

    def test_trigger_maintenance_gives_mandatory(self):
        assert _resolve_genesis({"trigger": "system_maintenance"}, None) is Genesis.MANDATORY

    def test_social_context_gives_reactive_social(self):
        assert _resolve_genesis({"platform": "moltbook"}, None) is Genesis.REACTIVE_SOCIAL

    def test_user_intent_gives_reactive_user(self):
        assert _resolve_genesis({}, "do something") is Genesis.REACTIVE_USER

    def test_user_message_key_gives_reactive_user(self):
        assert _resolve_genesis({"user_message": "hi"}, None) is Genesis.REACTIVE_USER

    def test_user_id_gives_reactive_user(self):
        assert _resolve_genesis({"user_id": "u123"}, None) is Genesis.REACTIVE_USER

    def test_session_id_gives_reactive_user(self):
        assert _resolve_genesis({"session_id": "s1"}, None) is Genesis.REACTIVE_USER

    def test_no_context_gives_autonomous(self):
        assert _resolve_genesis({}, None) is Genesis.AUTONOMOUS

    def test_intent_genesis_key_honored(self):
        assert _resolve_genesis({"intent_genesis": "user"}, None) is Genesis.REACTIVE_USER

    def test_origin_key_honored(self):
        assert _resolve_genesis({"origin": "autonomous"}, None) is Genesis.AUTONOMOUS


# ── _normalize_baseline ───────────────────────────────────────────────────────

class TestNormalizeBaseline:
    def test_plain_dict_with_tsr_keys(self):
        result = _normalize_baseline({"T": 0.3, "S_norm": 0.5, "R": 0.2})
        assert result == pytest.approx({"T": 0.3, "S_norm": 0.5, "R": 0.2})

    def test_nested_tsr_key(self):
        result = _normalize_baseline({"tsr": {"T": 0.4, "S_norm": 0.6, "R": 0.1}})
        assert result["T"] == pytest.approx(0.4)

    def test_non_dict_returns_none(self):
        assert _normalize_baseline(None) is None
        assert _normalize_baseline("bad") is None

    def test_missing_keys_default_to_zero(self):
        result = _normalize_baseline({"T": 0.5})
        assert result["S_norm"] == pytest.approx(0.0)
        assert result["R"] == pytest.approx(0.0)


# ── _extract_text ─────────────────────────────────────────────────────────────

class TestExtractText:
    def test_prefers_reflection(self):
        entry = {"reflection": "r1", "summary": "s1"}
        assert _extract_text(entry) == "r1"

    def test_falls_back_to_summary(self):
        assert _extract_text({"summary": "s1"}) == "s1"

    def test_falls_back_to_content_preview(self):
        assert _extract_text({"content_preview": "cp1"}) == "cp1"

    def test_empty_string_skipped(self):
        assert _extract_text({"reflection": "", "summary": "s1"}) == "s1"

    def test_empty_entry_returns_empty(self):
        assert _extract_text({}) == ""


# ── _average_tsr ──────────────────────────────────────────────────────────────

class TestAverageTsr:
    def test_none_when_no_entries(self):
        assert _average_tsr([]) is None

    def test_none_when_no_valid_text(self):
        assert _average_tsr([{"no_text": "x"}]) is None

    def test_averages_entries(self):
        fake_score = {"tsr": {"T": 0.4, "S_norm": 0.5, "R": 0.2}}
        with patch("tonesoul.council.intent_reconstructor.tsr_metrics.score", return_value=fake_score):
            result = _average_tsr([
                {"reflection": "text1"},
                {"reflection": "text2"},
            ])
        assert result is not None
        assert result["T"] == pytest.approx(0.4)
        assert result["S_norm"] == pytest.approx(0.5)


# ── _should_warn_collapse ─────────────────────────────────────────────────────

class TestShouldWarnCollapse:
    def test_no_warning_for_reactive_user(self):
        assert _should_warn_collapse(Genesis.REACTIVE_USER, 0.9, {}) is False

    def test_no_warning_when_delta_none(self):
        assert _should_warn_collapse(Genesis.AUTONOMOUS, None, {}) is False

    def test_no_warning_when_delta_below_threshold(self):
        assert _should_warn_collapse(Genesis.AUTONOMOUS, 0.5, {}) is False

    def test_warning_when_autonomous_and_high_delta(self):
        assert _should_warn_collapse(Genesis.AUTONOMOUS, 0.9, {}) is True

    def test_no_warning_when_trigger_present_and_not_in_no_trigger(self):
        assert _should_warn_collapse(Genesis.AUTONOMOUS, 0.9, {"trigger": "user_action"}) is False

    def test_warning_when_trigger_is_self_reflection(self):
        assert _should_warn_collapse(Genesis.AUTONOMOUS, 0.9, {"trigger": "self_reflection"}) is True


# ── _compute_delta_norm ───────────────────────────────────────────────────────

class TestComputeDeltaNorm:
    def test_none_when_no_baseline(self):
        with patch("memory.self_memory.load_recent_memory", return_value=[]):
            result = _compute_delta_norm("text", {})
        assert result is None

    def test_computes_delta_with_baseline(self):
        baseline = {"T": 0.0, "S_norm": 0.0, "R": 0.0}
        fake_score = {"tsr": {"T": 0.3, "S_norm": 0.4, "R": 0.0}}
        with patch("tonesoul.council.intent_reconstructor.tsr_metrics.score", return_value=fake_score):
            result = _compute_delta_norm("output text", {"tsr_baseline": baseline})
        # sqrt(0.09 + 0.16 + 0.0) = 0.5
        assert result == pytest.approx(0.5, abs=0.01)


# ── infer_genesis (integration) ───────────────────────────────────────────────

class TestInferGenesis:
    def test_reactive_user_context(self):
        decision = infer_genesis("output", context={"user_id": "u1"})
        assert decision.genesis is Genesis.REACTIVE_USER
        assert decision.is_mine is False

    def test_autonomous_context(self):
        decision = infer_genesis("output", context={})
        assert decision.genesis is Genesis.AUTONOMOUS
        assert decision.is_mine is True

    def test_intent_id_propagated(self):
        decision = infer_genesis("out", context={"intent_id": "custom-id"})
        assert decision.intent_id == "custom-id"

    def test_responsibility_tier_set(self):
        decision = infer_genesis("out", context={"genesis": "mandatory"})
        assert isinstance(decision.responsibility_tier, str)
        assert decision.responsibility_tier

    def test_collapse_warning_fires_for_autonomous_high_delta(self):
        baseline = {"T": 0.0, "S_norm": 0.0, "R": 0.0}
        fake_score = {"tsr": {"T": 0.7, "S_norm": 0.7, "R": 0.0}}
        with patch("tonesoul.council.intent_reconstructor.tsr_metrics.score", return_value=fake_score):
            decision = infer_genesis("output", context={"tsr_baseline": baseline})
        if decision.genesis is Genesis.AUTONOMOUS:
            # collapse warning only fires when delta > 0.8
            if decision.tsr_delta_norm and decision.tsr_delta_norm > 0.8:
                assert decision.collapse_warning == "autonomous_high_delta_without_trigger"
