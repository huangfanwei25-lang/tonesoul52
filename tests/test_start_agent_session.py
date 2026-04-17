from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_start_agent_session_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "start_agent_session.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_state(
    state_path: Path,
    *,
    soul_integral: float = 0.72,
    tensions: list[dict] | None = None,
    vows: list[dict] | None = None,
    aegis_vetoes: list[dict] | None = None,
) -> None:
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-03-28T00:00:00+00:00",
                "soul_integral": soul_integral,
                "tension_history": (
                    tensions
                    if tensions is not None
                    else [{"topic": "shared-start", "severity": 0.31}]
                ),
                "active_vows": (
                    vows
                    if vows is not None
                    else [{"id": "v1", "content": "leave explicit handoff state"}]
                ),
                "aegis_vetoes": aegis_vetoes if aegis_vetoes is not None else [],
                "baseline_drift": {
                    "caution_bias": 0.52,
                    "innovation_bias": 0.58,
                    "autonomy_level": 0.34,
                },
                "session_count": 7,
            }
        ),
        encoding="utf-8",
    )


def _write_traces(traces_path: Path) -> None:
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-28T00:01:00+00:00",
                "topics": ["session-start"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["bundle session start"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


class _FakeShield:
    @classmethod
    def load(cls, store):
        return cls()

    def audit(self, store):
        return {"integrity": "intact"}


def test_start_agent_session_emits_machine_readable_bundle(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    claims_path = sidecar_dir / "task_claims.json"
    observer_cursors_path = sidecar_dir / "observer_cursors.json"

    _write_state(state_path)
    _write_traces(traces_path)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "codex",
                    "summary": "hold the runtime lane",
                    "paths": ["tonesoul/runtime_adapter.py"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-start",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["contract_version"] == "v1"
    assert output["bundle"] == "session_start"
    assert output["agent"] == "observer-start"
    assert output["acknowledged_observer_cursor"] is True
    assert output["claim_view"]["count"] == 1
    assert output["claim_view"]["claims"][0]["task_id"] == "task-1"
    assert output["compact_diagnostic"].startswith("[ToneSoul] file | SI=0.72")
    assert "aegis=intact" in output["compact_diagnostic"]
    assert output["compact_diagnostic"].endswith("| readiness=needs_clarification")
    assert output["readiness"]["status"] == "needs_clarification"
    assert output["readiness"]["ready"] is False
    assert output["readiness"]["claim_conflict_count"] == 1
    assert output["readiness"]["clarification_reasons"] == ["other_agent_claims_visible"]
    assert (
        output["import_posture"]["surfaces"]["posture"]["import_posture"] == "directly_importable"
    )
    assert output["import_posture"]["surfaces"]["claims"]["import_posture"] == "directly_importable"
    assert output["import_posture"]["surfaces"]["claims"]["receiver_obligation"] == "must_read"
    assert "TTL" in output["import_posture"]["surfaces"]["claims"]["note"]
    assert (
        output["import_posture"]["surfaces"]["delta_feed"]["import_posture"]
        == "ephemeral_until_acked"
    )
    assert output["import_posture"]["surfaces"]["evidence_readout"]["import_posture"] == "advisory"
    assert (
        output["import_posture"]["surfaces"]["evidence_readout"]["receiver_obligation"]
        == "should_consider"
    )
    assert (
        output["import_posture"]["surfaces"]["evidence_readout"]["evidence_readout_posture"][
            "classification_counts"
        ]["tested"]
        == 2
    )
    assert output["import_posture"]["surfaces"]["launch_claims"]["import_posture"] == "advisory"
    assert (
        output["import_posture"]["surfaces"]["launch_claims"]["receiver_obligation"]
        == "should_consider"
    )
    assert (
        output["import_posture"]["surfaces"]["launch_claims"]["launch_claim_posture"][
            "current_tier"
        ]
        == "collaborator_beta"
    )
    assert (
        output["import_posture"]["surfaces"]["launch_health_trend"]["import_posture"] == "advisory"
    )
    assert (
        output["import_posture"]["surfaces"]["launch_health_trend"]["receiver_obligation"]
        == "should_consider"
    )
    assert any(
        item["metric"] == "public_launch_forecast" and item["classification"] == "forecast_later"
        for item in output["import_posture"]["surfaces"]["launch_health_trend"][
            "launch_health_trend_posture"
        ]["metric_classes"]
    )
    assert (
        output["import_posture"]["surfaces"]["internal_state_observability"]["import_posture"]
        == "advisory"
    )
    assert output["import_posture"]["surfaces"]["internal_state_observability"][
        "internal_state_observability"
    ]["current_state"]["deliberation_conflict"] in {"clear", "visible"}
    assert output["import_posture"]["surfaces"]["subject_snapshot"]["present"] is False
    assert output["import_posture"]["readiness_alignment"] == "needs_clarification"
    assert output["import_posture"]["summary_text"].startswith("posture=directly_importable")
    repo_state = output["repo_state_awareness"]
    assert repo_state["present"] is True
    assert repo_state["classification"] == "baseline_unset"
    assert repo_state["misread_risk"] is True
    assert "does not imply" in repo_state["receiver_note"]
    assert "descriptive only" in repo_state["non_authority_rule"]
    assert output["receiver_parity"]["continuity"]["classification"] == "runtime_present"
    assert output["receiver_parity"]["working_style"]["status"] == "none"
    assert output["receiver_parity"]["rule"].startswith("ack is safe visibility only")
    assert any(
        "continuity effectiveness is only runtime_present" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert any(
        "No observer baseline yet" in alert for alert in output["import_posture"]["receiver_alerts"]
    )
    assert output["task_track_hint"]["present"] is True
    assert output["task_track_hint"]["suggested_track"] == "feature_track"
    assert output["task_track_hint"]["exploration_depth_hint"] == "x2"
    assert output["task_track_hint"]["claim_recommendation"] == "required"
    assert output["deliberation_mode_hint"]["present"] is True
    assert output["deliberation_mode_hint"]["suggested_mode"] == "standard_council"
    assert output["deliberation_mode_hint"]["claim_state"] == "active_collision"
    assert output["deliberation_mode_hint"]["readiness_state"] == "needs_clarification"
    assert output["deliberation_mode_hint"]["human_required"] is False
    assert (
        "claim_collision_visible" in output["deliberation_mode_hint"]["active_escalation_signals"]
    )
    assert (
        "readiness_needs_clarification"
        in output["deliberation_mode_hint"]["active_escalation_signals"]
    )
    assert "claim_collision_visible" in output["deliberation_mode_hint"]["escalation_triggers"]
    assert (
        "readiness_needs_clarification" in output["deliberation_mode_hint"]["escalation_triggers"]
    )
    mutation_preflight = output["mutation_preflight"]
    assert mutation_preflight["present"] is True
    assert mutation_preflight["current_context"]["task_track"] == "feature_track"
    assert mutation_preflight["current_context"]["claim_conflict_count"] == 1
    assert (
        mutation_preflight["next_followup"]["target"] == "shared_code_edit.path_overlap_preflight"
    )
    assert mutation_preflight["next_followup"]["classification"] == "existing_runtime_hook"
    assert "run_shared_edit_preflight.py" in mutation_preflight["next_followup"]["command"]
    by_name = {item["name"]: item for item in mutation_preflight["decision_points"]}
    assert by_name["shared_code_edit"]["posture"] == "coordinate_before_shared_edits"
    assert by_name["shared_code_edit"]["control_type"] == "existing_runtime_hook"
    assert by_name["claim_write"]["posture"] == "expected_on_shared_paths"
    assert by_name["canonical_commit"]["posture"] == "aegis_locked_commit"
    assert by_name["task_board_update"]["control_type"] == "human_gated"
    assert by_name["launch_claim_language"]["posture"] == "bounded_collaborator_beta_only"
    assert by_name["publish_push"]["posture"] == "review_before_push"
    publish_push_preflight = output["publish_push_preflight"]
    assert publish_push_preflight["present"] is True
    assert publish_push_preflight["classification"] == "review_before_push"
    assert publish_push_preflight["repo_state_classification"] == "baseline_unset"
    consumer_contract = output["consumer_contract"]
    assert consumer_contract["present"] is True
    assert consumer_contract["compatible_consumers"] == [
        "codex_cli",
        "claude_style_shell",
        "dashboard_operator_shell",
    ]
    assert consumer_contract["required_read_order"][0]["surface"] == "readiness"
    assert consumer_contract["required_read_order"][1]["surface"] == "canonical_center"
    assert consumer_contract["current_context"]["closeout_status"] in {
        "complete",
        "partial",
        "blocked",
        "underdetermined",
    }
    assert any(
        guard["name"] == "compaction_not_completion"
        for guard in consumer_contract["misread_guards"]
    )
    priority_guard = consumer_contract["priority_misread_guard"]
    assert priority_guard["name"] == "observer_stable_not_verified"
    assert priority_guard["trigger_surface"] == "observer_window.stable"
    assert "check readiness and canonical_center" in priority_guard["operator_action"]
    surface_versioning = output["surface_versioning"]
    assert surface_versioning["present"] is True
    assert surface_versioning["runtime_surfaces"][0]["surface"] == "session_start"
    assert surface_versioning["consumer_shells"][1]["consumer"] == "dashboard_operator_shell"
    hook_chain = output["hook_chain"]
    assert hook_chain["present"] is True
    assert hook_chain["stages"][0]["name"] == "shared_edit_path_overlap"
    assert hook_chain["stages"][1]["name"] == "publish_push_posture"
    assert hook_chain["stages"][2]["name"] == "task_board_parking"
    assert (
        hook_chain["stages"][0]["command"]
        == "python scripts/run_shared_edit_preflight.py --agent observer-start --path <repo-path>"
    )
    assert hook_chain["hooks"][0]["name"] == "shared_edit_path_overlap"
    assert hook_chain["current_recommendation"]["present"] is True
    assert (
        hook_chain["current_recommendation"]["target"]
        == output["mutation_preflight"]["next_followup"]["target"]
    )
    assert any(item["status"] == "recommended_now" for item in hook_chain["hooks"])
    task_board_preflight = output["task_board_preflight"]
    assert task_board_preflight["present"] is True
    assert task_board_preflight["classification"] in {
        "docs_plans_first",
        "human_review",
        "parking_clear",
    }
    assert "suggested_destination" in task_board_preflight or "summary_text" in task_board_preflight
    subsystem_parity = output["subsystem_parity"]
    assert subsystem_parity["present"] is True
    assert subsystem_parity["counts"]["baseline"] == 3
    assert subsystem_parity["counts"]["beta_usable"] == 5
    assert subsystem_parity["counts"]["partial"] == 2
    assert subsystem_parity["counts"]["deferred"] == 1
    assert (
        subsystem_parity["next_focus"]["resolved_to"] == "shared_code_edit.path_overlap_preflight"
    )
    assert subsystem_parity["next_focus"]["source_family"] == "mutation_preflight_hooks"
    assert subsystem_parity["next_focus"]["focus_pressures"] == [
        "readiness=needs_clarification",
        "task_track=feature_track",
        "claim_recommendation=required",
    ]
    parity_by_name = {item["name"]: item for item in subsystem_parity["families"]}
    assert parity_by_name["session_start_bundle"]["status"] == "baseline"
    assert parity_by_name["packet_hot_state"]["status"] == "beta_usable"
    assert parity_by_name["mutation_preflight_hooks"]["status"] == "beta_usable"
    assert output["working_style_playbook"]["present"] is False
    assert output["working_style_playbook"]["checklist"] == []
    assert (
        "No shared working-style anchor is visible"
        in output["working_style_playbook"]["application_rule"]
    )
    assert output["working_style_validation"]["status"] == "insufficient"
    assert output["working_style_validation"]["checks"]["anchor_visible"] is False
    assert (
        "style continuity cannot be validated"
        in output["working_style_validation"]["receiver_note"]
    )
    assert output["underlying_commands"][0] == "python -m tonesoul.diagnose --agent observer-start"
    assert output["underlying_commands"][1] == (
        "python scripts/run_r_memory_packet.py --agent observer-start --ack"
    )
    assert output["underlying_commands"][3] == (
        "python scripts/run_shared_edit_preflight.py --agent observer-start --path <repo-path>"
    )
    assert output["underlying_commands"][4] == (
        "python scripts/run_publish_push_preflight.py --agent observer-start"
    )
    assert output["underlying_commands"][5] == (
        "python scripts/run_task_board_preflight.py --agent observer-start --proposal-kind external_idea --target-path task.md"
    )
    assert output["packet"]["delta_feed"]["observer_id"] == "observer-start"
    assert output["packet"]["delta_feed"]["first_observation"] is True
    assert output["packet"]["active_claims"][0]["task_id"] == "task-1"

    cursor_data = json.loads(observer_cursors_path.read_text(encoding="utf-8"))
    assert cursor_data["observer-start"]["active_claim_ids"] == ["task-1"]


def test_start_agent_session_can_skip_ack(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    observer_cursors_path = tmp_path / ".aegis" / "observer_cursors.json"

    _write_state(state_path)
    _write_traces(traces_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-preview",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["acknowledged_observer_cursor"] is False
    assert output["readiness"]["status"] == "pass"
    assert output["readiness"]["ready"] is True
    assert output["task_track_hint"]["present"] is False
    assert output["task_track_hint"]["suggested_track"] == "unclassified"
    assert output["deliberation_mode_hint"]["present"] is False
    assert output["deliberation_mode_hint"]["suggested_mode"] == "unclassified"
    assert output["repo_state_awareness"]["classification"] == "baseline_unset"
    assert output["import_posture"]["surfaces"]["delta_feed"]["present"] is True
    assert output["underlying_commands"][1] == (
        "python scripts/run_r_memory_packet.py --agent observer-preview"
    )
    cursor_data = json.loads(observer_cursors_path.read_text(encoding="utf-8"))
    assert "observer-preview" not in cursor_data


def test_start_agent_session_tier0_returns_fast_path_bundle(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    _write_state(state_path)
    _write_traces(traces_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "tier0-fast",
            "--tier",
            "0",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["tier"] == 0
    assert output["bundle_posture"] == "fast_path"
    assert output["readiness"]["status"] == "pass"
    assert output["task_track_hint"]["suggested_track"] == "unclassified"
    assert output["deliberation_mode_hint"]["suggested_mode"] == "unclassified"
    assert output["canonical_center"]["present"] is True
    assert output["mutation_preflight"]["present"] is True
    assert output["consumer_contract"]["present"] is True
    assert output["next_pull"]["recommended_commands"][0] == (
        "python scripts/start_agent_session.py --agent tier0-fast --tier 1"
    )
    # Tier 0 must NOT include heavy surfaces
    assert "packet" not in output
    assert "import_posture" not in output
    assert "receiver_parity" not in output
    assert "publish_push_preflight" not in output
    assert "task_board_preflight" not in output
    assert "subsystem_parity" not in output
    assert "working_style_playbook" not in output
    assert "working_style_validation" not in output
    assert "claim_view" not in output
    # hook_chain and surface_versioning deferred to tier 1
    assert "hook_chain" not in output
    assert "surface_versioning" not in output
    assert "underlying_commands" not in output


def test_run_session_start_bundle_slim_returns_compact_shell(monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    _write_state(state_path)
    _write_traces(traces_path)
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    output = module.run_session_start_bundle(
        agent_id="slim-shell",
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        slim=True,
    )

    payload_bytes = len(json.dumps(output, ensure_ascii=False).encode("utf-8"))

    assert output["bundle"] == "session_start"
    assert output["tier"] == "slim"
    assert output["bundle_posture"] == "mcp_entry_shell"
    assert output["_compact"] is True
    assert output["readiness"] in {"pass", "needs_clarification", "blocked"}
    assert output["claim_boundary"]["current_tier"] == "collaborator_beta"
    assert "council_deliberate" in output["available_tools"]
    assert "governance_load" in output["available_tools"]
    assert payload_bytes < 2048


def test_start_agent_session_cli_slim_executes_directly(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    _write_state(state_path)
    _write_traces(traces_path)
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "slim-cli",
            "--slim",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["tier"] == "slim"
    assert output["bundle_posture"] == "mcp_entry_shell"
    assert output["claim_boundary"]["rule"] == "evidence_bounded"
    assert len(json.dumps(output, ensure_ascii=False).encode("utf-8")) < 2048


def test_start_agent_session_tier1_returns_orientation_shell(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    _write_state(state_path)
    _write_traces(traces_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "tier1-shell",
            "--tier",
            "1",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["tier"] == 1
    assert output["bundle_posture"] == "orientation_shell"
    assert output["canonical_center"]["parent_surfaces"] == ["task.md", "DESIGN.md"]
    assert output["subsystem_parity"]["present"] is True
    assert output["observer_shell"]["present"] is True
    assert "stable" in output["observer_shell"]["counts"]
    assert "contested" in output["observer_shell"]["counts"]
    assert "stale" in output["observer_shell"]["counts"]
    assert output["observer_shell"]["closeout_attention"]["summary_text"].startswith(
        "latest compaction closeout"
    )
    assert output["observer_shell"]["closeout_attention"]["status"] in {
        "complete",
        "partial",
        "blocked",
        "underdetermined",
    }
    assert "source_family" in output["observer_shell"]["closeout_attention"]
    assert "operator_action" in output["observer_shell"]["closeout_attention"]
    assert "attention_pressures" in output["observer_shell"]["closeout_attention"]
    assert output["consumer_contract"]["present"] is True
    assert output["consumer_contract"]["required_read_order"][0]["surface"] == "readiness"
    assert output["consumer_contract"]["required_read_order"][2]["surface"] == "closeout_attention"
    assert output["observer_shell"]["hot_memory_ladder"]["layers"][0]["layer"] == "canonical_center"
    assert output["observer_shell"]["hot_memory_ladder"]["current_pull_boundary"][
        "pull_posture"
    ] in {
        "tier1_enough",
        "recover_parent_truth_first",
        "resolve_live_coordination_first",
        "review_handoff_before_deeper_pull",
        "refresh_anchor_before_deeper_pull",
    }
    assert output["closeout_attention"]["status"] in {
        "complete",
        "partial",
        "blocked",
        "underdetermined",
    }
    assert output["mutation_preflight"]["present"] is True
    assert output["next_pull"]["recommended_commands"][0] == (
        "python scripts/start_agent_session.py --agent tier1-shell"
    )
    assert "packet" not in output
    assert "import_posture" not in output
    assert "receiver_parity" not in output
    assert "publish_push_preflight" not in output
    assert "task_board_preflight" not in output
    assert "working_style_playbook" not in output
    assert "working_style_validation" not in output
    assert "claim_view" not in output


def test_start_agent_session_blocks_on_critical_risk(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    claims_path = tmp_path / ".aegis" / "task_claims.json"

    _write_state(
        state_path,
        soul_integral=0.33,
        tensions=[
            {"topic": "risk-a", "severity": 0.95},
            {"topic": "risk-b", "severity": 0.92},
            {"topic": "risk-c", "severity": 0.89},
        ],
        aegis_vetoes=[
            {"reason": "guard-1"},
            {"reason": "guard-2"},
        ],
    )
    _write_traces(traces_path)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "agent-a",
                    "summary": "shared path a",
                    "paths": ["tonesoul/runtime_adapter.py"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                },
                "task-2": {
                    "task_id": "task-2",
                    "agent": "agent-b",
                    "summary": "shared path b",
                    "paths": ["scripts/start_agent_session.py"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:10+00:00",
                    "expires_at": "4070908920.0",
                },
                "task-3": {
                    "task_id": "task-3",
                    "agent": "agent-c",
                    "summary": "shared path c",
                    "paths": ["docs/AI_QUICKSTART.md"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:20+00:00",
                    "expires_at": "4070908920.0",
                },
                "task-4": {
                    "task_id": "task-4",
                    "agent": "agent-d",
                    "summary": "shared path d",
                    "paths": ["task.md"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:30+00:00",
                    "expires_at": "4070908920.0",
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-critical",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["readiness"]["status"] == "blocked"
    assert output["readiness"]["ready"] is False
    assert "risk_level_is_critical" in output["readiness"]["blocking_reasons"]
    assert output["readiness"]["risk_level"] == "critical"
    assert output["import_posture"]["surfaces"]["readiness"]["freshness_hours"] == 0.0


def test_start_agent_session_blocks_on_stop_handoff(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-stop",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Hold here until the human resolves the fork.",
                    "carry_forward": ["do not continue alone"],
                    "pending_paths": ["task.md"],
                    "evidence_refs": ["docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md"],
                    "next_action": "STOP: requires human decision on plan fork",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:03:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-stop",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["readiness"]["status"] == "blocked"
    assert "stop_handoff_present" in output["readiness"]["blocking_reasons"]
    assert output["readiness"]["stop_signal_count"] >= 1
    assert output["task_track_hint"]["suggested_track"] == "system_track"
    assert output["deliberation_mode_hint"]["present"] is True
    assert output["deliberation_mode_hint"]["suggested_mode"] == "do_not_deliberate"
    assert output["deliberation_mode_hint"]["resume_mode_after_unblock"] == "elevated_council"
    assert output["deliberation_mode_hint"]["human_required"] is True
    assert (
        "blocked_state_requires_unblock_first"
        in output["deliberation_mode_hint"]["active_escalation_signals"]
    )


def test_start_agent_session_surfaces_system_track_hint_from_canonical_scope(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-system",
                    "agent": "codex",
                    "session_id": "sess-system",
                    "summary": "Cross-lane authority cleanup touching canonical surfaces.",
                    "carry_forward": ["keep counts reality-checked before simplification"],
                    "pending_paths": [
                        "task.md",
                        "docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md",
                        "spec/governance/r_memory_packet_v1.schema.json",
                        "scripts/start_agent_session.py",
                        "tests/test_start_agent_session.py",
                    ],
                    "evidence_refs": ["docs/architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md"],
                    "next_action": "reconcile control-plane entrypoint and schema scope",
                    "source": "cli",
                    "updated_at": "2026-03-29T00:09:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-system-track",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    track_hint = output["task_track_hint"]
    assert track_hint["present"] is True
    assert track_hint["suggested_track"] == "system_track"
    assert track_hint["exploration_depth_hint"] == "x3"
    assert track_hint["claim_recommendation"] == "required"
    assert track_hint["review_recommendation"] == "required"
    assert "canonical_or_architecture_surface_visible" in track_hint["reasons"]
    assert "pending_path_count_ge_5" in track_hint["reasons"]
    assert "cross_family_scope_visible" in track_hint["reasons"]
    assert "task.md" in track_hint["scope_basis"]["pending_paths"]
    mode_hint = output["deliberation_mode_hint"]
    assert mode_hint["present"] is True
    assert mode_hint["suggested_mode"] == "elevated_council"
    assert mode_hint["human_required"] is False
    assert mode_hint["claim_state"] == "none"


def test_start_agent_session_surfaces_lightweight_review_for_quick_change(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-quick",
                    "agent": "codex",
                    "session_id": "sess-quick",
                    "summary": "Tight docs-only wording fix.",
                    "carry_forward": ["tighten one line in AI reference"],
                    "pending_paths": ["docs/AI_REFERENCE.md"],
                    "evidence_refs": ["docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md"],
                    "next_action": "tighten one sentence without changing structure",
                    "source": "cli",
                    "updated_at": "2026-03-29T00:11:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-quick-track",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    track_hint = output["task_track_hint"]
    assert track_hint["present"] is True
    assert track_hint["suggested_track"] == "quick_change"
    assert track_hint["exploration_depth_hint"] == "x0"
    mode_hint = output["deliberation_mode_hint"]
    assert mode_hint["present"] is True
    assert mode_hint["suggested_mode"] == "lightweight_review"
    assert mode_hint["human_required"] is False
    assert mode_hint["active_escalation_signals"] == []
    assert "quick_change_can_stay_lightweight" in mode_hint["review_cues"]
    assert "no_claim_collision_visible" in mode_hint["review_cues"]
    assert "No active escalation signals are currently visible" in mode_hint["receiver_note"]
    assert "active_escalation=none" in mode_hint["summary_text"]


def test_start_agent_session_distinguishes_active_and_conditional_escalation_for_feature_track(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-feature-light",
                    "agent": "codex",
                    "session_id": "sess-feature-light",
                    "summary": "Implement one bounded feature without coordination pressure.",
                    "carry_forward": ["keep the feature lane scoped to a single runtime path"],
                    "pending_paths": [
                        "tonesoul/runtime_adapter.py",
                        "tests/test_runtime_adapter.py",
                    ],
                    "evidence_refs": [
                        "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"
                    ],
                    "next_action": "tighten one runtime readout and its regression test",
                    "source": "cli",
                    "updated_at": "2026-03-29T00:11:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-feature-light",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    track_hint = output["task_track_hint"]
    assert track_hint["present"] is True
    assert track_hint["suggested_track"] == "feature_track"
    mode_hint = output["deliberation_mode_hint"]
    assert mode_hint["present"] is True
    assert mode_hint["suggested_mode"] == "lightweight_review"
    assert mode_hint["active_escalation_signals"] == []
    assert "claim_collision_visible" in mode_hint["conditional_escalation_triggers"]
    assert "readiness_needs_clarification" in mode_hint["conditional_escalation_triggers"]
    assert "risk_bucket_elevated_or_critical" in mode_hint["conditional_escalation_triggers"]
    assert "bounded_feature_track_can_stay_lightweight" in mode_hint["review_cues"]
    assert "No active escalation signals are currently visible" in mode_hint["receiver_note"]
    assert "active_escalation=none" in mode_hint["summary_text"]


def test_start_agent_session_marks_recycled_carry_forward_as_must_not_promote(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    subject_snapshots_path = sidecar_dir / "subject_snapshots.json"
    compactions_path = sidecar_dir / "compacted.json"

    _write_state(state_path)
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-2",
                "agent": "codex",
                "timestamp": "2026-03-28T00:05:00+00:00",
                "topics": ["runtime_adapter", "redis"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["observe recycled carry-forward at session start"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    subject_snapshots_path.write_text(
        json.dumps(
            [
                {
                    "snapshot_id": "subj-1",
                    "agent": "codex",
                    "session_id": "sess-0",
                    "summary": "Operate as a packet-first runtime steward with explicit boundaries.",
                    "stable_vows": ["never smuggle theory into runtime truth"],
                    "durable_boundaries": ["do not edit protected human-managed files"],
                    "decision_preferences": ["prefer packet before broad repo scan"],
                    "verified_routines": [
                        "end sessions with checkpoint or compaction before release"
                    ],
                    "active_threads": ["subject snapshot hardening"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                    "refresh_signals": ["refresh when durable boundaries change"],
                    "source": "cli",
                    "updated_at": "2026-03-28T00:00:30+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-new",
                    "agent": "codex",
                    "session_id": "sess-2",
                    "summary": "Repeated bounded handoff with no new backing evidence.",
                    "carry_forward": ["keep packet-first session cadence stable"],
                    "pending_paths": ["tonesoul/runtime_adapter.py"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                    "next_action": "refresh subject snapshot active threads",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:05:00+00:00",
                },
                {
                    "compaction_id": "cmp-old",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Previous bounded handoff for the runtime lane.",
                    "carry_forward": ["keep packet-first session cadence stable"],
                    "pending_paths": ["tonesoul/runtime_adapter.py"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                    "next_action": "refresh subject snapshot active threads",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:04:00+00:00",
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-carry-forward",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    compaction_surface = output["import_posture"]["surfaces"]["compactions"]
    working_style_surface = output["import_posture"]["surfaces"]["working_style"]
    assert compaction_surface["import_posture"] == "advisory"
    assert compaction_surface["receiver_obligation"] == "must_not_promote"
    assert compaction_surface["closeout_status"] == "partial"
    assert compaction_surface["stop_reason"] == ""
    assert compaction_surface["unresolved_count"] == 0
    assert compaction_surface["human_input_required"] is False
    assert any(
        "recycled carry_forward" in hazard for hazard in compaction_surface["promotion_hazards"]
    )
    assert working_style_surface["present"] is True
    assert working_style_surface["import_posture"] == "advisory"
    assert working_style_surface["receiver_obligation"] == "should_consider"
    assert working_style_surface["decay_posture"] == "slow"
    assert working_style_surface["working_style_anchor"]["decision_preferences"] == [
        "prefer packet before broad repo scan"
    ]
    assert working_style_surface["working_style_anchor"]["verified_routines"] == [
        "end sessions with checkpoint or compaction before release"
    ]
    assert (
        working_style_surface["working_style_anchor"]["receiver_posture"]
        == "advisory_apply_not_promote"
    )
    track_hint = output["task_track_hint"]
    assert track_hint["present"] is True
    assert track_hint["suggested_track"] == "feature_track"
    assert track_hint["exploration_depth_hint"] == "x2"
    assert track_hint["claim_recommendation"] == "required"
    assert track_hint["review_recommendation"] == "conditional"
    working_style_observability = working_style_surface["working_style_observability"]
    assert working_style_observability["status"] == "partial"
    assert working_style_observability["drift_risk"] == "medium"
    assert working_style_observability["reinforced_item_count"] == 1
    assert (
        "decision_preferences: prefer packet before broad repo scan"
        in working_style_observability["reinforced_items"]
    )
    assert (
        "verified_routines: end sessions with checkpoint or compaction before release"
        in working_style_observability["unreinforced_items"]
    )
    working_style_import_limits = working_style_surface["working_style_import_limits"]
    assert working_style_import_limits["apply_posture"] == "explicit_reuse_only"
    assert any(item.startswith("scan_order:") for item in working_style_import_limits["safe_apply"])
    assert any(
        item.startswith("task_scope_or_success_criteria:")
        for item in working_style_import_limits["must_not_import"]
    )
    playbook = output["working_style_playbook"]
    assert playbook["present"] is True
    assert playbook["summary_text"].startswith("prefs=prefer packet before broad repo scan")
    assert "Preference: prefer packet before broad repo scan" in playbook["checklist"]
    assert (
        "Routine: end sessions with checkpoint or compaction before release"
        in playbook["checklist"]
    )
    assert any(
        item.startswith("Prompt default: keep P0/P1/P2 explicit") for item in playbook["checklist"]
    )
    assert any(item.startswith("Render caveat: Treat shell `??`") for item in playbook["checklist"])
    assert "bounded operating habits" in playbook["application_rule"]
    assert "Do not promote this playbook" in playbook["non_promotion_rule"]
    validation = output["working_style_validation"]
    assert validation["status"] == "caution"
    assert validation["score"] == 1.0
    assert validation["checks"]["anchor_visible"] is True
    assert validation["checks"]["import_limits_visible"] is True
    assert "explicit reuse beats assumption" in validation["receiver_note"]
    assert any(
        "Latest carry-forward repeats an older handoff without new evidence" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert any(
        "Latest compaction closeout is partial" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    mode_hint = output["deliberation_mode_hint"]
    assert mode_hint["suggested_mode"] == "lightweight_review"
    assert mode_hint["human_required"] is False
    assert mode_hint["active_escalation_signals"] == []
    assert "feature_track_scope" in mode_hint["review_cues"]
    assert "risk_bucket_elevated_or_critical" in mode_hint["escalation_triggers"]
    assert "claim_collision_visible" in mode_hint["escalation_triggers"]
    assert "Bounded feature work now defaults to lightweight review" in mode_hint["receiver_note"]
    assert "No active escalation signals are currently visible" in mode_hint["receiver_note"]
    assert any(
        "Working-style continuity is advisory only" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert any(
        "Shared working-style continuity is only partially reinforced" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert not any(
        "Working-style import is bounded to scan order, evidence handling, prompt shape, session cadence, and render interpretation"
        in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert any(
        "Working-style import is bounded to scan order, evidence handling, prompt shape, session cadence, and render interpretation"
        in alert
        for alert in output["receiver_parity"]["alerts"]
    )


def test_start_agent_session_surfaces_blocked_compaction_closeout(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-blocked",
                    "agent": "codex",
                    "session_id": "sess-blocked",
                    "summary": "Stop here until a human resolves the authority fork.",
                    "carry_forward": ["hold current authority boundaries steady"],
                    "pending_paths": ["task.md"],
                    "evidence_refs": ["docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md"],
                    "next_action": "STOP: requires human decision on authority fork",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:06:00+00:00",
                    "closeout": {
                        "status": "blocked",
                        "stop_reason": "external_blocked",
                        "unresolved_items": ["human must choose which authority surface wins"],
                        "human_input_required": True,
                        "note": "Blocked on human confirmation before the next mutation.",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-blocked-closeout",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    compaction_surface = output["import_posture"]["surfaces"]["compactions"]
    assert compaction_surface["closeout_status"] == "blocked"
    assert compaction_surface["stop_reason"] == "external_blocked"
    assert compaction_surface["unresolved_count"] == 1
    assert compaction_surface["human_input_required"] is True
    assert compaction_surface["receiver_obligation"] == "must_review"
    assert output["closeout_attention"]["source_family"] == "bounded_handoff_closeout"
    assert "status=blocked" in output["closeout_attention"]["attention_pressures"]
    assert "human_input_required=true" in output["closeout_attention"]["attention_pressures"]
    assert "Do not continue shared mutation yet" in output["closeout_attention"]["operator_action"]
    assert any(
        "Latest compaction closeout is blocked" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )
    assert any(
        "stop_reason=external_blocked" in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )


def test_start_agent_session_surfaces_council_dossier_interpretation_guard(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    compactions_path = tmp_path / ".aegis" / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    compactions_path.parent.mkdir(parents=True, exist_ok=True)
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-dossier",
                    "agent": "codex",
                    "session_id": "sess-3",
                    "summary": "Carry bounded council dissent forward for the next agent.",
                    "carry_forward": ["review contested decision before further edits"],
                    "pending_paths": ["tonesoul/council/dossier.py"],
                    "evidence_refs": ["tests/test_council_dossier.py"],
                    "next_action": "review dossier before mutating council logic",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:06:00+00:00",
                    "council_dossier": {
                        "final_verdict": "approve",
                        "confidence_posture": "contested",
                        "coherence_score": 0.74,
                        "dissent_ratio": 0.2,
                        "minority_report": [
                            {
                                "perspective": "critic",
                                "decision": "concern",
                                "confidence": 0.81,
                                "reasoning": "The draft may be overclaiming calibration.",
                                "evidence": [
                                    "docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md"
                                ],
                            }
                        ],
                        "vote_summary": [],
                        "evidence_refs": [
                            "docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md"
                        ],
                        "grounding_summary": {
                            "has_ungrounded_claims": False,
                            "total_evidence_sources": 2,
                        },
                        "confidence_decomposition": {
                            "calibration_status": "descriptive_only",
                            "agreement_score": 0.8,
                            "coverage_posture": "partial",
                            "distinct_perspectives": 4,
                            "evidence_density": 0.5,
                            "evidence_posture": "moderate",
                            "grounding_posture": "grounded",
                            "adversarial_posture": "survived_dissent",
                        },
                        "evolution_suppression_flag": True,
                        "opacity_declaration": "partially_observable",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-dossier",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    dossier_surface = output["import_posture"]["surfaces"]["council_dossier"]
    assert dossier_surface["import_posture"] == "advisory"
    assert dossier_surface["receiver_obligation"] == "should_consider"
    assert "descriptive agreement signals" in dossier_surface["note"]
    assert dossier_surface["dossier_interpretation"]["confidence_posture"] == "contested"
    assert dossier_surface["dossier_interpretation"]["calibration_status"] == "descriptive_only"
    assert dossier_surface["dossier_interpretation"]["adversarial_posture"] == "survived_dissent"
    assert dossier_surface["dossier_interpretation"]["has_minority_report"] is True
    assert dossier_surface["dossier_interpretation"]["evolution_suppression_flag"] is True
    assert (
        "Descriptive agreement record only"
        in dossier_surface["dossier_interpretation"]["realism_note"]
    )
    receiver_parity = output["receiver_parity"]
    assert receiver_parity["council"]["calibration_status"] == "descriptive_only"
    assert receiver_parity["council"]["has_minority_report"] is True
    assert receiver_parity["council"]["evolution_suppression_flag"] is True
    assert receiver_parity["summary_text"].startswith(
        "receiver_parity council=descriptive_only dissent=visible suppression=flagged"
    )
    assert receiver_parity["rule"].startswith("ack is safe visibility only")
    assert any("descriptive_only" in alert for alert in output["import_posture"]["receiver_alerts"])
    assert any("minority dissent" in alert for alert in output["import_posture"]["receiver_alerts"])
    assert any(
        "evolution suppression" in alert for alert in output["import_posture"]["receiver_alerts"]
    )


def test_start_agent_session_scores_reinforced_working_style_as_sufficient(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    subject_snapshots_path = sidecar_dir / "subject_snapshots.json"
    compactions_path = sidecar_dir / "compacted.json"
    routing_events_path = sidecar_dir / "routing_events.json"

    _write_state(state_path)
    _write_traces(traces_path)
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    subject_snapshots_path.write_text(
        json.dumps(
            [
                {
                    "snapshot_id": "subj-r1",
                    "agent": "codex",
                    "session_id": "sess-r1",
                    "summary": "Operate as a packet-first runtime steward.",
                    "stable_vows": ["never smuggle theory into runtime truth"],
                    "durable_boundaries": ["do not edit protected human-managed files"],
                    "decision_preferences": [
                        "prefer packet before broad repo scan",
                        "prefer bounded shared surfaces over long interpretive prose",
                    ],
                    "verified_routines": [
                        "start collaborative sessions with diagnose then packet",
                        "end sessions with checkpoint or compaction before release",
                    ],
                    "active_threads": ["working-style continuity"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                    "refresh_signals": ["refresh when durable boundaries change"],
                    "source": "cli",
                    "updated_at": "2026-03-28T00:00:30+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-r1",
                    "agent": "codex",
                    "session_id": "sess-r2",
                    "summary": "Packet-first runtime handoff stays bounded.",
                    "carry_forward": [
                        "prefer packet before broad repo scan",
                        "end sessions with checkpoint or compaction before release",
                    ],
                    "pending_paths": ["tonesoul/runtime_adapter.py"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md", "tests/test_runtime_adapter.py"],
                    "next_action": "start collaborative sessions with diagnose then packet",
                    "source": "cli",
                    "updated_at": "2026-03-28T00:05:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    routing_events_path.write_text(
        json.dumps(
            [
                {
                    "event_id": "route-r1",
                    "agent": "codex",
                    "surface": "checkpoint",
                    "action": "preview",
                    "forced": False,
                    "overlap": False,
                    "misroute_signal": False,
                    "updated_at": "2026-03-28T00:05:30+00:00",
                    "summary": "prefer bounded shared surfaces over long interpretive prose",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "start_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-reinforced",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    validation = output["working_style_validation"]
    assert validation["status"] == "sufficient"
    assert validation["score"] == 1.0
    assert validation["checks"]["anchor_visible"] is True
    assert validation["checks"]["playbook_visible"] is True
    assert validation["checks"]["observability_visible"] is True
    assert validation["checks"]["import_limits_visible"] is True
    assert "enough shared style material" in validation["receiver_note"]


def test_start_agent_session_cli_executes_directly(tmp_path: Path) -> None:
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    _write_state(state_path)
    _write_traces(traces_path)

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "start_agent_session.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "cli-smoke",
            "--no-ack",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["agent"] == "cli-smoke"
    assert "canonical_center" in payload
    assert payload["canonical_center"]["parent_surfaces"] == ["task.md", "DESIGN.md"]
    assert payload["canonical_center"]["canonical_anchor_references"][0] == "AXIOMS.json"
    assert payload["canonical_center"]["source_precedence"][1]["layer"] == "live_coordination_truth"
    assert (
        payload["canonical_center"]["successor_correction"]["highest_risk_misread"]
        == "observer_stable_is_execution_permission"
    )
    assert "mutation_preflight" in payload
    assert (
        payload["mutation_preflight"]["next_followup"]["target"] == "publish_push.posture_preflight"
    )
    assert (
        payload["mutation_preflight"]["next_followup"]["classification"] == "existing_runtime_hook"
    )
    assert payload["publish_push_preflight"]["present"] is True
    assert payload["hook_chain"]["present"] is True
    assert payload["hook_chain"]["stages"][2]["name"] == "task_board_parking"
    assert payload["task_board_preflight"]["present"] is True
    assert "subsystem_parity" in payload
    assert (
        payload["subsystem_parity"]["next_focus"]["resolved_to"]
        == payload["mutation_preflight"]["next_followup"]["target"]
    )
    assert "working_style_playbook" in payload
    assert "working_style_validation" in payload


def test_start_agent_session_cli_tier0_executes_directly(tmp_path: Path) -> None:
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    _write_state(state_path)
    _write_traces(traces_path)

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "start_agent_session.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "cli-tier0",
            "--tier",
            "0",
            "--no-ack",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["tier"] == 0
    assert payload["bundle_posture"] == "fast_path"
    assert payload["canonical_center"]["present"] is True
    assert payload["mutation_preflight"]["present"] is True
    assert "hook_chain" not in payload  # deferred to tier 1
    assert "packet" not in payload
    assert "subsystem_parity" not in payload
    assert "working_style_playbook" not in payload


def test_start_agent_session_cli_tier1_executes_directly(tmp_path: Path) -> None:
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    _write_state(state_path)
    _write_traces(traces_path)

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "start_agent_session.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "cli-tier1",
            "--tier",
            "1",
            "--no-ack",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["tier"] == 1
    assert payload["bundle_posture"] == "orientation_shell"
    assert payload["observer_shell"]["present"] is True
    assert payload["subsystem_parity"]["present"] is True
    assert "packet" not in payload
    assert "import_posture" not in payload
    assert "working_style_playbook" not in payload


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root
