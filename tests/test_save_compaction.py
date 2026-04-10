from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_compaction_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_compaction.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_compaction_writes_noncanonical_summary(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    payload_path = tmp_path / "payload.json"

    payload_path.write_text(
        json.dumps(
            {
                "agent": "codex",
                "session_id": "sess-101",
                "summary": "Condense the runtime state into a resumability summary.",
                "carry_forward": ["keep Aegis before mutation"],
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
                    "vote_summary": [
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.75,
                        }
                    ],
                    "deliberation_mode": "standard_council",
                    "change_of_position": [],
                    "evidence_refs": ["docs/spec.md"],
                    "grounding_summary": {
                        "has_ungrounded_claims": False,
                        "total_evidence_sources": 1,
                    },
                    "opacity_declaration": "partially_observable",
                },
                "next_action": "teach the next agent to read packet first",
                "source": "file",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--input",
            str(payload_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["session_id"] == "sess-101"
    assert output["summary"].startswith("Condense the runtime state")
    assert output["closeout"]["status"] == "partial"
    assert output["closeout"]["unresolved_items"] == []

    saved = json.loads((tmp_path / ".aegis" / "compacted.json").read_text(encoding="utf-8"))
    assert saved[0]["agent"] == "codex"
    assert saved[0]["next_action"] == "teach the next agent to read packet first"
    assert saved[0]["council_dossier"]["confidence_posture"] == "contested"
    assert saved[0]["closeout"]["status"] == "partial"


def test_save_compaction_accepts_minimal_input_payload(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    payload_path = tmp_path / "compaction.json"
    payload_path.write_text(
        json.dumps(
            {
                "agent": "codex",
                "summary": "Minimal compaction payload.",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--input",
            str(payload_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["carry_forward"] == []
    assert output["evidence_refs"] == []
    assert output["council_dossier"] == {}
    assert output["closeout"]["status"] == "complete"


def test_save_compaction_reads_payload_from_stdin(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    class _FakeStdin:
        def isatty(self) -> bool:
            return False

        def read(self) -> str:
            return json.dumps(
                {
                    "agent": "observer",
                    "session_id": "sess-stdin",
                    "summary": "Compaction loaded from stdin.",
                    "carry_forward": ["re-check freshness before import"],
                    "pending_paths": ["scripts/start_agent_session.py"],
                    "source": "stdin",
                }
            )

    monkeypatch.setattr(sys, "stdin", _FakeStdin())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["source"] == "stdin"
    saved = json.loads((tmp_path / ".aegis" / "compacted.json").read_text(encoding="utf-8"))
    assert saved[0]["carry_forward"] == ["re-check freshness before import"]
    assert saved[0]["closeout"]["status"] == "partial"


def test_save_compaction_uses_cli_payload_when_stdin_is_tty(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    class _FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr(sys, "stdin", _FakeStdin())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "CLI payload should work when stdin is a tty.",
            "--closeout-status",
            "complete",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["summary"] == "CLI payload should work when stdin is a tty."
    assert output["closeout"]["status"] == "complete"


def test_save_compaction_respects_limit_and_newest_first_order(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    for summary in ["first", "second", "third"]:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "save_compaction.py",
                "--state-path",
                str(state_path),
                "--traces-path",
                str(traces_path),
                "--agent",
                "codex",
                "--summary",
                summary,
                "--limit",
                "2",
            ],
        )
        module.main()
        capsys.readouterr()

    saved = json.loads((tmp_path / ".aegis" / "compacted.json").read_text(encoding="utf-8"))
    assert [entry["summary"] for entry in saved] == ["third", "second"]


def test_save_compaction_prefers_legacy_sidecar_when_present(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    legacy_path = tmp_path / "compacted.json"
    legacy_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--summary",
            "Write to the existing legacy compaction sidecar.",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["summary"] == "Write to the existing legacy compaction sidecar."
    saved = json.loads(legacy_path.read_text(encoding="utf-8"))
    assert saved[0]["agent"] == "codex"
    assert not (tmp_path / ".aegis" / "compacted.json").exists()


def test_save_compaction_accepts_explicit_blocked_closeout(
    capsys, monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    payload_path = tmp_path / "blocked_compaction.json"
    payload_path.write_text(
        json.dumps(
            {
                "agent": "codex",
                "summary": "Pause before mutating the shared runtime lane.",
                "pending_paths": ["tonesoul/runtime_adapter.py"],
                "closeout_status": "blocked",
                "stop_reason": "external_blocked",
                "human_input_required": True,
                "unresolved_items": ["human must confirm whether to reopen the runtime lane"],
                "closeout_note": "Blocked on human confirmation before the next mutation.",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--input",
            str(payload_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["closeout"]["status"] == "blocked"
    assert output["closeout"]["stop_reason"] == "external_blocked"
    assert output["closeout"]["human_input_required"] is True
    assert output["closeout"]["unresolved_items"] == [
        "human must confirm whether to reopen the runtime lane"
    ]


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root


def test_save_compaction_force_file_store_env_builds_explicit_store(capsys, monkeypatch) -> None:
    module = _load_script_module()
    captured: list[dict] = []

    class _StubFileStore:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def append_compaction(self, payload, *, limit: int, ttl_seconds: int) -> None:
            captured.append(
                {
                    "payload": dict(payload),
                    "limit": limit,
                    "ttl_seconds": ttl_seconds,
                }
            )

    def _unexpected_get_store(*args, **kwargs):
        raise AssertionError("save_compaction should not fall back to tonesoul.store.get_store")

    monkeypatch.setenv("TONESOUL_FORCE_FILE_STORE", "1")
    monkeypatch.setattr("tonesoul.backends.file_store.FileStore", _StubFileStore)
    monkeypatch.setattr("tonesoul.store.get_store", _unexpected_get_store)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--agent",
            "codex",
            "--summary",
            "Compaction through explicit file-backed store.",
            "--closeout-status",
            "complete",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["summary"] == "Compaction through explicit file-backed store."
    assert output["closeout"]["status"] == "complete"
    assert captured[0]["payload"]["summary"] == "Compaction through explicit file-backed store."
