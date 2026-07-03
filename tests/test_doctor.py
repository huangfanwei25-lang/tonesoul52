from __future__ import annotations

import json

import scripts.doctor as doctor


def test_check_module_reports_gap_without_importing(monkeypatch):
    calls: list[str] = []

    def fake_find_spec(module: str):
        calls.append(module)
        return None

    monkeypatch.setattr(doctor.importlib.util, "find_spec", fake_find_spec)

    item = doctor.check_module("hypothesis", "python.import.hypothesis")

    assert item["status"] == "GAP"
    assert item["repair"] == 'pip install -e ".[dev]"'
    assert calls == ["hypothesis"]


def test_git_checkout_gap_for_source_zip(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda tool: f"/bin/{tool}")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("git should not run when .git metadata is absent")

    monkeypatch.setattr(doctor, "_run_command", fail_if_called)

    item = doctor.check_git(tmp_path)

    assert item["status"] == "GAP"
    assert "source zip" in item["detail"]
    assert item["repair"] == "Use a git clone instead of a source zip"


def test_empty_submodule_directory_is_gap(tmp_path):
    (tmp_path / ".gitmodules").write_text(
        '[submodule "OpenClaw-Memory"]\n'
        "\tpath = OpenClaw-Memory\n"
        "\turl = https://example.invalid/OpenClaw-Memory.git\n",
        encoding="utf-8",
    )
    (tmp_path / "OpenClaw-Memory").mkdir()

    item = doctor.check_submodules(tmp_path)

    assert item["status"] == "GAP"
    assert "OpenClaw-Memory" in item["detail"]
    assert item["repair"] == "git submodule update --init"


def test_submodule_drift_from_git_status_is_gap(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitmodules").write_text(
        '[submodule "OpenClaw-Memory"]\n'
        "\tpath = OpenClaw-Memory\n"
        "\turl = https://example.invalid/OpenClaw-Memory.git\n",
        encoding="utf-8",
    )
    submodule_dir = tmp_path / "OpenClaw-Memory"
    submodule_dir.mkdir()
    (submodule_dir / "README.md").write_text("initialized\n", encoding="utf-8")
    monkeypatch.setattr(doctor.shutil, "which", lambda tool: f"/bin/{tool}")
    monkeypatch.setattr(
        doctor,
        "_run_command",
        lambda *args, **kwargs: (0, "+abc123 OpenClaw-Memory (heads/main)", ""),
    )

    item = doctor.check_submodules(tmp_path)

    assert item["status"] == "GAP"
    assert "drifted: OpenClaw-Memory" in item["detail"]
    assert item["data"]["drifted"] == ["OpenClaw-Memory"]


def test_clean_submodule_status_with_leading_space_is_pass(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitmodules").write_text(
        '[submodule "OpenClaw-Memory"]\n'
        "\tpath = OpenClaw-Memory\n"
        "\turl = https://example.invalid/OpenClaw-Memory.git\n",
        encoding="utf-8",
    )
    submodule_dir = tmp_path / "OpenClaw-Memory"
    submodule_dir.mkdir()
    (submodule_dir / "README.md").write_text("initialized\n", encoding="utf-8")
    monkeypatch.setattr(doctor.shutil, "which", lambda tool: f"/bin/{tool}")
    monkeypatch.setattr(
        doctor,
        "_run_command",
        lambda *args, **kwargs: (0, " abc123 OpenClaw-Memory (heads/main)", ""),
    )

    item = doctor.check_submodules(tmp_path)

    assert item["status"] == "PASS"


def test_node_modules_missing_is_gap(tmp_path):
    (tmp_path / "apps" / "web").mkdir(parents=True)

    item = doctor.check_node_modules(tmp_path)

    assert item["status"] == "GAP"
    assert item["repair"] == "npm --prefix apps/web install"


def test_optional_tool_missing_is_skip(monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda tool: None)

    item = doctor.check_optional_tool("gh", ("gh", "--version"))

    assert item["status"] == "SKIP"
    assert "optional" in item["detail"]


def test_main_json_output_is_structured(monkeypatch, capsys):
    checks = [
        doctor.result("python.version", "PASS", "ok"),
        doctor.result(
            "python.import.hypothesis", "GAP", "missing", repair='pip install -e ".[dev]"'
        ),
        doctor.result("optional.gh", "SKIP", "optional"),
    ]
    monkeypatch.setattr(doctor, "run_all_checks", lambda: checks)

    exit_code = doctor.main(["--json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["summary"] == {"pass": 1, "gap": 1, "skip": 1, "exit_code": 1}
    assert payload["checks"][1]["repair"] == 'pip install -e ".[dev]"'


def test_render_text_attaches_fix_to_each_gap():
    checks = [
        doctor.result("python.version", "PASS", "ok"),
        doctor.result("node.modules", "GAP", "missing", repair="npm --prefix apps/web install"),
    ]

    text = doctor.render_text(checks)

    assert "[GAP] node.modules: missing" in text
    assert "fix: npm --prefix apps/web install" in text
    assert "Summary: PASS=1 GAP=1 SKIP=0 exit=1" in text
