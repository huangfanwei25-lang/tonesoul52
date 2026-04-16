"""Bounded task-board parking discipline helpers."""

from __future__ import annotations

from typing import Any

_TASK_MD_ALLOWED_KINDS = {
    "ratified_followthrough",
    "execution_status",
    "accepted_short_board_rotation",
}
_DOCS_PLANS_FIRST_KINDS = {
    "external_idea",
    "speculative_roadmap",
    "theory_import",
    "ecosystem_borrowing",
    "unratified_program",
    "unspecified",
}


def build_task_board_preflight(
    *,
    readiness: dict[str, Any],
    canonical_center: dict[str, Any],
    task_track_hint: dict[str, Any],
    proposal_kind: str = "unspecified",
    target_path: str = "task.md",
) -> dict[str, Any]:
    """Classify whether a new idea belongs in task.md or docs/plans first."""

    normalized_kind = str(proposal_kind or "unspecified").strip() or "unspecified"
    normalized_target = str(target_path or "task.md").replace("\\", "/").strip() or "task.md"

    readiness_status = str(readiness.get("status", "unknown") or "unknown")
    current_short_board = canonical_center.get("current_short_board") or {}
    short_board_visible = bool(current_short_board.get("present"))
    short_board_summary = str(current_short_board.get("summary_text", "") or "").strip()
    suggested_track = str(task_track_hint.get("suggested_track", "unclassified") or "unclassified")

    reasons: list[str] = []

    if normalized_target == "task.md":
        if not short_board_visible:
            classification = "human_review"
            reasons.append("current_short_board_not_visible")
        elif readiness_status == "blocked":
            classification = "human_review"
            reasons.append("readiness_blocked")
        elif normalized_kind in _TASK_MD_ALLOWED_KINDS:
            classification = "task_md_allowed"
            reasons.append("proposal_is_ratified_followthrough")
        else:
            classification = "docs_plans_first"
            reasons.append("proposal_not_ratified_for_task_md")
    elif normalized_target.startswith("docs/plans/"):
        if normalized_kind in _TASK_MD_ALLOWED_KINDS:
            classification = "human_review"
            reasons.append("ratified_followthrough_target_mismatch")
        else:
            classification = "parking_clear"
            reasons.append("docs_plans_is_correct_parking_lane")
    else:
        classification = "human_review"
        reasons.append("target_is_not_task_md_or_docs_plans")

    if (
        normalized_kind in _DOCS_PLANS_FIRST_KINDS
        and "proposal_not_ratified_for_task_md" not in reasons
    ):
        reasons.append("proposal_kind_defaults_to_docs_plans")

    if classification == "task_md_allowed":
        suggested_destination = "task.md"
        task_md_write_allowed = True
        promotion_posture = "ratified_followthrough_only"
        receiver_note = "This looks like ratified short-board follow-through. Keep the task.md change narrow and aligned with the visible short board."
    elif classification == "parking_clear":
        suggested_destination = normalized_target
        task_md_write_allowed = False
        promotion_posture = "parking_only"
        receiver_note = "This idea belongs in docs/plans for now. Keep it out of task.md until a human or accepted program explicitly ratifies it."
    elif classification == "docs_plans_first":
        suggested_destination = "docs/plans/"
        task_md_write_allowed = False
        promotion_posture = "parking_only"
        receiver_note = "This looks like a new idea or unratified follow-up. Route it to docs/plans first instead of competing with the active short board in task.md."
    else:
        suggested_destination = "human_review"
        task_md_write_allowed = False
        promotion_posture = "human_review_required"
        if "current_short_board_not_visible" in reasons:
            receiver_note = "Do not mutate task.md yet. The current short board is not visible, so the repo cannot confirm that this change belongs in the ratified board."
        elif "readiness_blocked" in reasons:
            receiver_note = "Do not mutate task.md yet. Readiness is blocked, so even a plausible board update needs human review before it changes the active execution lane."
        else:
            receiver_note = "Do not mutate task.md yet. The current short board or readiness state is not clear enough to decide automatically."

    return {
        "present": True,
        "classification": classification,
        "proposal_kind": normalized_kind,
        "target_path": normalized_target,
        "suggested_destination": suggested_destination,
        "routing_outcome": classification,
        "task_md_write_allowed": task_md_write_allowed,
        "promotion_posture": promotion_posture,
        "readiness_status": readiness_status,
        "task_track": suggested_track,
        "short_board_visible": short_board_visible,
        "current_short_board": short_board_summary,
        "reasons": reasons,
        "summary_text": (
            f"task_board={classification} write_task_md={'yes' if task_md_write_allowed else 'no'} "
            f"promotion={promotion_posture} proposal={normalized_kind} target={normalized_target} track={suggested_track}"
        ),
        "receiver_rule": (
            "task.md only carries accepted programs, active short boards, and ratified follow-through. New ideas belong in docs/plans until explicitly promoted."
        ),
        "receiver_note": receiver_note,
        "recommended_command": (
            "python scripts/run_task_board_preflight.py --agent <your-id> "
            "--proposal-kind <kind> --target-path <path>"
        ),
        "non_authority_rule": (
            "Task-board preflight is a parking discipline helper. It does not ratify scope, override humans, or promote external ideas into the active short board."
        ),
    }
