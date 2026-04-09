from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_r_memory_packet_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_r_memory_packet.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_run_r_memory_packet_emits_json(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    claims_path = sidecar_dir / "task_claims.json"
    checkpoints_path = sidecar_dir / "checkpoints.json"
    compactions_path = sidecar_dir / "compacted.json"
    subject_snapshots_path = sidecar_dir / "subject_snapshots.json"
    observer_cursors_path = sidecar_dir / "observer_cursors.json"
    routing_events_path = sidecar_dir / "routing_events.json"
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-03-26T00:00:00+00:00",
                "soul_integral": 0.6,
                "tension_history": [],
                "active_vows": [],
                "aegis_vetoes": [],
                "baseline_drift": {
                    "caution_bias": 0.5,
                    "innovation_bias": 0.6,
                    "autonomy_level": 0.35,
                },
                "session_count": 4,
            }
        ),
        encoding="utf-8",
    )
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-26T00:01:00+00:00",
                "topics": ["runtime"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["emit packet"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "codex",
                    "summary": "sync gateway packet",
                    "paths": ["scripts/gateway.py"],
                    "source": "cli",
                    "created_at": "2026-03-26T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                }
            }
        ),
        encoding="utf-8",
    )
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-1",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Packet-first handoff summary.",
                    "carry_forward": ["read packet before long prose"],
                    "pending_paths": ["scripts/gateway.py"],
                    "evidence_refs": [
                        "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md"
                    ],
                    "council_dossier": {
                        "dossier_version": "v1",
                        "final_verdict": "approve",
                        "confidence_posture": "contested",
                        "coherence_score": 0.62,
                        "dissent_ratio": 0.35,
                        "minority_report": [
                            {
                                "perspective": "critic",
                                "decision": "concern",
                                "confidence": 0.75,
                                "reasoning": "migration path missing",
                                "evidence": ["docs/spec.md"],
                            }
                        ],
                        "vote_summary": [],
                        "deliberation_mode": "standard_council",
                        "change_of_position": [],
                        "evidence_refs": ["docs/spec.md"],
                        "grounding_summary": {
                            "has_ungrounded_claims": False,
                            "total_evidence_sources": 1,
                        },
                        "confidence_decomposition": {
                            "calibration_status": "descriptive_only",
                            "agreement_score": 0.5,
                            "coverage_posture": "partial",
                            "distinct_perspectives": 2,
                            "evidence_density": 0.5,
                            "evidence_posture": "moderate",
                            "grounding_posture": "not_required",
                            "adversarial_posture": "survived_dissent",
                        },
                        "evolution_suppression_flag": True,
                        "opacity_declaration": "partially_observable",
                    },
                    "next_action": "keep compaction non-canonical",
                    "source": "cli",
                    "updated_at": "2026-03-26T00:03:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    checkpoints_path.write_text(
        json.dumps(
            {
                "cp-1": {
                    "checkpoint_id": "cp-1",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Ack-aware packet handoff still needs validation.",
                    "pending_paths": ["tonesoul/diagnose.py"],
                    "next_action": "re-run packet with observer cursor",
                    "source": "cli",
                    "updated_at": "2026-03-26T00:02:30+00:00",
                    "expires_at": "4070908920.0",
                }
            }
        ),
        encoding="utf-8",
    )
    subject_snapshots_path.write_text(
        json.dumps(
            [
                {
                    "snapshot_id": "subj-1",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Stay packet-first and keep theory out of runtime assumptions.",
                    "stable_vows": ["do not commit personal memory data"],
                    "durable_boundaries": ["protected files stay human-managed"],
                    "decision_preferences": ["prefer packet before broad repo scan"],
                    "verified_routines": ["leave compaction before handoff"],
                    "active_threads": ["subject-snapshot rollout"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                    "refresh_signals": ["refresh when session cadence changes"],
                    "source": "cli",
                    "updated_at": "2026-03-28T00:04:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    routing_events_path.write_text(
        json.dumps(
            [
                {
                    "event_id": "route-1",
                    "agent": "codex",
                    "summary": "resume packet cleanup",
                    "surface": "checkpoint",
                    "action": "preview",
                    "written": False,
                    "confidence": "high",
                    "reason": "pending paths or next action indicate resumability state",
                    "forced": False,
                    "overlap": False,
                    "misroute_signal": False,
                    "secondary_signal_count": 1,
                    "secondary_signals": {"checkpoint": True},
                    "source": "cli",
                    "updated_at": "2026-03-28T00:05:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_r_memory_packet.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-1",
            "--ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)
    assert output["contract_version"] == "v1"
    assert output["posture"]["session_count"] == 4
    assert set(output["posture"]["risk_posture"]) >= {"score", "level", "recommended_action"}
    assert output["posture"]["freshness_hours"] >= 0.0
    assert "project_memory_summary" in output
    assert "repo_progress" in output["project_memory_summary"]
    assert "operator_guidance" in output
    assert output["operator_guidance"]["backend_mode"] == "file"
    assert "checkpoint" in output["operator_guidance"]["coordination_commands"]
    assert "signal_router" in output["operator_guidance"]["coordination_commands"]
    assert "subject_snapshot" in output["operator_guidance"]["coordination_commands"]
    assert "apply_subject_refresh" in output["operator_guidance"]["coordination_commands"]
    assert output["operator_guidance"]["session_start"][0].startswith(
        "python scripts/start_agent_session.py --agent"
    )
    assert output["operator_guidance"]["session_start"][2].startswith(
        "python scripts/run_r_memory_packet.py --agent"
    )
    assert output["operator_guidance"]["session_end"][0].startswith(
        "python scripts/end_agent_session.py --agent"
    )
    assert output["operator_guidance"]["session_end"][2].startswith(
        "python scripts/save_checkpoint.py"
    )
    assert output["operator_guidance"]["session_end"][3].startswith(
        "python scripts/save_compaction.py"
    )
    assert "checkpoint or compaction" in output["operator_guidance"]["completion_rule"]
    assert output["operator_guidance"]["preflight_chain"]["hooks"][0]["status"] == "available"
    assert (
        output["operator_guidance"]["preflight_chain"]["current_recommendation"]["present"] is False
    )
    assert output["recent_traces"][0]["agent"] == "codex"
    assert output["recent_traces"][0]["freshness_hours"] >= 0.0
    assert output["active_claims"][0]["task_id"] == "task-1"
    assert output["active_claims"][0]["freshness_hours"] >= 0.0
    assert output["recent_checkpoints"][0]["checkpoint_id"] == "cp-1"
    assert output["recent_checkpoints"][0]["freshness_hours"] >= 0.0
    assert output["recent_compactions"][0]["compaction_id"] == "cmp-1"
    assert output["recent_compactions"][0]["freshness_hours"] >= 0.0
    assert output["recent_compactions"][0]["council_dossier"]["confidence_posture"] == "contested"
    assert (
        output["recent_compactions"][0]["council_dossier"]["confidence_decomposition"][
            "calibration_status"
        ]
        == "descriptive_only"
    )
    assert output["recent_compactions"][0]["council_dossier"]["evolution_suppression_flag"] is True
    assert (
        "Descriptive agreement record only"
        in output["recent_compactions"][0]["council_dossier"]["realism_note"]
    )
    assert output["recent_subject_snapshots"][0]["snapshot_id"] == "subj-1"
    assert output["recent_subject_snapshots"][0]["freshness_hours"] >= 0.0
    assert output["recent_routing_events"][0]["surface"] == "checkpoint"
    assert output["recent_routing_events"][0]["freshness_hours"] >= 0.0
    assert output["project_memory_summary"]["subject_anchor"]["summary"].startswith(
        "Stay packet-first"
    )
    assert output["project_memory_summary"]["routing_summary"]["total_events"] == 1
    assert output["project_memory_summary"]["routing_summary"]["summary_text"].startswith(
        "router=writes=0 previews=1"
    )
    assert (
        output["project_memory_summary"]["evidence_readout_posture"]["classification_counts"][
            "tested"
        ]
        == 2
    )
    assert any(
        lane["lane"] == "axiom_and_theory_claims" and lane["classification"] == "document_backed"
        for lane in output["project_memory_summary"]["evidence_readout_posture"]["lanes"]
    )
    assert (
        output["project_memory_summary"]["launch_claim_posture"]["current_tier"]
        == "collaborator_beta"
    )
    assert (
        output["project_memory_summary"]["launch_claim_posture"]["next_target_tier"]
        == "public_launch"
    )
    assert (
        output["project_memory_summary"]["launch_health_trend_posture"]["current_state"][
            "launch_default_mode"
        ]
        == "file-backed"
    )
    assert any(
        item["metric"] == "coordination_backend_alignment" and item["classification"] == "trendable"
        for item in output["project_memory_summary"]["launch_health_trend_posture"][
            "metric_classes"
        ]
    )
    assert (
        output["project_memory_summary"]["internal_state_observability"]["current_state"][
            "coordination_strain"
        ]
        == "low"
    )
    assert (
        output["project_memory_summary"]["internal_state_observability"]["current_state"][
            "stop_reason_pressure"
        ]
        == "medium"
    )
    assert any(
        item["claim"] == "council_decision_quality"
        and item["current_classification"] == "descriptive_only"
        for item in output["project_memory_summary"]["launch_claim_posture"]["blocked_overclaims"]
    )
    assert output["project_memory_summary"]["subject_refresh"]["status"] == "manual_review"
    assert (
        "Do not promote active claims into durable identity"
        in output["project_memory_summary"]["subject_refresh"]["promotion_hazards"][0]
    )
    assert any(
        reminder.startswith(
            "Evidence posture: evidence=tested(session_control_and_handoff,council_mechanics)"
        )
        for reminder in output["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Launch claim posture: launch_claims=current:collaborator_beta")
        for reminder in output["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Launch health posture: launch_health current=collaborator_beta")
        for reminder in output["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Internal state posture: internal_state coordination=low")
        for reminder in output["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith(
            "Launch coordination default: Current runtime matches the launch-default coordination story"
        )
        for reminder in output["operator_guidance"]["current_reminders"]
    )
    assert output["coordination_mode"]["mode"] == "file-backed"
    assert output["coordination_mode"]["delta_feed_enabled"] is True
    assert output["coordination_mode"]["surface_modes"]["checkpoints"] == "file-backed"
    assert output["coordination_mode"]["surface_modes"]["visitors"] == "unavailable"
    assert output["coordination_mode"]["launch_default_mode"] == "file-backed"
    assert output["coordination_mode"]["launch_alignment"] == "aligned_with_launch_default"
    assert output["delta_feed"]["observer_id"] == "observer-1"
    assert output["delta_feed"]["first_observation"] is True
    cursor_data = json.loads(observer_cursors_path.read_text(encoding="utf-8"))
    assert "observer-1" in cursor_data
    assert cursor_data["observer-1"]["latest_checkpoint_id"] == "cp-1"


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root
