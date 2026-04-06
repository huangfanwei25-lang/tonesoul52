from __future__ import annotations

from tonesoul.task_board_preflight import build_task_board_preflight


def _make_canonical_center(*, short_board_visible: bool = True) -> dict:
    return {
        "current_short_board": {
            "present": short_board_visible,
            "summary_text": "Phase 758: task-board parking discipline",
        }
    }


def test_task_board_preflight_defaults_to_docs_plans_for_external_ideas() -> None:
    payload = build_task_board_preflight(
        readiness={"status": "pass"},
        canonical_center=_make_canonical_center(),
        task_track_hint={"suggested_track": "feature_track"},
        proposal_kind="external_idea",
        target_path="task.md",
    )

    assert payload["classification"] == "docs_plans_first"
    assert payload["routing_outcome"] == "docs_plans_first"
    assert payload["task_md_write_allowed"] is False
    assert payload["promotion_posture"] == "parking_only"
    assert payload["suggested_destination"] == "docs/plans/"
    assert "proposal_not_ratified_for_task_md" in payload["reasons"]
    assert "write_task_md=no" in payload["summary_text"]


def test_task_board_preflight_allows_ratified_followthrough_into_task_md() -> None:
    payload = build_task_board_preflight(
        readiness={"status": "pass"},
        canonical_center=_make_canonical_center(),
        task_track_hint={"suggested_track": "feature_track"},
        proposal_kind="ratified_followthrough",
        target_path="task.md",
    )

    assert payload["classification"] == "task_md_allowed"
    assert payload["task_md_write_allowed"] is True
    assert payload["promotion_posture"] == "ratified_followthrough_only"
    assert payload["suggested_destination"] == "task.md"
    assert "proposal_is_ratified_followthrough" in payload["reasons"]


def test_task_board_preflight_requests_human_review_when_short_board_missing() -> None:
    payload = build_task_board_preflight(
        readiness={"status": "pass"},
        canonical_center=_make_canonical_center(short_board_visible=False),
        task_track_hint={"suggested_track": "feature_track"},
        proposal_kind="execution_status",
        target_path="task.md",
    )

    assert payload["classification"] == "human_review"
    assert payload["task_md_write_allowed"] is False
    assert payload["promotion_posture"] == "human_review_required"
    assert "current_short_board_not_visible" in payload["reasons"]


def test_task_board_preflight_can_clear_docs_plans_target() -> None:
    payload = build_task_board_preflight(
        readiness={"status": "pass"},
        canonical_center=_make_canonical_center(),
        task_track_hint={"suggested_track": "feature_track"},
        proposal_kind="external_idea",
        target_path="docs/plans/new_note.md",
    )

    assert payload["classification"] == "parking_clear"
    assert payload["task_md_write_allowed"] is False
    assert payload["promotion_posture"] == "parking_only"
    assert payload["suggested_destination"] == "docs/plans/new_note.md"
    assert "docs_plans_is_correct_parking_lane" in payload["reasons"]
