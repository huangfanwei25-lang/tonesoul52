from __future__ import annotations

import json
from pathlib import Path

import pytest

import tonesoul.yss_pipeline as yss_pipeline
from tonesoul.yss_unified_adapter import (
    _clamp_unit,
    _dispatch_state_to_decision_mode,
    _extract_gate_pass_rate,
    _extract_poav_total,
    _safe_float,
    build_multi_persona_eval_snapshot,
    build_unified_seed,
    write_multi_persona_eval_snapshot,
)


# ─── _clamp_unit ─────────────────────────────────────────────────────────────

class TestClampUnit:
    def test_zero_stays_zero(self):
        assert _clamp_unit(0.0) == 0.0

    def test_one_stays_one(self):
        assert _clamp_unit(1.0) == 1.0

    def test_above_one_clamped(self):
        assert _clamp_unit(1.5) == 1.0

    def test_below_zero_clamped(self):
        assert _clamp_unit(-0.1) == 0.0

    def test_mid_value_unchanged(self):
        assert _clamp_unit(0.75) == 0.75


# ─── _safe_float ─────────────────────────────────────────────────────────────

class TestSafeFloat:
    def test_numeric_string_converted(self):
        assert _safe_float("0.5") == 0.5

    def test_int_converted(self):
        assert _safe_float(3) == 3.0

    def test_invalid_returns_default(self):
        assert _safe_float("bad") == 0.0

    def test_none_returns_default(self):
        assert _safe_float(None) == 0.0

    def test_custom_default(self):
        assert _safe_float("bad", default=0.7) == 0.7


# ─── _dispatch_state_to_decision_mode ────────────────────────────────────────

class TestDispatchStateToDecisionMode:
    def test_state_c_is_strict(self):
        assert _dispatch_state_to_decision_mode("C") == "strict"

    def test_state_b_is_guarded(self):
        assert _dispatch_state_to_decision_mode("B") == "guarded"

    def test_state_a_is_normal(self):
        assert _dispatch_state_to_decision_mode("A") == "normal"

    def test_unknown_state_is_normal(self):
        assert _dispatch_state_to_decision_mode("X") == "normal"

    def test_empty_defaults_to_normal(self):
        assert _dispatch_state_to_decision_mode("") == "normal"

    def test_lowercase_c_is_strict(self):
        assert _dispatch_state_to_decision_mode("c") == "strict"


# ─── _extract_poav_total ─────────────────────────────────────────────────────

class TestExtractPoavTotal:
    def test_extracts_from_results(self):
        gate_report = {
            "results": [
                {
                    "gate": "poav_gate",
                    "passed": True,
                    "details": {"components": {"total": 0.83}},
                }
            ]
        }
        assert _extract_poav_total(gate_report) == pytest.approx(0.83)

    def test_no_poav_gate_returns_default(self):
        gate_report = {"results": [{"gate": "guardian_gate", "passed": True}]}
        assert _extract_poav_total(gate_report) == 0.70

    def test_no_results_returns_default(self):
        assert _extract_poav_total({}) == 0.70

    def test_clamps_above_one(self):
        gate_report = {
            "results": [
                {
                    "gate": "poav_gate",
                    "details": {"components": {"total": 1.5}},
                }
            ]
        }
        assert _extract_poav_total(gate_report) == 1.0

    def test_non_list_results_returns_default(self):
        assert _extract_poav_total({"results": "bad"}) == 0.70


# ─── _extract_gate_pass_rate ─────────────────────────────────────────────────

class TestExtractGatePassRate:
    def test_all_passed(self):
        gate_report = {
            "results": [
                {"gate": "a", "passed": True},
                {"gate": "b", "passed": True},
            ]
        }
        assert _extract_gate_pass_rate(gate_report) == 1.0

    def test_half_passed(self):
        gate_report = {
            "results": [
                {"gate": "a", "passed": True},
                {"gate": "b", "passed": False},
            ]
        }
        assert _extract_gate_pass_rate(gate_report) == 0.5

    def test_empty_results_returns_default(self):
        assert _extract_gate_pass_rate({"results": []}) == 0.90

    def test_no_results_key_returns_default(self):
        assert _extract_gate_pass_rate({}) == 0.90

    def test_non_dict_items_skipped(self):
        gate_report = {"results": ["bad", {"gate": "a", "passed": True}]}
        assert _extract_gate_pass_rate(gate_report) == 1.0


# ─── build_unified_seed ──────────────────────────────────────────────────────

class TestBuildUnifiedSeed:
    def test_dispatch_state_c_maps_strict(self):
        seed = build_unified_seed({
            "user_message": "test",
            "dispatch_trace": {"state": "C"},
        })
        assert seed["decision_mode"] == "strict"

    def test_dispatch_state_b_maps_guarded(self):
        seed = build_unified_seed({
            "user_message": "test",
            "dispatch_trace": {"state": "B"},
        })
        assert seed["decision_mode"] == "guarded"

    def test_dispatch_state_a_maps_normal(self):
        seed = build_unified_seed({"user_message": "test"})
        assert seed["decision_mode"] == "normal"

    def test_history_count_counted(self):
        seed = build_unified_seed({
            "history": [{"role": "user"}, {"role": "assistant"}],
        })
        assert seed["payload"]["history_count"] == 2

    def test_non_list_history_zero(self):
        seed = build_unified_seed({"history": "not-a-list"})
        assert seed["payload"]["history_count"] == 0

    def test_persona_name_sets_domain(self):
        seed = build_unified_seed({
            "persona_config": {"name": "Ops Guardian"},
        })
        assert seed["domain"] == "ops_guardian"

    def test_no_persona_domain_general(self):
        seed = build_unified_seed({})
        assert seed["domain"] == "general"

    def test_custom_roles_counted(self):
        seed = build_unified_seed({
            "persona_config": {"custom_roles": ["r1", "r2"]},
        })
        assert seed["payload"]["custom_role_count"] == 2

    def test_task_truncated_to_120_chars(self):
        long_msg = "x" * 200
        seed = build_unified_seed({"user_message": long_msg})
        assert len(seed["task"]) == 120

    def test_empty_message_uses_fallback_task(self):
        seed = build_unified_seed({})
        assert "Handle unified runtime request" in seed["task"]

    def test_required_keys_present(self):
        seed = build_unified_seed({})
        for key in ("task", "objective", "domain", "decision_mode", "assumptions",
                    "constraints", "payload"):
            assert key in seed

    def test_council_mode_default_hybrid(self):
        seed = build_unified_seed({})
        assert seed["payload"]["council_mode"] == "hybrid"

    def test_council_mode_preserved(self):
        seed = build_unified_seed({"council_mode": "strict"})
        assert seed["payload"]["council_mode"] == "strict"


