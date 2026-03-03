from pathlib import Path

import scripts.verify_submodule_integrity as verify_submodule_integrity


def test_build_report_passes_when_gitlinks_match_gitmodules(tmp_path: Path) -> None:
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text(
        '[submodule "OpenClaw-Memory"]\n'
        "path = OpenClaw-Memory\n"
        "url = https://example.com/OpenClaw-Memory.git\n",
        encoding="utf-8",
    )

    def runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
        assert cwd == tmp_path
        if command == ["git", "ls-files", "-s"]:
            return (0, "160000 abcdef1234567890 0\tOpenClaw-Memory\n", "")
        if command == ["git", "submodule", "status"]:
            return (0, " abcdef1234567890 OpenClaw-Memory\n", "")
        return (1, "", "unexpected command")

    payload = verify_submodule_integrity.build_report(tmp_path, runner=runner)
    assert payload["overall_ok"] is True
    assert payload["issue_count"] == 0


def test_build_report_flags_missing_gitmodules_mapping(tmp_path: Path) -> None:
    def runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
        if command == ["git", "ls-files", "-s"]:
            return (0, "160000 deadbeef12345678 0\ttae_fix\n", "")
        if command == ["git", "submodule", "status"]:
            return (1, "", "fatal: no submodule mapping found in .gitmodules")
        return (1, "", "unexpected command")

    payload = verify_submodule_integrity.build_report(tmp_path, runner=runner)
    assert payload["overall_ok"] is False
    assert payload["issue_count"] >= 1
    assert any(
        "gitlinks present but .gitmodules is missing" in issue for issue in payload["issues"]
    )
