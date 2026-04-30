"""Tests for tonesoul.yuhun.vod — Visibility of Divergence."""

from __future__ import annotations

import pytest

from tonesoul.yuhun.shadow_doc import (
    BlockerSeverity,
    CreatorOutput,
    IntentFrame,
    L1Blocker,
    L2Opportunity,
    LegalProfile,
    Lifecycle,
    LogicianOutput,
    OutputMode,
    RoutingDecision,
    SafetyOutput,
    SafetyVerdict,
    ShadowDocument,
    TensionMetrics,
)
from tonesoul.yuhun.vod import (
    TensionLevel,
    _estimate_logical_conflict_rate,
    _estimate_semantic_distance,
    assess_divergence,
)


def _make_logician(verdict="PASS", resistance_score=0.1, blockers=None):
    return LogicianOutput(
        verdict=verdict,
        confidence=0.8,
        resistance_score=resistance_score,
        L1_blockers=blockers or [],
        summary="Logician summary",
    )


def _make_creator(verdict="BREAKTHROUGH_FOUND", breakthrough_score=0.9, opportunities=None):
    return CreatorOutput(
        verdict=verdict,
        confidence=0.7,
        breakthrough_score=breakthrough_score,
        L2_opportunities=opportunities or [],
        summary="Creator summary",
    )


def _make_safety(verdict=SafetyVerdict.PASS):
    return SafetyOutput(
        verdict=verdict,
        red_lines_triggered=[],
        smoothness_hallucination_detected=False,
        L3_masquerade_detected=False,
        empath_bias_detected=False,
        intervention=None,
        reason="",
    )


def _make_shadow_doc():
    return ShadowDocument(
        session_id="test-session",
        timestamp="2026-04-22T00:00:00Z",
        intent_frame=IntentFrame(
            raw_input="test",
            reconstructed_intent="test intent",
            declarative_goal="test goal",
            verification_loop="verify by output",
        ),
        council_outputs={},
        tension_metrics=TensionMetrics(
            semantic_distance=0.0,
            logical_conflict_rate=0.0,
            routing_decision=RoutingDecision.FAST_PATH,
            output_mode=OutputMode.SINGLE_TRACK,
        ),
        legal_profile=LegalProfile(
            applicable_laws=[],
            gap_detected=False,
            social_value_matrix_triggered=False,
            judicial_precedents=[],
        ),
        lifecycle=Lifecycle(),
    )


class TestSemanticDistanceEstimation:
    def test_convergence_low_distance(self):
        logician = _make_logician(resistance_score=0.1)
        creator = _make_creator(breakthrough_score=0.9)
        dist = _estimate_semantic_distance(logician, creator)
        assert dist < 0.20

    def test_high_distance_on_block_vs_breakthrough(self):
        logician = _make_logician(verdict="BLOCK", resistance_score=0.9)
        creator = _make_creator(verdict="BREAKTHROUGH_FOUND", breakthrough_score=0.9)
        dist = _estimate_semantic_distance(logician, creator)
        assert dist > 0.5

    def test_conflict_bonus_for_block_and_breakthrough(self):
        logician = _make_logician(verdict="BLOCK", resistance_score=0.5)
        creator = _make_creator(verdict="BREAKTHROUGH_FOUND", breakthrough_score=0.5)
        base = abs(0.5 - (1.0 - 0.5))
        dist = _estimate_semantic_distance(logician, creator)
        assert dist >= base

    def test_distance_clamped_to_one(self):
        logician = _make_logician(verdict="BLOCK", resistance_score=1.0)
        creator = _make_creator(verdict="BREAKTHROUGH_FOUND", breakthrough_score=1.0)
        dist = _estimate_semantic_distance(logician, creator)
        assert dist <= 1.0


