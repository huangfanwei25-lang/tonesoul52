"""Bounded operator-facing preflight chain readout."""

from __future__ import annotations

from typing import Any


def _normalize_recommended_stage(target: str) -> str:
    normalized = str(target or "").strip()
    stage_map = {
        "shared_code_edit.path_overlap_preflight": "shared_edit_path_overlap",
        "publish_push.posture_preflight": "publish_push_posture",
        "task_board.parking_preflight": "task_board_parking",
    }
    return stage_map.get(normalized, "")


def build_hook_chain_readout(
    *,
    agent_id: str,
    recommended_target: str = "",
    recommended_reason: str = "",
) -> dict[str, Any]:
    """Return the current bounded preflight chain for collaborators."""
    normalized_agent = str(agent_id or "<your-id>").strip() or "<your-id>"
    recommended_stage = _normalize_recommended_stage(recommended_target)
    stages = [
        {
            "name": "shared_edit_path_overlap",
            "target": "shared_code_edit.path_overlap_preflight",
            "trigger_family": "shared_code_mutation",
            "when": "Before editing shared or claim-sensitive repo paths.",
            "activation_signals": [
                "shared paths may overlap another visible claim",
                "mutation_preflight points to shared_code_edit.path_overlap_preflight",
            ],
            "command": (
                f"python scripts/run_shared_edit_preflight.py --agent {normalized_agent} "
                "--path <repo-path>"
            ),
            "outcomes": ["clear", "coordinate", "claim_first", "blocked"],
            "scope_limit": "path-overlap and claim-pressure only; not a general permission system",
            "receiver_note": (
                "Use this first when the next step mutates code or docs that another agent may also touch."
            ),
        },
        {
            "name": "publish_push_posture",
            "target": "publish_push.posture_preflight",
            "trigger_family": "outward_side_effect",
            "when": "Before git push, deployment, or outward-facing publish actions.",
            "activation_signals": [
                "the next step pushes, deploys, or publishes outward-facing changes",
                "mutation_preflight points to publish_push.posture_preflight",
            ],
            "command": (f"python scripts/run_publish_push_preflight.py --agent {normalized_agent}"),
            "outcomes": ["clear", "review_before_push", "blocked"],
            "scope_limit": "release and launch-posture review only; not a general editing permission system",
            "receiver_note": (
                "This is a release/posture check, not a general editing permission system."
            ),
        },
        {
            "name": "task_board_parking",
            "target": "task_board.parking_preflight",
            "trigger_family": "task_board_mutation",
            "when": "Before writing a new idea, roadmap, or outside theory into task.md.",
            "activation_signals": [
                "the next step writes a new idea or unratified roadmap into task.md",
                "mutation_preflight points to task_board.parking_preflight",
            ],
            "command": (
                f"python scripts/run_task_board_preflight.py --agent {normalized_agent} "
                "--proposal-kind external_idea --target-path task.md"
            ),
            "outcomes": ["task_md_allowed", "docs_plans_first", "parking_clear", "human_review"],
            "scope_limit": "task-board parking discipline only; not a planning ratification system",
            "receiver_note": (
                "The short board stays ratified-only; unratified ideas belong in docs/plans first."
            ),
        },
    ]
    hooks = []
    for stage in stages:
        status = "recommended_now" if stage["name"] == recommended_stage else "available"
        stage["status"] = status
        if status == "recommended_now" and recommended_reason:
            stage["why_now"] = recommended_reason
        hooks.append(
            {
                "name": stage["name"],
                "target": stage["target"],
                "trigger_family": stage["trigger_family"],
                "status": status,
            }
        )
    recommendation_present = bool(recommended_stage and recommended_target)
    return {
        "present": True,
        "summary_text": (
            "hook_chain=shared_edit_path_overlap -> publish_push_posture -> task_board_parking"
            + (f" recommended={recommended_stage}" if recommendation_present else "")
        ),
        "receiver_rule": (
            "Run the narrowest preflight that matches the next side effect. These checks classify posture and parking discipline; they do not create sovereign permissions."
        ),
        "selection_rule": (
            "Prefer mutation_preflight.next_followup when it is visible; otherwise choose the narrowest hook that matches the next side effect."
        ),
        "operator_note": (
            "Use shared-edit overlap for path mutation, publish/push posture for outward actions, and task-board parking before promoting new ideas into task.md."
        ),
        "current_recommendation": {
            "present": recommendation_present,
            "name": recommended_stage or "",
            "target": str(recommended_target or "").strip(),
            "reason": str(recommended_reason or "").strip(),
        },
        "hooks": hooks,
        "stages": stages,
    }
