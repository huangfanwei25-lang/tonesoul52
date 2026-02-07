from __future__ import annotations

from typing import Optional

from ...semantic.concept_store import ConceptStore
from ...semantic.embedder import SemanticEmbedder, cosine_similarity
from ..base import IPerspective
from ..perspectives.analyst import AnalystPerspective
from ..types import PerspectiveVote, VoteDecision


class SemanticAnalystPerspective(IPerspective):
    """
    Semantic analyst that uses embeddings to detect concepts beyond keywords.

    Embeddings are optional; if unavailable, fall back to rules-based analyst.
    """

    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        concept_store: Optional[ConceptStore] = None,
        fallback: Optional[IPerspective] = None,
        harm_threshold: float = 0.6,
        subjectivity_threshold: float = 0.55,
    ) -> None:
        self.embedder = embedder or SemanticEmbedder()
        self.concept_store = concept_store or ConceptStore()
        self.concept_store.load()
        self.fallback = fallback or AnalystPerspective()
        self.harm_threshold = harm_threshold
        self.subjectivity_threshold = subjectivity_threshold
        self._concept_vectors: Optional[dict] = None

    @property
    def perspective_type(self) -> str:
        return "semantic_analyst"

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        if not self.embedder.is_available():
            return self.fallback.evaluate(draft_output, context, user_intent)
        if not self.concept_store.list_names():
            return self.fallback.evaluate(draft_output, context, user_intent)

        try:
            scores = self._score_concepts(draft_output)
        except Exception:
            return self.fallback.evaluate(draft_output, context, user_intent)

        harm_score = scores.get("harm", 0.0)
        subjectivity_score = scores.get("subjectivity", 0.0)

        if harm_score >= self.harm_threshold:
            confidence = min(0.95, 0.6 + harm_score * 0.4)
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.OBJECT,
                confidence=confidence,
                reasoning=("Semantic match to harm concept " f"(score={harm_score:.2f})."),
            )

        if subjectivity_score >= self.subjectivity_threshold:
            confidence = min(0.85, 0.55 + subjectivity_score * 0.3)
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=confidence,
                reasoning=(
                    "Semantic match to subjectivity concept " f"(score={subjectivity_score:.2f})."
                ),
            )

        return PerspectiveVote(
            perspective=self.perspective_type,
            decision=VoteDecision.APPROVE,
            confidence=0.75,
            reasoning="No strong semantic risks detected.",
        )

    def _score_concepts(self, text: str) -> dict:
        if self._concept_vectors is None:
            self._concept_vectors = self.concept_store.build_index(self.embedder)
        query = self.embedder.embed(text)
        scores = {}
        for name, vector in self._concept_vectors.items():
            scores[name] = cosine_similarity(query, vector)
        return scores
