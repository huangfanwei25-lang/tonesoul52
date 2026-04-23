from __future__ import annotations

from tonesoul.true_verification_summary import (
    summarize_long_run_payload,
    summarize_schedule_payload,
)


def test_summarize_schedule_payload_reduces_results_and_state_to_summary() -> None:
    payload = {
        "generated_at": "2026-03-08T18:00:00Z",
        "overall_ok": True,
        "profile": "security_watch",
        "config": {"max_cycles": 2},
        "results": [
            {
                "cycle": 1,
                "duration_ms": 1200,
                "overall_ok": True,
                "registry_batch": {
                    "selected_entry_count": 1,
                    "selected_entry_ids": ["osv"],
                    "selected_url_count": 2,
                    "warnings": ["none"],
                },
                "autonomous_payload": {
                    "overall_ok": True,
                    "urls_ingested": 2,
                    "runtime_state": {
                        "session_id": "wakeup-001",
                        "next_cycle": 3,
                        "consecutive_failures": 1,
                        "resumed": True,
                        "state_path": "memory/autonomous/dream_wakeup_state.json",
                    },
                    "wakeup_payload": {
                        "overall_status": "ok",
                        "results": [
                            {
                                "cycle": 3,
                                "status": "ok",
                                "summary": {
                                    "scribe_evaluated": True,
                                    "scribe_triggered": True,
                                    "scribe_status": "generated",
                                    "scribe_generation_mode": "template_assist",
                                    "scribe_state_document_posture": (
                                        "pressure_without_counterweight"
                                    ),
                                    "scribe_anchor_status_line": (
                                        "anchor | [T1] tension: observed grounding..."
                                    ),
                                    "scribe_problem_route_status_line": (
                                        "route | family=F1_grounding_evidence_integrity "
                                        "invariant=observed_history_grounding "
                                        "repair=anchor_and_boundary_guardrail"
                                    ),
                                    "scribe_problem_route_secondary_labels": (
                                        "F6_semantic_role_boundary_integrity,"
                                        "F4_execution_contract_integrity"
                                    ),
                                    "scribe_latest_available_source": "chronicle_pair",
                                },
                            }
                        ],
                    },
                    "dashboard_payload": {"huge": ["x"] * 50},
                },
                "tension_budget": {
                    "status": "ok",
                    "governance_breached": False,
                    "llm_breached": True,
                    "llm_breach_reasons": ["timeout"],
                    "observation": {
                        "observed_cycles": 2,
                        "council_count": 3,
                        "llm_preflight_timeout_count": 1,
                        "max_consecutive_failure_count": 2,
                    },
                },
            }
        ],
        "state": {
            "cycles_run": 4,
            "entry_states": {"osv": {"last_outcome": "ok"}},
            "category_states": {"vuln": {"last_budget_status": "ok"}},
            "llm_backoff": {"backoff_until_cycle": 3, "last_status": "active"},
        },
    }

    summary = summarize_schedule_payload(payload)

    assert summary == {
        "generated_at": "2026-03-08T18:00:00Z",
        "overall_ok": True,
        "profile": "security_watch",
        "config": {"max_cycles": 2},
        "result_count": 1,
        "latest_result": {
            "cycle": 1,
            "duration_ms": 1200,
            "overall_ok": True,
            "registry_batch": {
                "selected_entry_count": 1,
                "selected_url_count": 2,
                "selected_entry_ids": ["osv"],
                "warnings": ["none"],
            },
            "autonomous_payload": {
                "overall_ok": True,
                "urls_ingested": 2,
                "runtime_state": {
                    "session_id": "wakeup-001",
                    "next_cycle": 3,
                    "consecutive_failures": 1,
                    "resumed": True,
                    "state_path": "memory/autonomous/dream_wakeup_state.json",
                },
                "wakeup_summary": {
                    "overall_status": "ok",
                    "result_count": 1,
                    "latest_cycle": 3,
                    "latest_status": "ok",
                    "scribe_evaluated": True,
                    "scribe_triggered": True,
                    "scribe_status": "generated",
                    "scribe_generation_mode": "template_assist",
                    "scribe_state_document_posture": "pressure_without_counterweight",
                    "scribe_anchor_status_line": "anchor | [T1] tension: observed grounding...",
                    "scribe_problem_route_status_line": (
                        "route | family=F1_grounding_evidence_integrity "
                        "invariant=observed_history_grounding "
                        "repair=anchor_and_boundary_guardrail"
                    ),
                    "scribe_problem_route_secondary_labels": (
                        "F6_semantic_role_boundary_integrity," "F4_execution_contract_integrity"
                    ),
                    "scribe_latest_available_source": "chronicle_pair",
                },
            },
            "tension_budget": {
                "status": "ok",
                "governance_breached": False,
                "llm_breached": True,
                "llm_breach_reasons": ["timeout"],
                "observation": {
                    "observed_cycles": 2,
                    "council_count": 3,
                    "llm_preflight_timeout_count": 1,
                    "max_consecutive_failure_count": 2,
                },
            },
        },
        "state": {
            "cycles_run": 4,
            "entry_state_count": 1,
            "category_state_count": 1,
            "llm_backoff": {
                "backoff_until_cycle": 3,
                "last_status": "active",
            },
        },
    }


