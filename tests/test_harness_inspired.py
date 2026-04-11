"""Tests for Harness Engineering-inspired features.

Phase transition model, intentional forgetting, and governance retro.
"""

from __future__ import annotations

from tonesoul.governance.retro import (
    RetroConfig,
    RetroResult,
    run_retro,
    should_run_retro,
)
from tonesoul.memory.crystallizer import (
    PHASE_TRANSITION_MAP,
    Crystal,
    SeedStage,
)
from tonesoul.memory.write_gateway import (
    _intentional_forgetting_gate,
)

# ---------------------------------------------------------------------------
# Phase Transition Model
# ---------------------------------------------------------------------------


class TestPhaseTransition:
    """Crystal phase maps ETCL stages to Ice/Water/Steam/Crystal."""

    def test_draft_is_ice(self):
        c = Crystal(rule="test", source_pattern="x", weight=0.5, created_at="2026-01-01")
        assert c.phase == "ice"

    def test_retrieval_is_water(self):
        c = Crystal(
            rule="test",
            source_pattern="x",
            weight=0.5,
            created_at="2026-01-01",
            stage=SeedStage.T2_RETRIEVAL.value,
        )
        assert c.phase == "water"

    def test_apply_is_steam(self):
        c = Crystal(
            rule="test",
            source_pattern="x",
            weight=0.5,
            created_at="2026-01-01",
            stage=SeedStage.T4_APPLY.value,
        )
        assert c.phase == "steam"

    def test_canonical_is_crystal(self):
        c = Crystal(
            rule="test",
            source_pattern="x",
            weight=0.5,
            created_at="2026-01-01",
            stage=SeedStage.T6_CANONICAL.value,
        )
        assert c.phase == "crystal"

    def test_phase_in_to_dict(self):
        c = Crystal(
            rule="test",
            source_pattern="x",
            weight=0.5,
            created_at="2026-01-01",
            stage=SeedStage.T3_ALIGN.value,
        )
        d = c.to_dict()
        assert d["phase"] == "water"

    def test_all_stages_mapped(self):
        for stage in SeedStage:
            assert stage.value in PHASE_TRANSITION_MAP


# ---------------------------------------------------------------------------
# Intentional Forgetting Gate
# ---------------------------------------------------------------------------


class TestIntentionalForgetting:
    """Content not worth remembering should be filtered out."""

    def test_empty_content_rejected(self):
        keep, reasons = _intentional_forgetting_gate({"content": ""})
        assert not keep
        assert "content_too_short" in reasons

    def test_trivially_short_rejected(self):
        keep, reasons = _intentional_forgetting_gate({"content": "hi"})
        assert not keep
        assert "content_too_short" in reasons

    def test_ephemeral_tag_rejected(self):
        keep, reasons = _intentional_forgetting_gate(
            {
                "content": "some debug output that is long enough",
                "tags": ["debug", "ephemeral"],
            }
        )
        assert not keep
        assert "ephemeral_tag" in reasons

    def test_passive_noise_rejected(self):
        keep, reasons = _intentional_forgetting_gate(
            {
                "content": "background noise observation text",
                "observation_mode": "passive_noise",
            }
        )
        assert not keep
        assert "passive_noise" in reasons

    def test_valid_content_passes(self):
        keep, reasons = _intentional_forgetting_gate(
            {
                "content": "This is meaningful governance insight from council deliberation.",
                "tags": ["governance", "council"],
            }
        )
        assert keep
        assert reasons == []

    def test_summary_field_counts(self):
        """Summary field is also checked for length."""
        keep, _ = _intentional_forgetting_gate({"summary": "a meaningful summary of events"})
        assert keep


# ---------------------------------------------------------------------------
# Governance Retro
# ---------------------------------------------------------------------------


class TestGovernanceRetro:
    """Retro trigger and execution."""

    def test_trigger_by_soul_integral(self):
        should, reason = should_run_retro(soul_integral=0.60)
        assert should
        assert "soul_integral" in reason

    def test_trigger_by_sessions(self):
        should, reason = should_run_retro(sessions_since_last_retro=12)
        assert should
        assert "sessions" in reason

    def test_no_trigger_when_calm(self):
        should, reason = should_run_retro(soul_integral=0.2, sessions_since_last_retro=3)
        assert not should

    def test_custom_config(self):
        cfg = RetroConfig(soul_integral_threshold=0.30)
        should, _ = should_run_retro(soul_integral=0.35, config=cfg)
        assert should

    def test_run_retro_minimal(self):
        result = run_retro(dry_run=True)
        assert result.executed_at
        assert isinstance(result.notes, list)
        assert len(result.notes) >= 1

    def test_run_retro_with_crystals(self):
        crystals = [
            Crystal(
                rule="avoid X",
                source_pattern="p1",
                weight=0.8,
                created_at="2026-01-01",
                freshness_score=0.15,
                access_count=1,
            ),
            Crystal(
                rule="prefer Y",
                source_pattern="p2",
                weight=0.7,
                created_at="2026-01-01",
                freshness_score=0.90,
                access_count=5,
            ),
        ]
        result = run_retro(crystals=crystals, dry_run=True)
        assert result.crystals_decayed >= 1  # first crystal is stale
        assert result.crystals_promoted >= 1  # second crystal is active + high access

    def test_run_retro_with_enforcement_log(self):
        log = [
            {"step": "soul_band", "level": "alert"},
            {"step": "vow_block", "flags": ["truth"]},
            {"step": "drift_caution_inject", "caution_bias": 0.7},
        ]
        result = run_retro(enforcement_log=log, dry_run=True)
        assert result.enforcement_events_archived >= 2  # soul_band + drift_caution

    def test_retro_result_to_dict(self):
        result = RetroResult(
            executed_at="2026-04-12T00:00:00Z",
            crystals_decayed=2,
            notes=["test"],
        )
        d = result.to_dict()
        assert d["crystals_decayed"] == 2
        assert d["executed_at"] == "2026-04-12T00:00:00Z"

    def test_retro_config_from_dict(self):
        cfg = RetroConfig.from_dict({"soul_integral_threshold": 0.40, "max_stale_days": 7})
        assert cfg.soul_integral_threshold == 0.40
        assert cfg.max_stale_days == 7
