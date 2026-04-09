from __future__ import annotations

from pathlib import Path

from apps.dashboard.frontend.utils.session_start import (
    build_dashboard_command_shelf,
    build_operator_walkthrough_pack,
    build_tier0_start_strip,
    build_tier1_orientation_shell,
    build_tier2_deep_governance_drawer,
    run_session_start_bundle,
)


def test_build_tier0_start_strip_extracts_operator_summary():
    bundle = {
        "present": True,
        "tier": 0,
        "readiness": {"status": "pass"},
        "task_track_hint": {"suggested_track": "feature_track"},
        "deliberation_mode_hint": {"suggested_mode": "lightweight_review"},
        "canonical_center": {"summary_text": "short board visible"},
        "hook_chain": {
            "hooks": [
                {"name": "shared_edit_path_overlap", "status": "active"},
                {"name": "publish_push_posture", "status": "active"},
            ]
        },
        "mutation_preflight": {
            "receiver_rule": "keep bounded",
            "next_followup": {
                "target": "task_board.parking_preflight",
                "classification": "existing_runtime_hook",
                "command": "python scripts/run_task_board_preflight.py ...",
                "reason": "keep ideas parked",
            },
        },
    }

    result = build_tier0_start_strip(bundle)

    assert result["readiness_status"] == "pass"
    assert result["task_track"] == "feature_track"
    assert result["deliberation_mode"] == "lightweight_review"
    assert result["canonical_summary"] == "short board visible"
    assert result["next_followup"]["target"] == "task_board.parking_preflight"
    assert result["hook_badges"][0]["name"] == "shared_edit_path_overlap"


def test_build_tier1_orientation_shell_extracts_cards():
    bundle = {
        "present": True,
        "tier": 1,
        "canonical_center": {
            "source_precedence_summary": "canonical > live > derived",
            "current_short_board": {"summary_text": "Phase 768"},
            "successor_correction": {"summary_text": "observer stable != permission"},
        },
        "subsystem_parity": {
            "counts": {"baseline": 2, "beta_usable": 1, "partial": 1, "deferred": 0},
            "next_focus": {
                "resolved_to": "shared_code_edit.path_overlap_preflight",
                "source_family": "mutation_preflight_hooks",
                "operator_action": "Run the shared-edit preflight first.",
                "focus_pressures": ["readiness=pass", "task_track=feature_track"],
            },
            "families": [
                {
                    "name": "session_start_bundle",
                    "status": "baseline",
                    "main_gap": "none",
                    "next_bounded_move": "hold",
                }
            ],
        },
        "closeout_attention": {
            "present": True,
            "status": "partial",
            "source_family": "bounded_handoff_closeout",
            "operator_action": "Review unresolved items before treating the handoff as resumable work.",
            "attention_pressures": ["status=partial", "unresolved=1"],
            "summary_text": "latest closeout is partial",
            "receiver_rule": "read closeout first",
        },
        "observer_shell": {
            "summary_text": "observer ready",
            "receiver_note": "shell only",
            "counts": {"stable": 3, "contested": 1, "stale": 0},
            "stable_headlines": ["launch tier is collaborator_beta"],
            "contested_headlines": ["council confidence is descriptive_only"],
            "stale_headlines": [],
            "hot_memory_ladder": {
                "current_pull_boundary": {
                    "pull_posture": "review_handoff_before_deeper_pull",
                    "preferred_stop_at": "bounded_handoff",
                    "operator_action": "Review closeout before deeper pulls.",
                    "why_now": "bounded handoff remains contested",
                    "receiver_rule": "read handoff before replay",
                }
            },
        },
    }

    result = build_tier1_orientation_shell(bundle)

    assert result["canonical_cards"]["short_board"] == "Phase 768"
    assert result["canonical_cards"]["successor_correction"] == "observer stable != permission"
    assert result["parity_counts"]["baseline"] == 2
    assert result["next_focus"]["resolved_to"] == "shared_code_edit.path_overlap_preflight"
    assert result["next_focus"]["source_family"] == "mutation_preflight_hooks"
    assert result["closeout_attention"]["status"] == "partial"
    assert result["closeout_attention"]["source_family"] == "bounded_handoff_closeout"
    assert result["closeout_attention"]["attention_pressures"] == [
        "status=partial",
        "unresolved=1",
    ]
    assert result["observer_shell"]["contested_headlines"] == [
        "council confidence is descriptive_only"
    ]
    assert result["hot_memory_boundary"]["preferred_stop_at"] == "bounded_handoff"
    assert result["hot_memory_boundary"]["pull_posture"] == "review_handoff_before_deeper_pull"