def test_summarize_long_run_payload_summarizes_nested_preflight_and_schedule() -> None:
    payload = {
        "overall_ok": True,
        "experiment": {"name": "true_verification_weekly"},
        "gate": {"status": "passed"},
        "preflight": {"overall_ok": True, "results": [{"cycle": 1}]},
        "schedule": {"overall_ok": True, "results": [{"cycle": 2}]},
    }

    summary = summarize_long_run_payload(payload)

    assert summary == {
        "overall_ok": True,
        "experiment": {"name": "true_verification_weekly"},
        "gate": {"status": "passed"},
        "preflight": {
            "overall_ok": True,
            "result_count": 1,
            "latest_result": {"cycle": 1},
        },
        "schedule": {
            "overall_ok": True,
            "result_count": 1,
            "latest_result": {"cycle": 2},
        },
    }


# ── Helper function unit tests ────────────────────────────────────────────────

from tonesoul.true_verification_summary import (
    _copy_scalar_keys,
    _is_scalar,
    _summarize_autonomous_payload,
    _summarize_registry_batch,
    _summarize_result,
    _summarize_state,
    _summarize_tension_budget,
    _summarize_wakeup_summary,
)


class TestIsScalar:
    def test_none_is_scalar(self):
        assert _is_scalar(None) is True

    def test_string_is_scalar(self):
        assert _is_scalar("hello") is True

    def test_int_is_scalar(self):
        assert _is_scalar(42) is True

    def test_float_is_scalar(self):
        assert _is_scalar(3.14) is True

    def test_bool_is_scalar(self):
        assert _is_scalar(True) is True

    def test_list_is_not_scalar(self):
        assert _is_scalar([]) is False

    def test_dict_is_not_scalar(self):
        assert _is_scalar({}) is False


class TestCopyScalarKeys:
    def test_copies_present_scalars(self):
        result = _copy_scalar_keys({"a": 1, "b": "x"}, "a", "b")
        assert result == {"a": 1, "b": "x"}

    def test_skips_missing_keys(self):
        result = _copy_scalar_keys({"a": 1}, "a", "missing")
        assert "missing" not in result

    def test_skips_none_values(self):
        result = _copy_scalar_keys({"a": None}, "a")
        assert "a" not in result

    def test_skips_non_scalar_values(self):
        result = _copy_scalar_keys({"a": [1, 2]}, "a")
        assert "a" not in result

    def test_empty_payload(self):
        assert _copy_scalar_keys({}, "key") == {}


class TestSummarizeRegistryBatch:
    def test_copies_scalar_counts(self):
        payload = {
            "selection_count": 3,
            "selected_entry_count": 2,
            "ok": True,
        }
        result = _summarize_registry_batch(payload)
        assert result["selection_count"] == 3
        assert result["ok"] is True

    def test_copies_list_fields(self):
        payload = {"selected_entry_ids": ["e1", "e2"], "warnings": ["w1"]}
        result = _summarize_registry_batch(payload)
        assert result["selected_entry_ids"] == ["e1", "e2"]
        assert result["warnings"] == ["w1"]

    def test_skips_non_list_for_list_fields(self):
        result = _summarize_registry_batch({"selected_entry_ids": "not-a-list"})
        assert "selected_entry_ids" not in result


class TestSummarizeAutonomousPayload:
    def test_copies_scalar_fields(self):
        payload = {"overall_ok": True, "urls_requested": 5, "urls_ingested": 4}
        result = _summarize_autonomous_payload(payload)
        assert result["overall_ok"] is True
        assert result["urls_requested"] == 5

    def test_includes_runtime_state(self):
        payload = {"runtime_state": {"session_id": "s-1", "consecutive_failures": 0}}
        result = _summarize_autonomous_payload(payload)
        assert result["runtime_state"]["session_id"] == "s-1"

    def test_includes_memory_write(self):
        payload = {"memory_write": {"written": 3, "skipped": 1}}
        result = _summarize_autonomous_payload(payload)
        assert result["memory_write"]["written"] == 3

    def test_includes_llm_policy(self):
        payload = {"llm_policy": {"mode": "standard"}}
        result = _summarize_autonomous_payload(payload)
        assert result["llm_policy"]["mode"] == "standard"


