from __future__ import annotations

from tonesoul.hook_chain import _normalize_recommended_stage, build_hook_chain_readout


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


# ── _normalize_recommended_stage ──────────────────────────────────────────────


def test_normalize_recommended_stage_maps_all_known_targets() -> None:
    assert (
        _normalize_recommended_stage("shared_code_edit.path_overlap_preflight")
        == "shared_edit_path_overlap"
    )
    assert _normalize_recommended_stage("publish_push.posture_preflight") == "publish_push_posture"
    assert _normalize_recommended_stage("task_board.parking_preflight") == "task_board_parking"


def test_normalize_recommended_stage_returns_empty_for_unknown() -> None:
    assert _normalize_recommended_stage("unknown.target") == ""
    assert _normalize_recommended_stage("") == ""
    assert _normalize_recommended_stage("   ") == ""


def test_normalize_recommended_stage_strips_whitespace() -> None:
    assert (
        _normalize_recommended_stage("  shared_code_edit.path_overlap_preflight  ")
        == "shared_edit_path_overlap"
    )


# ── build_hook_chain_readout extra branches ───────────────────────────────────


def test_hook_chain_empty_agent_id_falls_back_to_placeholder() -> None:
    payload = build_hook_chain_readout(agent_id="")
    stages = payload["stages"]
    assert "<your-id>" in stages[0]["command"]
    assert "<your-id>" in stages[1]["command"]


def test_hook_chain_task_board_recommendation() -> None:
    payload = build_hook_chain_readout(
        agent_id="test-agent",
        recommended_target="task_board.parking_preflight",
        recommended_reason="New idea needs parking.",
    )
    assert payload["current_recommendation"]["present"] is True
    assert payload["current_recommendation"]["name"] == "task_board_parking"
    assert "recommended=task_board_parking" in payload["summary_text"]
    stage = next(s for s in payload["stages"] if s["name"] == "task_board_parking")
    assert stage["status"] == "recommended_now"
    assert stage["why_now"] == "New idea needs parking."
    recommended_hooks = [h for h in payload["hooks"] if h["status"] == "recommended_now"]
    assert len(recommended_hooks) == 1
    assert recommended_hooks[0]["name"] == "task_board_parking"


def test_hook_chain_shared_edit_recommendation() -> None:
    payload = build_hook_chain_readout(
        agent_id="test-agent",
        recommended_target="shared_code_edit.path_overlap_preflight",
        recommended_reason="Shared path overlap detected.",
    )
    assert payload["current_recommendation"]["name"] == "shared_edit_path_overlap"
    assert "recommended=shared_edit_path_overlap" in payload["summary_text"]
    other_hooks = [h for h in payload["hooks"] if h["name"] != "shared_edit_path_overlap"]
    assert all(h["status"] == "available" for h in other_hooks)


def test_hook_chain_unknown_recommended_target_leaves_all_available() -> None:
    payload = build_hook_chain_readout(
        agent_id="agent",
        recommended_target="nonexistent.target",
        recommended_reason="some reason",
    )
    assert payload["current_recommendation"]["present"] is False
    assert all(h["status"] == "available" for h in payload["hooks"])
