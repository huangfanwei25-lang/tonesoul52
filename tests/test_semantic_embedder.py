import builtins
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from tonesoul.semantic import embedder as embed_mod


def test_cosine_similarity_handles_orthogonal_and_zero_vectors():
    assert embed_mod.cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == 0.0
    assert embed_mod.cosine_similarity(np.array([0.0, 0.0]), np.array([1.0, 0.0])) == 0.0


def test_semantic_embedder_uses_sentence_transformer_when_available(monkeypatch):
    class FakeSentenceTransformer:
        def __init__(self, model_name, device=None):
            self.model_name = model_name
            self.device = device

        def encode(self, texts, convert_to_numpy=True):
            return np.array([[len(texts[0]), 1.0]], dtype=float)

    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )

    embedder = embed_mod.SemanticEmbedder(model_name="fake-model", device="cpu")

    assert embedder.is_available() is True
    assert np.array_equal(embedder.embed("abc"), np.array([3.0, 1.0]))
    assert embedder.similarity("abc", "abc") == pytest.approx(1.0)


def test_semantic_embedder_handles_missing_dependency_and_default_helpers(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("missing dependency")
        return original_import(name, *args, **kwargs)

    class FakeDefaultEmbedder:
        def embed(self, text):
            return np.array([1.0])

        def similarity(self, text_a, text_b):
            return 0.75

    monkeypatch.setattr(builtins, "__import__", fake_import)
    embedder = embed_mod.SemanticEmbedder()

    assert embedder.is_available() is False
    with pytest.raises(RuntimeError, match="Embedding model unavailable"):
        embedder.embed("x")

    monkeypatch.setattr(embed_mod, "_default_embedder", FakeDefaultEmbedder())
    assert np.array_equal(embed_mod.embed("x"), np.array([1.0]))
    assert embed_mod.similarity("a", "b") == 0.75


def test_cosine_similarity_parallel_vectors_returns_one():
    v = np.array([0.6, 0.8])
    assert embed_mod.cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_known_values():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    assert embed_mod.cosine_similarity(a, b) == pytest.approx(0.0)
    c = np.array([1.0, 1.0])
    d = np.array([1.0, 0.0])
    result = embed_mod.cosine_similarity(c, d)
    assert 0.5 < result < 1.0


def test_get_default_embedder_returns_singleton(monkeypatch):
    monkeypatch.setattr(embed_mod, "_default_embedder", None)
    e1 = embed_mod._get_default_embedder()
    e2 = embed_mod._get_default_embedder()
    assert e1 is e2


def test_embedder_is_available_false_without_model(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    embedder = embed_mod.SemanticEmbedder()
    assert embedder.is_available() is False
