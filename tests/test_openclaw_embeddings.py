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
