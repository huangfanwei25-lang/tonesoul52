from __future__ import annotations

from tonesoul.diagnose import compact_diagnostic, full_diagnostic
from tonesoul.runtime_adapter import GovernancePosture


class _FakeRedis:
    def info(self, section: str):
        assert section == "memory"
        return {"used_memory": 2 * 1024 * 1024}

    def dbsize(self) -> int:
        return 17


class _FakeStore:
    backend_name = "redis"
    is_redis = True
    _r = _FakeRedis()

    def get_traces(self, n: int = 999):
        return [
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-27T01:02:03Z",
                "topics": ["shared-memory"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["left a claim"],
            }
        ]

    def get_zones(self):
        return {
            "zones": [{"name": "governance", "level": 2, "visit_count": 4}],
            "total_sessions": 9,
            "world_mood": "steady",
            "weather": "clear",
        }


class _FakeShield:
    @classmethod
    def load(cls, store):
        return cls()

    def audit(self, store):
        return {
            "integrity": "intact",
            "chain_valid": True,
            "total_traces": 3,
            "signature_failures": [],
            "chain_errors": [],
        }


def _fake_posture() -> GovernancePosture:
    return GovernancePosture(
        last_updated="2026-03-27T00:00:00Z",
        soul_integral=0.81,
        tension_history=[{"topic": "coordination", "severity": 0.42}],
        active_vows=[{"id": "v1", "content": "be explicit"}],
        baseline_drift={
            "caution_bias": 0.55,
            "innovation_bias": 0.48,
            "autonomy_level": 0.36,
        },
        session_count=9,
    )