def test_run_session_start_bundle_parses_json(monkeypatch, tmp_path: Path):
    class FakeResult:
        returncode = 0
        stdout = '{"tier": 0, "present": true, "readiness": {"status": "pass"}}'
        stderr = ""

    def fake_run(command, cwd, capture_output, text, check):
        assert "--tier" in command
        assert cwd == tmp_path
        assert capture_output is True
        assert text is True
        assert check is False
        return FakeResult()

    monkeypatch.setattr("subprocess.run", fake_run)

    result = run_session_start_bundle(agent_id="dashboard-test", tier=0, repo_root=tmp_path)

    assert result["present"] is True
    assert result["tier"] == 0
    assert result["readiness"]["status"] == "pass"


def test_build_tier2_deep_governance_drawer_extracts_budgeted_groups():
    bundle = {
        "present": True,
        "tier": 2,
        "readiness": {"status": "needs_clarification", "claim_conflict_count": 1},
        "import_posture": {
            "surfaces": {
                "compactions": {
                    "receiver_obligation": "must_not_promote",
                    "closeout_status": "partial",
                    "note": "Carry-forward is resumability memory only.",
                },
                "council_dossier": {
                    "note": "Treat council review as bounded context.",
                    "dossier_interpretation": {"calibration_status": "descriptive_only"},
                },
                "subject_snapshot": {"note": "non-canonical working identity"},
                "working_style": {"note": "advisory only"},
            }
        },
        "mutation_preflight": {
            "next_followup": {
                "command": "python scripts/run_shared_edit_preflight.py --agent test --path task.md"
            },
            "decision_points": [
                {
                    "name": "shared_code_edit",
                    "posture": "coordinate_before_shared_edits",
                    "receiver_note": "Coordinate shared paths first.",
                    "current_guard": "run_shared_edit_preflight.py",
                },
                {
                    "name": "compaction_write",
                    "posture": "honest_closeout_required",
                    "receiver_note": "Keep closeout honest.",
                    "current_guard": "save_compaction.py",
                },
            ],
        },
        "publish_push_preflight": {
            "classification": "review_before_push",
            "summary_text": "publish_push=review_before_push",
            "receiver_note": "Review before outward push.",
            "recommended_command": "python scripts/run_publish_push_preflight.py --agent test",
        },
        "task_board_preflight": {
            "classification": "docs_plans_first",
            "summary_text": "task_board=docs_plans_first",
            "receiver_note": "Park new ideas in docs/plans first.",
            "recommended_command": "python scripts/run_task_board_preflight.py --agent test --proposal-kind external_idea --target-path task.md",
        },
        "closeout_attention": {
            "present": True,
            "status": "partial",
            "summary_text": "latest closeout is partial",
            "receiver_rule": "read closeout first",
        },
        "observer_shell": {
            "receiver_note": "observer shell is descriptive",
            "contested_headlines": ["council confidence is descriptive_only"],
        },
    }

    result = build_tier2_deep_governance_drawer(bundle)

    assert result["recommended_open"] is True
    assert "Mutation And Closeout" in result["active_group_names"]
    assert "Contested Continuity" in result["active_group_names"]
    assert result["groups"][0]["cards"][0]["title"] == "closeout attention"
    assert result["groups"][1]["cards"][0]["title"] == "compaction carry-forward"
    assert result["next_pull_commands"][0].startswith("python scripts/run_shared_edit_preflight.py")


