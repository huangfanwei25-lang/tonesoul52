from __future__ import annotations

import hashlib
from typing import Protocol

import numpy as np


class BaseEmbedding(Protocol):
    """Embedding interface for OpenClaw memory backends."""

    def encode(self, text: str) -> np.ndarray: ...


class SentenceTransformerEmbedding:
    """Default local embedding wrapper using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Install it or use HashEmbedding/MockEmbedding."
            ) from exc
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> np.ndarray:
        vec = np.asarray(self.model.encode(text), dtype=np.float32)
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


class HashEmbedding:
    """Deterministic offline embedding for no-network and test environments."""

    def __init__(self, dimension: int = 384):
        self.dimension = int(dimension)

    def encode(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension, dtype=np.float32)
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


class MockEmbedding:
    """Zero-vector embedding for deterministic tests."""

    def __init__(self, dimension: int = 384):
        self.dimension = int(dimension)

    def encode(self, text: str) -> np.ndarray:
        return np.zeros(self.dimension, dtype=np.float32)


__all__ = [
    "BaseEmbedding",
    "SentenceTransformerEmbedding",
    "HashEmbedding",
    "MockEmbedding",
]
