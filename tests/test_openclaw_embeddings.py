from __future__ import annotations

import builtins

import numpy as np
import pytest

from tonesoul.memory.openclaw import embeddings as emb_mod


def test_hash_embedding_is_deterministic_and_normalized():
    embedding = emb_mod.HashEmbedding(dimension=8)

    vec_a = embedding.encode("alpha")
    vec_b = embedding.encode("alpha")

    assert vec_a.shape == (8,)
    assert np.isclose(np.linalg.norm(vec_a), 1.0)
    assert np.allclose(vec_a, vec_b)


def test_mock_embedding_returns_zero_vector():
    embedding = emb_mod.MockEmbedding(dimension=4)

    assert np.array_equal(embedding.encode("anything"), np.zeros(4, dtype=np.float32))


def test_sentence_transformer_embedding_raises_runtime_error_when_dependency_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("missing dependency")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match="sentence-transformers is not installed"):
        emb_mod.SentenceTransformerEmbedding()


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestHashEmbedding:
    def test_different_texts_produce_different_vectors(self):
        embedding = emb_mod.HashEmbedding(dimension=16)
        v1 = embedding.encode("hello")
        v2 = embedding.encode("world")
        assert not np.allclose(v1, v2)

    def test_dimension_respected(self):
        for dim in (4, 32, 128):
            assert emb_mod.HashEmbedding(dimension=dim).encode("test").shape == (dim,)

    def test_output_dtype_is_float32(self):
        vec = emb_mod.HashEmbedding(dimension=8).encode("text")
        assert vec.dtype == np.float32

    def test_unit_norm(self):
        for text in ("a", "longer text here", "語魂"):
            vec = emb_mod.HashEmbedding(dimension=32).encode(text)
            assert np.isclose(np.linalg.norm(vec), 1.0)


class TestMockEmbedding:
    def test_all_entries_are_zero(self):
        vec = emb_mod.MockEmbedding(dimension=12).encode("anything")
        assert np.all(vec == 0.0)

    def test_dimension_respected(self):
        for dim in (4, 64):
            assert emb_mod.MockEmbedding(dimension=dim).encode("text").shape == (dim,)

    def test_output_dtype_is_float32(self):
        vec = emb_mod.MockEmbedding(dimension=8).encode("x")
        assert vec.dtype == np.float32

    def test_same_for_all_inputs(self):
        emb = emb_mod.MockEmbedding(dimension=4)
        assert np.array_equal(emb.encode("abc"), emb.encode("xyz"))