def test_build_tier2_deep_governance_drawer_stays_manual_when_clean():
    bundle = {
        "present": True,
        "tier": 2,
        "readiness": {"status": "pass", "claim_conflict_count": 0},
        "import_posture": {"surfaces": {}},
        "mutation_preflight": {"decision_points": []},
        "publish_push_preflight": {"classification": "clear", "recommended_command": ""},
        "task_board_preflight": {"classification": "parking_clear", "recommended_command": ""},
        "closeout_attention": {"present": False},
        "observer_shell": {"contested_headlines": []},
    }

    result = build_tier2_deep_governance_drawer(bundle)

    assert result["recommended_open"] is False
    assert result["trigger_reasons"] == []


def test_build_operator_walkthrough_pack_stays_tiered():
    tier0_shell = {
        "readiness_status": "pass",
        "next_followup": {
            "command": "python scripts/run_shared_edit_preflight.py --agent test --path task.md"
        },
    }
    tier1_shell = {
        "canonical_cards": {"short_board": "Phase 780"},
        "closeout_attention": {"present": True},
        "parity_counts": {"partial": 2},
    }
    tier2_drawer = {
        "recommended_open": True,
        "trigger_reasons": ["closeout_attention_present"],
        "next_pull_commands": ["python scripts/run_publish_push_preflight.py --agent test"],
    }

    result = build_operator_walkthrough_pack(
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
    )

    assert result["current_signals"]["tier0_readiness"] == "pass"
    assert result["current_signals"]["tier1_short_board_visible"] is True
    assert result["current_signals"]["tier2_recommended_open"] is True
    assert result["scenarios"][0]["default_tier"] == "Tier 0"
    assert result["scenarios"][1]["next_move"] == "Phase 780"
    assert result["scenarios"][2]["next_move"].startswith(
        "python scripts/run_publish_push_preflight.py"
    )


def test_build_dashboard_command_shelf_points_back_to_cli_runtime():
    tier0_shell = {
        "next_followup": {
            "target": "mutation_preflight.next_followup",
            "command": "python scripts/run_shared_edit_preflight.py --agent test --path task.md",
            "reason": "Visible because Tier 0 already exposes one bounded follow-up.",
        }
    }
    tier2_drawer = {
        "trigger_reasons": ["closeout_attention_present", "claim_conflict_visible"],
        "next_pull_commands": ["python scripts/run_publish_push_preflight.py --agent test"],
    }

    result = build_dashboard_command_shelf(
        agent_id="dashboard-workspace",
        tier0_shell=tier0_shell,
        tier2_drawer=tier2_drawer,
    )

    assert result["present"] is True
    assert result["commands"][0]["command"].endswith("--tier 0 --no-ack")
    assert result["commands"][0]["source_surface"] == "session_start.tier0"
    assert result["commands"][1]["command"].endswith("--tier 1 --no-ack")
    assert result["commands"][2]["command"].endswith("--ack")
    assert result["commands"][3]["command"].startswith(
        "python scripts/run_shared_edit_preflight.py"
    )
    assert result["commands"][3]["source_surface"] == "mutation_preflight.next_followup"
    assert result["commands"][3]["activation_reason"] == (
        "Visible because Tier 0 already exposes one bounded follow-up."
    )
    assert result["commands"][3]["return_rule"].startswith("If this move broadens scope")
    assert result["commands"][4]["tier"] == "Tier 2"
    assert (
        result["commands"][4]["source_surface"] == "tier2_deep_governance_drawer.next_pull_commands"
    )
    assert "closeout_attention_present" in result["commands"][4]["activation_reason"]
    assert result["commands"][4]["return_rule"].startswith("When Tier 2 trigger reasons clear")
