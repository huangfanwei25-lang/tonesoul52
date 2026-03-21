from __future__ import annotations

from datetime import datetime

from tonesoul.memory.semantic_graph import (
    ContradictionResult,
    EdgeType,
    NodeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
    create_semantic_graph,
)


def test_semantic_graph_dataclasses_serialize_core_fields() -> None:
    node = SemanticNode(
        id="n1",
        label="honesty",
        node_type=NodeType.CONCEPT,
        created_at=datetime(2026, 3, 19, 12, 0, 0),
        turn_index=2,
        weight=0.7,
        metadata={"source": "test"},
    )
    edge = SemanticEdge(
        source_id="n1",
        target_id="n2",
        edge_type=EdgeType.SUPPORTS,
        weight=0.6,
        turn_index=2,
        reasoning="shared topic",
    )
    contradiction = ContradictionResult(
        found=True,
        path=["n1", "n2"],
        description="conflict",
        severity=0.8,
    )

    assert node.to_dict() == {
        "id": "n1",
        "label": "honesty",
        "type": "concept",
        "created_at": "2026-03-19T12:00:00",
        "turn_index": 2,
        "weight": 0.7,
        "metadata": {"source": "test"},
    }
    assert edge.to_dict() == {
        "source": "n1",
        "target": "n2",
        "type": "supports",
        "weight": 0.6,
        "turn_index": 2,
        "reasoning": "shared topic",
    }
    assert contradiction.to_dict() == {
        "found": True,
        "path": ["n1", "n2"],
        "description": "conflict",
        "severity": 0.8,
    }


def test_add_node_reuses_existing_label_and_keeps_max_weight() -> None:
    graph = SemanticGraph()

    first = graph.add_node("honesty", NodeType.CONCEPT, weight=0.2, metadata={"source": "a"})
    second = graph.add_node("honesty", NodeType.CONCEPT, weight=0.7, metadata={"source": "b"})

    assert first.id == second.id
    assert second.weight == 0.7
    assert graph.get_node(first.id) is first
    assert graph.get_node(first.id).metadata == {"source": "a"}


def test_add_edge_updates_neighbors_and_lookup_tables() -> None:
    graph = SemanticGraph()
    honesty = graph.add_node("honesty", NodeType.CONCEPT)
    trust = graph.add_node("trust", NodeType.CONCEPT)

    edge = graph.add_edge(honesty, trust, EdgeType.SUPPORTS, weight=0.9, reasoning="linked")

    assert [node.label for node in graph.get_neighbors(honesty.id)] == ["trust"]
    assert [node.label for node in graph.get_neighbors(trust.id)] == ["honesty"]
    assert graph.get_edges_between(honesty.id, trust.id) == [edge]
    assert graph.find_nodes_by_label("hon") == [honesty]
    assert graph.find_nodes_by_type(NodeType.CONCEPT) == [honesty, trust]


def test_detect_contradictions_finds_direct_and_commitment_boundary_conflicts() -> None:
    graph = SemanticGraph()
    honesty = graph.add_node("honesty", NodeType.CONCEPT)
    deception = graph.add_node("deception", NodeType.CONCEPT)
    graph.add_edge(honesty, deception, EdgeType.CONTRADICTS, weight=0.75)

    commitment = graph.add_node("protect trust", NodeType.COMMITMENT)
    boundary = graph.add_node("refuse harm", NodeType.BOUNDARY)
    topic = graph.add_node("trust", NodeType.TOPIC)
    graph.add_edge(commitment, topic, EdgeType.RELATED_TO)
    graph.add_edge(boundary, topic, EdgeType.RELATED_TO)

    contradictions = graph.detect_contradictions()

    assert len(contradictions) == 2
    assert any(item.path == [honesty.id, deception.id] for item in contradictions)
    assert any(item.path == [commitment.id, boundary.id] for item in contradictions)
    assert any(item.severity == 0.6 for item in contradictions)


def test_retrieve_relevant_handles_blank_terms_and_max_results() -> None:
    graph = SemanticGraph()
    honesty = graph.add_node("honesty", NodeType.CONCEPT)
    trust = graph.add_node("trust", NodeType.CONCEPT)
    care = graph.add_node("care", NodeType.CONCEPT)
    graph.add_edge(honesty, trust, EdgeType.RELATED_TO)
    graph.add_edge(trust, care, EdgeType.RELATED_TO)

    blank = graph.retrieve_relevant([" ", ""])
    limited = graph.retrieve_relevant(["honesty"], max_hops=2, max_results=1)

    assert blank == {
        "matched_nodes": [],
        "related_nodes": [],
        "paths": [],
        "commitments_in_scope": [],
        "context_summary": "",
    }
    assert len(limited["matched_nodes"]) == 1
    assert len(limited["related_nodes"]) == 1
    assert limited["matched_nodes"][0]["label"] == "honesty"
    assert limited["context_summary"]


def test_extract_from_commitment_maps_types_and_truncates_labels() -> None:
    graph = SemanticGraph()

    boundary = graph.extract_from_commitment({"content": "x" * 60, "type": "boundary"})
    promise = graph.extract_from_commitment({"content": "keep this promise", "type": "promise"})
    concept = graph.extract_from_commitment({"content": "define honesty", "type": "definitional"})

    assert boundary.node_type == NodeType.BOUNDARY
    assert boundary.label == "x" * 50
    assert boundary.metadata["full_content"] == "x" * 60
    assert promise.node_type == NodeType.COMMITMENT
    assert concept.node_type == NodeType.CONCEPT


def test_extract_from_response_creates_topic_nodes_and_pairwise_edges() -> None:
    graph = SemanticGraph()

    nodes = graph.extract_from_response("response", ["honesty", "trust", "care"])

    assert [node.label for node in nodes] == ["honesty", "trust", "care"]
    assert graph.get_summary()["total_nodes"] == 3
    assert graph.get_summary()["edge_types"]["related_to"] == 3


def test_increment_turn_summary_export_and_reset() -> None:
    graph = create_semantic_graph()
    graph.increment_turn()
    topic = graph.add_node("topic", NodeType.TOPIC)
    concept = graph.add_node("concept", NodeType.CONCEPT)
    graph.add_edge(topic, concept, EdgeType.RELATED_TO)

    payload = graph.to_dict()

    assert topic.turn_index == 1
    assert payload["summary"]["current_turn"] == 1
    assert payload["summary"]["total_nodes"] == 2
    assert payload["summary"]["total_edges"] == 1

    graph.reset()

    assert graph.get_summary() == {
        "total_nodes": 0,
        "total_edges": 0,
        "node_types": {
            "concept": 0,
            "entity": 0,
            "commitment": 0,
            "boundary": 0,
            "topic": 0,
        },
        "edge_types": {
            "supports": 0,
            "contradicts": 0,
            "related_to": 0,
            "implies": 0,
            "depends_on": 0,
            "part_of": 0,
        },
        "current_turn": 0,
        "contradictions": 0,
    }
