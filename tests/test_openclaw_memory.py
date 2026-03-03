from __future__ import annotations

import numpy as np
import pytest

from memory import consolidator as consolidator_module
from tonesoul.memory.openclaw import hippocampus as openclaw_hippocampus_module
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
    assert results[0].metadata is not None


def test_hippocampus_wave_score_metadata_and_core_priority(tmp_path):
    db_path = tmp_path / "wave-core-db"
    hippo = Hippocampus(db_path=str(db_path), embedder=TinyEmbedding())

    low_id = hippo.memorize(
        content="boundary arbitration memory",
        source_file="low.md",
        memory_kind="decision",
        tension=0.8,
        wave={
            "uncertainty_shift": 0.2,
            "divergence_shift": 0.1,
            "risk_shift": 0.1,
            "revision_shift": 0.1,
        },
        tags=["obedience"],
    )
    high_id = hippo.memorize(
        content="boundary arbitration memory",
        source_file="high.md",
        memory_kind="decision",
        tension=0.8,
        wave={
            "uncertainty_shift": 0.85,
            "divergence_shift": 0.95,
            "risk_shift": 0.95,
            "revision_shift": 0.9,
        },
        tags=["boundary", "safety"],
    )

    by_id = {row["id"]: row for row in hippo.metadata[-2:]}
    assert by_id[high_id]["wave_score"] > by_id[low_id]["wave_score"]
    assert by_id[high_id]["memory_tier"] == "core"
    assert by_id[low_id]["memory_tier"] == "episodic"
    assert set(by_id[high_id]["wave_components"].keys()) == {
        "conflict_strength",
        "stance_shift",
        "boundary_cost",
        "consequence_weight",
    }

    results = hippo.recall(
        "boundary arbitration memory",
        top_k=2,
        query_tension=0.9,
        query_tension_mode="resonance",
    )
    assert len(results) == 2
    assert results[0].doc_id == high_id
    assert results[0].metadata is not None
    assert results[0].metadata.get("memory_tier") == "core"


def test_hippocampus_accepts_non_ascii_db_path(tmp_path):
    db_path = tmp_path / "語魂記憶"
    hippo = Hippocampus(db_path=str(db_path), embedder=TinyEmbedding())
    doc_id = hippo.memorize(content="unicode path memory", source_file="unicode.md", tension=0.5)
    assert doc_id

    reloaded = Hippocampus(db_path=str(db_path), embedder=TinyEmbedding())
    assert any(row["id"] == doc_id for row in reloaded.metadata)


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


def test_get_hippocampus_sanitizes_legacy_object_index(tmp_path, monkeypatch):
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    monkeypatch.setattr(openclaw_hippocampus_module, "faiss", None)

    db_path = tmp_path / "legacy-db"
    db_path.mkdir(parents=True, exist_ok=True)
    index_file = db_path / "tonesoul_cognitive.index"
    meta_file = db_path / "tonesoul_metadata.jsonl"

    with open(index_file, "wb") as handle:
        np.save(handle, np.array([{"legacy": 1}], dtype=object), allow_pickle=True)
    meta_file.write_text(
        '{"id":"legacy","source_file":"legacy.md","content":"legacy payload"}\n',
        encoding="utf-8",
    )

    hippo = consolidator_module.get_hippocampus(db_path=str(db_path))

    assert isinstance(hippo, Hippocampus)
    assert hippo.metadata == []
    assert index_file.exists()
    assert meta_file.exists()
    assert list(db_path.glob("tonesoul_cognitive.index.legacy_*.bak"))
    assert list(db_path.glob("tonesoul_metadata.jsonl.legacy_*.bak"))
