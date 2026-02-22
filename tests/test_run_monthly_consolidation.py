import scripts.run_monthly_consolidation as monthly


def test_build_check_commands_includes_allow_missing_discussion_flag() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=True)
    assert "--allow-missing-discussion" in commands["memory_hygiene"]


def test_build_check_commands_omits_allow_missing_discussion_flag() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=False)
    assert "--allow-missing-discussion" not in commands["memory_hygiene"]


def test_build_check_commands_includes_persona_swarm_strict_check() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=False)
    assert commands["persona_swarm"] == [
        monthly.sys.executable,
        "scripts/run_persona_swarm_framework.py",
        "--strict",
    ]


def test_build_check_commands_includes_memory_quality_strict_check() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=False)
    assert commands["memory_quality"] == [
        monthly.sys.executable,
        "scripts/run_memory_quality_report.py",
        "--strict",
    ]


def test_display_command_normalizes_python_executable() -> None:
    command = [
        r"C:\\Users\\user\\Desktop\\repo\\.venv\\Scripts\\python.exe",
        "scripts/run_monthly_consolidation.py",
        "--strict",
    ]
    assert (
        monthly._display_command(command) == "python scripts/run_monthly_consolidation.py --strict"
    )
