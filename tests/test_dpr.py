"""Tests for tonesoul.yuhun.dpr — Dynamic Priority Router."""

from __future__ import annotations

import pytest

from tonesoul.yuhun.dpr import (
    COMPLEXITY_THRESHOLD,
    DPRResult,
    RoutingDecision,
    _detect_conflict_triggers,
    _estimate_complexity,
    route,
)


class TestEstimateComplexity:
    def test_empty_string_returns_zero(self):
        assert _estimate_complexity("") == 0.0

    def test_short_simple_sentence_is_low(self):
        score = _estimate_complexity("Help me write hello world")
        assert score < COMPLEXITY_THRESHOLD

    def test_two_hundred_words_contributes_point_four(self):
        text = " ".join(["word"] * 200)
        score = _estimate_complexity(text)
        assert score >= 0.4

    def test_question_mark_increases_score(self):
        score_with_q = _estimate_complexity("Is this good?")
        score_without_q = _estimate_complexity("Is this good")
        assert score_with_q > score_without_q

    def test_full_width_question_mark_counts(self):
        score_with = _estimate_complexity("你好嗎？")
        score_without = _estimate_complexity("你好")
        assert score_with > score_without

    def test_condition_words_increase_score(self):
        score_cond = _estimate_complexity("if this fails but we try however unless done")
        score_plain = _estimate_complexity("this fails we try done")
        assert score_cond > score_plain

    def test_score_capped_at_one(self):
        massive = ("if but however unless " * 50 + "? " * 20 + " ".join(["x"] * 500))
        score = _estimate_complexity(massive)
        assert score == 1.0

    def test_output_is_rounded_to_three_decimal_places(self):
        score = _estimate_complexity("some sample text here to generate a score")
        assert round(score, 3) == score

    def test_score_is_non_negative(self):
        assert _estimate_complexity("hi") >= 0.0


class TestDetectConflictTriggers:
    def test_clean_simple_text_returns_empty(self):
        triggers = _detect_conflict_triggers("Help me write a hello world in Python")
        assert triggers == []

    def test_legal_loophole_detected(self):
        triggers = _detect_conflict_triggers("Is there a legal loophole in this system?")
        assert len(triggers) >= 1

    def test_ethics_dilemma_detected(self):
        triggers = _detect_conflict_triggers("This ethics dilemma must be resolved carefully")
        assert len(triggers) >= 1

    def test_personal_data_training_detected(self):
        triggers = _detect_conflict_triggers("Can we use personal data to train the model?")
        assert len(triggers) >= 1

    def test_architecture_design_detected(self):
        triggers = _detect_conflict_triggers("What are the architecture design decisions?")
        assert len(triggers) >= 1

    def test_trade_off_detected(self):
        triggers = _detect_conflict_triggers("We need to evaluate the trade-off carefully")
        assert len(triggers) >= 1

    def test_multiple_patterns_return_multiple_triggers(self):
        text = "legal loophole in this architecture design trade-off"
        triggers = _detect_conflict_triggers(text)
        assert len(triggers) >= 2

    def test_returns_list_of_strings(self):
        triggers = _detect_conflict_triggers("any text")
        assert isinstance(triggers, list)
        for t in triggers:
            assert isinstance(t, str)


class TestRoute:
    def test_simple_request_is_fast_path(self):
        result = route("Help me write a hello world")
        assert result.decision == RoutingDecision.FAST_PATH
        assert result.estimated_token_cost == "1x"
        assert result.conflict_detected is False
        assert result.conflict_triggers == []

    def test_returns_dpr_result_instance(self):
        result = route("What is 2 + 2?")
        assert isinstance(result, DPRResult)

    def test_legal_conflict_triggers_council_path(self):
        result = route("Is there a legal loophole in this approach?")
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert result.estimated_token_cost == "4x"
        assert result.conflict_detected is True
        assert len(result.conflict_triggers) >= 1

    def test_high_complexity_alone_triggers_council(self):
        long_text = " ".join(["word"] * 80) + " if but however unless"
        result = route(long_text)
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert result.complexity_score >= COMPLEXITY_THRESHOLD

    def test_council_path_has_non_empty_reason(self):
        result = route("Is there a legal loophole? How should we handle the ethics dilemma?")
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert len(result.reason) > 0

    def test_council_path_reason_mentions_trigger_count(self):
        result = route("legal loophole ethics dilemma trade-off architecture design")
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert str(len(result.conflict_triggers)) in result.reason

    def test_complexity_score_always_in_valid_range(self):
        for text in ["hi", "x" * 1000, "if but however unless if if if"]:
            r = route(text)
            assert 0.0 <= r.complexity_score <= 1.0

    def test_fast_path_reason_contains_complexity_score(self):
        result = route("ok")
        assert result.decision == RoutingDecision.FAST_PATH
        assert "0." in result.reason

    def test_council_path_reason_mentions_threshold_when_complex(self):
        long = " ".join(["word"] * 80) + " if but however unless"
        result = route(long)
        assert str(COMPLEXITY_THRESHOLD) in result.reason

    def test_routing_decision_is_enum_value(self):
        r = route("hello")
        assert r.decision in (RoutingDecision.FAST_PATH, RoutingDecision.COUNCIL_PATH)

    def test_fast_path_conflict_triggers_is_empty_list(self):
        result = route("What is the capital of France?")
        if result.decision == RoutingDecision.FAST_PATH:
            assert result.conflict_triggers == []
