from tonesoul.action_set import _decision_mode, resolve_action_set


def test_decision_mode_defaults_for_missing_or_invalid_kairos():
    assert _decision_mode({}) == "normal"
    assert _decision_mode({"time_island": {"kairos": "bad"}}) == "normal"
    assert _decision_mode({"time_island": {"kairos": {"decision_mode": "cautious"}}}) == "cautious"


def test_resolve_action_set_returns_allowed_actions_and_fallback_for_unknown_mode():
    cautious = resolve_action_set({"time_island": {"kairos": {"decision_mode": "cautious"}}})
    unknown = resolve_action_set({"time_island": {"kairos": {"decision_mode": "surprise"}}})

    assert cautious["allowed_actions"] == ["verify", "inquire"]
    assert cautious["strict_mode_policy"]["lockdown"] == ["verify", "cite", "inquire"]
    assert unknown["decision_mode"] == "surprise"
    assert unknown["allowed_actions"] == ["verify", "cite", "inquire"]
