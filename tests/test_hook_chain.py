from __future__ import annotations

from tonesoul.hook_chain import build_hook_chain_readout


def test_hook_chain_exposes_current_bounded_preflights() -> None:
    payload = build_hook_chain_readout(agent_id="codex")

    assert payload["present"] is True
    assert "shared_edit_path_overlap" in payload["summary_text"]
    assert "classify posture" in payload["receiver_rule"]
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
