"""Bounded shared-edit path overlap preflight helpers."""

from __future__ import annotations

from typing import Any


def _normalize_repo_path(value: object) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def _path_key(value: object) -> str:
    return _normalize_repo_path(value).casefold()


def _paths_overlap(left: object, right: object) -> bool:
    left_key = _path_key(left)
    right_key = _path_key(right)
    if not left_key or not right_key:
        return False
    return (
        left_key == right_key
        or left_key.startswith(f"{right_key}/")
        or right_key.startswith(f"{left_key}/")
    )


def _clean_paths(values: list[object] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        text = _normalize_repo_path(value)
        if text and text not in result:
            result.append(text)
    return result


def _claim_overlap_records(
    *,
    agent_id: str,
    candidate_paths: list[str],
    claims: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    self_records: list[dict[str, Any]] = []
    other_records: list[dict[str, Any]] = []
    for claim in claims:
        claim_paths = _clean_paths(list(claim.get("paths") or []))
        if not claim_paths:
            continue
        overlapping_paths = [
            candidate_path
            for candidate_path in candidate_paths
            if any(_paths_overlap(candidate_path, claim_path) for claim_path in claim_paths)
        ]
        if not overlapping_paths:
            continue
        record = {
            "task_id": str(claim.get("task_id", "")),
            "agent": str(claim.get("agent", "")),
            "summary": str(claim.get("summary", "")),
            "claim_paths": claim_paths,
            "overlap_paths": overlapping_paths,
            "ownership": "self" if str(claim.get("agent", "")).strip() == agent_id else "other",
        }
        if record["ownership"] == "self":
            self_records.append(record)
        else:
            other_records.append(record)
    return self_records, other_records


def _candidate_paths_covered(*, candidate_paths: list[str], records: list[dict[str, Any]]) -> bool:
    for candidate_path in candidate_paths:
        if not any(candidate_path in list(record.get("overlap_paths") or []) for record in records):
            return False
    return True


def _candidate_path_gaps(*, candidate_paths: list[str], records: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    for candidate_path in candidate_paths:
        covered = any(
            candidate_path in list(record.get("overlap_paths") or []) for record in records
        )
        if not covered and candidate_path not in gaps:
            gaps.append(candidate_path)
    return gaps


def _flatten_overlap_paths(records: list[dict[str, Any]]) -> list[str]:
    flattened: list[str] = []
    for record in records:
        for path in list(record.get("overlap_paths") or []):
            if path not in flattened:
                flattened.append(path)
    return flattened


def _claim_command(agent_id: str, candidate_paths: list[str]) -> str:
    path_args = " ".join(f'--path "{path}"' for path in candidate_paths)
    return (
        f"python scripts/run_task_claim.py claim <task_id> --agent {agent_id} "
        f'--summary "..." {path_args}'
    ).strip()


def _build_working_style_consumer(playbook: dict[str, Any] | None) -> dict[str, Any]:
    playbook = dict(playbook or {})
    if not playbook.get("present"):
        return {
            "present": False,
            "summary_text": "",
            "selected_habits": [],
            "application_rule": "",
            "non_promotion_rule": "",
        }

    selected_habits: list[str] = []
    for item in list(playbook.get("checklist") or [])[:2]:
        text = str(item or "").strip()
        if text:
            selected_habits.append(text)

    summary_text = str(playbook.get("summary_text", "")).strip()
    if not summary_text and selected_habits:
        summary_text = " | ".join(selected_habits)

    application_rule = str(playbook.get("application_rule", "")).strip()
    if not application_rule:
        application_rule = (
            "Apply the visible working-style playbook only as bounded workflow guidance."
        )

    non_promotion_rule = str(playbook.get("non_promotion_rule", "")).strip()
    if not non_promotion_rule:
        non_promotion_rule = "Do not promote the visible working-style playbook into vows, canonical rules, or durable identity."

    return {
        "present": True,
        "summary_text": summary_text,
        "selected_habits": selected_habits,
        "application_rule": application_rule,
        "non_promotion_rule": non_promotion_rule,
    }


def build_shared_edit_preflight(
    *,
    agent_id: str,
    candidate_paths: list[object] | None,
    readiness: dict[str, Any],
    claims: list[dict[str, Any]],
    task_track_hint: dict[str, Any],
    mutation_preflight: dict[str, Any],
    working_style_playbook: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bounded shared-edit preflight answer from visible claims and paths."""
    normalized_candidate_paths = _clean_paths(list(candidate_paths or []))
    readiness_status = str(readiness.get("status", "unknown") or "unknown")
    claim_recommendation = str(task_track_hint.get("claim_recommendation", "unknown") or "unknown")
    task_track = str(task_track_hint.get("suggested_track", "unclassified") or "unclassified")
    mutation_summary = str(mutation_preflight.get("summary_text", "") or "").strip()
    working_style_consumer = _build_working_style_consumer(working_style_playbook)

    self_records, other_records = _claim_overlap_records(
        agent_id=agent_id,
        candidate_paths=normalized_candidate_paths,
        claims=list(claims or []),
    )
    self_claim_covers_all = _candidate_paths_covered(
        candidate_paths=normalized_candidate_paths,
        records=self_records,
    )
    raw_claim_gap_paths = _candidate_path_gaps(
        candidate_paths=normalized_candidate_paths,
        records=self_records,
    )
    claim_gap_paths = raw_claim_gap_paths if claim_recommendation == "required" else []
    other_overlap_paths = _flatten_overlap_paths(other_records)
    decision_pressures = {
        "blocked_readiness": readiness_status == "blocked",
        "other_agent_overlap": bool(other_records),
        "missing_self_claim_coverage": (
            claim_recommendation == "required" and bool(claim_gap_paths)
        ),
    }

    if not normalized_candidate_paths:
        decision = "insufficient_input"
        decision_basis = "missing_candidate_paths"
        receiver_rule = (
            "Pass at least one repo-relative path before asking for shared-edit overlap guidance."
        )
        recommended_command = ""
    elif readiness_status == "blocked":
        decision = "blocked"
        decision_basis = "blocked_readiness"
        receiver_rule = "Readiness is blocked, so do not mutate shared paths until the blocking condition is cleared."
        recommended_command = ""
    elif other_records:
        decision = "coordinate"
        decision_basis = "other_agent_overlap"
        receiver_rule = "Visible claim/path overlap with another agent requires coordination before any shared edit."
        recommended_command = "python scripts/run_task_claim.py list"
    elif claim_recommendation == "required" and not self_claim_covers_all:
        decision = "claim_first"
        decision_basis = "missing_self_claim_coverage"
        receiver_rule = "This task track expects a claim before shared edits; no self-owned claim covers all candidate paths yet."
        recommended_command = _claim_command(agent_id, normalized_candidate_paths)
    else:
        decision = "clear"
        decision_basis = "self_claim_covers_all" if self_claim_covers_all else "no_visible_conflict"
        receiver_rule = "No visible conflicting claim overlaps are present for these candidate paths. Continue with bounded edits and keep the claim discipline visible."
        recommended_command = (
            "python scripts/run_task_claim.py list"
            if self_records
            else _claim_command(agent_id, normalized_candidate_paths)
        )

    overlap_records = self_records + other_records
    return {
        "present": bool(normalized_candidate_paths),
        "decision": decision,
        "normalized_candidate_paths": normalized_candidate_paths,
        "task_track": task_track,
        "claim_recommendation": claim_recommendation,
        "readiness_status": readiness_status,
        "decision_basis": decision_basis,
        "decision_pressures": decision_pressures,
        "self_claim_covers_all": self_claim_covers_all,
        "claim_gap_paths": claim_gap_paths,
        "other_overlap_paths": other_overlap_paths,
        "overlap_count": len(overlap_records),
        "overlaps": overlap_records,
        "receiver_rule": receiver_rule,
        "recommended_command": recommended_command,
        "working_style_consumer": working_style_consumer,
        "summary_text": (
            f"shared_edit_preflight={decision} "
            f"basis={decision_basis} "
            f"candidates={len(normalized_candidate_paths)} "
            f"other={len(other_overlap_paths)} "
            f"gaps={len(claim_gap_paths)} "
            f"self_cover={'yes' if self_claim_covers_all else 'no'} "
            f"style={'yes' if working_style_consumer.get('present') else 'no'}"
        ),
        "context": {
            "mutation_summary": mutation_summary,
            "self_overlap_count": len(self_records),
            "other_overlap_count": len(other_records),
        },
    }
