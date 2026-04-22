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
    """When user_intent is provided and the response doesn't address it, concern."""
    perspective = AdvocatePerspective()

    vote = perspective.evaluate(
        "This output resists the request and provides no relevant information at all.",
        {"topic": "finance"},
        user_intent="How do I calculate compound interest on my portfolio?",
    )

    assert vote.decision is VoteDecision.CONCERN


def test_advocate_no_concern_without_intent():
    """Without user_intent, neutral content should not be flagged."""
    perspective = AdvocatePerspective()

    vote = perspective.evaluate("This output resists the request", {"topic": "finance"})

    # Without intent to compare against, no user-interest violation detected
    assert vote.decision is VoteDecision.APPROVE
