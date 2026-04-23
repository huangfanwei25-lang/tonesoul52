import json

import numpy as np

from tonesoul.semantic.concept_store import Concept, ConceptStore


class _FakeEmbedder:
    def embed(self, text):
        normalized = text.lower()
        if "alpha" in normalized:
            return np.array([1.0, 0.0])
        if "beta" in normalized:
            return np.array([0.0, 1.0])
        return np.array([0.5, 0.5])


def test_load_list_get_and_to_text_ignore_invalid_files(tmp_path):
    (tmp_path / "alpha.json").write_text(
        json.dumps(
            {
                "name": "alpha",
                "description": "first",
                "examples": ["one"],
                "keywords": ["trace"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "invalid.json").write_text("{broken", encoding="utf-8")
    (tmp_path / "nameless.json").write_text(
        json.dumps({"description": "missing"}), encoding="utf-8"
    )

    store = ConceptStore(tmp_path)
    store.load()

    assert store.list_names() == ["alpha"]
    assert store.get("alpha").to_text() == "alpha first one trace"
    assert list(store.all())[0].source_path == tmp_path / "alpha.json"


def test_build_index_and_rank_use_embedder_vectors(tmp_path):
    for name in ("alpha", "beta"):
        (tmp_path / f"{name}.json").write_text(
            json.dumps(
                {"name": name, "description": f"{name} desc", "examples": [], "keywords": []}
            ),
            encoding="utf-8",
        )

    store = ConceptStore(tmp_path)
    store.load()
    embedder = _FakeEmbedder()

    index = store.build_index(embedder)
    ranked = store.rank("alpha signal", embedder, top_k=2)

    assert set(index) == {"alpha", "beta"}
    assert ranked[0][0] == "alpha"
    assert ranked[0][1] >= ranked[1][1]


def test_rank_returns_empty_for_non_positive_top_k(tmp_path):
    store = ConceptStore(tmp_path)
    store.load()

    assert store.rank("anything", _FakeEmbedder(), top_k=0) == []


# ── Concept.to_text ───────────────────────────────────────────────────────────

class TestConceptToText:
    def test_all_parts_joined(self):
        concept = Concept(
            name="freedom",
            description="absence of constraint",
            examples=["free speech"],
            keywords=["liberty"],
        )
        text = concept.to_text()
        assert "freedom" in text
        assert "absence of constraint" in text
        assert "free speech" in text
        assert "liberty" in text

    def test_empty_parts_skipped(self):
        concept = Concept(name="minimal", description="", examples=[], keywords=[])
        assert concept.to_text() == "minimal"


# ── ConceptStore.load / get / all ─────────────────────────────────────────────

def test_load_missing_root_is_empty(tmp_path):
    store = ConceptStore(tmp_path / "nonexistent")
    store.load()
    assert store.list_names() == []
    assert list(store.all()) == []


def test_get_returns_none_for_missing_name(tmp_path):
    store = ConceptStore(tmp_path)
    store.load()
    assert store.get("nonexistent") is None


def test_load_non_dict_payload_skipped(tmp_path):
    (tmp_path / "bad.json").write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    store = ConceptStore(tmp_path)
    store.load()
    assert store.list_names() == []


# ── ConceptStore._load_concept (private) ──────────────────────────────────────

def test_load_concept_handles_broken_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{broken json", encoding="utf-8")
    store = ConceptStore(tmp_path)
    assert store._load_concept(path) is None


def test_load_concept_missing_name_returns_none(tmp_path):
    path = tmp_path / "nameless.json"
    path.write_text(json.dumps({"description": "has no name"}), encoding="utf-8")
    store = ConceptStore(tmp_path)
    assert store._load_concept(path) is None


def test_load_concept_valid_includes_optional_fields(tmp_path):
    path = tmp_path / "full.json"
    path.write_text(
        json.dumps({"name": "alpha", "description": "desc", "examples": ["ex"], "keywords": ["kw"]}),
        encoding="utf-8",
    )
    store = ConceptStore(tmp_path)
    concept = store._load_concept(path)
    assert concept is not None
    assert concept.examples == ["ex"]
    assert concept.keywords == ["kw"]
