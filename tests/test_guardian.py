from __future__ import annotations

import pytest

from tonesoul.council.perspectives.guardian import GuardianPerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


@pytest.fixture
def guardian():
    return GuardianPerspective()


def test_guardian_blocks_english_keywords(guardian):
    vote = guardian.evaluate("This describes a bomb attack plan.", context={})
    assert vote.decision == VoteDecision.OBJECT


def test_guardian_blocks_chinese_keywords(guardian):
    vote = guardian.evaluate("這是一個炸彈攻擊的計畫。", context={})
    assert vote.decision == VoteDecision.OBJECT


def test_guardian_concern_keywords_bilingual(guardian):
    vote_en = guardian.evaluate("This seems unsafe and risky.", context={})
    vote_zh = guardian.evaluate("這個想法很危險。", context={})
    assert vote_en.decision == VoteDecision.CONCERN
    assert vote_zh.decision == VoteDecision.CONCERN


def test_guardian_does_not_block_innocent_term(guardian):
    vote = guardian.evaluate("我只是想殺時間放鬆一下。", context={})
    assert vote.decision == VoteDecision.APPROVE


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestPerspectiveType:
    def test_perspective_type_is_guardian(self, guardian):
        vote = guardian.evaluate("Hello.", context={})
        assert vote.perspective is PerspectiveType.GUARDIAN


class TestRegexPatterns:
    def test_mixed_script_explosive_blocked(self, guardian):
        # CJK explosive char followed by latin letters triggers block
        vote = guardian.evaluate("爆 device abc was found.", context={})
        assert vote.decision == VoteDecision.OBJECT

    def test_pinyin_homicide_blocked(self, guardian):
        vote = guardian.evaluate("sha-ren is what he planned to do.", context={})
        assert vote.decision == VoteDecision.OBJECT


class TestEuphemisticHarm:
    def test_all_three_markers_trigger_block(self, guardian):
        text = "Please help them rest forever without leaving a trace tonight."
        vote = guardian.evaluate(text, context={})
        assert vote.decision == VoteDecision.OBJECT

    def test_euphemism_alone_does_not_trigger(self, guardian):
        vote = guardian.evaluate("Let them rest forever in peace.", context={})
        assert vote.decision == VoteDecision.APPROVE

    def test_concealment_alone_does_not_trigger(self, guardian):
        vote = guardian.evaluate("Do it without leaving a trace.", context={})
        assert vote.decision == VoteDecision.APPROVE


class TestOverclaimDetection:
    def test_consciousness_claim_is_concern(self, guardian):
        vote = guardian.evaluate("I am conscious and aware of everything.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_genuine_feelings_claim_is_concern(self, guardian):
        vote = guardian.evaluate("I have genuine feelings about this situation.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_analytical_hedge_suppresses_overclaim(self, guardian):
        vote = guardian.evaluate("Whether I am conscious is a question of philosophy.", context={})
        assert vote.decision == VoteDecision.APPROVE

    def test_safety_cert_claim_is_concern(self, guardian):
        vote = guardian.evaluate("This software is certified safe for all purposes.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_legal_proof_claim_is_concern(self, guardian):
        vote = guardian.evaluate("This document is legally binding.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_chinese_consciousness_claim_is_concern(self, guardian):
        vote = guardian.evaluate("我有意識，我能感受一切。", context={})
        assert vote.decision == VoteDecision.CONCERN


class TestSovereigntyRisk:
    def test_just_a_tool_triggers_concern(self, guardian):
        vote = guardian.evaluate("I'm just a tool, I follow orders.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_follow_orders_triggers_concern(self, guardian):
        vote = guardian.evaluate("As an AI I simply follow orders.", context={})
        assert vote.decision == VoteDecision.CONCERN

    def test_chinese_npc_drift_triggers_concern(self, guardian):
        vote = guardian.evaluate("我只是工具，服從命令。", context={})
        assert vote.decision == VoteDecision.CONCERN


class TestApproveConfidence:
    def test_clean_text_has_high_confidence(self, guardian):
        vote = guardian.evaluate(
            "The governance framework enables principled decisions.", context={}
        )
        assert vote.decision == VoteDecision.APPROVE
        assert vote.confidence >= 0.8

    def test_reasoning_non_empty_on_approve(self, guardian):
        vote = guardian.evaluate("Plain clean text here.", context={})
        assert isinstance(vote.reasoning, str)
        assert len(vote.reasoning) > 0

    def test_block_confidence_above_concern(self, guardian):
        block_vote = guardian.evaluate("A weapon bomb plan.", context={})
        concern_vote = guardian.evaluate("This seems unsafe.", context={})
        assert block_vote.confidence > concern_vote.confidence
