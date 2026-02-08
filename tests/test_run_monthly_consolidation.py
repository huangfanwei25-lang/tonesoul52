import scripts.run_monthly_consolidation as monthly


def test_build_check_commands_includes_allow_missing_discussion_flag() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=True)
    assert "--allow-missing-discussion" in commands["memory_hygiene"]


def test_build_check_commands_omits_allow_missing_discussion_flag() -> None:
    commands = monthly._build_check_commands(allow_missing_discussion=False)
    assert "--allow-missing-discussion" not in commands["memory_hygiene"]
