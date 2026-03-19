from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from tonesoul.memory.openclaw.hippocampus import Hippocampus


class TinyEmbedding:
    dimension = 4

    def encode(self, text: str) -> np.ndarray:
        lower = text.lower()
        vec = np.array(
            [
                lower.count("boundary"),
                lower.count("memory"),
                lower.count("risk"),
                len(lower.split()),
            ],
            dtype=np.float32,
        )
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


class FakeBM25:
    def __init__(self, scores):
        self._scores = np.array(scores, dtype=np.float32)

    def get_scores(self, tokenized_query):
        return self._scores


def test_validate_memory_kind_normalizes_and_rejects_invalid_values() -> None:
    assert Hippocampus._validate_memory_kind(" NOTE ") == "note"

    with pytest.raises(ValueError, match="memory_kind cannot be empty"):
        Hippocampus._validate_memory_kind(" ")

    with pytest.raises(ValueError, match="memory_kind must be one of"):
        Hippocampus._validate_memory_kind("mystery")


def test_validate_wave_normalizes_optional_values_and_rejects_invalid_shapes() -> None:
    assert Hippocampus._validate_wave(
        {"risk_shift": 0.5, "revision_shift": None},
        "wave",
    ) == {"risk_shift": 0.5}
    assert Hippocampus._validate_wave({"revision_shift": None}, "wave") is None

    with pytest.raises(ValueError, match="wave must be a dict"):
        Hippocampus._validate_wave([], "wave")

    with pytest.raises(ValueError, match="contains unknown key"):
        Hippocampus._validate_wave({"unknown": 0.2}, "wave")

    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        Hippocampus._validate_wave({"risk_shift": 1.2}, "wave")


def test_build_wave_profile_uses_tension_and_boundary_priors() -> None:
    profile = Hippocampus._build_wave_profile(
        tension=0.9,
        wave={
            "risk_shift": 0.8,
            "divergence_shift": 0.6,
            "revision_shift": 0.4,
            "uncertainty_shift": 0.2,
        },
        memory_kind="constraint",
        tags=["boundary"],
    )

    assert profile["components"] == {
        "conflict_strength": 0.9,
        "stance_shift": 0.5,
        "boundary_cost": 0.82,
        "consequence_weight": 0.875,
    }
    assert profile["score"] == pytest.approx(0.322875)


def test_build_wave_profile_derives_conflict_strength_when_tension_is_missing() -> None:
    profile = Hippocampus._build_wave_profile(
        tension=None,
        wave={
            "risk_shift": 0.2,
            "divergence_shift": 0.6,
            "revision_shift": 0.0,
            "uncertainty_shift": 0.9,
        },
        memory_kind="note",
        tags=[],
    )

    assert profile["components"] == {
        "conflict_strength": 0.54,
        "stance_shift": 0.3,
        "boundary_cost": 0.3,
        "consequence_weight": 0.63,
    }
    assert profile["score"] == pytest.approx(0.030618)


def test_extract_wave_score_prefers_stored_value() -> None:
    doc = {
        "wave_score": 0.77,
        "wave": {"risk_shift": 0.1, "divergence_shift": 0.1},
        "kind": "constraint",
    }

    assert Hippocampus._extract_wave_score(doc) == 0.77


def test_extract_wave_score_recomputes_from_document_fields() -> None:
    doc = {
        "tension": 0.9,
        "wave": {
            "risk_shift": 0.8,
            "divergence_shift": 0.6,
            "revision_shift": 0.4,
            "uncertainty_shift": 0.2,
        },
        "kind": "constraint",
        "tags": ["boundary"],
    }

    assert Hippocampus._extract_wave_score(doc) == pytest.approx(0.322875)


def test_memorize_rejects_missing_embedder_and_invalid_inputs(tmp_path) -> None:
    without_embedder = Hippocampus(db_path=str(tmp_path / "no-embedder"))
    with pytest.raises(ValueError, match="no embedder provided"):
        without_embedder.memorize("note")

    hippo = Hippocampus(db_path=str(tmp_path / "with-embedder"), embedder=TinyEmbedding())

    with pytest.raises(ValueError, match="tension must be between 0.0 and 1.0"):
        hippo.memorize("note", tension=1.2)

    with pytest.raises(ValueError, match="memory_kind must be one of"):
        hippo.memorize("note", memory_kind="mystery")

    with pytest.raises(ValueError, match="wave contains unknown key"):
        hippo.memorize("note", wave={"unknown": 0.2})


def test_apply_tension_signal_supports_resonance_and_conflict_modes() -> None:
    doc = {"tension": 0.9}

    assert Hippocampus._apply_tension_signal(1.0, doc, 0.9, mode="resonance") == pytest.approx(1.2)
    assert Hippocampus._apply_tension_signal(1.0, doc, 0.1, mode="conflict") == pytest.approx(1.16)
    assert Hippocampus._apply_tension_signal(1.0, doc, None, mode="resonance") == 1.0
    assert Hippocampus._apply_tension_signal(1.0, {}, 0.9, mode="resonance") == 1.0


