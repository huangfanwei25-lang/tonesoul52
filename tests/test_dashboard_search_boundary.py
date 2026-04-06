from __future__ import annotations

from apps.dashboard.frontend.utils.search import (
    build_search_context_boundary_cue,
    build_search_context_from_hits,
    build_search_preview_model,
)


def test_search_context_boundary_cue_defaults_to_operator_truth_first():
    result = build_search_context_boundary_cue(enable_local=False, enable_web=False)

    assert result["mode"] == "off"
    assert "Search is off by default." == result["summary"]
    assert "Tier 0 / Tier 1" in result["boundary"]


def test_search_context_boundary_cue_marks_web_as_weakest_surface():
    result = build_search_context_boundary_cue(enable_local=False, enable_web=True)

    assert result["mode"] == "web"
    assert "external context" in result["summary"]
    assert "weakest surface" in result["boundary"]


def test_build_search_preview_model_keeps_auxiliary_provenance_visible():
    result = build_search_preview_model(
        query="session-start",
        local_hits=[
            {
                "path": "docs/AI_QUICKSTART.md",
                "snippet": "Run start_agent_session first.",
            }
        ],
        web_hits=[
            {
                "title": "External note",
                "url": "https://example.test/note",
                "snippet": "External context stays secondary.",
            }
        ],
    )

    assert result["present"] is True
    assert result["query"] == "session-start"
    assert result["items"][0]["source"] == "local"
    assert result["items"][1]["source"] == "web"
    assert "Tier 0 / Tier 1 / Tier 2" in result["operator_rule"]


def test_build_search_context_from_hits_preserves_local_and_web_sections():
    context = build_search_context_from_hits(
        local_hits=[{"path": "docs/README.md", "snippet": "Local section"}],
        web_hits=[{"title": "Web title", "url": "https://example.test", "snippet": "Web section"}],
    )

    assert "Local search hits:" in context
    assert "docs/README.md" in context
    assert "Web search hits:" in context
    assert "Web title" in context
