"""Bounded operator-facing preflight chain readout."""

from __future__ import annotations

from typing import Any


def build_hook_chain_readout(*, agent_id: str) -> dict[str, Any]:
    """Return the current bounded preflight chain for collaborators."""
    normalized_agent = str(agent_id or "<your-id>").strip() or "<your-id>"
    stages = [
        {
            "name": "shared_edit_path_overlap",
            "when": "Before editing shared or claim-sensitive repo paths.",
            "command": (
                f"python scripts/run_shared_edit_preflight.py --agent {normalized_agent} "
                "--path <repo-path>"
            ),
            "outcomes": ["clear", "coordinate", "claim_first", "blocked"],
            "receiver_note": (
                "Use this first when the next step mutates code or docs that another agent may also touch."
            ),
        },
        {
            "name": "publish_push_posture",
            "when": "Before git push, deployment, or outward-facing publish actions.",
            "command": (
                f"python scripts/run_publish_push_preflight.py --agent {normalized_agent}"
            ),
            "outcomes": ["clear", "review_before_push", "blocked"],
            "receiver_note": (
                "This is a release/posture check, not a general editing permission system."
            ),
        },
        {
            "name": "task_board_parking",
            "when": "Before writing a new idea, roadmap, or outside theory into task.md.",
            "command": (
                f"python scripts/run_task_board_preflight.py --agent {normalized_agent} "
                "--proposal-kind external_idea --target-path task.md"
            ),
            "outcomes": ["task_md_allowed", "docs_plans_first", "parking_clear", "human_review"],
            "receiver_note": (
                "The short board stays ratified-only; unratified ideas belong in docs/plans first."
            ),
        },
    ]
    return {
        "present": True,
        "summary_text": (
            "hook_chain=shared_edit_path_overlap -> publish_push_posture -> task_board_parking"
        ),
        "receiver_rule": (
            "Run the narrowest preflight that matches the next side effect. These checks classify posture and parking discipline; they do not create sovereign permissions."
        ),
        "operator_note": (
            "Use shared-edit overlap for path mutation, publish/push posture for outward actions, and task-board parking before promoting new ideas into task.md."
        ),
        "stages": stages,
    }
