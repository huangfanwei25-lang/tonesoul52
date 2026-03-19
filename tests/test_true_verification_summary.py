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