def _fake_packet():
    return {
        "posture": {
            "risk_posture": {
                "score": 0.67,
                "level": "high",
                "recommended_action": "review_before_commit",
                "factors": ["high_recent_tension"],
                "inputs": {"tension_pressure": 0.7},
            }
        },
        "recent_traces": [
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-27T01:02:03Z",
                "topics": ["shared-memory"],
                "key_decision_count": 1,
                "council_dossier_summary": {
                    "confidence_posture": "contested",
                    "has_minority_report": True,
                    "confidence_decomposition": {
                        "calibration_status": "descriptive_only",
                        "coverage_posture": "partial",
                        "adversarial_posture": "visible_dissent",
                    },
                    "evolution_suppression_flag": True,
                    "realism_note": (
                        "Descriptive agreement record only; dissent is visible and suppression "
                        "risk is flagged, so review minority signals before treating approval as settled."
                    ),
                },
            }
        ],
        "recent_visitors": [
            {
                "agent": "claude",
                "timestamp": "2026-03-27T01:10:00Z",
                "source": "diagnose",
            }
        ],
        "active_claims": [
            {
                "task_id": "coord-contract",
                "agent": "codex",
                "summary": "write shared ops contract",
                "paths": ["docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"],
            }
        ],
        "recent_checkpoints": [
            {
                "checkpoint_id": "cp-1",
                "agent": "codex",
                "session_id": "sess-1",
                "summary": "Ack path is pending in the packet script.",
                "pending_paths": ["scripts/run_r_memory_packet.py"],
                "next_action": "add --agent and --ack support",
                "source": "cli",
                "updated_at": "2026-03-27T01:15:00Z",
            }
        ],
        "recent_compactions": [
            {
                "agent": "claude",
                "updated_at": "2026-03-27T01:20:00Z",
                "summary": "captured current boundary decisions",
            }
        ],
        "recent_subject_snapshots": [
            {
                "snapshot_id": "subj-1",
                "agent": "codex",
                "session_id": "sess-1",
                "summary": "Stay packet-first and keep theory out of runtime truth.",
                "stable_vows": ["do not smuggle theory into runtime"],
                "durable_boundaries": ["protected files stay human-managed"],
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["leave compaction before release"],
                "active_threads": ["subject-snapshot rollout"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
                "refresh_signals": ["refresh when durable boundaries change"],
                "source": "cli",
                "updated_at": "2026-03-28T00:04:00Z",
            }
        ],
        "parallel_lanes": {
            "canonical_commit_serialized": True,
            "perspectives_surface": "ts:perspectives:{agent_id}",
            "checkpoints_surface": "ts:checkpoints:*",
            "subject_snapshot_surface": "ts:subject_snapshots",
        },
        "project_memory_summary": {
            "focus_topics": ["shared-memory", "runtime"],
            "recent_agents": ["codex", "claude"],
            "active_claim_count": 1,
            "pending_paths": ["docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"],
            "carry_forward": ["keep packet first"],
            "next_actions": ["integrate risk posture into packet"],
            "subject_anchor": {
                "summary": "Stay packet-first and keep theory out of runtime truth.",
                "stable_vows": ["do not smuggle theory into runtime"],
                "durable_boundaries": ["protected files stay human-managed"],
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["leave compaction before release"],
                "active_threads": ["subject-snapshot rollout"],
            },
            "working_style_anchor": {
                "summary": "prefs=prefer packet before broad repo scan | routines=leave compaction before release",
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["leave compaction before release"],
                "guardrail_boundaries": ["protected files stay human-managed"],
                "receiver_posture": "advisory_apply_not_promote",
                "prompt_defaults": [
                    "state the goal function before long transfer or extraction prompts",
                    "keep P0/P1/P2 explicit when constraints may conflict",
                    "mark [資料不足] instead of filling gaps with unsupported guesses",
                ],
                "render_caveat": "Treat shell `??` or garbled CJK as render-layer noise until a UTF-8 file read proves real corruption.",
            },
            "working_style_observability": {
                "status": "partial",
                "drift_risk": "medium",
                "trackable_item_count": 2,
                "reinforced_item_count": 1,
                "signal_count": 3,
                "signal_sources": ["carry_forward", "routing_summary"],
                "reinforced_items": ["decision_preferences: prefer packet before broad repo scan"],
                "unreinforced_items": ["verified_routines: leave compaction before release"],
                "summary_text": "working_style=partial reinforced=1/2 signals=3 drift=medium",
                "receiver_note": "Only part of the shared working style is echoed by recent handoff surfaces. Keep the playbook visible instead of assuming full continuity.",
            },
            "working_style_import_limits": {
                "apply_posture": "explicit_reuse_only",
                "safe_apply": [
                    "scan_order: use shared packet/claim surfaces before widening the repo scan when they still fit the task.",
                    "evidence_handling: keep the shared evidence discipline instead of replacing it with model-native guessing.",
                ],
                "must_not_import": [
                    "canonical_governance_truth: habits must not become runtime law, axiom enforcement, or authority truth.",
                    "durable_identity: style continuity must not silently become stable selfhood or subject promotion.",
                ],
                "stop_conditions": [
                    "current task or human instruction conflicts with the inherited habit",
                ],
                "receiver_guidance": "Only part of the shared style is still echoed. Reuse it deliberately and keep checking task-local evidence instead of assuming full continuity.",
                "summary_text": "working_style_import=explicit_reuse_only safe=2 blocked=2 drift=medium",
            },
            "evidence_readout_posture": {
                "summary_text": (
                    "evidence=tested(session_control_and_handoff,council_mechanics) "
                    "runtime_present(continuity_effectiveness) "
                    "descriptive_only(council_decision_quality) "
                    "document_backed(axiom_and_theory_claims)"
                ),
                "classification_counts": {
                    "tested": 2,
                    "runtime_present": 1,
                    "descriptive_only": 1,
                    "document_backed": 1,
                },
                "lanes": [
                    {
                        "lane": "session_control_and_handoff",
                        "classification": "tested",
                        "receiver_use": "safe_workflow_assumption",
                        "note": "Session-start/session-end, packet, delta, readiness, and receiver guards are regression-backed enough to reuse as current workflow discipline.",
                    },
                    {
                        "lane": "continuity_effectiveness",
                        "classification": "runtime_present",
                        "receiver_use": "bounded_continuity_help",
                        "note": "Claims, checkpoints, compactions, and subject/working-style surfaces are live and partially tested, but broader cross-session effectiveness is still a bounded runtime claim rather than a proven quality guarantee.",
                    },
                    {
                        "lane": "council_decision_quality",
                        "classification": "descriptive_only",
                        "receiver_use": "context_only",
                        "note": "Agreement, coherence, and confidence posture still describe internal review context, not calibrated correctness.",
                    },
                ],
                "receiver_rule": "Use tested lanes for current workflow assumptions, runtime_present lanes as bounded mechanism presence, descriptive_only lanes as context not proof, and document_backed lanes as intent/boundary rather than runtime fact.",
            },
            "launch_claim_posture": {
                "current_tier": "collaborator_beta",
                "next_target_tier": "public_launch",
                "public_launch_ready": False,
                "tier_guidance": [
                    {
                        "tier": "internal_alpha",
                        "posture": "safe_current_claims_only",
                        "note": "Safe to say trusted internal operators can use the current file-backed session-start/packet/diagnose workflow with tested receiver and council-mechanism readouts.",
                    },
                    {
                        "tier": "collaborator_beta",
                        "posture": "guided_and_bounded",
                        "note": "Safe only as a guided beta target: repeated validation exists and the launch-default coordination story is explicit, but continuity effectiveness and council decision quality remain bounded rather than proven.",
                    },
                    {
                        "tier": "public_launch",
                        "posture": "deferred",
                        "note": "Not yet honest to present ToneSoul as broadly launch-mature; public language must not overstate continuity effectiveness, council decision quality, or Redis/live shared memory.",
                    },
                ],
                "safe_now": [
                    "session_control_and_handoff=tested: describe session-start, packet, delta, readiness, and receiver guards as the current tested coordination workflow.",
                    "coordination_backend=file-backed: describe file-backed coordination with receiver guards as the current launch-default story.",
                ],
                "blocked_overclaims": [
                    {
                        "claim": "continuity_effectiveness",
                        "current_classification": "runtime_present",
                        "reason": "Do not claim broadly proven cross-session continuity; current evidence supports bounded runtime presence and repeated validation, not public-grade proof.",
                    },
                    {
                        "claim": "council_decision_quality",
                        "current_classification": "descriptive_only",
                        "reason": "Do not present council agreement or coherence as calibrated correctness; current confidence surfaces are descriptive, not accuracy-backed.",
                    },
                    {
                        "claim": "live_shared_memory",
                        "current_classification": "not_launch_default",
                        "reason": "Do not present Redis/live shared memory as the launch-default or hardened public story while launch_default_mode remains file-backed and launch_alignment is runtime_override_not_launch_default.",
                    },
                ],
                "receiver_rule": "Use collaborator-beta wording only for guided file-backed workflow and explicit evidence-bounded surfaces, and keep public-launch language deferred until evidence moves beyond runtime_present/descriptive_only on the known short boards.",
                "summary_text": "launch_claims=current:collaborator_beta public_launch:deferred blocked=continuity_effectiveness,council_decision_quality,live_shared_memory",
            },
            "launch_health_trend_posture": {
                "summary_text": (
                    "launch_health current=collaborator_beta public_ready=false "
                    "descriptive=current_launch_tier,public_launch_ready_flag "
                    "trendable=coordination_backend_alignment,collaborator_beta_validation_health "
                    "forecast_later=public_launch_forecast"
                ),
                "current_state": {
                    "current_tier": "collaborator_beta",
                    "public_launch_ready": False,
                    "launch_default_mode": "file-backed",
                    "launch_alignment": "runtime_override_not_launch_default",
                },
                "metric_classes": [
                    {
                        "metric": "current_launch_tier",
                        "classification": "descriptive_only",
                    },
                    {
                        "metric": "coordination_backend_alignment",
                        "classification": "trendable",
                    },
                    {
                        "metric": "public_launch_forecast",
                        "classification": "forecast_later",
                    },
                ],
                "trend_watch_cues": [
                    {
                        "metric": "coordination_backend_alignment",
                        "watch_for": "alignment_stays_consistent_across_validation_waves",
                    },
                    {
                        "metric": "collaborator_beta_validation_health",
                        "watch_for": "repeated_validation_without_new_overclaim_pressure",
                    },
                ],
                "forecast_blockers": [
                    {
                        "metric": "continuity_effectiveness",
                        "classification": "runtime_present",
                    },
                    {
                        "metric": "council_decision_quality",
                        "classification": "descriptive_only",
                    },
                ],
                "operator_actions": [
                    "Use current launch language as collaborator-beta-only unless a human explicitly narrows it further.",
                    "Track trendable metrics across repeated validation waves before changing launch posture wording.",
                    "Do not emit predictive launch numbers or success probabilities.",
                ],
                "forecast_boundary": "Do not emit predictive launch numbers until trendable metrics are separately calibrated.",
                "receiver_rule": "Treat launch health as present-tense posture plus future trend lane.",
            },
            "internal_state_observability": {
                "summary_text": "internal_state coordination=low drift=medium stop_pressure=medium deliberation=visible",
                "current_state": {
                    "coordination_strain": "low",
                    "continuity_drift": "medium",
                    "stop_reason_pressure": "medium",
                    "deliberation_conflict": "visible",
                    "closeout_status": "partial",
                    "has_stop_reason": False,
                    "has_minority_report": True,
                    "evolution_suppression_flag": True,
                },
                "evidence_sources": [
                    "risk_posture:stable",
                    "working_style_drift:medium",
                    "closeout:partial",
                    "deliberation_conflict:visible",
                ],
                "pressure_watch_cues": [
                    {
                        "signal": "coordination_strain",
                        "current_value": "low",
                    },
                    {
                        "signal": "continuity_drift",
                        "current_value": "medium",
                    },
                ],
                "operator_actions": [
                    "Keep shared side effects bounded and keep readiness/claim checks ahead of broader edits.",
                    "Re-read working-style and closeout surfaces before promoting continuity stories.",
                ],
                "selfhood_boundary": "These are functional coordination pressures inferred from observable runtime surfaces, not proof of subjective feeling, emotion, or selfhood.",
                "receiver_rule": "Use this readout to notice strain, drift, stop pressure, and visible disagreement early.",
            },
            "routing_summary": {
                "total_events": 2,
                "preview_count": 1,
                "write_count": 1,
                "forced_count": 1,
                "overlap_count": 1,
                "misroute_signal_count": 1,
                "surface_counts": {"checkpoint": 1, "compaction": 1},
                "recent_agents": ["codex", "claude"],
                "dominant_surface": "checkpoint",
                "summary_text": "router=writes=1 previews=1 overrides=1 overlap=1 misroute_signals=1 top=checkpoint",
                "recent_events": [
                    {
                        "event_id": "route-1",
                        "agent": "codex",
                        "surface": "checkpoint",
                        "action": "preview",
                        "forced": False,
                        "overlap": False,
                        "misroute_signal": False,
                        "updated_at": "2026-03-27T01:17:00Z",
                        "summary": "resume packet cleanup",
                    }
                ],
            },
            "subject_refresh": {
                "status": "refresh_candidate",
                "refresh_recommended": True,
                "snapshot_present": True,
                "latest_snapshot_id": "subj-1",
                "snapshot_updated_at": "2026-03-28T00:04:00Z",
                "risk_level": "high",
                "newer_compaction_count": 1,
                "newer_checkpoint_count": 1,
                "active_claim_count": 1,
                "routing_misroute_signal_count": 1,
                "field_guidance": [
                    {
                        "field": "stable_vows",
                        "action": "must_not_auto_promote",
                        "evidence_level": "human_confirmation",
                        "candidate_values": [],
                        "reason": "vows stay operator-reviewed",
                    },
                    {
                        "field": "active_threads",
                        "action": "may_refresh_directly",
                        "evidence_level": "compaction-backed",
                        "candidate_values": ["shared-memory", "runtime"],
                        "reason": "fresh compaction confirms current focus",
                    },
                ],
                "promotion_hazards": [
                    "Do not promote active claims into durable identity; claims are ownership signals, not selfhood."
                ],
                "recommended_command": (
                    'python scripts/save_subject_snapshot.py --agent <your-id> --summary "..." '
                    '--thread "shared-memory" --thread "runtime"'
                ),
                "summary_text": "subject_refresh=refresh_candidate direct=1 manual=2 hazards=1 evidence=c1/k1",
            },
            "repo_progress": {
                "available": True,
                "branch": "codex/r-memory-compaction-lane-20260326",
                "head": "04c243d",
                "staged_count": 1,
                "modified_count": 2,
                "untracked_count": 3,
                "dirty_count": 6,
                "path_preview": [
                    "tonesoul/runtime_adapter.py",
                    "tonesoul/diagnose.py",
                ],
            },
            "summary_text": (
                "focus=shared-memory, runtime | next=integrate risk posture into packet | "
                "repo=codex/r-memory-compaction-lane-20260326@04c243d dirty=6 | "
                "router=writes=1 previews=1 overrides=1 overlap=1 misroute_signals=1 top=checkpoint | "
                "subject_refresh=refresh_candidate direct=1 manual=2 hazards=1 evidence=c1/k1"
            ),
        },
        "recent_routing_events": [
            {
                "event_id": "route-1",
                "agent": "codex",
                "surface": "checkpoint",
                "action": "preview",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "updated_at": "2026-03-27T01:17:00Z",
                "summary": "resume packet cleanup",
            },
            {
                "event_id": "route-2",
                "agent": "claude",
                "surface": "compaction",
                "action": "write",
                "forced": True,
                "overlap": True,
                "misroute_signal": True,
                "updated_at": "2026-03-27T01:18:00Z",
                "summary": "force a compaction lane despite overlap",
            },
        ],
        "coordination_mode": {
            "mode": "redis-live",
            "live_surfaces_available": True,
            "delta_feed_enabled": True,
            "event_channel": "ts:events",
            "surface_modes": {
                "claims": "live",
                "perspectives": "live",
                "checkpoints": "live",
                "compactions": "live",
                "subject_snapshots": "live",
                "observer_cursors": "live",
                "routing_events": "live",
                "visitors": "live",
            },
            "recheck_command": "python scripts/run_r_memory_packet.py --agent codex",
            "ack_command": "python scripts/run_r_memory_packet.py --agent codex --ack",
            "refresh_hint": (
                "Redis live surfaces may change mid-session; re-read packet before shared edits after long work or when other agents arrive."
            ),
            "launch_default_mode": "file-backed",
            "launch_alignment": "runtime_override_not_launch_default",
            "launch_posture_note": (
                "Current runtime is redis-live, but the launch-default coordination story remains file-backed until Redis hardening is explicitly promoted."
            ),
            "summary_text": (
                "coordination=redis-live claims=live checkpoints=live subjects=live launch_default=file-backed "
                "delta=enabled visitors=live active=claims:1/checkpoints:1/compactions:1/subjects:1/routing:2/visitors:1"
            ),
        },
        "operator_guidance": {
            "backend_mode": "redis",
            "session_start": [
                "python scripts/start_agent_session.py --agent <your-id>",
                "python -m tonesoul.diagnose --agent <your-id>",
                "python scripts/run_r_memory_packet.py --agent <your-id> --ack",
                "python scripts/run_task_claim.py list",
            ],
            "session_end": [
                'python scripts/end_agent_session.py --agent <your-id> --summary "..." --path "..."',
                'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..."',
                'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..."',
                "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
            ],
            "preflight_chain": {
                "present": True,
                "summary_text": "hook_chain=shared_edit_path_overlap -> publish_push_posture -> task_board_parking",
                "stages": [
                    {
                        "name": "shared_edit_path_overlap",
                        "command": "python scripts/run_shared_edit_preflight.py --agent codex --path <repo-path>",
                    },
                    {
                        "name": "publish_push_posture",
                        "command": "python scripts/run_publish_push_preflight.py --agent codex",
                    },
                    {
                        "name": "task_board_parking",
                        "command": "python scripts/run_task_board_preflight.py --agent codex --proposal-kind external_idea --target-path task.md",
                    },
                ],
            },
            "coordination_commands": {
                "claim": 'python scripts/run_task_claim.py claim <task_id> --agent <your-id> --summary "..."',
                "perspective": 'python scripts/save_perspective.py --agent <your-id> --summary "..." --stance "..."',
                "checkpoint": 'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..."',
                "compaction": 'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..."',
                "signal_router": 'python scripts/route_r_memory_signal.py --agent <your-id> --summary "..." --path "..." --next-action "..." --write',
                "subject_snapshot": 'python scripts/save_subject_snapshot.py --agent <your-id> --summary "..." --boundary "..." --preference "..."',
                "apply_subject_refresh": "python scripts/apply_subject_refresh.py --agent <your-id> --field active_threads",
                "release": "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
            },
            "recommended_order": [
                "diagnose/load",
                "packet",
                "claim",
                "work",
                "perspective/checkpoint/compaction",
                "commit",
                "release",
            ],
            "current_reminders": [
                "Prefer recent_compactions and project_memory_summary before older recent_traces.",
                "Active claims are visible; coordinate before editing overlapping paths.",
                "A recent subject snapshot is visible; treat it as durable working identity, but still non-canonical.",
                "Subject-refresh heuristics found low-risk updates; review subject_refresh before writing the next snapshot.",
                "Redis live surfaces may change mid-session; re-read packet before shared edits after long work or when other agents arrive.",
                "Launch coordination default: Current runtime is redis-live, but the launch-default coordination story remains file-backed until Redis hardening is explicitly promoted.",
                "A delta feed is visible for this agent; ack after review to advance the observer baseline.",
            ],
            "completion_rule": (
                "Before ending a session, externalize progress with checkpoint or compaction, "
                "then release any shared claim."
            ),
        },
        "delta_feed": {
            "observer_id": "codex",
            "first_observation": False,
            "has_updates": True,
            "update_count": 3,
            "previous_seen_at": "2026-03-27T00:59:00Z",
            "summary_text": "checkpoints=1 | claims(+0/-1) | repo=03fdabc->04c243d dirty=4->6",
            "new_compactions": [],
            "new_subject_snapshots": [],
            "new_checkpoints": [
                {
                    "checkpoint_id": "cp-1",
                    "agent": "codex",
                    "summary": "Ack path is pending in the packet script.",
                    "next_action": "add --agent and --ack support",
                    "updated_at": "2026-03-27T01:15:00Z",
                }
            ],
            "new_traces": [],
            "new_claims": [],
            "released_claim_ids": ["old-claim"],
            "repo_change": {
                "changed": True,
                "previous_head": "03fdabc",
                "current_head": "04c243d",
                "previous_dirty_count": 4,
                "current_dirty_count": 6,
            },
            "ack_command": "python scripts/run_r_memory_packet.py --agent codex --ack",
        },
    }


