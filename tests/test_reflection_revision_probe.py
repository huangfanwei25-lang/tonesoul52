"""Tests for the reflection-revision probe (measurement instrument).

CI-safe: only the deterministic control arm runs (no model). These pin the
metric and that the control baseline is clean — so that any future LLM-arm
delta is attributable to the model, not the harness. The LLM noise-floor /
outcome arms require a serving model and are exercised by running the probe's
main() with Ollama up; they are intentionally not asserted in CI.
"""

from __future__ import annotations

from pathlib import Path

from tools.probe.reflection_revision_probe import content_delta, run_probe


def test_content_delta_identical_is_zero() -> None:
    assert content_delta("the same words here", "the same words here") == 0.0


def test_content_delta_disjoint_is_one() -> None:
    assert content_delta("alpha beta gamma", "delta epsilon zeta") == 1.0


def test_content_delta_partial_overlap_between_zero_and_one() -> None:
    d = content_delta("alpha beta gamma", "alpha beta delta")
    assert 0.0 < d < 1.0


def test_content_delta_empty_both_is_zero() -> None:
    assert content_delta("", "") == 0.0


def test_control_arm_is_deterministic(monkeypatch, tmp_path: Path) -> None:
    # The deterministic fallback must yield delta 0.0 for identical context, so
    # the LLM arms have a clean baseline to be measured against.
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.dream_engine import build_dream_engine

    engine = build_dream_engine(db_path=tmp_path / "soul.db")
    report = run_probe(engine, use_llm=False)

    assert report["control_delta"] == 0.0
    assert report["control_is_clean"] is True
    # LLM arms must NOT have run without a model — no faked numbers.
    assert report["llm_arms_ran"] is False
    assert report["noise_floor_delta"] is None
    assert report["outcome_delta"] is None
    assert report["outcome_exceeds_noise"] is None
