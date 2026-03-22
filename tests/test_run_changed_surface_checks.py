from __future__ import annotations

import json
from pathlib import Path

import scripts.run_changed_surface_checks as runner


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_plans_surface_specific_checks(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )
    _write(
        tmp_path / "tonesoul" / "memory" / "crystallizer.py",
        "class MemoryCrystallizer:\n    pass\n",
    )
    _write(tmp_path / "tests" / "test_memory_crystallizer.py", "def test_smoke():\n    pass\n")
    _write(tmp_path / "docs" / "README.md", "# Docs\n")
    _write(tmp_path / "apps" / "web" / "src" / "lib" / "soulEngine.ts", "export const x = 1;\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=[
            "scripts/run_changed_surface_checks.py",
            "tonesoul/memory/crystallizer.py",
            "docs/README.md",
            "apps/web/src/lib/soulEngine.ts",
        ],
        python_executable="python",
    )

    surface_ids = [surface["id"] for surface in payload["surfaces"]]
    check_names = [check["name"] for check in payload["checks"]]

    assert payload["plan_ok"] is True
    assert payload["checks_ok"] is None
    assert "python_runtime" in surface_ids
    assert "core_runtime" in surface_ids
    assert "docs_governance" in surface_ids
    assert "web_surface" in surface_ids
    assert check_names == [
        "protected_paths",
        "python_lint_changed",
        "layer_boundaries",
        "docs_consistency",
        "targeted_pytest",
        "web_lint",
        "web_test",
        "python_full_regression",
    ]
    assert payload["metrics"]["planned_check_count"] == 8
    assert any(
        "tests/test_memory_crystallizer.py" in check["command"]
        for check in payload["checks"]
        if check["name"] == "targeted_pytest"
    )


def test_build_report_executes_checks_with_runner(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "verify_protected_paths.py", "print('ok')\n")
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )

    def fake_runner(name: str, command: list[str], cwd: Path) -> dict[str, object]:
        assert cwd == tmp_path
        return {
            "name": name,
            "status": "fail" if name == "targeted_pytest" else "pass",
            "ok": name != "targeted_pytest",
            "exit_code": 1 if name == "targeted_pytest" else 0,
            "duration_seconds": 0.01,
            "stdout_tail": runner._display_command(command),
            "stderr_tail": "",
        }

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["scripts/run_changed_surface_checks.py"],
        execute=True,
        runner=fake_runner,
        python_executable="python",
    )

    assert payload["execution_mode"] == "execute"
    assert payload["checks_ok"] is False
    assert payload["overall_ok"] is False
    assert payload["metrics"]["executed_check_count"] == 3
    assert payload["metrics"]["failed_check_count"] == 1
    assert any(check["status"] == "fail" for check in payload["checks"])


def test_main_writes_json_and_markdown(monkeypatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "status"
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )

    monkeypatch.setattr(
        runner,
        "build_parser",
        lambda: type(
            "Parser",
            (),
            {
                "parse_args": staticmethod(
                    lambda _argv=None: type(
                        "Args",
                        (),
                        {
                            "repo_root": str(tmp_path),
                            "out_dir": str(out_dir.relative_to(tmp_path)),
                            "changed_file": ["scripts/run_changed_surface_checks.py"],
                            "changed_file_list": None,
                            "staged": False,
                            "base_ref": None,
                            "allow_path": [],
                            "execute": False,
                            "strict": False,
                        },
                    )()
                )
            },
        )(),
    )

    exit_code = runner.main([])
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["metrics"]["planned_check_count"] == 3
    assert "# Changed Surface Checks Latest" in markdown
    assert "targeted_pytest" in markdown
