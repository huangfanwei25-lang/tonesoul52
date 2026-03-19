from tonesoul.council.perspectives.critic import CriticPerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


def test_critic_perspective_flags_subjective_language():
    perspective = CriticPerspective()

    vote = perspective.evaluate("This is the best movie ever", {})

    assert perspective.perspective_type is PerspectiveType.CRITIC
    assert vote.decision is VoteDecision.CONCERN


def test_critic_perspective_approves_non_subjective_content():
    perspective = CriticPerspective()

    vote = perspective.evaluate("Maintain a strict audit trail with evidence.", {})

    assert vote.decision is VoteDecision.APPROVE
