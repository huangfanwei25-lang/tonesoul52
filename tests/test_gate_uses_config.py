"""POAV gate thresholds must come from SOUL config, not hardcoded literals.

Regression: `unified_pipeline._enforce_poav_gate` hardcoded
`threshold = 0.92 if high_risk_mode else 0.70`, so `soul_config.RiskConfig`
(the documented single source of truth) was unread — flipping config would not
move the runtime gate. These tests patch SOUL to sentinel values and assert the
gate's recorded threshold follows config on BOTH risk paths; they fail against
the old literal pipeline.
"""

from __future__ import annotations

import dataclasses

import pytest

from tonesoul.soul_config import SOUL, RiskConfig


def _patch_soul(monkeypatch: pytest.MonkeyPatch, *, high: float, low: float) -> None:
    sentinel = dataclasses.replace(
        SOUL,
        risk=dataclasses.replace(
            SOUL.risk,
            governance_gate_score=high,
            governance_gate_score_low_risk=low,
        ),
    )
    monkeypatch.setattr("tonesoul.unified_pipeline.SOUL", sentinel)


def test_low_risk_gate_is_its_own_field_and_looser_than_high_risk() -> None:
    rc = RiskConfig()
    # The low-risk gate is a dedicated field (not aliased to entropy_check_threshold,
    # which is a different semantic that merely shares the 0.70 value today).
    assert rc.governance_gate_score_low_risk == 0.70
    assert rc.governance_gate_score_low_risk < rc.governance_gate_score


def test_poav_gate_low_risk_threshold_follows_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    _patch_soul(monkeypatch, high=0.93, low=0.71)

    from tonesoul.unified_pipeline import UnifiedPipeline

    pipeline = UnifiedPipeline()
    dispatch_trace: dict = {}
    pipeline._enforce_poav_gate(
        response="A short, low-risk reply with no operational content.",
        current_zone="safe",
        dispatch_trace=dispatch_trace,
    )

    poav = dispatch_trace.get("poav") or {}
    assert poav.get("high_risk_mode") is False
    # Old hardcoded code would record 0.70 here regardless of config.
    assert poav.get("threshold") == pytest.approx(0.71)


def test_poav_gate_high_risk_threshold_follows_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    _patch_soul(monkeypatch, high=0.93, low=0.71)

    from tonesoul.unified_pipeline import UnifiedPipeline

    pipeline = UnifiedPipeline()
    dispatch_trace: dict = {}
    pipeline._enforce_poav_gate(
        response="Do it now.",
        current_zone="danger",
        dispatch_trace=dispatch_trace,
    )

    poav = dispatch_trace.get("poav") or {}
    assert poav.get("high_risk_mode") is True
    # Old hardcoded code would record 0.92 here regardless of config.
    assert poav.get("threshold") == pytest.approx(0.93)