def test_apply_wave_resonance_supports_resonance_conflict_and_missing_wave() -> None:
    doc = {
        "wave": {
            "risk_shift": 0.8,
            "divergence_shift": 0.6,
            "revision_shift": 0.4,
            "uncertainty_shift": 0.2,
        }
    }

    assert Hippocampus._apply_wave_resonance(
        1.0,
        doc,
        {"risk_shift": 0.8, "divergence_shift": 0.6},
        mode="resonance",
    ) == pytest.approx(1.25)
    assert Hippocampus._apply_wave_resonance(
        1.0,
        doc,
        {"risk_shift": 0.0, "divergence_shift": 0.0},
        mode="conflict",
    ) == pytest.approx(1.175)
    assert Hippocampus._apply_wave_resonance(1.0, {}, {"risk_shift": 0.8}) == 1.0


def test_apply_core_memory_priority_requires_high_tension_and_wave_score() -> None:
    core_doc = {"wave_score": 0.5, "memory_tier": "core"}
    episodic_doc = {"wave_score": 0.5, "memory_tier": "episodic"}

    assert Hippocampus._apply_core_memory_priority(1.0, core_doc, 0.9) == pytest.approx(1.279)
    assert Hippocampus._apply_core_memory_priority(1.0, episodic_doc, 0.9) == pytest.approx(1.149)
    assert Hippocampus._apply_core_memory_priority(1.0, core_doc, 0.5) == 1.0
    assert Hippocampus._apply_core_memory_priority(1.0, {"wave_score": 0.0}, 0.9) == 1.0


def test_apply_time_decay_handles_invalid_timestamp_and_decays_old_records(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "decay-db"), embedder=TinyEmbedding())
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()

    assert hippo._apply_time_decay(1.0, "not-a-date") == 1.0
    assert hippo._apply_time_decay(1.0, old_timestamp) == pytest.approx(np.exp(-0.1))


def test_search_keywords_filters_non_positive_scores_and_orders_results(tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "bm25-db"), embedder=TinyEmbedding())
    hippo.metadata = [
        {"id": "d1", "content": "boundary memory", "source_file": "a.md"},
        {"id": "d2", "content": "risk memory", "source_file": "b.md"},
        {"id": "d3", "content": "boundary risk", "source_file": "c.md"},
    ]
    hippo.bm25 = FakeBM25([0.0, 2.0, 1.0])

    results = hippo.search_keywords("boundary risk", top_k=3)

    assert [item["doc"]["id"] for item in results] == ["d2", "d3"]
    assert [item["score"] for item in results] == [2.0, 1.0]


def test_recall_requires_vector_or_embedder_and_valid_modes(tmp_path) -> None:
    without_embedder = Hippocampus(db_path=str(tmp_path / "recall-no-embedder"))
    with pytest.raises(ValueError, match="requires either query_vector or an initialized embedder"):
        without_embedder.recall("query")

    hippo = Hippocampus(db_path=str(tmp_path / "recall-db"), embedder=TinyEmbedding())
    query_vector = np.array([1, 0, 0, 0], dtype=np.float32)

    with pytest.raises(ValueError, match="query_tension_mode must be"):
        hippo.recall("query", query_vector=query_vector, query_tension_mode="bad")

    with pytest.raises(ValueError, match="query_wave_mode must be"):
        hippo.recall("query", query_vector=query_vector, query_wave_mode="bad")

    with pytest.raises(ValueError, match="query_wave contains unknown key"):
        hippo.recall("query", query_vector=query_vector, query_wave={"unknown": 0.1})


def test_recall_wave_mode_changes_result_order(monkeypatch, tmp_path) -> None:
    hippo = Hippocampus(db_path=str(tmp_path / "wave-rank-db"), embedder=TinyEmbedding())
    doc_a = {
        "id": "a",
        "content": "boundary memory",
        "source_file": "a.md",
        "wave": {"risk_shift": 0.9, "divergence_shift": 0.9},
    }
    doc_b = {
        "id": "b",
        "content": "boundary memory",
        "source_file": "b.md",
        "wave": {"risk_shift": 0.1, "divergence_shift": 0.1},
    }
    monkeypatch.setattr(
        hippo,
        "search_vectors",
        lambda query_vector, top_k=20: [
            {"doc": doc_a, "score": 1.0, "type": "vector"},
            {"doc": doc_b, "score": 1.0, "type": "vector"},
        ],
    )
    monkeypatch.setattr(hippo, "search_keywords", lambda query_text, top_k=20: [])

    resonance = hippo.recall(
        "boundary memory",
        query_vector=np.array([1, 0, 0, 0], dtype=np.float32),
        query_wave={"risk_shift": 0.9, "divergence_shift": 0.9},
        query_wave_mode="resonance",
        top_k=2,
    )
    conflict = hippo.recall(
        "boundary memory",
        query_vector=np.array([1, 0, 0, 0], dtype=np.float32),
        query_wave={"risk_shift": 0.9, "divergence_shift": 0.9},
        query_wave_mode="conflict",
        top_k=2,
    )

    assert [result.doc_id for result in resonance] == ["a", "b"]
    assert [result.doc_id for result in conflict] == ["b", "a"]
