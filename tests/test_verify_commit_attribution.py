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


def test_docs_only_exemption_applies_when_trailers_missing() -> None:
    report = attribution.parse_commit_message("docs: update architecture note\n")
    adjusted = attribution.apply_docs_only_exemption(
        report,
        ["docs/ARCHITECTURE_DEPLOYED.md", "README.md"],
    )
    assert adjusted["ok"] is True
    assert adjusted["docs_only"] is True
    assert adjusted["exempted"] is True
    assert adjusted["exemption_reason"] == "docs-only commit"


def test_docs_only_exemption_not_applied_for_code_changes() -> None:
    report = attribution.parse_commit_message("docs: update architecture note\n")
    adjusted = attribution.apply_docs_only_exemption(
        report,
        ["docs/ARCHITECTURE_DEPLOYED.md", "tonesoul/council/runtime.py"],
    )
    assert adjusted["ok"] is False
    assert adjusted["docs_only"] is False
    assert adjusted["exempted"] is False
