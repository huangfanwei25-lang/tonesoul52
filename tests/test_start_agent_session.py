from __future__ import annotations

import importlib.util
import json
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
                "tension_history": tensions if tensions is not None else [{"topic": "shared-start", "severity": 0.31}],
                "active_vows": vows if vows is not None else [{"id": "v1", "content": "leave explicit handoff state"}],
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


def test_start_agent_session_emits_machine_readable_bundle(capsys, monkeypatch, tmp_path: Path) -> None:
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
    assert output["compact_diagnostic"].endswith("| readiness=needs_clarification")
    assert output["readiness"]["status"] == "needs_clarification"
    assert output["readiness"]["ready"] is False
    assert output["readiness"]["claim_conflict_count"] == 1
    assert output["readiness"]["clarification_reasons"] == ["other_agent_claims_visible"]
    assert output["import_posture"]["surfaces"]["posture"]["import_posture"] == "directly_importable"
    assert output["import_posture"]["surfaces"]["claims"]["import_posture"] == "directly_importable"
    assert output["import_posture"]["surfaces"]["claims"]["receiver_obligation"] == "must_read"
    assert "TTL" in output["import_posture"]["surfaces"]["claims"]["note"]
    assert output["import_posture"]["surfaces"]["delta_feed"]["import_posture"] == "ephemeral_until_acked"
    assert output["import_posture"]["surfaces"]["subject_snapshot"]["present"] is False
    assert output["import_posture"]["readiness_alignment"] == "needs_clarification"
    assert output["import_posture"]["summary_text"].startswith("posture=directly_importable")
    assert output["underlying_commands"][0] == "python -m tonesoul.diagnose --agent observer-start"
    assert output["underlying_commands"][1] == (
        "python scripts/run_r_memory_packet.py --agent observer-start --ack"
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
    assert output["import_posture"]["surfaces"]["delta_feed"]["present"] is True
    assert output["underlying_commands"][1] == (
        "python scripts/run_r_memory_packet.py --agent observer-preview"
    )
    cursor_data = json.loads(observer_cursors_path.read_text(encoding="utf-8"))
    assert "observer-preview" not in cursor_data


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
                }
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
                    "verified_routines": ["end sessions with checkpoint or compaction before release"],
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
            "observer-carry-forward",
            "--no-ack",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    compaction_surface = output["import_posture"]["surfaces"]["compactions"]
    assert compaction_surface["import_posture"] == "advisory"
    assert compaction_surface["receiver_obligation"] == "must_not_promote"
    assert any("recycled carry_forward" in hazard for hazard in compaction_surface["promotion_hazards"])
    assert any(
        "Latest carry-forward repeats an older handoff without new evidence"
        in alert
        for alert in output["import_posture"]["receiver_alerts"]
    )


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root
