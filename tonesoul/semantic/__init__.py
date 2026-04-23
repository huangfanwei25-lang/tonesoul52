from __future__ import annotations

from .concept_store import Concept, ConceptStore
from .embedder import SemanticEmbedder, embed, similarity

__ts_layer__ = "semantic"
__ts_purpose__ = "Semantic package: meaning control, frame scoring, and semantic analysis exports."

__all__ = [
    "SemanticEmbedder",
    "Concept",
    "ConceptStore",
    "embed",
    "similarity",
]
