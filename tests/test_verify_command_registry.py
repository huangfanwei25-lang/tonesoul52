from pathlib import Path

import scripts.verify_command_registry as verify_command_registry
from tonesoul.config import EntryPoint


def test_build_report_flags_missing_entrypoint_path(tmp_path: Path) -> None:
    payload = verify_command_registry.build_report(
        repo_root=tmp_path,
        entrypoints=[
            EntryPoint(
                name="missing_script",
                path=str(tmp_path / "missing.py"),
                command="python missing.py",
            )
        ],
    )

    assert payload["overall_ok"] is False
    assert payload["issue_count"] >= 1
    assert payload["entries"][0]["path_exists"] is False


def test_build_report_passes_valid_local_python_script(tmp_path: Path) -> None:
    script_path = tmp_path / "tool.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")

    payload = verify_command_registry.build_report(
        repo_root=tmp_path,
        entrypoints=[
            EntryPoint(
                name="tool",
                path=str(script_path),
                command="python tool.py",
            )
        ],
    )

    assert payload["overall_ok"] is True
    assert payload["issue_count"] == 0
    assert payload["entries"][0]["script_exists"] is True


def test_build_report_flags_duplicate_names(tmp_path: Path) -> None:
    first = tmp_path / "one.py"
    second = tmp_path / "two.py"
    first.write_text("print('one')\n", encoding="utf-8")
    second.write_text("print('two')\n", encoding="utf-8")

    payload = verify_command_registry.build_report(
        repo_root=tmp_path,
        entrypoints=[
            EntryPoint(name="dup", path=str(first), command="python one.py"),
            EntryPoint(name="dup", path=str(second), command="python two.py"),
        ],
    )

    assert payload["overall_ok"] is False
    assert payload["issue_count"] >= 2
    assert any("duplicate entrypoint name" in msg for msg in payload["entries"][0]["issues"])
