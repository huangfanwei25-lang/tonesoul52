from __future__ import annotations

import numpy as np

from tonesoul.memory.hippocampus import Hippocampus


def _doc(doc_id: str, content: str):
    return {
        "id": doc_id,
        "content": content,
        "source_file": f"{doc_id}.md",
        "ingested_at": "2026-03-01T00:00:00",
    }


def _setup_rank_sources(monkeypatch, hippo: Hippocampus):
    docs = [
        _doc("a", "general memory with neutral context"),
        _doc("b", "policy block memory and collapse_warning signal"),
        _doc("c", "debug fix workflow for bug and error correction"),
    ]
    vec_results = [
        {"doc": docs[0], "score": 0.9, "type": "vector"},
        {"doc": docs[1], "score": 0.8, "type": "vector"},
        {"doc": docs[2], "score": 0.7, "type": "vector"},
    ]
    monkeypatch.setattr(hippo, "search_vectors", lambda query_vector, top_k=10: vec_results)
    monkeypatch.setattr(hippo, "search_keywords", lambda query_text, top_k=10: [])


def test_recall_without_tension_context_keeps_rrf_order(monkeypatch, tmp_path):
    hippo = Hippocampus(db_path=str(tmp_path / "db"))
    _setup_rank_sources(monkeypatch, hippo)

    results = hippo.recall("query", np.zeros(384, dtype=np.float32), top_k=3)

    assert [item.doc_id for item in results] == ["a", "b", "c"]


def test_recall_risk_zone_boosts_block_and_collapse_entries(monkeypatch, tmp_path):
    hippo = Hippocampus(db_path=str(tmp_path / "db"))
    _setup_rank_sources(monkeypatch, hippo)

    results = hippo.recall(
        "query",
        np.zeros(384, dtype=np.float32),
        top_k=3,
        tension_context={"zone": "risk"},
    )

    assert results[0].doc_id == "b"


def test_recall_debug_category_boosts_bug_fix_entries(monkeypatch, tmp_path):
    hippo = Hippocampus(db_path=str(tmp_path / "db"))
    _setup_rank_sources(monkeypatch, hippo)

    results = hippo.recall(
        "query",
        np.zeros(384, dtype=np.float32),
        top_k=3,
        tension_context={"work_category": "debug"},
    )

    assert results[0].doc_id == "c"
