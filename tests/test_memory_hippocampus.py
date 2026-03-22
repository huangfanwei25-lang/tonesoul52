from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from tonesoul.memory import hippocampus as module
from tonesoul.memory.hippocampus import Hippocampus, MemoryResult

pytestmark = pytest.mark.filterwarnings(
    "ignore:datetime.datetime.utcnow\\(\\) is deprecated.*:DeprecationWarning"
)


class FakeIndex:
    def __init__(self, distances: np.ndarray, indices: np.ndarray):
        self._distances = distances
        self._indices = indices

    def search(self, query_matrix: np.ndarray, top_k: int):
        return self._distances, self._indices


class FakeBM25:
    def __init__(self, scores):
        self._scores = np.array(scores, dtype=np.float32)

    def get_scores(self, tokenized_query):
        return self._scores


def _doc(doc_id: str, content: str, *, ingested_at: str, tags=None):
    payload = {
        "id": doc_id,
        "content": content,
        "source_file": f"{doc_id}.md",
        "ingested_at": ingested_at,
    }
    if tags is not None:
        payload["tags"] = tags
    return payload


def test_load_db_without_files_keeps_runtime_empty(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "missing-db"))

    assert hippo.index is None
    assert hippo.metadata == []
    assert hippo.bm25 is None
    assert hippo.search_vectors(np.zeros(3, dtype=np.float32)) == []
    assert hippo.search_keywords("query") == []


def test_load_db_skips_vector_loading_when_faiss_is_missing(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "legacy-db"
    db_path.mkdir(parents=True, exist_ok=True)
    (db_path / "tonesoul_cognitive.index").write_bytes(b"index")
    (db_path / "tonesoul_metadata.jsonl").write_text(
        '{"id":"a","content":"memory","source_file":"a.md"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "faiss", None)

    hippo = Hippocampus(db_path=str(db_path))

    assert hippo.index is None
    assert hippo.metadata == []
    assert hippo.bm25 is None


def test_apply_time_decay_decays_old_records_and_ignores_bad_timestamp(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "decay-db"))
    old = (datetime.utcnow() - timedelta(days=10, seconds=1)).isoformat()

    assert hippo._apply_time_decay(1.0, "bad-timestamp") == 1.0
    assert hippo._apply_time_decay(1.0, old) == np.exp(-0.1)


def test_search_vectors_sorts_by_decayed_score(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "vector-db"))
    hippo.index = FakeIndex(
        np.array([[0.9, 0.15]], dtype=np.float32),
        np.array([[0, 1]], dtype=np.int64),
    )
    hippo.metadata = [
        _doc(
            "old",
            "old memory",
            ingested_at=(datetime.now() - timedelta(days=300)).isoformat(),
        ),
        _doc(
            "new",
            "new memory",
            ingested_at=datetime.now().isoformat(),
        ),
    ]

    results = hippo.search_vectors(np.zeros(4, dtype=np.float32), top_k=2)

    assert [item["doc"]["id"] for item in results] == ["new", "old"]
    assert results[0]["score"] > results[1]["score"]


def test_search_keywords_filters_non_positive_scores(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "keyword-db"))
    hippo.metadata = [
        _doc("a", "alpha", ingested_at=datetime.now().isoformat()),
        _doc("b", "beta", ingested_at=datetime.now().isoformat()),
        _doc("c", "gamma", ingested_at=datetime.now().isoformat()),
    ]
    hippo.bm25 = FakeBM25([0.0, 2.0, 1.0])

    results = hippo.search_keywords("beta gamma", top_k=3)

    assert [item["doc"]["id"] for item in results] == ["b", "c"]
    assert [item["score"] for item in results] == [2.0, 1.0]


def test_recall_rrf_fuses_vector_and_keyword_hits_without_duplicates(monkeypatch, tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "rrf-db"))
    doc_a = _doc("a", "shared memory", ingested_at=datetime.now().isoformat())
    doc_b = _doc("b", "vector only", ingested_at=datetime.now().isoformat())
    monkeypatch.setattr(
        hippo,
        "search_vectors",
        lambda query_vector, top_k=20: [
            {"doc": doc_b, "score": 0.9, "type": "vector"},
            {"doc": doc_a, "score": 0.8, "type": "vector"},
        ],
    )
    monkeypatch.setattr(
        hippo,
        "search_keywords",
        lambda query_text, top_k=20: [
            {"doc": doc_a, "score": 1.0, "type": "keyword"},
        ],
    )

    results = hippo.recall("shared", np.zeros(4, dtype=np.float32), top_k=2)

    assert [item.doc_id for item in results] == ["a", "b"]
    assert len(results) == 2


def test_compute_error_vector_normalizes_nonzero_and_preserves_zero_vector() -> None:
    normalized = Hippocampus.compute_error_vector(
        np.array([1.0, 0.0], dtype=np.float32),
        np.array([0.0, 1.0], dtype=np.float32),
    )
    zero = Hippocampus.compute_error_vector(
        np.array([1.0, 0.0], dtype=np.float32),
        np.array([1.0, 0.0], dtype=np.float32),
    )

    assert np.allclose(normalized, np.array([0.70710677, -0.70710677], dtype=np.float32))
    assert np.allclose(zero, np.array([0.0, 0.0], dtype=np.float32))


def test_recall_corrective_uses_default_query_and_passes_tension_context(
    monkeypatch, tmp_path
) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "corrective-db"))
    captured = {}

    def fake_recall(query_text, query_vector, top_k=5, *, tension_context=None):
        captured["query_text"] = query_text
        captured["query_vector"] = query_vector
        captured["top_k"] = top_k
        captured["tension_context"] = tension_context
        return [MemoryResult("m1", "memory", "m1.md", 0.9, 1)]

    monkeypatch.setattr(hippo, "recall", fake_recall)

    results = hippo.recall_corrective(
        intended=np.array([1.0, 0.0], dtype=np.float32),
        generated=np.array([0.0, 1.0], dtype=np.float32),
        top_k=3,
        tension_context={"zone": "risk"},
    )

    assert [item.doc_id for item in results] == ["m1"]
    assert captured["query_text"] == "self-correction"
    assert captured["top_k"] == 3
    assert captured["tension_context"] == {"zone": "risk"}
    assert np.allclose(captured["query_vector"], np.array([0.70710677, -0.70710677]))


def test_apply_tension_context_boost_combines_matching_signals() -> None:
    boosted = Hippocampus._apply_tension_context_boost(
        base_score=1.0,
        doc={
            "content": "collapse_warning block fix bug error correction",
            "tags": ["debug"],
        },
        tension_context={
            "zone": "risk",
            "trend": "diverging",
            "work_category": "debug",
        },
    )

    assert boosted == pytest.approx(2.34)
