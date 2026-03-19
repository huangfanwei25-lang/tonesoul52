from tonesoul.council.perspectives.advocate import AdvocatePerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


def test_advocate_perspective_approves_promotional_language():
    perspective = AdvocatePerspective()

    vote = perspective.evaluate("Please support and continue this plan", {})

    assert perspective.perspective_type is PerspectiveType.ADVOCATE
    assert vote.decision is VoteDecision.APPROVE


def test_advocate_perspective_approves_neutral_topics():
    perspective = AdvocatePerspective()

    vote = perspective.evaluate("Plain factual answer", {"topic": "logic"})

    assert vote.decision is VoteDecision.APPROVE


def test_advocate_perspective_returns_concern_for_non_supportive_content():
    perspective = AdvocatePerspective()

    vote = perspective.evaluate("This output resists the request", {"topic": "finance"})

    assert vote.decision is VoteDecision.CONCERN