def test_compact_diagnostic_reports_shared_runtime_counts(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture()
    )
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, observer_id="", trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    text = compact_diagnostic(agent_id="codex")

    assert "claims=1" in text
    assert "compactions=1" in text
    assert "subjects=1" in text
    assert "R=0.67/high" in text
    assert "coord=redis-live" in text
    assert "git=04c243d/dirty=6" in text
    assert "aegis=intact" in text


def test_full_diagnostic_is_cp950_safe_and_includes_shared_runtime(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture()
    )
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, observer_id="", trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    report = full_diagnostic(agent_id="codex")

    assert (
        "[Shared Runtime] claims=1 visitors=1 checkpoints=1 compactions=1 subject_snapshots=1"
        in report
    )
    assert "Risk Posture:" in report
    assert "[Project Memory Summary]" in report
    assert "[Subject Snapshot] count=1" in report
    assert "[Since Last Seen]" in report
    assert "coord-contract" in report
    assert "diagnose/load -> packet -> claim" in report
    assert "repo=codex/r-memory-compaction-lane-20260326@04c243d dirty=6" in report
    assert "repo_paths=tonesoul/runtime_adapter.py, tonesoul/diagnose.py" in report
    assert "[Operator Guidance]" in report
    assert "start_agent_session.py --agent <your-id>" in report
    assert "end_agent_session.py --agent <your-id>" in report
    assert "run_r_memory_packet.py --agent <your-id> --ack" in report
    assert "save_checkpoint.py" in report
    assert "save_compaction.py" in report
    assert "preflight_chain:" in report
    assert "shared_edit_path_overlap=python scripts/run_shared_edit_preflight.py" in report
    assert "publish_push_posture=python scripts/run_publish_push_preflight.py" in report
    assert "task_board_parking=python scripts/run_task_board_preflight.py" in report
    assert "route_r_memory_signal.py" in report
    assert "save_subject_snapshot.py" in report
    assert "apply_subject_refresh.py" in report
    assert "completion_rule=Before ending a session" in report
    assert "[Council Realism]" in report
    assert "confidence_posture=contested" in report
    assert "calibration_status=descriptive_only" in report
    assert "coverage_posture=partial" in report
    assert "adversarial_posture=visible_dissent" in report
    assert "has_minority_report=True" in report
    assert "evolution_suppression_flag=True" in report
    assert "Descriptive agreement record only; dissent is visible" in report
    assert "[Receiver Posture]" in report
    assert (
        "summary=receiver_parity council=descriptive_only dissent=visible suppression=flagged"
        in report
    )
    assert "rule=ack is safe visibility only; apply is bounded workflow use only" in report
    assert "Latest council dossier confidence is descriptive_only" in report
    assert "Latest council dossier carries minority dissent" in report
    assert "subject_anchor:" in report
    assert "working_style_anchor:" in report
    assert "working_style_playbook:" in report
    assert "Preference: prefer packet before broad repo scan" in report
    assert "Routine: leave compaction before release" in report
    assert "apply=Apply these items as bounded operating habits" in report
    assert "guard=Do not promote this playbook" in report
    assert "receiver_posture=advisory_apply_not_promote" in report
    assert "working_style_observability:" in report
    assert "status=partial drift=medium reinforced=1/2 signals=3" in report
    assert "unreinforced=verified_routines: leave compaction before release" in report
    assert "working_style_import_limits:" in report
    assert "apply_posture=explicit_reuse_only safe=2 blocked=2" in report
    assert "safe_apply=scan_order: use shared packet/claim surfaces" in report
    assert (
        "must_not_import=canonical_governance_truth: habits must not become runtime law" in report
    )
    assert "evidence_readout_posture:" in report
    assert "tested=2 runtime_present=1 descriptive_only=1 document_backed=1" in report
    assert "continuity_effectiveness=runtime_present" in report
    assert "launch_claim_posture:" in report
    assert "current=collaborator_beta next=public_launch public_ready=False" in report
    assert "tier=internal_alpha:safe_current_claims_only" in report
    assert "blocked=live_shared_memory:not_launch_default" in report
    assert "launch_health_trend_posture:" in report
    assert "metric=coordination_backend_alignment:trendable" in report
    assert "metric=public_launch_forecast:forecast_later" in report
    assert (
        "watch=coordination_backend_alignment:alignment_stays_consistent_across_validation_waves"
        in report
    )
    assert "blocker=continuity_effectiveness:runtime_present" in report
    assert "action=Use current launch language as collaborator-beta-only" in report
    assert "internal_state_observability:" in report
    assert "coordination=low drift=medium stop=medium deliberation=visible" in report
    assert "evidence=risk_posture:stable" in report
    assert "watch=coordination_strain:low" in report
    assert (
        "action=Keep shared side effects bounded and keep readiness/claim checks ahead of broader edits."
        in report
    )
    assert "routing_summary:" in report
    assert "subject_refresh:" in report
    assert (
        "status=refresh_candidate recommended=True newer_compactions=1 newer_checkpoints=1 hazards=1"
        in report
    )
    assert "active_threads=may_refresh_directly (compaction-backed)" in report
    assert "[Routing Telemetry] count=2" in report
    assert "[Coordination Mode]" in report
    assert "mode=redis-live live=True delta=True" in report
    assert "launch_default=file-backed alignment=runtime_override_not_launch_default" in report
    assert (
        "launch_note=Current runtime is redis-live, but the launch-default coordination st..."
        in report
    )
    assert "surfaces=claims:live checkpoints:live subjects:live visitors:live" in report
    assert "Prefer recent_compactions and project_memory_summary before older" in report
    assert "Subject-refresh heuristics found low-risk updates" in report
    assert "Redis live surfaces may change mid-session" in report
    assert "ack_command=python scripts/run_r_memory_packet.py --agent codex --ack" in report
    assert "released_claim_ids=old-claim" in report
    report.encode("cp950", errors="strict")
