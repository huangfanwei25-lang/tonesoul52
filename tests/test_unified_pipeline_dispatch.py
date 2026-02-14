from __future__ import annotations

from tonesoul.unified_pipeline import UnifiedPipeline


def test_detect_semantic_tension_includes_prior_carryover() -> None:
    pipeline = UnifiedPipeline()
    profile = pipeline._detect_semantic_tension(
        tension_score=0.40,
        resonance_state="resonance",
        loop_detected=False,
        prior_tension={"delta_t": 0.80},
    )

    assert profile["tension_score"] == 0.4
    assert profile["adjusted_tension"] > profile["tension_score"]
    assert "prior_tension_carryover" in profile["reasons"]


def test_resolve_dispatch_state_conflict_for_loop() -> None:
    pipeline = UnifiedPipeline()
    profile = pipeline._detect_semantic_tension(
        tension_score=0.30,
        resonance_state="resonance",
        loop_detected=True,
        prior_tension=None,
    )
    state = pipeline._resolve_dispatch_state(profile)
    assert state == "C"


def test_process_exposes_dispatch_trace_in_metadata(monkeypatch) -> None:
    pipeline = UnifiedPipeline()

    monkeypatch.setattr(pipeline, "_get_gemini", lambda: None)
    monkeypatch.setattr(pipeline, "_get_council", lambda: None)
    monkeypatch.setattr(pipeline, "_get_tonebridge", lambda: None)
    monkeypatch.setattr(pipeline, "_get_deliberation", lambda: None)
    monkeypatch.setattr(pipeline, "_get_trajectory", lambda: None)
    monkeypatch.setattr(pipeline, "_get_commit_stack", lambda: None)
    monkeypatch.setattr(pipeline, "_get_commit_extractor", lambda: None)
    monkeypatch.setattr(pipeline, "_get_rupture_detector", lambda: None)
    monkeypatch.setattr(pipeline, "_get_semantic_graph", lambda: None)
    monkeypatch.setattr(pipeline, "_get_value_accumulator", lambda: None)
    monkeypatch.setattr(pipeline, "_get_visual_chain", lambda: None)

    result = pipeline.process(
        user_message="test message",
        history=[],
        full_analysis=False,
        prior_tension={"delta_t": 0.9},
    )

    assert result.dispatch_trace["state"] in {"A", "B", "C"}
    assert result.trajectory_analysis["dispatch"]["state"] == result.dispatch_trace["state"]
    assert result.council_verdict["metadata"]["dispatch_state"] == result.dispatch_trace["state"]
