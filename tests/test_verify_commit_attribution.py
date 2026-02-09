import scripts.verify_commit_attribution as attribution


def test_parse_commit_message_ok() -> None:
    message = (
        "feat(council): integrate vtp evaluator\n"
        "\n"
        "Agent: codex-gpt5\n"
        "Trace-Topic: phase32-vtp-runtime-integration\n"
    )
    report = attribution.parse_commit_message(message)

    assert report["ok"] is True
    assert report["agent"] == "codex-gpt5"
    assert report["topic"] == "phase32-vtp-runtime-integration"
    assert report["summary"] == "feat(council): integrate vtp evaluator"


def test_parse_commit_message_missing_trailers() -> None:
    message = "fix(ci): resolve lint drift\n"
    report = attribution.parse_commit_message(message)

    assert report["ok"] is False
    assert report["has_agent"] is False
    assert report["has_topic"] is False
    assert report["agent"] is None
    assert report["topic"] is None