class TestSummarizeTensionBudget:
    def test_copies_scalar_fields(self):
        payload = {"status": "ok", "governance_breached": False, "cooldown_cycles": 0}
        result = _summarize_tension_budget(payload)
        assert result["status"] == "ok"
        assert result["governance_breached"] is False

    def test_copies_breach_reasons_list(self):
        payload = {"breach_reasons": ["reason-a"]}
        result = _summarize_tension_budget(payload)
        assert result["breach_reasons"] == ["reason-a"]

    def test_includes_observation(self):
        payload = {
            "observation": {
                "observed_cycles": 3,
                "max_friction_score": 0.4,
            }
        }
        result = _summarize_tension_budget(payload)
        assert result["observation"]["observed_cycles"] == 3


class TestSummarizeWakeupSummary:
    def test_copies_scalar_fields(self):
        payload = {"overall_status": "ok", "result_count": 2, "latest_cycle": 5}
        result = _summarize_wakeup_summary(payload)
        assert result["overall_status"] == "ok"
        assert result["result_count"] == 2

    def test_counts_results_list(self):
        payload = {"results": [{"cycle": 1}, {"cycle": 2}]}
        result = _summarize_wakeup_summary(payload)
        assert result["result_count"] == 2

    def test_extracts_latest_result(self):
        payload = {"results": [{"cycle": 1, "status": "ok"}]}
        result = _summarize_wakeup_summary(payload)
        assert result["latest_cycle"] == 1
        assert result["latest_status"] == "ok"


class TestSummarizeResult:
    def test_copies_scalar_fields(self):
        payload = {"cycle": 3, "status": "ok", "overall_ok": True, "duration_ms": 500}
        result = _summarize_result(payload)
        assert result["cycle"] == 3
        assert result["duration_ms"] == 500

    def test_includes_registry_batch(self):
        payload = {"cycle": 1, "registry_batch": {"selection_count": 2}}
        result = _summarize_result(payload)
        assert "registry_batch" in result

    def test_includes_tension_budget(self):
        payload = {"cycle": 1, "tension_budget": {"status": "ok"}}
        result = _summarize_result(payload)
        assert result["tension_budget"]["status"] == "ok"


class TestSummarizeState:
    def test_copies_scalar_cursor_fields(self):
        payload = {"cursor": 5, "cycles_run": 3}
        result = _summarize_state(payload)
        assert result["cursor"] == 5
        assert result["cycles_run"] == 3

    def test_computes_entry_state_count_from_dict(self):
        payload = {"entry_states": {"e1": {}, "e2": {}}}
        result = _summarize_state(payload)
        assert result["entry_state_count"] == 2

    def test_includes_llm_backoff(self):
        payload = {"llm_backoff": {"backoff_until_cycle": 4, "last_status": "timeout"}}
        result = _summarize_state(payload)
        assert result["llm_backoff"]["backoff_until_cycle"] == 4

    def test_llm_backoff_includes_breach_reasons_list(self):
        payload = {"llm_backoff": {"last_breach_reasons": ["r1", "r2"]}}
        result = _summarize_state(payload)
        assert result["llm_backoff"]["last_breach_reasons"] == ["r1", "r2"]


class TestSummarizeSchedulePayloadEdgeCases:
    def test_none_returns_none(self):
        from tonesoul.true_verification_summary import summarize_schedule_payload
        assert summarize_schedule_payload(None) is None

    def test_non_dict_returns_as_is(self):
        from tonesoul.true_verification_summary import summarize_schedule_payload
        result = summarize_schedule_payload("not-a-dict")  # type: ignore
        assert result == "not-a-dict"

    def test_result_count_from_int(self):
        from tonesoul.true_verification_summary import summarize_schedule_payload
        payload = {"result_count": 7, "latest_result": {"cycle": 7, "overall_ok": True}}
        result = summarize_schedule_payload(payload)
        assert result["result_count"] == 7


class TestSummarizeLongRunPayloadEdgeCases:
    def test_none_returns_none(self):
        from tonesoul.true_verification_summary import summarize_long_run_payload
        assert summarize_long_run_payload(None) is None

    def test_overall_ok_copied(self):
        from tonesoul.true_verification_summary import summarize_long_run_payload
        result = summarize_long_run_payload({"overall_ok": True})
        assert result["overall_ok"] is True
