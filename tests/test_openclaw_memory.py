from __future__ import annotations

import numpy as np
import pytest

from memory import consolidator as consolidator_module
from tonesoul.memory.openclaw.embeddings import BaseEmbedding, HashEmbedding
from tonesoul.memory.openclaw.hippocampus import Hippocampus


class TinyEmbedding(BaseEmbedding):
    dimension = 4

    def encode(self, text: str) -> np.ndarray:
        lower = text.lower()
        vec = np.array(
            [
                lower.count("tension"),
                lower.count("memory"),
                lower.count("governance"),
                len(lower.split()),
            ],
            dtype=np.float32,
        )
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


def test_hippocampus_memorize_and_recall(tmp_path):
    db_path = tmp_path / "hippo-db"
    hippo = Hippocampus(db_path=str(db_path), embedder=TinyEmbedding())

    hippo.memorize(
        content="high tension memory governance",
        source_file="a.md",
        tension=0.9,
        tags=["high"],
    )
    hippo.memorize(
        content="low memory note",
        source_file="b.md",
        tension=0.1,
        tags=["low"],
    )

    results = hippo.recall("tension governance", top_k=2, query_tension=0.9)
    assert len(results) >= 1
    assert "high tension" in results[0].content


def test_hippocampus_blocks_path_traversal():
    with pytest.raises(ValueError):
        Hippocampus(db_path="../../../etc/passwd")


def test_get_hippocampus_uses_hash_profile(tmp_path, monkeypatch):
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    hippo = consolidator_module.get_hippocampus(db_path=str(tmp_path / "hash-db"))
    assert isinstance(hippo.embedder, HashEmbedding)


def test_get_hippocampus_auto_falls_back_to_hash(tmp_path, monkeypatch):
    class _FailingSentenceTransformer:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("simulated dependency failure")

    monkeypatch.delenv("TONESOUL_MEMORY_EMBEDDER", raising=False)
    monkeypatch.setattr(
        consolidator_module,
        "SentenceTransformerEmbedding",
        _FailingSentenceTransformer,
    )
    hippo = consolidator_module.get_hippocampus(db_path=str(tmp_path / "auto-db"))
    assert isinstance(hippo.embedder, HashEmbedding)
