from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_change_intent_report.py"
SPEC = importlib.util.spec_from_file_location("run_change_intent_report", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_report_contains_intent_and_handoff(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        MODULE, "_git_touched_paths", lambda _repo_root: ["apps/api/server.py", "task.md"]
    )

    payload = MODULE.build_report(
        repo_root=tmp_path,
        intent_id="intent-001",
        summary="治理摘要路由收斂",
        why="需要可追溯的治理狀態來源",
        scope="apps/web + apps/api",
        invariants=["不修改 AGENTS.md", "不降低測試覆蓋"],
        planned_files=["apps/web/src/app/api/governance-status/route.ts", "apps/api/server.py"],
        validation_commands=["python -m pytest tests/test_server_new_routes.py -q"],
    )

    assert payload["status"] == "ready"
    assert payload["intent_id"] == "intent-001"
    assert payload["planned_files"] == [
        "apps/web/src/app/api/governance-status/route.ts",
        "apps/api/server.py",
    ]
    assert payload["touched_files"] == ["apps/api/server.py", "task.md"]
    assert "change_intent_ready" in payload["primary_status_line"]
    assert payload["handoff"]["queue_shape"] == "change_intent_ready"


def test_render_markdown_sections_present() -> None:
    payload = {
        "generated_at": "2026-03-18T07:00:00Z",
        "status": "ready",
        "primary_status_line": "change_intent_ready | intent_id=intent-001 planned_files=2 touched_files=1",
        "runtime_status_line": "intent_scope | scope=workspace invariants=1 validations=1",
        "artifact_policy_status_line": "change_governance=explicit_intent",
        "intent_id": "intent-001",
        "summary": "治理收斂",
        "why": "需要可追溯來源",
        "scope": "workspace",
        "invariants": ["測試必須維持綠燈"],
        "planned_files": ["task.md"],
        "validation_commands": ["python -m pytest -q"],
        "touched_files": ["task.md"],
    }

    markdown = MODULE.render_markdown(payload)

    assert "# Change Intent Latest" in markdown
    assert "## Intent" in markdown
    assert "## Invariants" in markdown
    assert "## Validation Commands" in markdown
    assert "`task.md`" in markdown


def test_main_writes_json_and_markdown(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "status"
    monkeypatch.setattr(MODULE, "_git_touched_paths", lambda _repo_root: ["task.md"])
    monkeypatch.setattr(
        MODULE,
        "_parse_args",
        lambda: type(
            "Args",
            (),
            {
                "repo_root": tmp_path,
                "out_dir": out_dir,
                "intent_id": "intent-002",
                "summary": "收斂整理",
                "why": "建立可審計的變更理由",
                "scope": "workspace",
                "invariant": ["不改動受保護檔案"],
                "planned_file": ["task.md"],
                "validation_cmd": ["python -m pytest tests/test_run_change_intent_report.py -q"],
                "stdout": False,
            },
        )(),
    )

    exit_code = MODULE.main()
    assert exit_code == 0

    payload = json.loads((out_dir / MODULE.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / MODULE.MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert payload["intent_id"] == "intent-002"
    assert payload["touched_files"] == ["task.md"]
    assert "intent-002" in markdown


def _args(**kwargs):
    """Build a minimal Args object for monkeypatching _parse_args."""
    defaults = {
        "repo_root": None,  # must be overridden
        "out_dir": None,  # must be overridden
        "intent_id": "intent-strict",
        "summary": "strict test",
        "why": "必要的理由",
        "scope": "workspace",
        "invariant": ["不改動受保護檔案"],
        "planned_file": [],
        "validation_cmd": ["python -m pytest -q"],
        "stdout": False,
        "strict": True,
    }
    defaults.update(kwargs)
    return type("Args", (), defaults)()


def test_strict_mode_rejects_empty_why(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "status"
    monkeypatch.setattr(MODULE, "_git_touched_paths", lambda _: [])
    monkeypatch.setattr(
        MODULE, "_parse_args", lambda: _args(repo_root=tmp_path, out_dir=out_dir, why="  ")
    )

    exit_code = MODULE.main()
    assert exit_code == 1


def test_strict_mode_rejects_empty_invariants(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "status"
    monkeypatch.setattr(MODULE, "_git_touched_paths", lambda _: [])
    monkeypatch.setattr(
        MODULE, "_parse_args", lambda: _args(repo_root=tmp_path, out_dir=out_dir, invariant=[])
    )

    exit_code = MODULE.main()
    assert exit_code == 1


def test_strict_mode_rejects_empty_validation_cmds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "status"
    monkeypatch.setattr(MODULE, "_git_touched_paths", lambda _: [])
    monkeypatch.setattr(
        MODULE, "_parse_args", lambda: _args(repo_root=tmp_path, out_dir=out_dir, validation_cmd=[])
    )

    exit_code = MODULE.main()
    assert exit_code == 1


def test_strict_mode_passes_with_all_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "status"
    monkeypatch.setattr(MODULE, "_git_touched_paths", lambda _: ["task.md"])
    monkeypatch.setattr(MODULE, "_parse_args", lambda: _args(repo_root=tmp_path, out_dir=out_dir))

    exit_code = MODULE.main()
    assert exit_code == 0
