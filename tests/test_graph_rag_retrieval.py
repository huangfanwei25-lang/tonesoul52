"""Tests for GraphRAG-style multi-hop retrieval on semantic graph."""

from __future__ import annotations

from tonesoul.memory.semantic_graph import EdgeType, NodeType, SemanticGraph


def test_retrieve_empty_graph_returns_no_match_summary():
    graph = SemanticGraph()
    result = graph.retrieve_relevant(["test"])
    assert result["matched_nodes"] == []
    assert "No matching" in result["context_summary"]


def test_retrieve_direct_match():
    graph = SemanticGraph()
    graph.add_node("honesty", NodeType.CONCEPT)
    result = graph.retrieve_relevant(["honesty"])
    assert len(result["matched_nodes"]) == 1
    assert result["matched_nodes"][0]["label"] == "honesty"


def test_retrieve_multi_hop():
    graph = SemanticGraph()
    node_1 = graph.add_node("honesty", NodeType.CONCEPT)
    node_2 = graph.add_node("transparency", NodeType.CONCEPT)
    node_3 = graph.add_node("trust", NodeType.CONCEPT)
    graph.add_edge(node_1, node_2, EdgeType.SUPPORTS)
    graph.add_edge(node_2, node_3, EdgeType.IMPLIES)

    result = graph.retrieve_relevant(["honesty"], max_hops=2)
    labels = [node["label"] for node in result["matched_nodes"] + result["related_nodes"]]

    assert "honesty" in labels
    assert "transparency" in labels
    assert "trust" in labels


def test_retrieve_commitment_in_scope():
    graph = SemanticGraph()
    commitment = graph.add_node("always be truthful", NodeType.COMMITMENT)
    honesty = graph.add_node("honesty", NodeType.CONCEPT)
    graph.add_edge(commitment, honesty, EdgeType.RELATED_TO)

    result = graph.retrieve_relevant(["honesty"])
    assert len(result["commitments_in_scope"]) >= 1


def test_retrieve_respects_max_hops():
    graph = SemanticGraph()
    node_a = graph.add_node("A", NodeType.CONCEPT)
    node_b = graph.add_node("B", NodeType.CONCEPT)
    node_c = graph.add_node("C", NodeType.CONCEPT)
    node_d = graph.add_node("D", NodeType.CONCEPT)
    graph.add_edge(node_a, node_b, EdgeType.RELATED_TO)
    graph.add_edge(node_b, node_c, EdgeType.RELATED_TO)
    graph.add_edge(node_c, node_d, EdgeType.RELATED_TO)

    result = graph.retrieve_relevant(["A"], max_hops=1)
    labels = [node["label"] for node in result["related_nodes"]]

    assert "B" in labels
    assert "C" not in labels


def test_retrieve_empty_terms():
    graph = SemanticGraph()
    graph.add_node("test", NodeType.CONCEPT)
    result = graph.retrieve_relevant([])
    assert result["matched_nodes"] == []
    assert result["context_summary"] == ""


def test_retrieve_paths_recorded():
    graph = SemanticGraph()
    node_1 = graph.add_node("ethics", NodeType.CONCEPT)
    node_2 = graph.add_node("fairness", NodeType.CONCEPT)
    graph.add_edge(node_1, node_2, EdgeType.SUPPORTS)

    result = graph.retrieve_relevant(["ethics"])
    assert len(result["paths"]) >= 1
    assert result["paths"][0]["relation"] == "supports"
