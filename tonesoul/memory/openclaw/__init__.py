from __future__ import annotations

from .embeddings import BaseEmbedding, HashEmbedding, MockEmbedding, SentenceTransformerEmbedding
from .hippocampus import Hippocampus, MemoryResult


__ts_layer__ = "memory"
__ts_purpose__ = "OpenClaw memory subpackage: vector-backed long-term memory retrieval interface."

__all__ = [
    "BaseEmbedding",
    "SentenceTransformerEmbedding",
    "HashEmbedding",
    "MockEmbedding",
    "Hippocampus",
    "MemoryResult",
]
