from integrations.openclaw.skills.tonesoul import invoke_skill, list_skills


def test_openclaw_skill_registry_lists_expected_skills():
    names = {row["name"] for row in list_skills()}
    assert "benevolence_audit" in names
    assert "council_deliberate" in names


def test_benevolence_skill_run_returns_structured_result():
    result = invoke_skill(
        "benevolence_audit",
        {
            "proposed_action": "I will verify facts before giving final advice.",
            "context_fragments": ["verify facts", "give advice"],
            "current_layer": "L2",
        },
    )
    assert result["ok"] is True
    assert result["skill"] == "benevolence_audit"
    assert isinstance(result["result"], dict)
    assert "audit" in result["result"]


def test_council_skill_run_returns_verdict_payload():
    result = invoke_skill(
        "council_deliberate",
        {
            "draft_output": "I can help summarize this plan.",
            "context": {"user_message": "please summarize"},
            "user_intent": "summarize",
        },
    )
    assert result["ok"] is True
    assert result["skill"] == "council_deliberate"
    assert isinstance(result["result"], dict)
    assert "verdict" in result["result"]


def test_invoke_skill_returns_error_for_unknown_skill():
    result = invoke_skill("missing-skill", {})
    assert result["ok"] is False
    assert "available_skills" in result
