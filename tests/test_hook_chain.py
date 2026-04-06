from __future__ import annotations

from tonesoul.hook_chain import build_hook_chain_readout


def test_hook_chain_exposes_current_bounded_preflights() -> None:
    payload = build_hook_chain_readout(agent_id="codex")

    assert payload["present"] is True
    assert "shared_edit_path_overlap" in payload["summary_text"]
    assert "classify posture" in payload["receiver_rule"]
    assert payload["selection_rule"].startswith("Prefer mutation_preflight.next_followup")
    stages = payload["stages"]
    assert [stage["name"] for stage in stages] == [
        "shared_edit_path_overlap",
        "publish_push_posture",
        "task_board_parking",
    ]
    assert stages[0]["command"] == (
        "python scripts/run_shared_edit_preflight.py --agent codex --path <repo-path>"
    )
    assert stages[1]["outcomes"] == ["clear", "review_before_push", "blocked"]
    assert stages[2]["outcomes"] == [
        "task_md_allowed",
        "docs_plans_first",
        "parking_clear",
        "human_review",
    ]
    assert stages[0]["activation_signals"][0].startswith("shared paths may overlap")
    assert stages[1]["scope_limit"].startswith("release and launch-posture review")
    assert payload["current_recommendation"]["present"] is False
    assert [item["status"] for item in payload["hooks"]] == ["available", "available", "available"]


def test_hook_chain_can_mark_current_recommendation() -> None:
    payload = build_hook_chain_readout(
        agent_id="codex",
        recommended_target="publish_push.posture_preflight",
        recommended_reason="Outward publish is the current bounded friction.",
    )

    assert payload["current_recommendation"]["present"] is True
    assert payload["current_recommendation"]["name"] == "publish_push_posture"
    assert payload["current_recommendation"]["target"] == "publish_push.posture_preflight"
    assert "recommended=publish_push_posture" in payload["summary_text"]
    recommended = [item for item in payload["hooks"] if item["status"] == "recommended_now"]
    assert len(recommended) == 1
    assert recommended[0]["name"] == "publish_push_posture"
    stage = next(item for item in payload["stages"] if item["name"] == "publish_push_posture")
    assert stage["status"] == "recommended_now"
    assert stage["why_now"] == "Outward publish is the current bounded friction."