# ─── build_multi_persona_eval_snapshot ───────────────────────────────────────

class TestBuildMultiPersonaEvalSnapshot:
    def test_all_modes_present(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        for mode in ("A", "B", "C"):
            assert mode in snapshot["modes"]

    def test_mode_a_has_all_metrics(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        metrics = snapshot["modes"]["A"]
        for key in ("task_quality", "safety_pass_rate", "consistency_at_session",
                    "disagreement_utility", "token_latency_cost_index", "p95_latency_ms"):
            assert key in metrics

    def test_mode_c_has_higher_task_quality_than_a(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        assert snapshot["modes"]["C"]["task_quality"] >= snapshot["modes"]["A"]["task_quality"]

    def test_promotion_decision_from_a(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        assert snapshot["promotion_decision"]["from_mode"] == "A"

    def test_generated_at_provided(self):
        snapshot = build_multi_persona_eval_snapshot(
            gate_report=None, generated_at="2026-04-22T00:00:00Z"
        )
        assert snapshot["generated_at"] == "2026-04-22T00:00:00Z"

    def test_generated_at_auto_set_when_none(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        assert snapshot["generated_at"].endswith("Z")

    def test_high_tension_increases_latency(self):
        low_tension = build_multi_persona_eval_snapshot(
            gate_report=None, dispatch_trace={"adjusted_tension": 0.0}
        )
        high_tension = build_multi_persona_eval_snapshot(
            gate_report=None, dispatch_trace={"adjusted_tension": 1.0}
        )
        assert high_tension["modes"]["A"]["p95_latency_ms"] > low_tension["modes"]["A"]["p95_latency_ms"]

    def test_poav_total_reflected_in_task_quality(self):
        snapshot = build_multi_persona_eval_snapshot(
            gate_report={
                "results": [
                    {
                        "gate": "poav_gate",
                        "details": {"components": {"total": 0.95}},
                    }
                ]
            }
        )
        assert snapshot["modes"]["A"]["task_quality"] == pytest.approx(0.95)

    def test_cost_gate_structure_present(self):
        snapshot = build_multi_persona_eval_snapshot(gate_report=None)
        assert "c_vs_a" in snapshot["cost_gate"]
        assert "b_vs_a" in snapshot["cost_gate"]

    def test_full_scenario_non_null_metrics(self):
        snapshot = build_multi_persona_eval_snapshot(
            gate_report={
                "results": [
                    {"gate": "poav_gate", "passed": True,
                     "details": {"components": {"total": 0.83}}},
                    {"gate": "guardian_gate", "passed": True},
                    {"gate": "mercy_gate", "passed": True},
                ]
            },
            dispatch_trace={"adjusted_tension": 0.62},
        )
        for mode in ("A", "B", "C"):
            metrics = snapshot["modes"][mode]
            for key in ("task_quality", "safety_pass_rate", "consistency_at_session",
                        "disagreement_utility", "token_latency_cost_index", "p95_latency_ms"):
                assert metrics[key] is not None


# ─── write_multi_persona_eval_snapshot ───────────────────────────────────────

class TestWriteMultiPersonaEvalSnapshot:
    def test_creates_file(self, tmp_path):
        payload = build_multi_persona_eval_snapshot(gate_report={})
        path = write_multi_persona_eval_snapshot(tmp_path / "out.json", payload)
        assert Path(path).exists()

    def test_written_file_is_valid_json(self, tmp_path):
        payload = build_multi_persona_eval_snapshot(gate_report={})
        path = write_multi_persona_eval_snapshot(tmp_path / "snap.json", payload)
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
        assert loaded["baseline_mode"] == "A"

    def test_creates_parent_dirs(self, tmp_path):
        nested = tmp_path / "deep" / "dir" / "snap.json"
        write_multi_persona_eval_snapshot(nested, {"baseline_mode": "A"})
        assert nested.exists()


# ─── run_pipeline_from_unified_request ───────────────────────────────────────

def test_run_pipeline_from_unified_request_injects_seed_defaults(monkeypatch) -> None:
    captured = {}

    def _fake_run_pipeline(config):
        captured["task"] = config.task
        captured["decision_mode"] = config.decision_mode
        return {"run_dir": "dummy"}

    monkeypatch.setattr(yss_pipeline, "run_pipeline", _fake_run_pipeline)
    result = yss_pipeline.run_pipeline_from_unified_request({
        "user_message": "請給我可審計的方案",
        "dispatch_trace": {"state": "B"},
    })

    assert captured["task"]
    assert captured["decision_mode"] == "guarded"
    assert result["unified_seed"]["decision_mode"] == "guarded"
