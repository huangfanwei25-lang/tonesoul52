from __future__ import annotations

import json
from pathlib import Path

from tonesoul.dream_observability import build_dashboard, render_html


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_dashboard_warns_when_sources_are_missing(tmp_path: Path) -> None:
    payload = build_dashboard(
        journal_path=tmp_path / "missing_journal.jsonl",
        wakeup_path=tmp_path / "missing_wakeup.jsonl",
        max_points=40,
    )

    assert payload["overall_ok"] is True
    assert payload["metrics"]["journal_entry_count"] == 0
    assert payload["metrics"]["wakeup_cycle_count"] == 0
    assert payload["series"]["journal_friction"] == []
    assert payload["series"]["wakeup_max_lyapunov"] == []
    assert len(payload["warnings"]) == 2


def test_build_dashboard_extracts_journal_and_wakeup_metrics(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"

    _write_jsonl(
        journal_path,
        [
            {
                "payload": {
                    "timestamp": "2026-03-07T19:00:00Z",
                    "tension_before": {
                        "timestamp": "2026-03-07T19:00:00Z",
                        "signals": {"cognitive_friction": 0.21},
                        "prediction": {"lyapunov_exponent": 0.42},
                    },
                    "tension_after": {
                        "timestamp": "2026-03-07T19:00:02Z",
                        "signals": {"cognitive_friction": 0.08},
                        "prediction": {"lyapunov_exponent": -0.31},
                    },
                }
            },
            {
                "timestamp": "2026-03-07T20:00:00Z",
                "tension_before": {
                    "timestamp": "2026-03-07T20:00:00Z",
                    "signals": {"cognitive_friction": 0.73},
                    "prediction": {"lyapunov_exponent": 0.61},
                },
                "tension_after": {
                    "timestamp": "2026-03-07T20:00:03Z",
                    "signals": {"cognitive_friction": 0.29},
                    "prediction": {"lyapunov_exponent": -0.12},
                },
            },
        ],
    )

    _write_jsonl(
        wakeup_path,
        [
            {
                "cycle": 1,
                "status": "ok",
                "finished_at": "2026-03-07T19:10:00Z",
                "summary": {
                    "session_id": "wakeup_alpha",
                    "session_resumed": False,
                    "heartbeat_window_cycle": 1,
                    "consecutive_failure_count": 0,
                    "resume_state_path": "memory/autonomous/dream_wakeup_state.json",
                    "avg_friction_score": 0.66,
                    "max_friction_score": 0.81,
                    "max_lyapunov_proxy": 0.52,
                    "collision_success_rate": 0.5,
                    "council_count": 1,
                    "frozen_count": 0,
                    "write_gateway_written": 1,
                    "write_gateway_skipped": 0,
                    "write_gateway_rejected": 0,
                    "llm_call_count": 1,
                    "llm_prompt_tokens_total": 21,
                    "llm_completion_tokens_total": 13,
                    "llm_total_tokens": 34,
                    "llm_backends": ["ollama"],
                    "llm_preflight_latency_ms": 1800,
                    "llm_preflight_selection_latency_ms": 600,
                    "llm_preflight_probe_latency_ms": 1200,
                    "llm_preflight_timeout_count": 0,
                    "llm_preflight_reason": "ready",
                    "scribe_evaluated": True,
                    "scribe_triggered": True,
                    "scribe_status": "generated",
                    "scribe_generation_mode": "template_assist",
                    "scribe_state_document_posture": "pressure_without_counterweight",
                    "scribe_anchor_status_line": "anchor | [T1] tension: observed grounding...",
                    "scribe_problem_route_status_line": (
                        "route | family=F6_semantic_role_boundary_integrity "
                        "invariant=chronicle_self_scope "
                        "repair=semantic_boundary_guardrail "
                        "secondary=F4_execution_contract_integrity"
                    ),
                    "scribe_problem_route_secondary_labels": "F4_execution_contract_integrity",
                    "scribe_latest_available_source": "chronicle_pair",
                },
            },
            {
                "cycle": 2,
                "status": "idle",
                "finished_at": "2026-03-07T22:10:00Z",
                "summary": {
                    "session_id": "wakeup_alpha",
                    "session_resumed": True,
                    "heartbeat_window_cycle": 1,
                    "consecutive_failure_count": 0,
                    "resume_state_path": "memory/autonomous/dream_wakeup_state.json",
                    "avg_friction_score": 0.31,
                    "max_friction_score": 0.43,
                    "max_lyapunov_proxy": 0.12,
                    "collision_success_rate": 0.0,
                    "council_count": 0,
                    "frozen_count": 0,
                    "write_gateway_written": 0,
                    "write_gateway_skipped": 0,
                    "write_gateway_rejected": 1,
                    "llm_call_count": 0,
                    "llm_prompt_tokens_total": 0,
                    "llm_completion_tokens_total": 0,
                    "llm_total_tokens": 0,
                    "llm_backends": [],
                    "llm_preflight_latency_ms": 2002,
                    "llm_preflight_selection_latency_ms": 759,
                    "llm_preflight_probe_latency_ms": 1243,
                    "llm_preflight_timeout_count": 1,
                    "llm_preflight_reason": "timeout",
                    "scribe_evaluated": True,
                    "scribe_triggered": True,
                    "scribe_status": "generated",
                    "scribe_generation_mode": "template_assist",
                    "scribe_state_document_posture": "pressure_without_counterweight",
                    "scribe_anchor_status_line": "anchor | [T1] tension: observed grounding...",
                    "scribe_problem_route_status_line": (
                        "route | family=F6_semantic_role_boundary_integrity "
                        "invariant=chronicle_self_scope "
                        "repair=semantic_boundary_guardrail "
                        "secondary=F4_execution_contract_integrity"
                    ),
                    "scribe_problem_route_secondary_labels": "F4_execution_contract_integrity",
                    "scribe_latest_available_source": "chronicle_pair",
                },
            },
        ],
    )

    payload = build_dashboard(
        journal_path=journal_path,
        wakeup_path=wakeup_path,
        max_points=20,
    )

    assert payload["overall_ok"] is True
    assert payload["primary_status_line"].startswith(
        "dream_observability_ready | wakeup_cycles=2 schedule_cycles=0 warnings=0 overall_ok=yes"
    )
    assert (
        payload["runtime_status_line"]
        == "wakeup_scribe | status=generated posture=pressure_without_counterweight source=chronicle_pair"
    )
    assert payload["anchor_status_line"] == "anchor | [T1] tension: observed grounding..."
    assert (
        payload["problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert payload["problem_route_secondary_labels"] == "F4_execution_contract_integrity"
    assert payload["artifact_policy_status_line"] == (
        "dashboard_inputs | wakeup=yes schedule=no invalid_json=0"
    )
    assert payload["metrics"]["journal_friction_point_count"] == 4
    assert payload["metrics"]["journal_lyapunov_point_count"] == 4
    assert payload["metrics"]["wakeup_avg_friction_point_count"] == 2
    assert payload["metrics"]["wakeup_consecutive_failures_point_count"] == 2
    assert payload["metrics"]["wakeup_session_resumed_point_count"] == 2
    assert payload["summary"]["journal_friction"]["max"] == 0.73
    assert payload["summary"]["journal_friction"]["latest"] == 0.29
    assert payload["summary"]["journal_friction"]["convergence_events"] >= 1
    assert payload["summary"]["wakeup_avg_friction"]["latest"] == 0.31
    assert payload["summary"]["wakeup_max_lyapunov"]["latest"] == 0.12
    assert payload["summary"]["wakeup_collision_success_rate"]["latest"] == 0.0
    assert payload["summary"]["wakeup_consecutive_failures"]["latest"] == 0.0
    assert payload["summary"]["wakeup_runtime_session_count"] == 1
    assert payload["summary"]["wakeup_resumed_cycle_total"] == 1
    assert payload["summary"]["wakeup_latest_session_id"] == "wakeup_alpha"
    assert (
        payload["summary"]["wakeup_latest_resume_state_path"]
        == "memory/autonomous/dream_wakeup_state.json"
    )
    assert payload["summary"]["wakeup_latest_heartbeat_window_cycle"] == 1
    assert payload["summary"]["wakeup_write_gateway_written_total"] == 1
    assert payload["summary"]["wakeup_write_gateway_rejected_total"] == 1
    assert payload["summary"]["wakeup_llm_prompt_tokens"]["latest"] == 0.0
    assert payload["summary"]["wakeup_llm_completion_tokens"]["latest"] == 0.0
    assert payload["summary"]["wakeup_llm_total_tokens"]["latest"] == 0.0
    assert payload["summary"]["wakeup_llm_preflight_latency"]["latest"] == 2002.0
    assert payload["summary"]["wakeup_llm_selection_latency"]["latest"] == 759.0
    assert payload["summary"]["wakeup_llm_probe_latency"]["latest"] == 1243.0
    assert payload["summary"]["wakeup_llm_preflight_timeout_total"] == 1
    assert payload["summary"]["wakeup_council_total"] == 1
    assert payload["summary"]["wakeup_scribe_triggered_total"] == 2
    assert payload["summary"]["wakeup_latest_scribe_status"] == "generated"
    assert payload["summary"]["wakeup_latest_scribe_generation_mode"] == "template_assist"
    assert (
        payload["summary"]["wakeup_latest_scribe_state_document_posture"]
        == "pressure_without_counterweight"
    )
    assert (
        payload["summary"]["wakeup_latest_scribe_anchor_status_line"]
        == "anchor | [T1] tension: observed grounding..."
    )
    assert (
        payload["summary"]["wakeup_latest_scribe_problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert (
        payload["summary"]["wakeup_latest_scribe_problem_route_secondary_labels"]
        == "F4_execution_contract_integrity"
    )
    assert payload["summary"]["wakeup_latest_scribe_available_source"] == "chronicle_pair"
    assert payload["recent_wakeup_cycles"][-1]["status"] == "idle"
    assert payload["recent_wakeup_cycles"][0]["session_id"] == "wakeup_alpha"
    assert payload["recent_wakeup_cycles"][0]["llm_backends"] == ["ollama"]
    assert payload["recent_wakeup_cycles"][0]["write_gateway_written"] == 1
    assert payload["recent_wakeup_cycles"][-1]["write_gateway_rejected"] == 1
    assert payload["recent_wakeup_cycles"][-1]["llm_preflight_reason"] == "timeout"
    assert payload["recent_wakeup_cycles"][-1]["session_resumed"] is True
    assert payload["recent_wakeup_cycles"][-1]["heartbeat_window_cycle"] == 1
    assert payload["recent_wakeup_cycles"][-1]["scribe_status"] == "generated"
    assert payload["recent_wakeup_cycles"][-1]["scribe_generation_mode"] == "template_assist"
    assert (
        payload["recent_wakeup_cycles"][-1]["scribe_state_document_posture"]
        == "pressure_without_counterweight"
    )
    assert (
        payload["recent_wakeup_cycles"][-1]["scribe_anchor_status_line"]
        == "anchor | [T1] tension: observed grounding..."
    )
    assert (
        payload["recent_wakeup_cycles"][-1]["scribe_problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert (
        payload["recent_wakeup_cycles"][-1]["scribe_problem_route_secondary_labels"]
        == "F4_execution_contract_integrity"
    )
    assert payload["metrics"]["wakeup_collision_success_rate_point_count"] == 2
    assert payload["metrics"]["wakeup_write_gateway_written_point_count"] == 2
    assert payload["metrics"]["wakeup_write_gateway_rejected_point_count"] == 2
    assert payload["metrics"]["wakeup_llm_prompt_tokens_point_count"] == 2
    assert payload["metrics"]["wakeup_llm_completion_tokens_point_count"] == 2
    assert payload["metrics"]["wakeup_llm_total_tokens_point_count"] == 2
    assert payload["metrics"]["wakeup_llm_preflight_latency_point_count"] == 2
    assert payload["metrics"]["wakeup_scribe_triggered_point_count"] == 2
    assert payload["wakeup_runtime_state"]["session_count"] == 1
    assert payload["wakeup_runtime_state"]["resumed_cycle_count"] == 1
    assert payload["wakeup_scribe_state"]["latest_status"] == "generated"
    assert (
        payload["wakeup_scribe_state"]["latest_anchor_status_line"]
        == "anchor | [T1] tension: observed grounding..."
    )
    assert (
        payload["wakeup_scribe_state"]["latest_problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert (
        payload["wakeup_scribe_state"]["latest_problem_route_secondary_labels"]
        == "F4_execution_contract_integrity"
    )
    assert payload["handoff"]["queue_shape"] == "dream_observability_ready"
    assert payload["handoff"]["primary_status_line"] == payload["primary_status_line"]
    assert payload["handoff"]["anchor_status_line"] == payload["anchor_status_line"]


def test_build_dashboard_extracts_schedule_governance_and_backoff_metrics(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"
    schedule_history_path = tmp_path / "registry_schedule_history.jsonl"
    schedule_state_path = tmp_path / "registry_schedule_state.json"
    journal_path.write_text("", encoding="utf-8")
    wakeup_path.write_text("", encoding="utf-8")

    _write_jsonl(
        schedule_history_path,
        [
            {
                "cycle": 1,
                "finished_at": "2026-03-08T01:00:00Z",
                "registry_batch": {
                    "selected_categories": ["research"],
                    "deferred_category_count": 0,
                },
                "autonomous_payload": {
                    "runtime_state": {
                        "session_id": "wakeup_alpha",
                        "next_cycle": 2,
                        "consecutive_failures": 0,
                        "resumed": False,
                        "state_path": "memory/autonomous/dream_wakeup_state.json",
                    },
                    "llm_policy": {
                        "active": False,
                        "mode": "none",
                        "action": "normal",
                        "reason_count": 0,
                        "breach_reasons": [],
                    },
                },
                "tension_budget": {
                    "cooled_categories": ["research"],
                    "llm_backoff_requested": True,
                    "governance_breach_reasons": ["max_friction_score>0.8 (observed=0.91)"],
                    "llm_breach_reasons": [
                        "llm_preflight_latency_ms>1800 (observed=2002)",
                    ],
                },
            },
            {
                "cycle": 2,
                "finished_at": "2026-03-08T02:00:00Z",
                "registry_batch": {
                    "selected_categories": ["news"],
                    "deferred_category_count": 1,
                },
                "autonomous_payload": {
                    "runtime_state": {
                        "session_id": "wakeup_alpha",
                        "next_cycle": 3,
                        "consecutive_failures": 2,
                        "resumed": True,
                        "state_path": "memory/autonomous/dream_wakeup_state.json",
                    },
                    "llm_policy": {
                        "active": True,
                        "mode": "probe_latency",
                        "action": "disable_reflection",
                        "reason_count": 1,
                        "breach_reasons": [
                            "llm_probe_latency_ms>1200 (observed=1243)",
                        ],
                    },
                },
                "tension_budget": {
                    "cooled_categories": [],
                    "llm_backoff_requested": False,
                    "governance_breach_reasons": [],
                    "llm_breach_reasons": [],
                },
            },
        ],
    )
    schedule_state_path.write_text(
        json.dumps(
            {
                "cycles_run": 2,
                "updated_at": "2026-03-08T02:00:00Z",
                "category_states": {
                    "research": {
                        "tension_cooldown_until_cycle": 3,
                    }
                },
                "llm_backoff": {
                    "backoff_until_cycle": 4,
                    "last_status": "breached",
                    "last_mode": "probe_latency",
                    "last_breach_reasons": [
                        "llm_probe_latency_ms>1200 (observed=1243)",
                    ],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_dashboard(
        journal_path=journal_path,
        wakeup_path=wakeup_path,
        schedule_history_path=schedule_history_path,
        schedule_state_path=schedule_state_path,
        max_points=20,
    )

    assert payload["overall_ok"] is True
    assert payload["metrics"]["schedule_cycle_count"] == 2
    assert payload["summary"]["schedule_governance_cooldown_applied_total"] == 1
    assert payload["summary"]["schedule_governance_cooldown_deferred_total"] == 1
    assert payload["summary"]["schedule_llm_backoff_requested_total"] == 1
    assert payload["summary"]["schedule_llm_backoff_active_total"] == 1
    assert payload["summary"]["schedule_wakeup_runtime_session_count"] == 1
    assert payload["summary"]["schedule_wakeup_resumed_cycle_total"] == 1
    assert payload["summary"]["schedule_wakeup_latest_session_id"] == "wakeup_alpha"
    assert payload["series"]["schedule_governance_cooldown_applied"][0]["value"] == 1.0
    assert payload["series"]["schedule_llm_backoff_active"][-1]["value"] == 1.0
    assert payload["series"]["schedule_wakeup_session_resumed"][-1]["value"] == 1.0
    assert payload["series"]["schedule_wakeup_consecutive_failures"][-1]["value"] == 2.0
    assert payload["recent_schedule_cycles"][-1]["llm_backoff_active"] is True
    assert payload["recent_schedule_cycles"][-1]["wakeup_session_id"] == "wakeup_alpha"
    assert payload["recent_schedule_cycles"][-1]["wakeup_session_resumed"] is True
    assert payload["recent_schedule_cycles"][-1]["wakeup_consecutive_failures"] == 2
    assert payload["recent_schedule_cycles"][-1]["wakeup_next_cycle"] == 3
    assert payload["schedule_state"]["active_governance_cooldown_count"] == 1
    assert payload["schedule_state"]["llm_backoff_active"] is True
    assert payload["schedule_state"]["llm_backoff_mode"] == "probe_latency"
    assert payload["schedule_runtime_state"]["session_count"] == 1
    assert payload["schedule_runtime_state"]["resumed_cycle_count"] == 1


def test_render_html_contains_dashboard_sections(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"
    schedule_history_path = tmp_path / "registry_schedule_history.jsonl"
    schedule_state_path = tmp_path / "registry_schedule_state.json"
    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-03-07T19:00:00Z",
                "tension_before": {
                    "timestamp": "2026-03-07T19:00:00Z",
                    "signals": {"cognitive_friction": 0.4},
                    "prediction": {"lyapunov_exponent": 0.2},
                },
            }
        ],
    )
    _write_jsonl(
        wakeup_path,
        [
            {
                "cycle": 1,
                "status": "ok",
                "finished_at": "2026-03-07T19:10:00Z",
                "summary": {
                    "session_id": "wakeup_alpha",
                    "session_resumed": False,
                    "heartbeat_window_cycle": 1,
                    "consecutive_failure_count": 0,
                    "resume_state_path": "memory/autonomous/dream_wakeup_state.json",
                    "avg_friction_score": 0.5,
                    "max_friction_score": 0.7,
                    "max_lyapunov_proxy": 0.4,
                    "collision_success_rate": 1.0,
                    "council_count": 1,
                    "frozen_count": 0,
                    "write_gateway_written": 1,
                    "write_gateway_skipped": 0,
                    "write_gateway_rejected": 0,
                    "llm_call_count": 1,
                    "llm_prompt_tokens_total": 11,
                    "llm_completion_tokens_total": 7,
                    "llm_total_tokens": 18,
                    "llm_backends": ["ollama"],
                    "llm_preflight_latency_ms": 1400,
                    "llm_preflight_selection_latency_ms": 500,
                    "llm_preflight_probe_latency_ms": 900,
                    "llm_preflight_timeout_count": 0,
                    "llm_preflight_reason": "ready",
                    "scribe_evaluated": True,
                    "scribe_triggered": True,
                    "scribe_status": "generated",
                    "scribe_generation_mode": "template_assist",
                    "scribe_state_document_posture": "pressure_without_counterweight",
                    "scribe_problem_route_status_line": (
                        "route | family=F6_semantic_role_boundary_integrity "
                        "invariant=chronicle_self_scope "
                        "repair=semantic_boundary_guardrail "
                        "secondary=F4_execution_contract_integrity"
                    ),
                    "scribe_problem_route_secondary_labels": "F4_execution_contract_integrity",
                    "scribe_latest_available_source": "chronicle_pair",
                },
            }
        ],
    )
    _write_jsonl(
        schedule_history_path,
        [
            {
                "cycle": 1,
                "finished_at": "2026-03-08T01:20:00Z",
                "registry_batch": {
                    "selected_categories": ["research"],
                    "deferred_category_count": 0,
                },
                "autonomous_payload": {
                    "runtime_state": {
                        "session_id": "wakeup_alpha",
                        "next_cycle": 2,
                        "consecutive_failures": 1,
                        "resumed": True,
                        "state_path": "memory/autonomous/dream_wakeup_state.json",
                    },
                    "llm_policy": {
                        "active": True,
                        "mode": "probe_latency",
                        "action": "disable_reflection",
                        "reason_count": 1,
                    },
                },
                "tension_budget": {
                    "cooled_categories": ["research"],
                    "llm_backoff_requested": True,
                },
            }
        ],
    )
    schedule_state_path.write_text(
        json.dumps(
            {
                "cycles_run": 1,
                "category_states": {
                    "research": {
                        "tension_cooldown_until_cycle": 2,
                    }
                },
                "llm_backoff": {
                    "backoff_until_cycle": 3,
                    "last_status": "breached",
                    "last_mode": "probe_latency",
                    "last_breach_reasons": ["llm_probe_latency_ms>1200 (observed=1243)"],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    html = render_html(
        build_dashboard(
            journal_path=journal_path,
            wakeup_path=wakeup_path,
            schedule_history_path=schedule_history_path,
            schedule_state_path=schedule_state_path,
            max_points=20,
        )
    )

    assert "Dream Observability Dashboard" in html
    assert "Journal Friction" in html
    assert "Wake-up Max Lyapunov" in html
    assert "Wake-up Collision Success" in html
    assert "Wake-up Failure Streak" in html
    assert "Wake-up Session Resume" in html
    assert "Write Gateway Written" in html
    assert "Wake-up LLM Tokens" in html
    assert "Wake-up LLM Prompt Tokens" in html
    assert "Wake-up LLM Preflight" in html
    assert "Wake-up LLM Probe Latency" in html
    assert "Runtime Sessions" in html
    assert "Scribe Status" in html
    assert "Schedule Cooldown Applied" in html
    assert "Schedule LLM Backoff Active" in html
    assert "Schedule Wake-up Resume" in html
    assert "Schedule Wake-up Failure Streak" in html
    assert "Schedule Wakeup Sessions" in html
    assert "Recent Wake-up Cycles" in html
    assert "Recent Schedule Cycles" in html
    assert "pressure_without_counterweight" in html
    assert "Scribe Route" in html
    assert "Scribe Secondary" in html
    assert "semantic_boundary_guardrail" in html
    assert "F4_execution_contract_integrity" in html
