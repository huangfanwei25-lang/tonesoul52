from __future__ import annotations

from tonesoul.ystm.representation import (
    EmbeddingConfig,
    _clean_str,
    _math_coords_from_segment,
    _to_optional_float,
    build_nodes,
    simple_embed,
    tokenize,
)


def test_tokenize_and_simple_embed_are_deterministic() -> None:
    assert tokenize("Alpha, beta! Alpha") == ["alpha", "beta", "alpha"]
    assert (
        simple_embed("Alpha beta", dims=6).tolist() == simple_embed("Alpha beta", dims=6).tolist()
    )


def test_helper_converters_handle_blank_and_invalid_values() -> None:
    assert _clean_str("  hello  ") == "hello"
    assert _clean_str("   ") is None
    assert _to_optional_float("1.25") == 1.25
    assert _to_optional_float("nope") is None
    assert _math_coords_from_segment({}) is None


def test_build_nodes_prefers_explicit_source_and_math_fields() -> None:
    segment = {
        "text": "alpha",
        "mode": "analysis",
        "domain": "governance",
        "turn_id": 7,
        "source_type": "top",
        "source_uri": "https://top.example",
        "source_hash": "top-hash",
        "source_grade": "A",
        "source_retrieved_at": "2026-03-20T00:00:00Z",
        "source_verified_by": "human",
        "source": {
            "type": "nested",
            "uri": "https://nested.example",
            "hash": "nested-hash",
            "grade": "C",
        },
        "math_height": 1.5,
        "math_geology": "ridge",
        "math_ruggedness": 0.75,
        "math_coords": {"height": 9.0, "geology": "plain", "ruggedness": 9.0},
    }

    node = build_nodes([segment], created_by="tester", config=EmbeddingConfig(dims=4))[0]

    assert node.source.type == "top"
    assert node.source.uri == "https://top.example"
    assert node.source.hash == "top-hash"
    assert node.source.grade == "A"
    assert node.math_coords is not None
    assert node.math_coords.height == 1.5
    assert node.math_coords.geology == "ridge"
    assert node.math_coords.ruggedness == 0.75
    assert node.audit.created_by == "tester"


def test_build_nodes_defaults_source_hash_and_builds_drift_from_previous_node_only() -> None:
    nodes = build_nodes(
        [
            {"text": "alpha", "mode": "analysis", "domain": "governance", "turn_id": 1},
            {"text": "beta", "mode": "risk", "domain": "safety", "turn_id": 2},
        ],
        created_by="worker",
        config=EmbeddingConfig(dims=4),
    )

    assert nodes[0].source.type == "demo"
    assert nodes[0].source.hash is not None
    assert nodes[0].math_coords is None
    assert nodes[0].drift.delta_norm is None
    assert nodes[1].drift.drift_ref == {"from_node_id": "node_001"}
    assert nodes[1].drift.delta_v is not None
    assert nodes[1].drift.delta_norm is not None
