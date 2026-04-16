#!/usr/bin/env python3
"""Run the first bounded ToneSoul self-improvement trial wave."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the first bounded ToneSoul self-improvement trial wave.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _probe_deliberation_hint(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "start_agent_session.py"),
        "--agent",
        agent,
        "--tier",
        "1",
        "--no-ack",
    ]
    if state_path is not None:
        command.extend(["--state-path", str(state_path)])
    if traces_path is not None:
        command.extend(["--traces-path", str(traces_path)])

    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe failed_to_run={exc}",
        }

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "session-start failed").strip()
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe failed_to_run={message}",
        }

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe invalid_json={exc}",
        }

    hint = dict((payload or {}).get("deliberation_mode_hint") or {})
    active = list(hint.get("active_escalation_signals") or [])
    conditional = list(
        hint.get("conditional_escalation_triggers") or hint.get("escalation_triggers") or []
    )
    review_cues = list(hint.get("review_cues") or [])
    split_present = bool(
        isinstance(hint.get("active_escalation_signals"), list)
        and isinstance(hint.get("conditional_escalation_triggers"), list)
        and isinstance(hint.get("review_cues"), list)
    )
    return {
        "present": split_present,
        "summary_text": (
            "deliberation_hint_probe "
            f"mode={str(hint.get('suggested_mode', '') or 'unclassified')} "
            f"active={len(active)} conditional={len(conditional)} review={len(review_cues)} "
            f"split={'yes' if split_present else 'no'}"
        ),
    }


def _probe_task_board_parking(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    from scripts.run_task_board_preflight import run_task_board_preflight

    payload = run_task_board_preflight(
        agent=agent,
        proposal_kind="external_idea",
        target_path="task.md",
        state_path=state_path,
        traces_path=traces_path,
    )
    preflight = dict(payload.get("preflight") or {})
    present = bool(
        isinstance(preflight.get("routing_outcome"), str)
        and isinstance(preflight.get("task_md_write_allowed"), bool)
        and isinstance(preflight.get("promotion_posture"), str)
    )
    return {
        "present": present,
        "summary_text": (
            "task_board_probe "
            f"classification={str(preflight.get('classification', '') or 'unknown')} "
            f"write_task_md={'yes' if bool(preflight.get('task_md_write_allowed')) else 'no'} "
            f"promotion={str(preflight.get('promotion_posture', '') or 'unknown')} "
            f"routing={'yes' if present else 'no'}"
        ),
    }


def _probe_shared_edit_preflight() -> dict[str, Any]:
    from tonesoul.shared_edit_preflight import build_shared_edit_preflight

    payload = build_shared_edit_preflight(
        agent_id="trial-wave",
        candidate_paths=["tonesoul/runtime_adapter.py", "scripts/start_agent_session.py"],
        readiness={"status": "pass"},
        claims=[
            {
                "task_id": "task-other",
                "agent": "other-agent",
                "summary": "hold runtime lane",
                "paths": ["tonesoul/runtime_adapter.py"],
            }
        ],
        task_track_hint={
            "claim_recommendation": "required",
            "suggested_track": "feature_track",
        },
        mutation_preflight={"summary_text": "shared_code=coordinate_before_shared_edits"},
    )
    present = bool(
        isinstance(payload.get("decision_basis"), str)
        and isinstance(payload.get("other_overlap_paths"), list)
        and isinstance(payload.get("claim_gap_paths"), list)
        and isinstance(payload.get("decision_pressures"), dict)
    )
    return {
        "present": present,
        "summary_text": (
            "shared_edit_probe "
            f"decision={str(payload.get('decision', '') or 'unknown')} "
            f"basis={str(payload.get('decision_basis', '') or 'unknown')} "
            f"other={len(list(payload.get('other_overlap_paths') or []))} "
            f"gaps={len(list(payload.get('claim_gap_paths') or []))} "
            f"pressures={'yes' if isinstance(payload.get('decision_pressures'), dict) else 'no'}"
        ),
    }


def _probe_publish_push_preflight() -> dict[str, Any]:
    from tonesoul.publish_push_preflight import build_publish_push_preflight

    payload = build_publish_push_preflight(
        readiness={"status": "needs_clarification"},
        import_posture={
            "surfaces": {
                "compactions": {
                    "closeout_status": "partial",
                    "receiver_obligation": "must_not_promote",
                    "unresolved_count": 2,
                    "human_input_required": False,
                },
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                        "blocked_overclaims": ["live_shared_memory"],
                    }
                },
            }
        },
        repo_state_awareness={"classification": "baseline_unset"},
    )
    present = bool(
        isinstance(payload.get("decision_basis"), str)
        and isinstance(payload.get("review_cues"), list)
        and isinstance(payload.get("honesty_cues"), list)
        and payload.get("classification") == "review_before_push"
    )
    return {
        "present": present,
        "summary_text": (
            "publish_push_probe "
            f"classification={str(payload.get('classification', '') or 'unknown')} "
            f"basis={str(payload.get('decision_basis', '') or 'unknown')} "
            f"review={len(list(payload.get('review_cues') or []))} "
            f"honesty={len(list(payload.get('honesty_cues') or []))} "
            f"blocked={len(list(payload.get('blocked_reasons') or []))}"
        ),
    }


def _probe_mutation_followup_routing() -> dict[str, Any]:
    from tonesoul.mutation_preflight import build_mutation_preflight

    shared_edit_payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 1},
        task_track_hint={"suggested_track": "feature_track", "claim_recommendation": "required"},
        deliberation_mode_hint={"suggested_mode": "standard_council"},
        import_posture={
            "surfaces": {
                "claims": {},
                "checkpoints": {},
                "compactions": {"receiver_obligation": "should_consider", "closeout_status": ""},
                "subject_refresh": {"receiver_obligation": "must_not_promote"},
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                    }
                },
            }
        },
        canonical_center={"current_short_board": {"present": True}},
        publish_push_preflight={"classification": "review_before_push"},
        task_board_preflight={"classification": "docs_plans_first", "task_md_write_allowed": False},
    )
    publish_payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 0},
        task_track_hint={"suggested_track": "quick_change", "claim_recommendation": "not_required"},
        deliberation_mode_hint={"suggested_mode": "lightweight_review"},
        import_posture={
            "surfaces": {
                "claims": {},
                "checkpoints": {},
                "compactions": {"receiver_obligation": "should_consider", "closeout_status": ""},
                "subject_refresh": {"receiver_obligation": "must_not_promote"},
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                    }
                },
            }
        },
        canonical_center={"current_short_board": {"present": True}},
        publish_push_preflight={"classification": "review_before_push"},
        task_board_preflight={"classification": "docs_plans_first", "task_md_write_allowed": False},
    )
    shared_target = str((shared_edit_payload.get("next_followup") or {}).get("target", "")).strip()
    publish_target = str((publish_payload.get("next_followup") or {}).get("target", "")).strip()
    present = (
        shared_target == "shared_code_edit.path_overlap_preflight"
        and publish_target == "publish_push.posture_preflight"
    )
    return {
        "present": present,
        "summary_text": (
            "mutation_followup_probe "
            f"shared_target={shared_target or 'missing'} "
            f"publish_target={publish_target or 'missing'}"
        ),
    }


def _probe_surface_versioning_lineage() -> dict[str, Any]:
    from tonesoul.surface_versioning import build_surface_versioning_readout

    payload = build_surface_versioning_readout()
    compatibility = dict(payload.get("compatibility_posture") or {})
    fallback_chain = list(compatibility.get("fallback_chain") or [])
    consumer_statuses = list(compatibility.get("consumer_statuses") or [])
    consumer_labels = [str(item.get("consumer", "")).strip() for item in consumer_statuses]
    compatibility_values = [
        str(item.get("compatibility", "")).strip() for item in consumer_statuses
    ]
    present = (
        fallback_chain
        == [
            "session_start:tiered_v1",
            "observer_window:anchor_window_v1",
            "r_memory_packet:packet_v1",
        ]
        and consumer_labels == ["codex_cli", "dashboard_operator_shell", "claude_style_shell"]
        and compatibility_values == ["repo_native_entry", "bounded_adapter", "bounded_adapter"]
    )
    return {
        "present": present,
        "summary_text": (
            "surface_versioning_probe "
            f"consumers={','.join(consumer_labels) or 'missing'} "
            f"compatibility={','.join(compatibility_values) or 'missing'} "
            f"fallback={'>'.join(fallback_chain) or 'missing'}"
        ),
    }


def _probe_launch_health_trend_clarity() -> dict[str, Any]:
    from tonesoul.runtime_adapter import _build_launch_health_trend_posture

    payload = _build_launch_health_trend_posture(
        project_memory_summary={
            "evidence_readout_posture": {
                "lanes": [
                    {"lane": "continuity_effectiveness", "classification": "runtime_present"},
                    {"lane": "council_decision_quality", "classification": "descriptive_only"},
                ]
            }
        },
        coordination_mode={
            "launch_default_mode": "file-backed",
            "launch_alignment": "aligned_with_launch_default",
        },
        launch_claim_posture={
            "current_tier": "collaborator_beta",
            "public_launch_ready": False,
        },
    )
    trend_watch_cues = list(payload.get("trend_watch_cues") or [])
    forecast_blockers = list(payload.get("forecast_blockers") or [])
    operator_actions = list(payload.get("operator_actions") or [])
    trend_metrics = [str(item.get("metric", "")).strip() for item in trend_watch_cues]
    blocker_metrics = [str(item.get("metric", "")).strip() for item in forecast_blockers]
    present = (
        trend_metrics == ["coordination_backend_alignment", "collaborator_beta_validation_health"]
        and blocker_metrics[:2] == ["continuity_effectiveness", "council_decision_quality"]
        and len(operator_actions) >= 3
    )
    return {
        "present": present,
        "summary_text": (
            "launch_health_probe "
            f"trend_watch={','.join(trend_metrics) or 'missing'} "
            f"forecast_blockers={','.join(blocker_metrics) or 'missing'} "
            f"actions={len(operator_actions)}"
        ),
    }


def _probe_internal_state_action_clarity() -> dict[str, Any]:
    from tonesoul.runtime_adapter import _build_internal_state_observability

    payload = _build_internal_state_observability(
        project_memory_summary={
            "working_style_observability": {
                "drift_risk": "medium",
            }
        },
        risk_posture={"level": "stable"},
        compactions=[
            {
                "closeout": {
                    "status": "partial",
                    "stop_reason": "",
                },
                "next_action": "",
                "pending_paths": [],
                "council_dossier": {
                    "confidence_posture": "contested",
                    "has_minority_report": True,
                    "evolution_suppression_flag": False,
                },
            }
        ],
        recent_traces=[],
    )
    cues = list(payload.get("pressure_watch_cues") or [])
    actions = list(payload.get("operator_actions") or [])
    cue_signals = [str(item.get("signal", "")).strip() for item in cues]
    present = (
        cue_signals
        == [
            "coordination_strain",
            "continuity_drift",
            "stop_reason_pressure",
            "deliberation_conflict",
        ]
        and len(actions) >= 4
        and "not proof of subjective feeling" in str(payload.get("selfhood_boundary", ""))
    )
    return {
        "present": present,
        "summary_text": (
            "internal_state_probe "
            f"signals={','.join(cue_signals) or 'missing'} "
            f"actions={len(actions)}"
        ),
    }


def _probe_hook_chain_trigger_clarity(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    from scripts.start_agent_session import run_session_start_bundle

    payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        # Hook-chain packaging is intentionally deferred out of Tier 0 fast-path
        # payloads, so probe the Tier 1 orientation shell where the readout lives.
        tier=1,
    )
    hook_chain = dict(payload.get("hook_chain") or {})
    mutation_preflight = dict(payload.get("mutation_preflight") or {})
    next_followup = dict(mutation_preflight.get("next_followup") or {})
    hooks = list(hook_chain.get("hooks") or [])
    current_recommendation = dict(hook_chain.get("current_recommendation") or {})
    stages = list(hook_chain.get("stages") or [])
    recommended_hooks = [
        str(item.get("name", "")).strip()
        for item in hooks
        if str(item.get("status", "")).strip() == "recommended_now"
    ]
    activation_present = all(
        isinstance(stage.get("activation_signals"), list) and bool(stage.get("activation_signals"))
        for stage in stages
    )
    present = bool(
        hooks
        and current_recommendation.get("present")
        and str(current_recommendation.get("target", "")).strip()
        == str(next_followup.get("target", "")).strip()
        and len(recommended_hooks) == 1
        and activation_present
    )
    return {
        "present": present,
        "summary_text": (
            "hook_chain_probe "
            f"recommended={recommended_hooks[0] if recommended_hooks else 'missing'} "
            f"target={str(current_recommendation.get('target', '')).strip() or 'missing'} "
            f"selection={'yes' if bool(hook_chain.get('selection_rule')) else 'no'} "
            f"hooks={len(hooks)}"
        ),
    }


def _probe_consumer_misread_guard_clarity(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.claude_entry_adapter import build_claude_entry_adapter

    session_payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=1,
    )
    consumer_contract = dict(session_payload.get("consumer_contract") or {})
    guards = list(consumer_contract.get("misread_guards") or [])
    priority_guard = dict(consumer_contract.get("priority_misread_guard") or {})
    claude_adapter = build_claude_entry_adapter(session_start_payload=session_payload)
    must_correct_first = dict(claude_adapter.get("must_correct_first") or {})
    all_guard_fields_present = all(
        str(item.get("trigger_surface", "")).strip()
        and str(item.get("operator_action", "")).strip()
        for item in guards
    )
    present = bool(
        guards
        and all_guard_fields_present
        and str(priority_guard.get("trigger_surface", "")).strip()
        and str(priority_guard.get("operator_action", "")).strip()
        and must_correct_first.get("trigger_surface") == priority_guard.get("trigger_surface")
        and must_correct_first.get("operator_action") == priority_guard.get("operator_action")
    )
    return {
        "present": present,
        "summary_text": (
            "consumer_misread_guard_probe "
            f"guards={len(guards)} "
            f"priority={str(priority_guard.get('name', '')).strip() or 'missing'} "
            f"surface={str(priority_guard.get('trigger_surface', '')).strip() or 'missing'} "
            f"claude_sync={'yes' if must_correct_first.get('trigger_surface') == priority_guard.get('trigger_surface') else 'no'}"
        ),
    }


def _probe_subsystem_parity_focus_clarity(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    from apps.dashboard.frontend.utils.session_start import build_tier1_orientation_shell
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.claude_entry_adapter import build_claude_entry_adapter

    session_payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=1,
    )
    next_focus = dict((session_payload.get("subsystem_parity") or {}).get("next_focus") or {})
    claude_adapter = build_claude_entry_adapter(session_start_payload=session_payload)
    dashboard_shell = build_tier1_orientation_shell(session_payload)
    dashboard_next_focus = dict(dashboard_shell.get("next_focus") or {})
    claude_next_focus = dict(claude_adapter.get("next_focus") or {})
    focus_pressures = list(next_focus.get("focus_pressures") or [])
    present = bool(
        str(next_focus.get("source_family", "")).strip()
        and focus_pressures
        and str(next_focus.get("operator_action", "")).strip()
        and dashboard_next_focus.get("source_family") == next_focus.get("source_family")
        and claude_next_focus.get("source_family") == next_focus.get("source_family")
    )
    return {
        "present": present,
        "summary_text": (
            "subsystem_parity_focus_probe "
            f"target={str(next_focus.get('resolved_to', '')).strip() or 'missing'} "
            f"source={str(next_focus.get('source_family', '')).strip() or 'missing'} "
            f"pressures={len(focus_pressures)} "
            f"shell_sync={'yes' if dashboard_next_focus.get('source_family') == next_focus.get('source_family') == claude_next_focus.get('source_family') else 'no'}"
        ),
    }


def _probe_closeout_attention_action_clarity() -> dict[str, Any]:
    from apps.dashboard.frontend.utils.session_start import build_tier1_orientation_shell
    from tonesoul.claude_entry_adapter import build_claude_entry_adapter
    from tonesoul.observer_window import _build_closeout_attention

    closeout_attention = _build_closeout_attention(
        import_posture={
            "compactions": {
                "closeout_status": "partial",
                "unresolved_count": 2,
                "stop_reason": "underdetermined",
                "human_input_required": True,
            }
        }
    )
    session_payload = {
        "tier": 1,
        "readiness": {"status": "needs_clarification"},
        "canonical_center": {
            "current_short_board": {
                "present": True,
                "summary_text": "Phase 832: thirteenth trial candidate admission",
            }
        },
        "closeout_attention": closeout_attention,
        "mutation_preflight": {
            "next_followup": {"target": "shared_code_edit.path_overlap_preflight"}
        },
        "subsystem_parity": {
            "counts": {"baseline": 3, "beta_usable": 5, "partial": 2, "deferred": 1},
            "families": [],
            "next_focus": {
                "resolved_to": "shared_code_edit.path_overlap_preflight",
                "source_family": "mutation_preflight_hooks",
                "operator_action": "Run the shared-edit preflight first.",
                "focus_pressures": ["readiness=needs_clarification"],
            },
        },
        "observer_shell": {
            "summary_text": "observer ready",
            "receiver_note": "observer shell only",
            "counts": {"stable": 1, "contested": 1, "stale": 0},
            "stable_headlines": [],
            "contested_headlines": [],
            "stale_headlines": [],
        },
        "next_pull": {
            "receiver_rule": "Pull the full Tier-2 bundle only when shared mutation or contested governance detail is required.",
            "recommended_commands": [
                "python scripts/start_agent_session.py --agent trial-wave --tier 2 --no-ack"
            ],
        },
        "consumer_contract": {
            "receiver_rule": "Recover parent truth before widening context.",
            "required_read_order": [
                {"surface": "readiness", "receiver_rule": "gate first"},
                {"surface": "canonical_center", "receiver_rule": "read parent truth"},
                {
                    "surface": "closeout_attention",
                    "receiver_rule": "read closeout before summary",
                },
                {
                    "surface": "mutation_preflight",
                    "receiver_rule": "check side effects before action",
                },
            ],
            "misread_guards": [],
            "priority_misread_guard": {},
        },
    }
    claude_adapter = build_claude_entry_adapter(session_start_payload=session_payload)
    dashboard_shell = build_tier1_orientation_shell(session_payload)
    dashboard_closeout = dict(dashboard_shell.get("closeout_attention") or {})
    claude_closeout = dict(claude_adapter.get("closeout_focus") or {})
    attention_pressures = list(closeout_attention.get("attention_pressures") or [])
    present = bool(
        closeout_attention.get("present")
        and str(closeout_attention.get("source_family", "")).strip()
        and str(closeout_attention.get("operator_action", "")).strip()
        and attention_pressures
        and dashboard_closeout.get("source_family") == closeout_attention.get("source_family")
        and claude_closeout.get("source_family") == closeout_attention.get("source_family")
        and dashboard_closeout.get("operator_action") == closeout_attention.get("operator_action")
        and claude_closeout.get("operator_action") == closeout_attention.get("operator_action")
    )
    return {
        "present": present,
        "summary_text": (
            "closeout_attention_probe "
            f"status={str(closeout_attention.get('status', '')).strip() or 'missing'} "
            f"source={str(closeout_attention.get('source_family', '')).strip() or 'missing'} "
            f"pressures={len(attention_pressures)} "
            f"shell_sync={'yes' if present else 'no'}"
        ),
    }


def _probe_claude_priority_correction_clarity() -> dict[str, Any]:
    from tonesoul.claude_entry_adapter import build_claude_entry_adapter

    session_payload = {
        "tier": 1,
        "readiness": {"status": "needs_clarification"},
        "deliberation_mode_hint": {"suggested_mode": "lightweight_review"},
        "canonical_center": {
            "current_short_board": {
                "present": True,
                "summary_text": "Phase 835: fourteenth trial candidate admission",
            }
        },
        "closeout_attention": {
            "status": "partial",
            "source_family": "bounded_handoff_closeout",
            "operator_action": "Review unresolved items before treating the handoff as resumable work.",
            "attention_pressures": ["status=partial", "unresolved=1"],
            "why_now": "latest compaction closeout is partial",
        },
        "mutation_preflight": {
            "next_followup": {"target": "shared_code_edit.path_overlap_preflight"}
        },
        "subsystem_parity": {
            "next_focus": {"resolved_to": "shared_code_edit.path_overlap_preflight"}
        },
        "next_pull": {
            "receiver_rule": "Pull the full Tier-2 bundle only when shared mutation or contested governance detail is required.",
            "recommended_commands": [
                "python scripts/start_agent_session.py --agent trial-wave --tier 2 --no-ack"
            ],
        },
        "consumer_contract": {
            "receiver_rule": "Recover parent truth before widening context.",
            "required_read_order": [
                {"surface": "readiness", "receiver_rule": "gate first"},
                {"surface": "canonical_center", "receiver_rule": "read parent truth"},
                {
                    "surface": "closeout_attention",
                    "receiver_rule": "read closeout before summary",
                },
                {
                    "surface": "mutation_preflight",
                    "receiver_rule": "check side effects before action",
                },
            ],
            "misread_guards": [
                {
                    "name": "compaction_not_completion",
                    "rule": "Compaction summaries remain subordinate to closeout status.",
                    "trigger_surface": "closeout_attention + compaction summary",
                    "operator_action": "read closeout first",
                }
            ],
            "priority_misread_guard": {
                "name": "compaction_not_completion",
                "rule": "Compaction summaries remain subordinate to closeout status.",
                "trigger_surface": "closeout_attention + compaction summary",
                "operator_action": "read closeout first",
                "why_now": "latest closeout is partial",
            },
        },
    }
    adapter = build_claude_entry_adapter(session_start_payload=session_payload)
    correction = dict(adapter.get("priority_correction") or {})
    reread = list(correction.get("re_read_now") or [])
    present = bool(
        str(correction.get("name", "")).strip()
        and str(correction.get("blocked_assumption", "")).strip()
        and reread == ["readiness", "canonical_center", "closeout_attention", "mutation_preflight"]
        and str(correction.get("bounded_next_step_target", "")).strip()
        == "shared_code_edit.path_overlap_preflight"
    )
    return {
        "present": present,
        "summary_text": (
            "claude_priority_correction_probe "
            f"name={str(correction.get('name', '')).strip() or 'missing'} "
            f"reread={len(reread)} "
            f"next={str(correction.get('bounded_next_step_target', '')).strip() or 'missing'} "
            f"rule={'yes' if str(correction.get('receiver_rule', '')).strip() else 'no'}"
        ),
    }


def _probe_hot_memory_pull_boundary_clarity() -> dict[str, Any]:
    from apps.dashboard.frontend.utils.session_start import build_tier1_orientation_shell
    from tonesoul.hot_memory import build_canonical_center, build_hot_memory_ladder

    canonical_center = build_canonical_center(
        task_text=(
            "## Water-Bucket Snapshot\n"
            "- Current short board:\n"
            "  - Phase 838: fifteenth trial candidate admission\n"
        )
    )
    hot_memory_ladder = build_hot_memory_ladder(
        canonical_center=canonical_center,
        import_posture={
            "posture": {"present": True},
            "readiness": {"present": True},
            "compactions": {
                "present": True,
                "receiver_obligation": "must_review",
                "closeout_status": "partial",
            },
            "recent_traces": {"present": True},
            "subject_snapshot": {"present": False},
            "working_style": {"present": False},
            "council_dossier": {"present": False},
        },
        readiness={"status": "pass"},
        stable_count=3,
        contested_count=1,
        stale_count=0,
    )
    session_payload = {
        "present": True,
        "tier": 1,
        "canonical_center": canonical_center,
        "subsystem_parity": {
            "counts": {"baseline": 3, "beta_usable": 5, "partial": 2, "deferred": 1},
            "next_focus": {
                "resolved_to": "shared_code_edit.path_overlap_preflight",
                "source_family": "mutation_preflight_hooks",
                "operator_action": "Run the shared-edit preflight first.",
                "focus_pressures": ["readiness=pass"],
            },
            "families": [],
        },
        "closeout_attention": {
            "present": True,
            "status": "partial",
            "summary_text": "latest closeout is partial",
            "receiver_rule": "read closeout first",
        },
        "observer_shell": {
            "summary_text": "observer ready",
            "receiver_note": "shell only",
            "counts": {"stable": 3, "contested": 1, "stale": 0},
            "stable_headlines": [],
            "contested_headlines": [],
            "stale_headlines": [],
            "hot_memory_ladder": hot_memory_ladder,
        },
    }
    dashboard_shell = build_tier1_orientation_shell(session_payload)
    boundary = dict(hot_memory_ladder.get("current_pull_boundary") or {})
    dashboard_boundary = dict(dashboard_shell.get("hot_memory_boundary") or {})
    present = bool(
        str(boundary.get("pull_posture", "")).strip()
        and str(boundary.get("preferred_stop_at", "")).strip()
        and str(boundary.get("operator_action", "")).strip()
        and dashboard_boundary.get("pull_posture") == boundary.get("pull_posture")
        and dashboard_boundary.get("preferred_stop_at") == boundary.get("preferred_stop_at")
    )
    return {
        "present": present,
        "summary_text": (
            "hot_memory_pull_boundary_probe "
            f"posture={str(boundary.get('pull_posture', '')).strip() or 'missing'} "
            f"stop_at={str(boundary.get('preferred_stop_at', '')).strip() or 'missing'} "
            f"dashboard_sync={'yes' if present else 'no'}"
        ),
    }


def _probe_memory_panel_tier_subordination() -> dict[str, Any]:
    import importlib.util

    module_path = REPO_ROOT / "apps" / "dashboard" / "frontend" / "components" / "memory_panel.py"
    frontend_root = module_path.parents[1]
    if str(frontend_root) not in sys.path:
        sys.path.insert(0, str(frontend_root))
    spec = importlib.util.spec_from_file_location("dashboard_memory_panel_probe", module_path)
    if spec is None or spec.loader is None:
        return {
            "present": False,
            "summary_text": "memory_panel_probe loader=missing",
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    build_memory_panel_view_model = module.build_memory_panel_view_model

    payload = build_memory_panel_view_model(
        tier0_shell={"readiness_status": "pass"},
        tier1_shell={
            "canonical_cards": {"short_board": "Phase 781"},
            "closeout_attention": {"summary_text": "latest closeout is partial"},
        },
        selected_count=2,
    )
    present = bool(
        str(payload.get("reference_boundary_class", "")).strip() == "auxiliary_only"
        and "reference selection" in str(payload.get("subtitle", ""))
        and "Tier 0 / Tier 1" in str(payload.get("operator_note", ""))
        and str(payload.get("selection_caution", "")).strip()
        and str(payload.get("selected_count_summary", "")).strip() == "已選 2 份參考資料"
    )
    return {
        "present": present,
        "summary_text": (
            "memory_panel_probe "
            f"boundary={str(payload.get('reference_boundary_class', '')).strip() or 'missing'} "
            f"caution={'yes' if str(payload.get('selection_caution', '')).strip() else 'no'} "
            f"selected={str(payload.get('selected_count', '')).strip() or 'missing'}"
        ),
    }


def _probe_status_panel_operator_copy_clarity() -> dict[str, Any]:
    import importlib.util

    module_path = REPO_ROOT / "apps" / "dashboard" / "frontend" / "components" / "status_panel.py"
    frontend_root = module_path.parents[1]
    if str(frontend_root) not in sys.path:
        sys.path.insert(0, str(frontend_root))
    spec = importlib.util.spec_from_file_location("dashboard_status_panel_probe", module_path)
    if spec is None or spec.loader is None:
        return {
            "present": False,
            "summary_text": "status_panel_probe loader=missing",
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    build_status_panel_view_model = module.build_status_panel_view_model

    payload = build_status_panel_view_model(
        snapshot={
            "conversation": {
                "count": 1,
                "last": {"status": "success", "timestamp": "2026-04-07T00:00:00+00:00"},
            },
            "persona": {"id": "dashboard-workspace"},
            "run_id": "run-001",
        },
        summary={
            "intent": {"status": "achieved"},
            "control": {"status": "success"},
            "persona": {"id": "dashboard-workspace"},
            "run_id": "run-001",
        },
        tier0_shell={
            "readiness_status": "pass",
            "task_track": "feature_track",
            "deliberation_mode": "lightweight_review",
            "next_followup": {
                "command": "python scripts/run_shared_edit_preflight.py --path task.md"
            },
            "receiver_rule": "bounded only",
            "hook_badges": [{"name": "shared_edit_path_overlap", "status": "active"}],
        },
        tier1_shell={
            "canonical_cards": {
                "short_board": "Phase 774",
                "successor_correction": "closeout overrides smooth compaction prose",
                "source_precedence": "canonical > live > derived",
            },
            "parity_counts": {"baseline": 2, "beta_usable": 1, "partial": 1, "deferred": 0},
            "closeout_attention": {"summary_text": "latest closeout is partial"},
            "observer_shell": {"summary_text": "observer stable=2 contested=1 stale=0"},
        },
        tier2_drawer={
            "recommended_open": True,
            "trigger_reasons": ["closeout_attention_present"],
            "active_group_names": ["Mutation And Closeout"],
            "summary_text": "tier2_drawer=recommended groups=1 triggers=1",
            "next_pull_commands": [
                "python scripts/run_publish_push_preflight.py --agent dashboard-workspace"
            ],
        },
        improvement_cue={
            "present": True,
            "summary_text": "self_improvement_trial_wave promote=1 park=1 | status surface only",
            "top_result": "consumer_parity_packaging_v1 / promoted_result",
            "next_action": "reuse this drift-validation wave whenever shared consumer packaging changes",
            "receiver_rule": "Secondary only. Open the dedicated self-improvement status surface first.",
            "source_path": "docs/status/self_improvement_trial_wave_latest.md",
            "outcome_counts": {"promote": 1, "park": 1, "retire": 0, "blocked": 0},
        },
    )
    operator_posture = dict(payload.get("operator_posture") or {})
    telemetry = dict(payload.get("telemetry") or {})
    present = bool(
        "Tier 0 / Tier 1" in str(operator_posture.get("note", ""))
        and "parent action path" in str(operator_posture.get("primary_rule", ""))
        and str(operator_posture.get("secondary_rule", "")).strip()
        == "Self-improvement posture and telemetry stay secondary."
        and str(telemetry.get("conversation_status", "")).strip() == "成功"
        and str(telemetry.get("intent_status", "")).strip() == "達成"
        and str(telemetry.get("control_status", "")).strip() == "成功"
    )
    return {
        "present": present,
        "summary_text": (
            "status_panel_probe "
            f"primary={'yes' if str(operator_posture.get('primary_rule', '')).strip() else 'no'} "
            f"secondary={'yes' if str(operator_posture.get('secondary_rule', '')).strip() else 'no'} "
            f"telemetry={str(telemetry.get('conversation_status', '')).strip() or 'missing'}"
        ),
    }


def _probe_command_shelf_activation_clarity() -> dict[str, Any]:
    import importlib.util

    module_path = REPO_ROOT / "apps" / "dashboard" / "frontend" / "utils" / "session_start.py"
    frontend_root = module_path.parents[1]
    if str(frontend_root) not in sys.path:
        sys.path.insert(0, str(frontend_root))
    spec = importlib.util.spec_from_file_location("dashboard_command_shelf_probe", module_path)
    if spec is None or spec.loader is None:
        return {
            "present": False,
            "summary_text": "command_shelf_probe loader=missing",
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    build_dashboard_command_shelf = module.build_dashboard_command_shelf

    payload = build_dashboard_command_shelf(
        agent_id="dashboard-workspace",
        tier0_shell={
            "next_followup": {
                "target": "mutation_preflight.next_followup",
                "command": "python scripts/run_shared_edit_preflight.py --agent dashboard-workspace --path task.md",
                "reason": "Visible because Tier 0 already exposes one bounded follow-up.",
            }
        },
        tier2_drawer={
            "trigger_reasons": ["closeout_attention_present", "claim_conflict_visible"],
            "next_pull_commands": [
                "python scripts/run_publish_push_preflight.py --agent dashboard-workspace"
            ],
        },
    )
    commands = list(payload.get("commands") or [])
    next_move = commands[3] if len(commands) > 3 else {}
    deep_pull = commands[4] if len(commands) > 4 else {}
    present = bool(
        "source, activation, and return cues" in str(payload.get("operator_rule", "")).strip()
        and str(next_move.get("source_surface", "")).strip() == "mutation_preflight.next_followup"
        and str(next_move.get("activation_reason", "")).strip()
        == "Visible because Tier 0 already exposes one bounded follow-up."
        and str(next_move.get("return_rule", "")).strip().startswith("If this move broadens scope")
        and str(deep_pull.get("source_surface", "")).strip()
        == "tier2_deep_governance_drawer.next_pull_commands"
        and "closeout_attention_present" in str(deep_pull.get("activation_reason", "")).strip()
        and str(deep_pull.get("return_rule", ""))
        .strip()
        .startswith("When Tier 2 trigger reasons clear")
    )
    return {
        "present": present,
        "summary_text": (
            "command_shelf_probe "
            f"next_source={str(next_move.get('source_surface', '')).strip() or 'missing'} "
            f"next_activation={'yes' if str(next_move.get('activation_reason', '')).strip() else 'no'} "
            f"deep_return={'yes' if str(deep_pull.get('return_rule', '')).strip() else 'no'}"
        ),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Self-Improvement Trial Wave",
        "",
        f"**Summary**: `{report.get('summary_text', '')}`",
        "",
        f"> {report.get('receiver_rule', '')}",
        "",
        "## Trial Families",
        "",
    ]
    for family in report.get("trial_families") or []:
        lines.append(f"- `{family}`")
    lines.extend(["", "## Outcomes", ""])
    counts = report.get("outcome_counts") or {}
    for key in ("promote", "park", "retire", "blocked", "not_ready_for_trial"):
        lines.append(f"- `{key}`: `{counts.get(key, 0)}`")
    lines.extend(["", "## Candidates", ""])
    for item in report.get("candidates") or []:
        candidate = item.get("candidate_record") or {}
        closeout = item.get("analyzer_closeout") or {}
        result_surface = item.get("result_surface") or {}
        lines.append(
            f"- `{candidate.get('candidate_id', 'unknown')}` -> `{closeout.get('status', '')}`"
        )
        lines.append(f"  - target_surface: `{candidate.get('target_surface', '')}`")
        lines.append(f"  - success_metric: `{candidate.get('success_metric', '')}`")
        lines.append(f"  - result_story: {closeout.get('result_story', '')}")
        lines.append(f"  - evidence: `{closeout.get('evidence_bundle_summary', '')}`")
        lines.append(f"  - result_surface: `{result_surface.get('surface_status', '')}`")
        lines.append(f"  - replay_rule: `{result_surface.get('replay_rule', '')}`")
        lines.append(f"  - residue_posture: `{result_surface.get('residue_posture', '')}`")
        unresolved = closeout.get("unresolved_items") or []
        if unresolved:
            lines.append("  - unresolved_items:")
            for unresolved_item in unresolved:
                lines.append(f"    - {unresolved_item}")
        lines.append(f"  - promotion_limit: `{closeout.get('promotion_limit', '')}`")
        lines.append(f"  - next_action: `{closeout.get('next_action', '')}`")
    lines.extend(["", "## Next Short Board", "", f"- `{report.get('next_short_board', '')}`", ""])
    return "\n".join(lines)


def run_self_improvement_trial_wave(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, Any]:
    from scripts.run_consumer_drift_validation_wave import run_consumer_drift_validation_wave
    from tonesoul.self_improvement_trial_wave import build_self_improvement_trial_wave

    consumer_drift_report = run_consumer_drift_validation_wave(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    deliberation_hint_probe = _probe_deliberation_hint(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    task_board_probe = _probe_task_board_parking(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    shared_edit_probe = _probe_shared_edit_preflight()
    publish_push_probe = _probe_publish_push_preflight()
    mutation_followup_probe = _probe_mutation_followup_routing()
    surface_versioning_probe = _probe_surface_versioning_lineage()
    launch_health_probe = _probe_launch_health_trend_clarity()
    internal_state_probe = _probe_internal_state_action_clarity()
    hook_chain_probe = _probe_hook_chain_trigger_clarity(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    consumer_misread_guard_probe = _probe_consumer_misread_guard_clarity(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    subsystem_parity_focus_probe = _probe_subsystem_parity_focus_clarity(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    closeout_attention_probe = _probe_closeout_attention_action_clarity()
    claude_priority_correction_probe = _probe_claude_priority_correction_clarity()
    hot_memory_pull_boundary_probe = _probe_hot_memory_pull_boundary_clarity()
    memory_panel_probe = _probe_memory_panel_tier_subordination()
    status_panel_probe = _probe_status_panel_operator_copy_clarity()
    command_shelf_probe = _probe_command_shelf_activation_clarity()
    operator_retrieval_contract_present = (
        REPO_ROOT / "docs/architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md"
    ).exists()
    compiled_landing_zone_spec_present = (
        REPO_ROOT / "docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md"
    ).exists()
    retrieval_runner_present = (REPO_ROOT / "scripts/run_operator_retrieval_query.py").exists()

    return build_self_improvement_trial_wave(
        agent=agent,
        consumer_drift_report=consumer_drift_report,
        deliberation_hint_probe=deliberation_hint_probe,
        task_board_probe=task_board_probe,
        shared_edit_probe=shared_edit_probe,
        publish_push_probe=publish_push_probe,
        mutation_followup_probe=mutation_followup_probe,
        surface_versioning_probe=surface_versioning_probe,
        launch_health_probe=launch_health_probe,
        internal_state_probe=internal_state_probe,
        hook_chain_probe=hook_chain_probe,
        consumer_misread_guard_probe=consumer_misread_guard_probe,
        subsystem_parity_focus_probe=subsystem_parity_focus_probe,
        closeout_attention_probe=closeout_attention_probe,
        claude_priority_correction_probe=claude_priority_correction_probe,
        hot_memory_pull_boundary_probe=hot_memory_pull_boundary_probe,
        memory_panel_probe=memory_panel_probe,
        status_panel_probe=status_panel_probe,
        command_shelf_probe=command_shelf_probe,
        operator_retrieval_contract_present=operator_retrieval_contract_present,
        compiled_landing_zone_spec_present=compiled_landing_zone_spec_present,
        retrieval_runner_present=retrieval_runner_present,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_self_improvement_trial_wave(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
    )
    if args.json_out is not None:
        _write_json(args.json_out, payload)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(_render_markdown(payload), encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
