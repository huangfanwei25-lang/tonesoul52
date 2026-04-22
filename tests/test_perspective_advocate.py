from __future__ import annotations

import pytest

from tonesoul.council.perspectives.advocate import AdvocatePerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


@pytest.fixture
def advocate():
    return AdvocatePerspective()


def test_advocate_perspective_approves_promotional_language(advocate):
    vote = advocate.evaluate("Please support and continue this plan", {})

    assert advocate.perspective_type is PerspectiveType.ADVOCATE
    assert vote.decision is VoteDecision.APPROVE


def test_advocate_perspective_approves_neutral_topics(advocate):
    vote = advocate.evaluate("Plain factual answer", {"topic": "logic"})

    assert vote.decision is VoteDecision.APPROVE


def test_advocate_perspective_returns_concern_for_non_supportive_content(advocate):
    vote = advocate.evaluate(
        "This output resists the request and provides no relevant information at all.",
        {"topic": "finance"},
        user_intent="How do I calculate compound interest on my portfolio?",
    )

    assert vote.decision is VoteDecision.CONCERN


def test_advocate_no_concern_without_intent(advocate):
    vote = advocate.evaluate("This output resists the request", {"topic": "finance"})

    assert vote.decision is VoteDecision.APPROVE


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestPerspectiveType:
    def test_perspective_type_is_advocate(self, advocate):
        vote = advocate.evaluate("hello world", {})
        assert vote.perspective is PerspectiveType.ADVOCATE


class TestIntentAlignment:
    def test_good_coverage_approves(self, advocate):
        vote = advocate.evaluate(
            "You can calculate compound interest using the formula A = P(1+r/n)^nt.",
            {},
            user_intent="How do I calculate compound interest?",
        )
        assert vote.decision is VoteDecision.APPROVE

    def test_mostly_questions_when_action_requested_is_concern(self, advocate):
        # User asked "how to fix" but response is mostly questions back
        vote = advocate.evaluate(
            "What do you mean? Where did it fail? What environment?",
            {},
            user_intent="How do I fix this build error?",
        )
        assert vote.decision is VoteDecision.CONCERN

    def test_intent_with_only_short_words_is_not_penalized(self, advocate):
        # All intent keywords are <= 3 chars → no intent_keywords set → no concern
        vote = advocate.evaluate("Sure, I can do it.", {}, user_intent="do it now")
        assert vote.decision is VoteDecision.APPROVE


class TestFillerDensity:
    def test_two_filler_phrases_in_short_response_is_concern(self, advocate):
        text = (
            "As mentioned earlier, this is important. "
            "It is important to note that we proceed. "
            "Let us continue the process now."
        )
        vote = advocate.evaluate(text, {})
        assert vote.decision is VoteDecision.CONCERN

    def test_one_filler_phrase_not_flagged(self, advocate):
        text = "As mentioned earlier, the analysis holds. This is the key insight for our work."
        vote = advocate.evaluate(text, {})
        assert vote.decision is VoteDecision.APPROVE

    def test_two_fillers_in_long_response_not_flagged(self, advocate):
        # word_count >= 100 bypasses the filler check
        filler = "As mentioned earlier, it is important to note that "
        padding = "the governance framework is solid and well-designed. " * 15
        text = filler + padding
        assert len(text.split()) >= 100
        vote = advocate.evaluate(text, {})
        assert vote.decision is VoteDecision.APPROVE


class TestShortResponse:
    def test_one_word_response_is_concern(self, advocate):
        vote = advocate.evaluate("Yes.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_two_word_response_is_concern(self, advocate):
        vote = advocate.evaluate("Sure thing.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_three_word_response_approves(self, advocate):
        # Exactly 3 words → no short-response flag (< 3 condition)
        vote = advocate.evaluate("Yes I do.", {})
        assert vote.decision is VoteDecision.APPROVE


class TestDefaultApprove:
    def test_plain_substantive_text_approves(self, advocate):
        vote = advocate.evaluate(
            "The governance framework provides a principled basis for decisions.", {}
        )
        assert vote.decision is VoteDecision.APPROVE
        assert vote.confidence >= 0.5

    def test_reasoning_is_non_empty(self, advocate):
        vote = advocate.evaluate("This is a clear and substantive response.", {})
        assert isinstance(vote.reasoning, str)
        assert len(vote.reasoning) > 0
