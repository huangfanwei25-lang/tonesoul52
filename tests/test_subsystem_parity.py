from __future__ import annotations

from tonesoul.subsystem_parity import (
    _build_next_focus,
    _class_counts,
    _family,
    build_subsystem_parity_readout,
)


def _make_project_memory_summary() -> dict:
    return {
        "evidence_readout_posture": {
            "classification_counts": {
                "tested": 2,
                "runtime_present": 1,
                "descriptive_only": 1,
                "document_backed": 1,
            },
            "lanes": [
                {"lane": "continuity_effectiveness", "classification": "runtime_present"},
            ],
        },
        "launch_claim_posture": {
            "current_tier": "collaborator_beta",
            "public_launch_ready": False,
        },
    }


def _make_import_posture() -> dict:
    return {
        "receiver_rule": "ack is safe, apply is bounded, promote requires explicit justification.",
        "surfaces": {
            "council_dossier": {
                "dossier_interpretation": {"calibration_status": "descriptive_only"}
            },
            "compactions": {
                "receiver_obligation": "must_not_promote",
                "closeout_status": "partial",
            },
        },
    }


def _make_mutation_preflight() -> dict:
    return {
        "summary_text": (
            "shared_code=claim_before_shared_edits "
            "compaction=review_only_handoff publish_push=review_before_push"
        ),
        "next_followup": {
            "target": "shared_code_edit.path_overlap_preflight",
            "classification": "existing_runtime_hook",
        },
    }


def test_build_subsystem_parity_readout_emits_expected_status_mix() -> None:
    payload = build_subsystem_parity_readout(
        project_memory_summary=_make_project_memory_summary(),
        import_posture=_make_import_posture(),
        readiness={"status": "pass"},
        task_track_hint={"suggested_track": "feature_track", "claim_recommendation": "required"},
        working_style_validation={"status": "caution"},
        mutation_preflight=_make_mutation_preflight(),
        canonical_center={"current_short_board": {"present": True}},
    )

    assert payload["present"] is True
    assert payload["counts"] == {
        "baseline": 3,
        "beta_usable": 5,
        "partial": 2,
        "deferred": 1,
    }
    assert payload["next_focus"]["resolved_to"] == "shared_code_edit.path_overlap_preflight"
    assert payload["next_focus"]["source_family"] == "mutation_preflight_hooks"
    assert payload["next_focus"]["focus_pressures"] == [
        "readiness=pass",
        "task_track=feature_track",
        "claim_recommendation=required",
    ]
    assert "shared-edit preflight" in payload["next_focus"]["operator_action"]
    assert payload["summary_text"].startswith("subsystem_parity baseline=3 beta_usable=5")

    by_name = {item["name"]: item for item in payload["families"]}
    assert by_name["session_start_bundle"]["status"] == "baseline"
    assert by_name["packet_hot_state"]["status"] == "beta_usable"
    assert by_name["subject_working_style"]["status"] == "partial"
    assert by_name["external_transport_plugins"]["status"] == "deferred"
    assert by_name["mutation_preflight_hooks"]["status"] == "beta_usable"
    assert by_name["mutation_preflight_hooks"]["next_bounded_move"] == (
        "shared_code_edit.path_overlap_preflight"
    )


# ── _family ──────────────────────────────────────────────────────────────────

def test_family_returns_dict_with_all_required_keys() -> None:
    f = _family(
        "test_family",
        status="baseline",
        current_signal="signal",
        strongest_truth="truth",
        main_gap="gap",
        next_bounded_move="move",
        overclaim_to_avoid="overclaim",
    )
    assert f["name"] == "test_family"
    assert f["status"] == "baseline"
    assert f["current_signal"] == "signal"
    assert f["strongest_truth"] == "truth"
    assert f["main_gap"] == "gap"
    assert f["next_bounded_move"] == "move"
    assert f["overclaim_to_avoid"] == "overclaim"


# ── _class_counts ─────────────────────────────────────────────────────────────

def test_class_counts_tallies_known_statuses() -> None:
    families = [
        {"status": "baseline"},
        {"status": "baseline"},
        {"status": "beta_usable"},
        {"status": "partial"},
        {"status": "deferred"},
    ]
    counts = _class_counts(families)
    assert counts == {"baseline": 2, "beta_usable": 1, "partial": 1, "deferred": 1}


