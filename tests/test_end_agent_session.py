from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_end_agent_session_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "end_agent_session.py"
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
                "tension_history": [{"topic": "session-end", "severity": 0.31}],
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
                "topics": ["session-end"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["bundle session end"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_end_agent_session_compaction_and_release(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    claims_path = sidecar_dir / "task_claims.json"
    compactions_path = sidecar_dir / "compacted.json"

    _write_state(state_path)
    _write_traces(traces_path)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-codex": {
                    "task_id": "task-codex",
                    "agent": "codex",
                    "summary": "hold the runtime lane",
                    "paths": ["tonesoul/runtime_adapter.py"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                },
                "task-other": {
                    "task_id": "task-other",
                    "agent": "claude",
                    "summary": "parallel lane",
                    "paths": ["docs/AI_REFERENCE.md"],
                    "source": "cli",
                    "created_at": "2026-03-28T00:02:10+00:00",
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
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "leave a bounded handoff for the runtime lane",
            "--path",
            "tonesoul/runtime_adapter.py",
            "--carry-forward",
            "keep session-end bundle aligned with session-start bundle",
            "--next-action",
            "run the next observer handoff test",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["contract_version"] == "v1"
    assert output["bundle"] == "session_end"
    assert output["mode"] == "compaction"
    assert output["closeout"]["status"] == "partial"
    assert output["checkpoint"] is None
    assert output["compaction"]["agent"] == "codex"
    assert output["compaction"]["closeout"]["status"] == "partial"
    assert output["released_claims"]["strategy"] == "all_for_agent"
    assert output["released_claims"]["released_task_ids"] == ["task-codex"]
    assert output["released_claims"]["not_released_task_ids"] == []
    assert output["released_claims"]["remaining_claims"][0]["task_id"] == "task-other"
    assert output["underlying_commands"][0].startswith(
        "python scripts/save_compaction.py --agent codex"
    )
    assert (
        output["underlying_commands"][1]
        == "python scripts/run_task_claim.py release <task_id> --agent codex"
    )

    stored_compactions = json.loads(compactions_path.read_text(encoding="utf-8"))
    assert stored_compactions[0]["summary"] == "leave a bounded handoff for the runtime lane"
    assert stored_compactions[0]["closeout"]["status"] == "partial"
    remaining_claims = json.loads(claims_path.read_text(encoding="utf-8"))
    assert "task-codex" not in remaining_claims
    assert "task-other" in remaining_claims


def test_end_agent_session_both_mode_with_no_release(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    claims_path = sidecar_dir / "task_claims.json"
    checkpoints_path = sidecar_dir / "checkpoints.json"

    _write_state(state_path)
    _write_traces(traces_path)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-codex": {
                    "task_id": "task-codex",
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
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--mode",
            "both",
            "--checkpoint-id",
            "cp-final",
            "--summary",
            "leave both a checkpoint and a compaction before a context reset",
            "--path",
            "tonesoul/diagnose.py",
            "--next-action",
            "verify the next session sees the new handoff",
            "--no-release",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["mode"] == "both"
    assert output["closeout"]["status"] == "partial"
    assert output["checkpoint"]["checkpoint_id"] == "cp-final"
    assert output["compaction"]["summary"].startswith("leave both a checkpoint")
    assert output["compaction"]["closeout"]["status"] == "partial"
    assert output["released_claims"]["strategy"] == "none"
    assert output["released_claims"]["released_task_ids"] == []
    assert output["underlying_commands"][0].startswith(
        "python scripts/save_checkpoint.py --checkpoint-id cp-final --agent codex"
    )
    assert output["underlying_commands"][1].startswith(
        "python scripts/save_compaction.py --agent codex"
    )
    assert len(output["underlying_commands"]) == 2

    stored_checkpoints = json.loads(checkpoints_path.read_text(encoding="utf-8"))
    assert (
        stored_checkpoints["cp-final"]["next_action"]
        == "verify the next session sees the new handoff"
    )
    remaining_claims = json.loads(claims_path.read_text(encoding="utf-8"))
    assert "task-codex" in remaining_claims


def test_end_agent_session_can_apply_bounded_subject_refresh(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    subject_snapshots_path = tmp_path / ".aegis" / "subject_snapshots.json"

    _write_state(state_path)
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-28T00:01:00+00:00",
                "topics": ["runtime_adapter", "redis"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["bundle session end with bounded subject refresh"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    subject_snapshots_path.parent.mkdir(parents=True, exist_ok=True)
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

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "leave a bounded handoff for the runtime lane",
            "--path",
            "tonesoul/runtime_adapter.py",
            "--next-action",
            "run the next observer handoff test",
            "--refresh-active-threads",
            "--no-release",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["mode"] == "compaction"
    assert output["closeout"]["status"] == "partial"
    assert output["subject_refresh_application"]["ok"] is True
    assert output["subject_refresh_application"]["field"] == "active_threads"
    assert output["subject_refresh_application"]["candidate_values"] == ["runtime_adapter", "redis"]
    assert output["underlying_commands"][0].startswith(
        "python scripts/save_compaction.py --agent codex"
    )
    assert output["underlying_commands"][1].startswith(
        "python scripts/apply_subject_refresh.py --agent codex --field active_threads"
    )

    saved = json.loads(subject_snapshots_path.read_text(encoding="utf-8"))
    assert saved[0]["active_threads"] == ["subject snapshot hardening", "runtime_adapter", "redis"]
    assert "active_threads compaction-backed refresh applied" in saved[0]["refresh_signals"]


def test_end_agent_session_does_not_promote_recycled_carry_forward_without_new_evidence(
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
                "key_decisions": ["attempt a recycled subject refresh"],
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
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "leave a repeated handoff for the runtime lane",
            "--path",
            "tonesoul/runtime_adapter.py",
            "--carry-forward",
            "keep packet-first session cadence stable",
            "--evidence-ref",
            "docs/AI_QUICKSTART.md",
            "--next-action",
            "run the next observer handoff test",
            "--refresh-active-threads",
            "--no-release",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["mode"] == "compaction"
    assert output["closeout"]["status"] == "partial"
    assert output["subject_refresh_application"]["ok"] is False
    assert output["subject_refresh_application"]["reason"] == "promotion_hazards_present"
    assert any(
        "recycled carry_forward" in hazard
        for hazard in output["subject_refresh_application"]["subject_refresh"]["promotion_hazards"]
    )
    saved = json.loads(subject_snapshots_path.read_text(encoding="utf-8"))
    assert saved[0]["snapshot_id"] == "subj-1"


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root


def test_end_agent_session_accepts_blocked_closeout_grammar(
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
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "Stop here until a human resolves the authority fork.",
            "--path",
            "task.md",
            "--next-action",
            "STOP: requires human decision on authority fork",
            "--closeout-status",
            "blocked",
            "--stop-reason",
            "external_blocked",
            "--unresolved-item",
            "human must choose which authority surface wins",
            "--human-input-required",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["closeout"]["status"] == "blocked"
    assert output["closeout"]["stop_reason"] == "external_blocked"
    assert output["closeout"]["human_input_required"] is True
    assert output["closeout"]["unresolved_items"] == [
        "human must choose which authority surface wins"
    ]
    assert output["compaction"]["closeout"]["status"] == "blocked"
    assert "--closeout-status blocked" in output["underlying_commands"][0]


def test_end_agent_session_keeps_complete_closeout_when_no_pending_paths_or_next_action(
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
            "end_agent_session.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "Bounded task completed cleanly with no carry-forward.",
            "--closeout-status",
            "complete",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["closeout"]["status"] == "complete"
    assert output["compaction"]["closeout"]["status"] == "complete"
    assert "--closeout-status complete" in output["underlying_commands"][0]


def test_end_agent_session_force_file_store_env_builds_explicit_store(capsys, monkeypatch) -> None:
    module = _load_script_module()
    captured: list[dict] = []

    class _StubFileStore:
        def __init__(self, *args, **kwargs) -> None:
            self.backend_name = "file"

        def append_compaction(self, payload, *, limit: int, ttl_seconds: int) -> None:
            captured.append(
                {
                    "payload": dict(payload),
                    "limit": limit,
                    "ttl_seconds": ttl_seconds,
                }
            )

    def _unexpected_get_store(*args, **kwargs):
        raise AssertionError("end_agent_session should not fall back to tonesoul.store.get_store")

    monkeypatch.setenv("TONESOUL_FORCE_FILE_STORE", "1")
    monkeypatch.setattr("tonesoul.backends.file_store.FileStore", _StubFileStore)
    monkeypatch.setattr("tonesoul.store.get_store", _unexpected_get_store)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "end_agent_session.py",
            "--agent",
            "codex",
            "--summary",
            "Bounded task completed cleanly with explicit file-backed closeout.",
            "--closeout-status",
            "complete",
            "--no-release",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["closeout"]["status"] == "complete"
    assert output["compaction"]["closeout"]["status"] == "complete"
    assert output["released_claims"]["strategy"] == "none"
    assert captured[0]["payload"]["summary"].startswith("Bounded task completed cleanly")
