"""Bounded successor-facing repo-state awareness."""

from __future__ import annotations

from typing import Any


def build_repo_state_awareness(
    *,
    project_memory_summary: dict[str, Any],
    delta_feed: dict[str, Any],
) -> dict[str, Any]:
    """Explain repo movement without turning git state into authority."""

    repo_progress = project_memory_summary.get("repo_progress") or {}
    repo_change = delta_feed.get("repo_change") or {}

    repo_head = str(repo_progress.get("head", "")).strip()
    dirty_count = int(repo_progress.get("dirty_count", 0) or 0)
    first_observation = bool(delta_feed.get("first_observation", False))
    repo_changed = bool(repo_change.get("changed", False))
    coordination_update_count = sum(
        len(delta_feed.get(key) or [])
        for key in (
            "new_compactions",
            "new_subject_snapshots",
            "new_checkpoints",
            "new_traces",
            "new_claims",
            "released_claim_ids",
        )
    )

    classification = "steady"
    receiver_note = (
        "Repo state is unchanged relative to the current observer baseline. "
        "This remains descriptive only; canonical planning truth still comes from the accepted center."
    )
    action_hint = "Use live coordination and the current short board as normal."
    alert_text = ""

    if first_observation:
        classification = "baseline_unset"
        receiver_note = (
            "No observer baseline exists yet. Current git state is visible, but a quiet delta does not imply "
            "that nothing changed before this session-start snapshot."
        )
        action_hint = "Ack after review to establish a baseline before treating later quiet delta as stability."
        alert_text = "No observer baseline yet; do not read missing delta as 'no repo change'."
    elif repo_changed and coordination_update_count == 0:
        classification = "repo_changed_without_coordination"
        receiver_note = (
            "Git state moved without fresh coordination surfaces. Re-read touched files before assuming the "
            "workstream stayed where the last handoff left it."
        )
        action_hint = "Review the current repo state or run path preflight before shared edits."
        alert_text = (
            "Repo state changed without fresh coordination updates; do not equate 'no new handoff' with "
            "'no work moved'."
        )
    elif dirty_count > 0 and coordination_update_count == 0:
        classification = "repo_dirty_without_coordination"
        receiver_note = (
            "The repo is currently dirty even though coordination delta is quiet. "
            "A calm handoff surface does not mean the working tree is unchanged."
        )
        action_hint = "Inspect current changes before assuming the repo matches the last acknowledged baseline."
        alert_text = "Repo is dirty while coordination delta is quiet; no delta != no repo changes."
    elif repo_changed:
        classification = "repo_changed_with_coordination"
        receiver_note = (
            "Git state and coordination surfaces both moved. Prefer current readiness, claims, and bounded handoff "
            "before inferring continuity from older summaries."
        )
        action_hint = "Review current coordination surfaces, then re-read the affected files."
    elif coordination_update_count > 0:
        classification = "coordination_updates_without_repo_change"
        receiver_note = (
            "Coordination surfaces moved without a repo-head/dirty delta. Review the new handoff state, but do not "
            "treat that as proof that canonical planning changed."
        )
        action_hint = "Apply new coordination updates as bounded context, not as new parent truth."

    misread_risk = classification in {
        "baseline_unset",
        "repo_changed_without_coordination",
        "repo_dirty_without_coordination",
    }

    return {
        "present": True,
        "classification": classification,
        "repo_head": repo_head,
        "dirty_count": dirty_count,
        "repo_change_detected": repo_changed,
        "coordination_update_count": coordination_update_count,
        "misread_risk": misread_risk,
        "summary_text": (
            f"classification={classification} head={repo_head or 'unknown'} dirty={dirty_count} "
            f"repo_changed={repo_changed} coordination_updates={coordination_update_count}"
        ),
        "receiver_note": receiver_note,
        "action_hint": action_hint,
        "alert_text": alert_text,
        "non_authority_rule": (
            "Repo-state awareness is descriptive only. It does not authorize scope, override canonical planning, "
            "or replace readiness/claim checks."
        ),
    }
