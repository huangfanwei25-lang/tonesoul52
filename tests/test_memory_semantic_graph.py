from __future__ import annotations

import pytest

from tonesoul.memory.semantic_graph import (
    ContradictionResult,
    EdgeType,
    NodeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
    create_semantic_graph,
)


# ── SemanticNode.to_dict ──────────────────────────────────────────────────────

class TestSemanticNodeToDict:
    def test_includes_required_keys(self):
        graph = SemanticGraph()
        node = graph.add_node("freedom", NodeType.CONCEPT)
        d = node.to_dict()
        assert d["id"] == node.id
        assert d["label"] == "freedom"
        assert d["type"] == "concept"
        assert "created_at" in d
        assert d["turn_index"] == 0
        assert d["weight"] == 1.0

    def test_metadata_included(self):
        graph = SemanticGraph()
        node = graph.add_node("alpha", NodeType.ENTITY, metadata={"source": "test"})
        assert node.to_dict()["metadata"] == {"source": "test"}


# ── SemanticEdge.to_dict ──────────────────────────────────────────────────────

class TestSemanticEdgeToDict:
    def test_includes_required_keys(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        edge = graph.add_edge(a, b, EdgeType.SUPPORTS)
        d = edge.to_dict()
        assert d["source"] == a.id
        assert d["target"] == b.id
        assert d["type"] == "supports"
        assert d["weight"] == 1.0
        assert "turn_index" in d


# ── ContradictionResult.to_dict ───────────────────────────────────────────────

class TestContradictionResultToDict:
    def test_serializes_all_fields(self):
        result = ContradictionResult(
            found=True,
            path=["a", "b"],
            description="desc",
            severity=0.8,
        )
        d = result.to_dict()
        assert d["found"] is True
        assert d["path"] == ["a", "b"]
        assert d["description"] == "desc"
        assert d["severity"] == pytest.approx(0.8)


# ── SemanticGraph.add_node ────────────────────────────────────────────────────

class TestAddNode:
    def test_creates_new_node(self):
        graph = SemanticGraph()
        node = graph.add_node("concept_x", NodeType.CONCEPT)
        assert node.label == "concept_x"
        assert node.node_type == NodeType.CONCEPT

    def test_dedup_returns_existing_node(self):
        graph = SemanticGraph()
        node1 = graph.add_node("concept_x", NodeType.CONCEPT, weight=0.5)
        node2 = graph.add_node("concept_x", NodeType.CONCEPT, weight=0.9)
        assert node1.id == node2.id
        assert len(graph._nodes) == 1

    def test_dedup_updates_weight_to_max(self):
        graph = SemanticGraph()
        node1 = graph.add_node("concept_x", NodeType.CONCEPT, weight=0.3)
        graph.add_node("concept_x", NodeType.CONCEPT, weight=0.8)
        assert node1.weight == pytest.approx(0.8)

    def test_different_type_creates_separate_node(self):
        graph = SemanticGraph()
        graph.add_node("alpha", NodeType.CONCEPT)
        graph.add_node("alpha", NodeType.ENTITY)
        assert len(graph._nodes) == 2


# ── SemanticGraph.find_nodes_by_label ────────────────────────────────────────

class TestFindNodesByLabel:
    def test_partial_label_match(self):
        graph = SemanticGraph()
        graph.add_node("market pullback", NodeType.TOPIC)
        graph.add_node("market recovery", NodeType.TOPIC)
        graph.add_node("unrelated", NodeType.CONCEPT)
        results = graph.find_nodes_by_label("market")
        assert len(results) == 2

    def test_no_match_returns_empty(self):
        graph = SemanticGraph()
        graph.add_node("alpha", NodeType.CONCEPT)
        assert graph.find_nodes_by_label("zzz") == []


# ── SemanticGraph.find_nodes_by_type ─────────────────────────────────────────

class TestFindNodesByType:
    def test_filters_by_type(self):
        graph = SemanticGraph()
        graph.add_node("c1", NodeType.CONCEPT)
        graph.add_node("e1", NodeType.ENTITY)
        graph.add_node("c2", NodeType.CONCEPT)
        results = graph.find_nodes_by_type(NodeType.CONCEPT)
        assert len(results) == 2
        assert all(n.node_type == NodeType.CONCEPT for n in results)

    def test_empty_graph_returns_empty(self):
        assert SemanticGraph().find_nodes_by_type(NodeType.BOUNDARY) == []


# ── SemanticGraph.get_node ────────────────────────────────────────────────────

class TestGetNode:
    def test_returns_node_by_id(self):
        graph = SemanticGraph()
        node = graph.add_node("alpha", NodeType.CONCEPT)
        assert graph.get_node(node.id) is node

    def test_missing_id_returns_none(self):
        assert SemanticGraph().get_node("nonexistent") is None


# ── SemanticGraph.get_neighbors ───────────────────────────────────────────────

class TestGetNeighbors:
    def test_connected_nodes_returned(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        graph.add_edge(a, b, EdgeType.RELATED_TO)
        neighbors = graph.get_neighbors(a.id)
        assert any(n.id == b.id for n in neighbors)

    def test_isolated_node_returns_empty(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        assert graph.get_neighbors(a.id) == []

    def test_unknown_id_returns_empty(self):
        assert SemanticGraph().get_neighbors("ghost") == []


# ── SemanticGraph.get_edges_between ──────────────────────────────────────────

class TestGetEdgesBetween:
    def test_returns_matching_edges(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        graph.add_edge(a, b, EdgeType.SUPPORTS)
        edges = graph.get_edges_between(a.id, b.id)
        assert len(edges) == 1
        assert edges[0].edge_type == EdgeType.SUPPORTS

    def test_reverse_order_also_matches(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        graph.add_edge(a, b, EdgeType.IMPLIES)
        assert len(graph.get_edges_between(b.id, a.id)) == 1

    def test_no_edge_returns_empty(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        assert graph.get_edges_between(a.id, b.id) == []


# ── SemanticGraph.detect_contradictions ──────────────────────────────────────

class TestDetectContradictions:
    def test_no_contradiction_edge_returns_empty(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.CONCEPT)
        graph.add_edge(a, b, EdgeType.SUPPORTS)
        assert graph.detect_contradictions() == []

    def test_explicit_contradicts_edge_detected(self):
        graph = SemanticGraph()
        a = graph.add_node("claim_A", NodeType.CONCEPT)
        b = graph.add_node("claim_B", NodeType.CONCEPT)
        graph.add_edge(a, b, EdgeType.CONTRADICTS)
        results = graph.detect_contradictions()
        assert len(results) == 1
        assert results[0].found is True
        assert a.id in results[0].path
        assert b.id in results[0].path


# ── SemanticGraph.increment_turn / reset / get_summary ───────────────────────

class TestGraphLifecycle:
    def test_increment_turn(self):
        graph = SemanticGraph()
        assert graph._current_turn == 0
        graph.increment_turn()
        graph.increment_turn()
        assert graph._current_turn == 2

    def test_reset_clears_graph(self):
        graph = SemanticGraph()
        graph.add_node("A", NodeType.CONCEPT)
        graph.increment_turn()
        graph.reset()
        assert len(graph._nodes) == 0
        assert len(graph._edges) == 0
        assert graph._current_turn == 0

    def test_get_summary_counts_nodes_and_edges(self):
        graph = SemanticGraph()
        a = graph.add_node("A", NodeType.CONCEPT)
        b = graph.add_node("B", NodeType.ENTITY)
        graph.add_edge(a, b, EdgeType.RELATED_TO)
        summary = graph.get_summary()
        assert summary["total_nodes"] == 2
        assert summary["total_edges"] == 1

    def test_to_dict_has_nodes_edges_summary(self):
        graph = SemanticGraph()
        graph.add_node("A", NodeType.CONCEPT)
        d = graph.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "summary" in d

    def test_create_semantic_graph_factory(self):
        graph = create_semantic_graph()
        assert isinstance(graph, SemanticGraph)
