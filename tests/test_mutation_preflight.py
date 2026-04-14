from __future__ import annotations

from tonesoul.mutation_preflight import build_mutation_preflight


def _make_import_posture(
    *,
    compaction_obligation: str = "should_consider",
    compaction_closeout_status: str = "",
    subject_refresh_obligation: str = "must_not_promote",
    launch_tier: str = "collaborator_beta",
    public_launch_ready: bool = False,
) -> dict:
    return {
        "surfaces": {
            "claims": {
                "note": "Claims are short-lived coordination signals with TTL.",
            },
            "checkpoints": {
                "note": "Checkpoint next_action is resumability guidance only.",
            },
            "compactions": {
                "receiver_obligation": compaction_obligation,
                "closeout_status": compaction_closeout_status,
                "note": "Compaction keeps resumability bounded and non-canonical.",
            },
            "subject_refresh": {
                "receiver_obligation": subject_refresh_obligation,
                "note": "Subject refresh must not silently promote higher-authority identity.",
            },
            "launch_claims": {
                "launch_claim_posture": {
                    "current_tier": launch_tier,
                    "public_launch_ready": public_launch_ready,
                    "receiver_rule": "Use collaborator-beta wording only for guided file-backed workflow.",
                }
            },
        }
    }


def _make_canonical_center(*, short_board_present: bool = True) -> dict:
    return {
        "current_short_board": {
            "present": short_board_present,
            "items": ["Phase 746: mutation preflight"],
        }
    }


def _make_publish_push_preflight(classification: str = "review_before_push") -> dict:
    return {
        "classification": classification,
        "receiver_note": "Use repo-state, closeout, and launch posture before outward-facing side effects.",
    }


def _make_task_board_preflight(classification: str = "docs_plans_first") -> dict:
    if classification == "human_review":
        receiver_note = "Do not mutate task.md yet. The current short board is not visible, so the repo cannot confirm that this change belongs in the ratified board."
        task_md_write_allowed = False
    elif classification == "task_md_allowed":
        receiver_note = "This looks like ratified short-board follow-through."
        task_md_write_allowed = True
    else:
        receiver_note = "Park outside ideas in docs/plans until they are explicitly ratified."
        task_md_write_allowed = False
    return {
        "classification": classification,
        "task_md_write_allowed": task_md_write_allowed,
        "receiver_note": receiver_note,
    }


def test_build_mutation_preflight_blocks_shared_edit_when_readiness_is_blocked() -> None:
    payload = build_mutation_preflight(
        readiness={"status": "blocked", "claim_conflict_count": 0},
        task_track_hint={"suggested_track": "system_track", "claim_recommendation": "required"},
        deliberation_mode_hint={"suggested_mode": "do_not_deliberate"},
        import_posture=_make_import_posture(compaction_closeout_status="blocked"),
        canonical_center=_make_canonical_center(),
        publish_push_preflight=_make_publish_push_preflight("blocked"),
        task_board_preflight=_make_task_board_preflight("human_review"),
    )

    by_name = {item["name"]: item for item in payload["decision_points"]}
    assert by_name["shared_code_edit"]["posture"] == "blocked"
    assert by_name["shared_code_edit"]["control_type"] == "existing_runtime_hook"
    assert by_name["compaction_write"]["posture"] == "honest_closeout_required"
    assert by_name["task_board_update"]["control_type"] == "human_gated"
    assert by_name["task_board_update"]["posture"] == "human_review_required"
    assert payload["current_context"]["deliberation_mode"] == "do_not_deliberate"
    assert by_name["publish_push"]["posture"] == "blocked"
    assert payload["next_followup"]["target"] == "shared_code_edit.path_overlap_preflight"
    assert payload["next_followup"]["classification"] == "existing_runtime_hook"


def test_build_mutation_preflight_prefers_claim_before_shared_edits() -> None:
    payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 0},
        task_track_hint={"suggested_track": "feature_track", "claim_recommendation": "required"},
        deliberation_mode_hint={"suggested_mode": "standard_council"},
        import_posture=_make_import_posture(),
        canonical_center=_make_canonical_center(),
        publish_push_preflight=_make_publish_push_preflight("review_before_push"),
        task_board_preflight=_make_task_board_preflight("docs_plans_first"),
    )

    by_name = {item["name"]: item for item in payload["decision_points"]}
    assert by_name["shared_code_edit"]["posture"] == "claim_before_shared_edits"
    assert by_name["claim_write"]["control_type"] == "existing_runtime_hook"
    assert "run_shared_edit_preflight.py" in by_name["shared_code_edit"]["current_guard"]
    assert by_name["subject_refresh_write"]["posture"] == "must_not_promote"
    assert by_name["launch_claim_language"]["posture"] == "bounded_collaborator_beta_only"
    assert by_name["publish_push"]["posture"] == "review_before_push"
    assert by_name["task_board_update"]["posture"] == "docs_plans_first"
    assert "run_task_board_preflight.py" in by_name["task_board_update"]["current_guard"]
    assert "task_board=docs_plans_first" in payload["summary_text"]
    assert payload["next_followup"]["target"] == "shared_code_edit.path_overlap_preflight"
    assert "run_shared_edit_preflight.py" in payload["next_followup"]["command"]


def test_build_mutation_preflight_marks_task_board_as_human_gated_when_short_board_missing() -> (
    None
):
    payload = build_mutation_preflight(
        readiness={"status": "needs_clarification", "claim_conflict_count": 1},
        task_track_hint={"suggested_track": "quick_change", "claim_recommendation": "optional"},
        deliberation_mode_hint={"suggested_mode": "lightweight_review"},
        import_posture=_make_import_posture(compaction_obligation="must_not_promote"),
        canonical_center=_make_canonical_center(short_board_present=False),
        publish_push_preflight=_make_publish_push_preflight("review_before_push"),
        task_board_preflight=_make_task_board_preflight("human_review"),
    )

    by_name = {item["name"]: item for item in payload["decision_points"]}
    assert by_name["shared_code_edit"]["posture"] == "coordinate_before_shared_edits"
    assert by_name["compaction_write"]["posture"] == "review_only_handoff"
    assert by_name["task_board_update"]["posture"] == "human_review_required"
    assert "not visible" in by_name["task_board_update"]["receiver_note"]
    assert payload["receiver_rule"].startswith("Readiness and live coordination gate")
    assert payload["next_followup"]["target"] == "shared_code_edit.path_overlap_preflight"


def test_build_mutation_preflight_prefers_publish_push_when_shared_edit_is_bounded() -> None:
    payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 0},
        task_track_hint={"suggested_track": "quick_change", "claim_recommendation": "not_required"},
        deliberation_mode_hint={"suggested_mode": "lightweight_review"},
        import_posture=_make_import_posture(),
        canonical_center=_make_canonical_center(),
        publish_push_preflight=_make_publish_push_preflight("review_before_push"),
        task_board_preflight=_make_task_board_preflight("docs_plans_first"),
    )

    assert payload["next_followup"]["target"] == "publish_push.posture_preflight"
    assert "run_publish_push_preflight.py" in payload["next_followup"]["command"]
