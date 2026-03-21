import json

import numpy as np

from tonesoul.semantic.concept_store import ConceptStore


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
