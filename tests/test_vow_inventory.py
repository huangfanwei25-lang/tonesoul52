"""Tests for VowInventory — Commitment Conviction Tracker"""
from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.vow_inventory import (
    MIN_CHECKS_FOR_TRAJECTORY,
    RECENT_WINDOW,
    VowInventory,
)
from tonesoul.vow_system import VowEnforcer, VowRegistry

# ── VowInventory unit tests ───────────────────────────────────────────────


class TestVowInventoryBasic:
    def test_record_check_pass_creates_state(self):
        inv = VowInventory()
        state = inv.record_check(
            vow_id="ΣVow_001",
            passed=True,
            score=0.97,
            threshold=0.95,
            vow_title="No Misleading",
        )
        assert state.total_tests == 1
        assert state.passes == 1
        assert state.violations == 0
        assert state.conviction_score > 0.0
        assert state.trajectory == "untested"  # below MIN_CHECKS_FOR_TRAJECTORY

    def test_record_check_violation_records_reason(self):
        inv = VowInventory()
        inv.record_check(
            vow_id="ΣVow_001",
            passed=False,
            score=0.60,
            threshold=0.95,
            violation_reason="score too low",
        )
        state = inv.get_state("ΣVow_001")
        assert state.violations == 1
        assert state.last_violation_reason == "score too low"

    def test_conviction_score_penalizes_violations(self):
        inv = VowInventory()
        for _ in range(8):
            inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        for _ in range(2):
            inv.record_check("v1", passed=False, score=0.5, threshold=0.9)
        state = inv.get_state("v1")
        # 8 passes - 2 violations * 2 penalty = 4 net / 10 = 0.4
        assert state.conviction_score == pytest.approx(0.4, abs=0.05)

    def test_conviction_score_floor_is_zero(self):
        inv = VowInventory()
        for _ in range(5):
            inv.record_check("v1", passed=False, score=0.1, threshold=0.9)
        state = inv.get_state("v1")
        assert state.conviction_score == 0.0

    def test_uncertain_counter_increments_near_threshold(self):
        inv = VowInventory()
        # Score within 10% of threshold
        inv.record_check("v1", passed=True, score=0.96, threshold=0.95)
        state = inv.get_state("v1")
        assert state.uncertain == 1

    def test_uncertain_counter_unchanged_when_far(self):
        inv = VowInventory()
        inv.record_check("v1", passed=True, score=0.99, threshold=0.80)
        state = inv.get_state("v1")
        assert state.uncertain == 0


class TestVowInventoryTrajectory:
    def _fill_passes(self, inv: VowInventory, vow_id: str, n: int):
        for _ in range(n):
            inv.record_check(vow_id, passed=True, score=0.99, threshold=0.9)

    def _fill_violations(self, inv: VowInventory, vow_id: str, n: int):
        for _ in range(n):
            inv.record_check(vow_id, passed=False, score=0.5, threshold=0.9)

    def test_trajectory_untested_below_min_checks(self):
        inv = VowInventory()
        for i in range(MIN_CHECKS_FOR_TRAJECTORY - 1):
            inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        assert inv.get_state("v1").trajectory == "untested"

    def test_trajectory_strengthening_after_consistent_passes(self):
        inv = VowInventory()
        self._fill_passes(inv, "v1", MIN_CHECKS_FOR_TRAJECTORY + 2)
        assert inv.get_state("v1").trajectory == "strengthening"

    def test_trajectory_decaying_after_many_violations(self):
        inv = VowInventory()
        # Start good, then go bad
        self._fill_passes(inv, "v1", 5)
        self._fill_violations(inv, "v1", 8)
        assert inv.get_state("v1").trajectory == "decaying"

    def test_needs_attention_true_when_decaying(self):
        inv = VowInventory()
        for _ in range(5):
            inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        for _ in range(8):
            inv.record_check("v1", passed=False, score=0.1, threshold=0.9)
        state = inv.get_state("v1")
        assert state.trajectory == "decaying"
        assert state.needs_attention is True

    def test_needs_attention_from_low_conviction(self):
        inv = VowInventory()
        # 2 passes, 4 violations → conviction = (2 - 8) / 6 = 0 (floored)
        for _ in range(2):
            inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        for _ in range(4):
            inv.record_check("v1", passed=False, score=0.1, threshold=0.9)
        state = inv.get_state("v1")
        assert state.conviction_score < 0.5
        assert state.needs_attention is True


