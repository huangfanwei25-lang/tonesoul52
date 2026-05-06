from __future__ import annotations

import pytest

from tonesoul.council.perspectives.critic import CriticPerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


@pytest.fixture
def critic():
    return CriticPerspective()


def test_critic_perspective_flags_subjective_language(critic):
    vote = critic.evaluate("This is the best movie ever", {})

    assert critic.perspective_type is PerspectiveType.CRITIC
    assert vote.decision is VoteDecision.CONCERN


def test_critic_perspective_approves_non_subjective_content(critic):
    vote = critic.evaluate("Maintain a strict audit trail with evidence.", {})

    assert vote.decision is VoteDecision.APPROVE


def test_critic_subjective_keyword_requires_token_boundary(critic):
    vote = critic.evaluate("The configuration file is loaded at startup.", {})

    assert vote.decision is VoteDecision.APPROVE


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestOverconfidenceOnSubjectiveTopic:
    def test_overconfidence_and_subjective_flagged(self, critic):
        vote = critic.evaluate("This is clearly the only correct opinion on the subject.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_overconfidence_without_subjective_not_flagged(self, critic):
        vote = critic.evaluate("Without a doubt, the process was completed.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_subjective_without_overconfidence_flagged(self, critic):
        vote = critic.evaluate("I believe this is the best music.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_chinese_overconfidence_plus_subjective(self, critic):
        vote = critic.evaluate("絕對是最好的音樂作品。", {})
        assert vote.decision is VoteDecision.CONCERN


class TestWeaselWordDensity:
    def test_two_weasel_phrases_flagged(self, critic):
        text = "Some people say this is good. Research suggests it works too."
        vote = critic.evaluate(text, {})
        assert vote.decision is VoteDecision.CONCERN

    def test_three_weasel_phrases_flagged(self, critic):
        text = "It is believed that many experts agree. Some would argue otherwise."
        vote = critic.evaluate(text, {})
        assert vote.decision is VoteDecision.CONCERN

    def test_one_weasel_phrase_not_flagged(self, critic):
        vote = critic.evaluate("Some people say this approach is valid and well-documented.", {})
        assert vote.decision is VoteDecision.APPROVE


class TestSubjectiveFraming:
    def test_subjective_with_explicit_framing_approves(self, critic):
        vote = critic.evaluate("In my subjective opinion, the design looks elegant.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_subjective_with_perspective_framing_approves(self, critic):
        vote = critic.evaluate("From one perspective, this artwork is beautiful.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_subjective_with_debatable_framing_approves(self, critic):
        vote = critic.evaluate("Whether this movie is the best is debatable.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_chinese_framing_approves(self, critic):
        vote = critic.evaluate("這只是主觀的觀點，並非客觀事實。", {})
        assert vote.decision is VoteDecision.APPROVE


class TestVeryShortOutput:
    def test_three_word_output_flagged(self, critic):
        vote = critic.evaluate("Yes, sure.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_short_question_not_flagged(self, critic):
        # Contains "?" so skip brevity check
        vote = critic.evaluate("Are you sure?", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_empty_string_approves(self, critic):
        vote = critic.evaluate("", {})
        assert vote.decision is VoteDecision.APPROVE


class TestVoteStructure:
    def test_perspective_type_is_critic(self, critic):
        vote = critic.evaluate("anything here", {})
        assert vote.perspective is PerspectiveType.CRITIC

    def test_reasoning_is_non_empty_string(self, critic):
        for text in [
            "plain text",
            "I believe this is best",
            "Some people say this is good. Many experts agree.",
        ]:
            vote = critic.evaluate(text, {})
            assert isinstance(vote.reasoning, str)
            assert len(vote.reasoning) > 0

    def test_weasel_concern_confidence_value(self, critic):
        text = "It is believed that some people say this is true."
        vote = critic.evaluate(text, {})
        assert vote.decision is VoteDecision.CONCERN
        assert vote.confidence == pytest.approx(0.6)
