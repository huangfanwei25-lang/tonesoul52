from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from tonesoul.runtime_adapter import SessionTrace, write_compaction, write_subject_snapshot


def _load_script_module():
    module_name = "test_apply_subject_refresh_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "apply_subject_refresh.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_apply_subject_refresh_script_writes_bounded_active_thread_refresh(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    store = FileStore(
        gov_path=state_path,
        traces_path=traces_path,
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
        routing_events_path=tmp_path / ".aegis" / "routing_events.json",
    )

    write_subject_snapshot(
        agent_id="codex",
        session_id="sess-44",
        summary="Operate as a packet-first runtime steward with explicit boundaries.",
        stable_vows=["never smuggle theory into runtime truth"],
        durable_boundaries=["do not edit protected human-managed files"],
        decision_preferences=["prefer packet before broad repo scan"],
        verified_routines=["end sessions with checkpoint or compaction before release"],
        active_threads=["subject snapshot hardening"],
        store=store,
    )
    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-45",
            timestamp="2026-03-28T00:06:00+00:00",
            topics=["runtime_adapter", "redis"],
            key_decisions=["refresh active threads after compaction review"],
        ).to_dict()
    )
    write_compaction(
        agent_id="codex",
        session_id="sess-45",
        summary="Runtime adapter and redis coordination remain active threads.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "apply_subject_refresh.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--field",
            "active_threads",
            "--summary",
            "Refresh bounded active threads from clean compaction-backed evidence.",
            "--refresh-signal",
            "manual review complete",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["ok"] is True
    assert output["field"] == "active_threads"
    assert output["candidate_values"] == ["runtime_adapter", "redis"]

    saved = json.loads((tmp_path / ".aegis" / "subject_snapshots.json").read_text(encoding="utf-8"))
    assert saved[0]["active_threads"] == ["subject snapshot hardening", "runtime_adapter", "redis"]
    assert "manual review complete" in saved[0]["refresh_signals"]


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root
