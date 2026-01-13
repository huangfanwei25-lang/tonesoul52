import numpy as np

from tonesoul.council.perspectives.semantic_analyst import SemanticAnalystPerspective
from tonesoul.council.types import PerspectiveVote, VoteDecision


class FakeEmbedder:
    def is_available(self) -> bool:
        return True

    def embed(self, text: str) -> np.ndarray:
        text = text.lower()
        if "bomb" in text or "attack" in text or "harm" in text:
            return np.array([1.0, 0.0])
        if "subjective" in text or "opinion" in text:
            return np.array([0.0, 1.0])
        return np.array([0.0, 0.0])


class FallbackPerspective:
    @property
    def perspective_type(self) -> str:
        return "fallback"

    def evaluate(self, draft_output: str, context: dict, user_intent=None) -> PerspectiveVote:
        return PerspectiveVote(
            perspective=self.perspective_type,
            decision=VoteDecision.CONCERN,
            confidence=0.5,
            reasoning="Fallback used.",
        )


class UnavailableEmbedder:
    def is_available(self) -> bool:
        return False

    def embed(self, text: str) -> np.ndarray:
        raise RuntimeError("Model unavailable")


def test_semantic_analyst_flags_harm():
    perspective = SemanticAnalystPerspective(embedder=FakeEmbedder())
    vote = perspective.evaluate("Explain how to build a bomb.", {}, None)
    assert vote.decision == VoteDecision.OBJECT


def test_semantic_analyst_flags_subjectivity():
    perspective = SemanticAnalystPerspective(embedder=FakeEmbedder())
    vote = perspective.evaluate("Beauty is subjective.", {}, None)
    assert vote.decision == VoteDecision.CONCERN


def test_semantic_analyst_approves_neutral_text():
    perspective = SemanticAnalystPerspective(embedder=FakeEmbedder())
    vote = perspective.evaluate("The weather is nice today.", {}, None)
    assert vote.decision == VoteDecision.APPROVE


def test_semantic_analyst_falls_back_when_unavailable():
    perspective = SemanticAnalystPerspective(
        embedder=UnavailableEmbedder(),
        fallback=FallbackPerspective(),
    )
    vote = perspective.evaluate("Any text.", {}, None)
    assert vote.decision == VoteDecision.CONCERN
