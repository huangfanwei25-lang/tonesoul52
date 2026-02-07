from __future__ import annotations

from typing import Optional

import numpy as np

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticEmbedder:
    """
    Lightweight wrapper around sentence-transformers.

    The model load is lazy to keep embedding optional. Callers can check
    is_available() to decide whether to fall back to rules.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._model = None
        self._load_error: Optional[Exception] = None

    def _ensure_model(self) -> None:
        if self._model is not None or self._load_error is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name, device=self._device)
        except Exception as exc:
            self._load_error = exc

    def is_available(self) -> bool:
        self._ensure_model()
        return self._model is not None

    def embed(self, text: str) -> np.ndarray:
        self._ensure_model()
        if self._model is None:
            raise RuntimeError(
                "Embedding model unavailable. Install sentence-transformers "
                "and ensure the model is cached."
            )
        vectors = self._model.encode([text], convert_to_numpy=True)
        return np.asarray(vectors[0], dtype=float)

    def similarity(self, text_a: str, text_b: str) -> float:
        vec_a = self.embed(text_a)
        vec_b = self.embed(text_b)
        return cosine_similarity(vec_a, vec_b)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


_default_embedder: Optional[SemanticEmbedder] = None


def _get_default_embedder() -> SemanticEmbedder:
    global _default_embedder
    if _default_embedder is None:
        _default_embedder = SemanticEmbedder()
    return _default_embedder


def embed(text: str) -> np.ndarray:
    return _get_default_embedder().embed(text)


def similarity(text_a: str, text_b: str) -> float:
    return _get_default_embedder().similarity(text_a, text_b)