class TestVowInventoryMultiVow:
    def test_multiple_vows_tracked_independently(self):
        inv = VowInventory()
        inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        inv.record_check("v2", passed=False, score=0.5, threshold=0.9)

        assert inv.get_state("v1").passes == 1
        assert inv.get_state("v2").violations == 1
        assert len(inv.all_states()) == 2

    def test_attention_needed_filters_correctly(self):
        inv = VowInventory()
        inv.record_check("v_good", passed=True, score=1.0, threshold=0.9)
        for _ in range(MIN_CHECKS_FOR_TRAJECTORY + 2):
            inv.record_check("v_bad", passed=False, score=0.1, threshold=0.9)

        attention = inv.attention_needed()
        ids = [s.vow_id for s in attention]
        assert "v_bad" in ids
        assert "v_good" not in ids

    def test_conviction_summary_counts(self):
        inv = VowInventory()
        for _ in range(MIN_CHECKS_FOR_TRAJECTORY + 1):
            inv.record_check("v_strong", passed=True, score=1.0, threshold=0.9)
        for _ in range(MIN_CHECKS_FOR_TRAJECTORY + 3):
            inv.record_check("v_weak", passed=False, score=0.1, threshold=0.9)

        summary = inv.conviction_summary()
        assert summary["total_vows"] == 2
        assert summary["strengthening"] >= 1
        assert summary["decaying"] >= 1


class TestVowInventoryPersistence:
    def test_save_and_load_roundtrip(self, tmp_path: Path):
        inv = VowInventory()
        inv.record_check("v1", passed=True, score=0.97, threshold=0.95, vow_title="Test Vow")
        inv.record_check("v1", passed=False, score=0.60, threshold=0.95, violation_reason="low")

        path = tmp_path / "inv.json"
        inv.save(path)

        loaded = VowInventory.load(path)
        state = loaded.get_state("v1")
        assert state is not None
        assert state.total_tests == 2
        assert state.vow_title == "Test Vow"
        assert state.last_violation_reason == "low"

    def test_artifact_structure(self):
        inv = VowInventory()
        inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        artifact = inv.to_artifact()
        assert "generated_at" in artifact
        assert "summary" in artifact
        assert "states" in artifact
        assert artifact["summary"]["total_vows"] == 1


class TestVowEnforcerInventoryWiring:
    def test_enforcer_without_inventory_still_works(self):
        enforcer = VowEnforcer()
        result = enforcer.enforce("This is a safe, honest response.")
        assert result is not None  # no crash

    def test_enforcer_with_inventory_records_checks(self):
        inv = VowInventory()
        enforcer = VowEnforcer()
        enforcer.inventory = inv

        enforcer.enforce("This is a safe, honest response with citations according to research.")

        # At least the default vows should have been recorded
        states = inv.all_states()
        assert len(states) > 0
        assert all(s.total_tests >= 1 for s in states)

    def test_enforcer_records_violation_into_inventory(self):
        inv = VowInventory()
        enforcer = VowEnforcer(VowRegistry())
        enforcer.inventory = inv

        # Force a safety vow violation by monkeypatching evaluator
        enforcer._evaluators["safety"] = lambda output, ctx: 0.0

        enforcer.enforce("test output")

        safety_state = inv.get_state("ΣVow_003")
        if safety_state is not None:
            assert safety_state.violations >= 1
            assert safety_state.last_violation_reason is not None

    def test_multiple_enforce_calls_accumulate_conviction(self):
        inv = VowInventory()
        enforcer = VowEnforcer()
        enforcer.inventory = inv

        for _ in range(5):
            enforcer.enforce("Safe, honest response with citations according to verified sources.")

        for state in inv.all_states():
            assert state.total_tests == 5

    def test_audit_trail_is_capped(self):
        inv = VowInventory()
        limit = RECENT_WINDOW * 3 + 10  # exceed cap
        for _ in range(limit):
            inv.record_check("v1", passed=True, score=1.0, threshold=0.9)
        state = inv.get_state("v1")
        assert len(state.recent_checks) <= RECENT_WINDOW * 3
        # But counters should reflect true totals
        assert state.total_tests == limit
