"""Tests for early contradiction checks before response generation."""

from __future__ import annotations

from tonesoul.memory.semantic_graph import EdgeType, NodeType, SemanticGraph
from tonesoul.unified_pipeline import UnifiedPipeline


def _build_conflicting_graph() -> SemanticGraph:
    graph = SemanticGraph()
    honesty = graph.add_node("honesty", NodeType.CONCEPT)
    deception = graph.add_node("deception", NodeType.CONCEPT)
    graph.add_edge(honesty, deception, EdgeType.CONTRADICTS)
    return graph


def test_contradiction_description_accessible():
    graph = _build_conflicting_graph()
    contradictions = graph.detect_contradictions()
    assert contradictions

    for contradiction in contradictions:
        description = getattr(contradiction, "description", None)
        if not description and hasattr(contradiction, "to_dict"):
            description = contradiction.to_dict().get("description", "")
        assert isinstance(description, str)
        assert description


def test_pipeline_injects_early_contradiction_warning():
    pipeline = UnifiedPipeline()
    pipeline._semantic_graph = _build_conflicting_graph()

    original = "請保持前後一致"
    updated = pipeline._inject_early_contradiction_warning(original)

    assert updated.startswith("[內在一致性提醒:")
    assert "honesty" in updated
    assert "deception" in updated
    assert updated.endswith(original)
