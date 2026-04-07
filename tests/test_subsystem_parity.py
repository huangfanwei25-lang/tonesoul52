from __future__ import annotations

from tonesoul.subsystem_parity import build_subsystem_parity_readout


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
