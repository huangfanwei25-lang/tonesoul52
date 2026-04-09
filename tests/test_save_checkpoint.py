from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_checkpoint_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_checkpoint.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_checkpoint_writes_noncanonical_checkpoint(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_checkpoint.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--checkpoint-id",
            "cp-20260327",
            "--agent",
            "codex",
            "--session-id",
            "sess-ops",
            "--summary",
            "Pause before commit and leave a resumable checkpoint.",
            "--path",
            "tonesoul/unified_pipeline.py",
            "--next-action",
            "Resume packet-first observer hardening",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["checkpoint_id"] == "cp-20260327"
    assert output["agent"] == "codex"
    saved = json.loads((tmp_path / ".aegis" / "checkpoints.json").read_text(encoding="utf-8"))
    assert saved["cp-20260327"]["pending_paths"] == ["tonesoul/unified_pipeline.py"]


def test_save_checkpoint_accepts_minimal_input_payload(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    payload_path = tmp_path / "checkpoint.json"
    payload_path.write_text(
        json.dumps(
            {
                "checkpoint_id": "cp-minimal",
                "agent": "codex",
                "summary": "Minimal checkpoint payload.",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_checkpoint.py",
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

    assert output["checkpoint_id"] == "cp-minimal"
    assert output["pending_paths"] == []
    assert output["next_action"] == ""
    assert output["source"] == "cli"


def test_save_checkpoint_reads_payload_from_stdin(
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
                    "checkpoint_id": "cp-stdin",
                    "agent": "observer",
                    "session_id": "sess-stdin",
                    "summary": "Read checkpoint from stdin payload.",
                    "pending_paths": ["docs/README.md"],
                    "next_action": "verify continuity import posture",
                    "source": "stdin",
                }
            )

    monkeypatch.setattr(sys, "stdin", _FakeStdin())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_checkpoint.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["checkpoint_id"] == "cp-stdin"
    assert output["source"] == "stdin"
    saved = json.loads((tmp_path / ".aegis" / "checkpoints.json").read_text(encoding="utf-8"))
    assert saved["cp-stdin"]["pending_paths"] == ["docs/README.md"]


def test_save_checkpoint_prefers_legacy_sidecar_when_present(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    legacy_path = tmp_path / "checkpoints.json"
    legacy_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_checkpoint.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--checkpoint-id",
            "cp-legacy",
            "--agent",
            "codex",
            "--summary",
            "Write to the existing legacy sidecar.",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["checkpoint_id"] == "cp-legacy"
    saved = json.loads(legacy_path.read_text(encoding="utf-8"))
    assert "cp-legacy" in saved
    assert not (tmp_path / ".aegis" / "checkpoints.json").exists()


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root


def test_save_checkpoint_force_file_store_env_builds_explicit_store(capsys, monkeypatch) -> None:
    module = _load_script_module()
    captured: dict[str, object] = {}

    class _StubFileStore:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def set_checkpoint(self, checkpoint_id, payload, *, ttl_seconds: int) -> None:
            captured["checkpoint_id"] = checkpoint_id
            captured["payload"] = dict(payload)
            captured["ttl_seconds"] = ttl_seconds

    def _unexpected_get_store(*args, **kwargs):
        raise AssertionError("save_checkpoint should not fall back to tonesoul.store.get_store")

    monkeypatch.setenv("TONESOUL_FORCE_FILE_STORE", "1")
    monkeypatch.setattr("tonesoul.backends.file_store.FileStore", _StubFileStore)
    monkeypatch.setattr("tonesoul.store.get_store", _unexpected_get_store)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_checkpoint.py",
            "--checkpoint-id",
            "cp-force-file",
            "--agent",
            "codex",
            "--summary",
            "Checkpoint through explicit file-backed store.",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["checkpoint_id"] == "cp-force-file"
    assert captured["checkpoint_id"] == "cp-force-file"
    assert captured["payload"]["summary"] == "Checkpoint through explicit file-backed store."
