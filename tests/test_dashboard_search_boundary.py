from __future__ import annotations

from apps.dashboard.frontend.utils.search import build_search_context_boundary_cue


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