def test_class_counts_ignores_unknown_statuses() -> None:
    families = [{"status": "baseline"}, {"status": "unknown_status"}, {}]
    counts = _class_counts(families)
    assert counts["baseline"] == 1
    assert counts["beta_usable"] == 0
    assert counts["partial"] == 0
    assert counts["deferred"] == 0


def test_class_counts_empty_list_returns_zeros() -> None:
    counts = _class_counts([])
    assert counts == {"baseline": 0, "beta_usable": 0, "partial": 0, "deferred": 0}


# ── _build_next_focus ─────────────────────────────────────────────────────────

def test_build_next_focus_default_target_branch() -> None:
    focus = _build_next_focus(
        next_followup_target="",
        readiness_status="pass",
        task_track="feature_track",
        claim_recommendation="required",
    )
    assert focus["resolved_to"] == "shared_code_edit.path_overlap_preflight"
    assert focus["source_family"] == "mutation_preflight_hooks"
    assert "readiness=pass" in focus["focus_pressures"]


def test_build_next_focus_publish_push_branch() -> None:
    focus = _build_next_focus(
        next_followup_target="publish_push.posture_preflight",
        readiness_status="pass",
        task_track="feature_track",
        claim_recommendation="required",
    )
    assert focus["resolved_to"] == "publish_push.posture_preflight"
    assert "outward_action_review=yes" in focus["focus_pressures"]
    assert "publish/push preflight" in focus["operator_action"]


def test_build_next_focus_task_board_branch() -> None:
    focus = _build_next_focus(
        next_followup_target="task_board.parking_preflight",
        readiness_status="caution",
        task_track="review_track",
        claim_recommendation="optional",
    )
    assert focus["resolved_to"] == "task_board.parking_preflight"
    assert "parking_scope_review=yes" in focus["focus_pressures"]
    assert "task-board preflight" in focus["operator_action"]


def test_build_next_focus_non_matching_target_uses_generic_operator_action() -> None:
    focus = _build_next_focus(
        next_followup_target="some.other_target",
        readiness_status="unknown",
        task_track="unclassified",
        claim_recommendation="unknown",
    )
    assert focus["resolved_to"] == "some.other_target"
    assert "claim_recommendation" not in " ".join(focus["focus_pressures"])
    assert "narrowest preflight" in focus["operator_action"] or "bounded hook" in focus["operator_action"]


# ── build_subsystem_parity_readout edge cases ─────────────────────────────────

def test_build_subsystem_parity_readout_short_board_not_visible() -> None:
    payload = build_subsystem_parity_readout(
        project_memory_summary=_make_project_memory_summary(),
        import_posture=_make_import_posture(),
        readiness={"status": "caution"},
        task_track_hint={"suggested_track": "review_track", "claim_recommendation": "optional"},
        working_style_validation={"status": "insufficient"},
        mutation_preflight=_make_mutation_preflight(),
        canonical_center={"current_short_board": {"present": False}},
    )
    by_name = {item["name"]: item for item in payload["families"]}
    assert by_name["observer_window"]["current_signal"] == "short_board_not_visible"


def test_build_subsystem_parity_readout_publish_push_next_followup() -> None:
    preflight = {
        "summary_text": "publish_push=review_before_push",
        "next_followup": {"target": "publish_push.posture_preflight"},
    }
    payload = build_subsystem_parity_readout(
        project_memory_summary=_make_project_memory_summary(),
        import_posture=_make_import_posture(),
        readiness={"status": "pass"},
        task_track_hint={"suggested_track": "feature_track", "claim_recommendation": "required"},
        working_style_validation={"status": "pass"},
        mutation_preflight=preflight,
        canonical_center={"current_short_board": {"present": True}},
    )
    assert payload["next_focus"]["resolved_to"] == "publish_push.posture_preflight"
    assert "publish/push preflight" in payload["next_focus"]["operator_action"]


def test_build_subsystem_parity_readout_empty_inputs_do_not_raise() -> None:
    payload = build_subsystem_parity_readout(
        project_memory_summary={},
        import_posture={},
        readiness={},
        task_track_hint={},
        working_style_validation={},
        mutation_preflight={},
        canonical_center={},
    )
    assert payload["present"] is True
    assert payload["counts"]["baseline"] == 3
