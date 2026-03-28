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


def _write_state(state_path: Path) -> None:
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-03-28T00:00:00+00:00",
                "soul_integral": 0.72,
                "tension_history": [{"topic": "shared-start", "severity": 0.31}],
                "active_vows": [{"id": "v1", "content": "leave explicit handoff state"}],
                "aegis_vetoes": [],
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
    assert output["underlying_commands"][1] == (
        "python scripts/run_r_memory_packet.py --agent observer-preview"
    )
    cursor_data = json.loads(observer_cursors_path.read_text(encoding="utf-8"))
    assert "observer-preview" not in cursor_data


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root
