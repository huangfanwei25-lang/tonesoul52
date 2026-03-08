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
                    "dashboard_payload": {"huge": ["x"] * 50},
                },
                "tension_budget": {
                    "status": "ok",
                    "governance_breached": False,
                    "llm_breached": True,
                    "llm_breach_reasons": ["timeout"],
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
            },
            "tension_budget": {
                "status": "ok",
                "governance_breached": False,
                "llm_breached": True,
                "llm_breach_reasons": ["timeout"],
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
