from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_route_r_memory_signal_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "route_r_memory_signal.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_route_r_memory_signal_previews_checkpoint_route(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "route_r_memory_signal.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "resume packet cleanup",
            "--pending-path",
            "tonesoul/diagnose.py",
            "--next-action",
            "finish delta formatting",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)
    routing_events_path = tmp_path / ".aegis" / "routing_events.json"
    routing_events = json.loads(routing_events_path.read_text(encoding="utf-8"))

    assert output["route"]["surface"] == "checkpoint"
    assert output["route"]["confidence"] == "high"
    assert output["route"]["payload"]["pending_paths"] == ["tonesoul/diagnose.py"]
    assert output["routing_event"]["action"] == "preview"
    assert output["routing_event"]["surface"] == "checkpoint"
    assert routing_events[0]["action"] == "preview"
    assert "written" not in output


def test_route_r_memory_signal_can_write_subject_snapshot(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "route_r_memory_signal.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "packet-first startup is now a durable operating preference",
            "--boundary",
            "do not skip diagnose plus packet startup",
            "--preference",
            "prefer signal routing over dumping raw notes",
            "--write",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)
    subject_path = tmp_path / ".aegis" / "subject_snapshots.json"
    routing_events_path = tmp_path / ".aegis" / "routing_events.json"
    saved = json.loads(subject_path.read_text(encoding="utf-8"))
    routing_events = json.loads(routing_events_path.read_text(encoding="utf-8"))

    assert output["route"]["surface"] == "subject_snapshot"
    assert output["written"]["summary"].startswith("packet-first startup")
    assert output["routing_event"]["action"] == "write"
    assert output["routing_event"]["misroute_signal"] is False
    assert saved[0]["durable_boundaries"] == ["do not skip diagnose plus packet startup"]
    assert saved[0]["decision_preferences"] == ["prefer signal routing over dumping raw notes"]
    assert routing_events[0]["surface"] == "subject_snapshot"
