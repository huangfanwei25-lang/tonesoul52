from __future__ import annotations

from tonesoul import constraint_stack as constraint_mod
from tonesoul.action_set import ACTION_POLICY, resolve_action_set
from tonesoul.dcs import build_dcs_result


def test_lockdown_action_set_stays_within_static_policy() -> None:
    action_set = resolve_action_set({"time_island": {"kairos": {"decision_mode": "lockdown"}}})

    assert action_set["decision_mode"] == "lockdown"
    assert set(action_set["allowed_actions"]) <= set(ACTION_POLICY["lockdown"])


def test_unknown_decision_mode_falls_back_to_normal_policy() -> None:
    action_set = resolve_action_set({"time_island": {"kairos": {"decision_mode": "unknown"}}})

    assert action_set["decision_mode"] == "unknown"
    assert action_set["allowed_actions"] == ACTION_POLICY["normal"]


def test_dcs_lockdown_halts_on_poav_breach() -> None:
    result = build_dcs_result(
        decision_mode="lockdown",
        p0_passed=True,
        poav_total=0.2,
        poav_threshold=0.7,
    )

    assert result["state"] == "closed"
    assert result["decision"] == "halt"
    assert "poav" in result["triggered"]["closed"]


def test_dcs_lockdown_policy_override_cannot_reopen_closed_path() -> None:
    result = build_dcs_result(
        decision_mode="lockdown",
        p0_passed=True,
        poav_total=0.2,
        poav_threshold=0.7,
        policy={
            "dcs": {"decision_modes": {"lockdown": {"close_on": [], "soft_close_on": []}}},
        },
    )

    assert result["state"] == "closed"
    assert result["decision"] == "halt"
    assert "poav" in result["triggered"]["closed"]


def test_constraint_stack_ignores_non_list_constraint_injection() -> None:
    lines = constraint_mod._merge_constraints(
        {
            "constraints": {"inject": "DROP ALL"},
            "assumptions": "pretend list",
        }
    )

    assert lines == ["Context constraints:", "", "Assumptions:"]


def test_constraint_stack_doc_uses_resolved_lockdown_policy_not_user_supplied_actions() -> None:
    doc = constraint_mod.build_constraints_doc(
        {
            "constraints": ["stay bounded"],
            "assumptions": ["operator review required"],
            "allowed_actions": ["delete_everything"],
            "time_island": {"kairos": {"decision_mode": "lockdown"}},
        },
        "Template",
        mercy_objective={
            "decision_mode": "lockdown",
            "score": 0.1,
            "weights": {"care": 1.0},
            "signals": {"care": 0.1},
        },
    )

    assert "delete_everything" not in doc
    assert "verify" in doc
    assert "cite" in doc
    assert "inquire" in doc