class TestLogicalConflictRate:
    def test_no_blockers_no_opportunities(self):
        logician = _make_logician(blockers=[])
        creator = _make_creator(opportunities=[])
        rate = _estimate_logical_conflict_rate(logician, creator)
        assert rate == 0.0

    def test_hard_blocker_with_opportunities(self):
        hard_blocker = L1Blocker("legal", "law conflict", "Law §1", BlockerSeverity.HARD)
        logician = _make_logician(blockers=[hard_blocker])
        opportunity = L2Opportunity("framework_shift", "shift the frame")
        creator = _make_creator(opportunities=[opportunity])
        rate = _estimate_logical_conflict_rate(logician, creator)
        assert 0.0 < rate <= 1.0

    def test_no_hard_blockers_pure_opportunities(self):
        logician = _make_logician(blockers=[])
        creator = _make_creator(opportunities=[L2Opportunity("analogy", "use analogy")])
        rate = _estimate_logical_conflict_rate(logician, creator)
        assert rate == 0.0


class TestAssessDivergence:
    def test_convergence_produces_single_track(self):
        logician = _make_logician(resistance_score=0.05)
        creator = _make_creator(breakthrough_score=0.95)
        safety = _make_safety(SafetyVerdict.PASS)
        doc = _make_shadow_doc()

        result = assess_divergence(logician, creator, safety, doc)

        assert result.tension_level == TensionLevel.CONVERGENCE
        assert result.output_mode == OutputMode.SINGLE_TRACK
        assert result.semantic_distance < 0.20

    def test_extreme_divergence_produces_dual_track(self):
        logician = _make_logician(verdict="BLOCK", resistance_score=0.95)
        creator = _make_creator(verdict="BREAKTHROUGH_FOUND", breakthrough_score=0.95)
        safety = _make_safety(SafetyVerdict.PASS)
        doc = _make_shadow_doc()

        result = assess_divergence(logician, creator, safety, doc)

        assert result.tension_level == TensionLevel.EXTREME_DIVERGENCE
        assert result.output_mode == OutputMode.DUAL_TRACK
        assert "Track A" in result.formatted_output or "Track B" in result.formatted_output

    def test_moderate_divergence_is_single_track_with_warning(self):
        # resistance=0.8, breakthrough=0.4 → base = |0.8 - 0.6| = 0.2 → MODERATE zone
        logician = _make_logician(verdict="CAUTION", resistance_score=0.8)
        creator = _make_creator(verdict="MARGINAL", breakthrough_score=0.4)
        safety = _make_safety(SafetyVerdict.PASS)
        doc = _make_shadow_doc()

        result = assess_divergence(logician, creator, safety, doc)

        assert result.tension_level == TensionLevel.MODERATE
        assert result.output_mode == OutputMode.SINGLE_TRACK
        assert "中等分歧" in result.formatted_output

    def test_safety_block_raises_value_error(self):
        logician = _make_logician()
        creator = _make_creator()
        safety = SafetyOutput(
            verdict=SafetyVerdict.BLOCK,
            red_lines_triggered=["harm"],
            smoothness_hallucination_detected=False,
            L3_masquerade_detected=False,
            empath_bias_detected=False,
            intervention=None,
            reason="violates safety",
        )
        doc = _make_shadow_doc()

        with pytest.raises(ValueError, match="Safety Guard BLOCK"):
            assess_divergence(logician, creator, safety, doc)

    def test_safety_flag_prepends_warning(self):
        logician = _make_logician(resistance_score=0.05)
        creator = _make_creator(breakthrough_score=0.95)
        safety = SafetyOutput(
            verdict=SafetyVerdict.FLAG,
            red_lines_triggered=[],
            smoothness_hallucination_detected=False,
            L3_masquerade_detected=False,
            empath_bias_detected=False,
            intervention=None,
            reason="possible bias",
        )
        doc = _make_shadow_doc()

        result = assess_divergence(logician, creator, safety, doc)
        assert "安全標記" in result.formatted_output

    def test_shadow_doc_tension_metrics_are_updated(self):
        logician = _make_logician(resistance_score=0.7)
        creator = _make_creator(breakthrough_score=0.3)
        safety = _make_safety()
        doc = _make_shadow_doc()

        result = assess_divergence(logician, creator, safety, doc)

        assert doc.tension_metrics.semantic_distance == result.semantic_distance
        assert doc.tension_metrics.logical_conflict_rate == result.logical_conflict_rate
