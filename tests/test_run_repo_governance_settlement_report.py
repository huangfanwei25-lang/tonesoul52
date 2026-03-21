from __future__ import annotations

import json
from pathlib import Path

import scripts.run_repo_governance_settlement_report as governance_report


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_report_identifies_metadata_only_blocker(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": False,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
                {"name": "commit_attribution", "ok": False},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
            "rationale": "dirty worktree",
            "suggested_commands": [
                "git worktree add <clean-path> feat/env-perception-attribution-backfill"
            ],
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 24,
                    "sample_paths": [
                        "scripts/run_repo_healthcheck.py",
                        "tests/test_run_repo_governance_settlement_report.py",
                    ],
                    "recommended_actions": ["keep gates and settlement scripts together"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 3,
                "refreshable_admissibility_preview_count": 1,
            },
            "subjectivity_focus_preview": {
                "path": "docs/status/subjectivity_review_batch_latest.json",
                "queue_shape": "stable_history_only",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "stable_deferred_history | A distributed vulnerability database for "
                    "Open Source | rows=50 lineages=12 cycles=30"
                ),
                "runtime_status_line": "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7",
                "scribe_status_line": (
                    "subjectivity_scribe | status=generated mode=template_assist"
                ),
                "anchor_status_line": (
                    "anchor | [subjectivity_tension_a1] tension: authority pressure..."
                ),
                "problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=admissibility_grounding "
                    "repair=admissibility_prompt_boundary"
                ),
                "problem_route_secondary_labels": ("F6_semantic_role_boundary_integrity"),
                "dream_weekly_alignment_line": (
                    "dream_weekly_alignment | alignment=diverged "
                    "weekly=F1_grounding_evidence_integrity "
                    "dream=F6_semantic_role_boundary_integrity"
                ),
                "artifact_policy_status_line": (
                    "subjectivity_batch_artifacts_ready | strict=true review_groups=2"
                ),
                "admissibility_primary_status_line": (
                    "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                ),
            },
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/subjectivity_report_latest.json",
                            "queue_shape": "deferred_monitoring",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "deferred_monitoring | records=195 unresolved=50 deferred=50 "
                                "settled=31 reviewed_vows=0 | top_unresolved_status=deferred"
                            ),
                            "admissibility_primary_status_line": (
                                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                            ),
                        },
                        {
                            "path": "docs/status/subjectivity_review_batch_latest.json",
                            "queue_shape": "stable_history_only",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "stable_deferred_history | A distributed vulnerability database for "
                                "Open Source | rows=50 lineages=12 cycles=30"
                            ),
                            "runtime_status_line": (
                                "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7"
                            ),
                            "scribe_status_line": (
                                "subjectivity_scribe | status=generated mode=template_assist"
                            ),
                            "anchor_status_line": (
                                "anchor | [subjectivity_tension_a1] tension: authority pressure..."
                            ),
                            "problem_route_status_line": (
                                "route | family=F1_grounding_evidence_integrity "
                                "invariant=admissibility_grounding "
                                "repair=admissibility_prompt_boundary"
                            ),
                            "problem_route_secondary_labels": (
                                "F6_semantic_role_boundary_integrity"
                            ),
                            "dream_weekly_alignment_line": (
                                "dream_weekly_alignment | alignment=diverged "
                                "weekly=F1_grounding_evidence_integrity "
                                "dream=F6_semantic_role_boundary_integrity"
                            ),
                            "artifact_policy_status_line": (
                                "subjectivity_batch_artifacts_ready | strict=true review_groups=2"
                            ),
                            "admissibility_primary_status_line": (
                                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                            ),
                        },
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["overall_ok"] is False
    assert payload["settlement"]["status"] == "runtime_green_metadata_blocked"
    assert payload["settlement"]["metadata_only_blocker"] is True
    assert payload["settlement"]["runtime_green_except_metadata"] is True
    assert payload["healthcheck"]["failing_checks"] == ["commit_attribution"]
    assert payload["repo_governance_group"]["entry_count"] == 24
    assert payload["worktree_settlement"]["refreshable_handoff_preview_count"] == 3
    assert payload["worktree_settlement"]["refreshable_admissibility_preview_count"] == 1
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] == {
        "path": "docs/status/subjectivity_review_batch_latest.json",
        "queue_shape": "stable_history_only",
        "requires_operator_action": "false",
        "primary_status_line": (
            "stable_deferred_history | A distributed vulnerability database for "
            "Open Source | rows=50 lineages=12 cycles=30"
        ),
        "runtime_status_line": "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7",
        "anchor_status_line": ("anchor | [subjectivity_tension_a1] tension: authority pressure..."),
        "artifact_policy_status_line": (
            "subjectivity_batch_artifacts_ready | strict=true review_groups=2"
        ),
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=admissibility_grounding "
            "repair=admissibility_prompt_boundary"
        ),
        "problem_route_secondary_labels": "F6_semantic_role_boundary_integrity",
        "dream_weekly_alignment_line": (
            "dream_weekly_alignment | alignment=diverged "
            "weekly=F1_grounding_evidence_integrity "
            "dream=F6_semantic_role_boundary_integrity"
        ),
        "scribe_status_line": "subjectivity_scribe | status=generated mode=template_assist",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
    }
    assert payload["worktree_settlement"]["handoff_previews"][0]["queue_shape"] == (
        "deferred_monitoring"
    )
    assert (
        payload["worktree_settlement"]["handoff_previews"][1]["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert (
        payload["worktree_settlement"]["handoff_previews"][1]["requires_operator_action"] == "false"
    )
    assert payload["issues"] == ["metadata_only_commit_attribution_blocker"]
    assert "Metadata-only blocker: `true`" in markdown
    assert "Runtime green except attribution: `true`" in markdown
    assert "Refreshable handoff previews: `3`" in markdown
    assert "Refreshable admissibility previews: `1`" in markdown
    assert "Subjectivity focus" in markdown
    assert "Subjectivity runtime posture" in markdown
    assert "Subjectivity Scribe posture" in markdown
    assert "Subjectivity anchor posture" in markdown
    assert "Subjectivity problem route" in markdown
    assert "Subjectivity problem route secondary" in markdown
    assert "Subjectivity alignment" in markdown
    assert "Subjectivity artifact policy" in markdown
    assert "Subjectivity admissibility" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "runtime_status_line" in markdown
    assert "scribe_status_line" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "dream_weekly_alignment_line" in markdown
    assert "artifact_policy_status_line" in markdown
    assert "admissibility_primary_status_line" in markdown
    assert "requires_operator_action" in markdown
    assert "deferred_monitoring" in markdown


def test_build_report_surfaces_non_metadata_runtime_blocker(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": False,
            "checks": [
                {"name": "python_tests", "ok": False},
                {"name": "commit_attribution", "ok": False},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
        },
    )
    _write_json(tmp_path / "runtime_groups.json", {"change_groups": []})

    payload, _ = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
    )

    assert payload["settlement"]["status"] == "runtime_blocked"
    assert payload["settlement"]["metadata_only_blocker"] is False
    assert payload["worktree_settlement"]["refreshable_handoff_preview_count"] == 0
    assert payload["worktree_settlement"]["refreshable_admissibility_preview_count"] == 0
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] is None
    assert payload["issues"] == [
        "blocking_check:python_tests",
        "blocking_check:commit_attribution",
    ]
    assert payload["warnings"] == [
        "missing_repo_governance_runtime_group",
        "missing_worktree_settlement_artifact",
    ]


def test_main_strict_writes_artifacts_and_fails_when_not_green(monkeypatch, tmp_path: Path) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_repo_governance_settlement_report.py",
        "healthcheck": {
            "generated_at": "2026-03-08T00:00:00Z",
            "overall_ok": False,
            "pass_count": 10,
            "fail_count": 1,
            "failing_checks": ["commit_attribution"],
        },
        "attribution": {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
            "rationale": "dirty",
            "suggested_commands": [],
        },
        "repo_governance_group": {
            "entry_count": 24,
            "sample_paths": [],
            "recommended_actions": [],
        },
        "worktree_settlement": {
            "dirty": True,
            "planner_recommendation": "manual_review_required",
            "refreshable_handoff_preview_count": 3,
            "refreshable_admissibility_preview_count": 1,
            "handoff_previews": [],
        },
        "settlement": {
            "status": "runtime_green_metadata_blocked",
            "metadata_only_blocker": True,
            "runtime_green_except_metadata": True,
            "next_actions": [],
        },
        "issues": ["metadata_only_commit_attribution_blocker"],
        "warnings": [],
    }
    monkeypatch.setattr(
        governance_report,
        "build_report",
        lambda *args, **kwargs: (payload, "# Repo\n"),
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_governance_settlement_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = governance_report.main()

    assert exit_code == 1
    json_path = out_dir / governance_report.JSON_FILENAME
    md_path = out_dir / governance_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["settlement"]["status"] == "runtime_green_metadata_blocked"


def test_build_report_mirrors_weekly_host_status_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 1,
            },
            "subjectivity_focus_preview": None,
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
                            "queue_shape": "weekly_host_status",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                                "runtime_source=host_tick session=weekly-session resumed=yes"
                            ),
                            "runtime_status_line": (
                                "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                                "failures=1 max_failure=1 tension=breached"
                            ),
                            "anchor_status_line": (
                                "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
                            ),
                            "problem_route_status_line": (
                                "route | family=F1_grounding_evidence_integrity "
                                "invariant=observed_history_grounding "
                                "repair=anchor_and_boundary_guardrail"
                            ),
                            "problem_route_secondary_labels": (
                                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
                            ),
                            "dream_weekly_alignment_line": (
                                "dream_weekly_alignment | alignment=aligned "
                                "weekly=F1_grounding_evidence_integrity "
                                "dream=F1_grounding_evidence_integrity"
                            ),
                            "artifact_policy_status_line": (
                                "host_trigger_mode=single_tick | experiment_summary=ignored "
                                "reason=host_tick_single_tick_mode"
                            ),
                            "scribe_status_line": (
                                "scribe | status=generated mode=template_assist "
                                "posture=pressure_without_counterweight"
                            ),
                            "admissibility_primary_status_line": (
                                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                            ),
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["overall_ok"] is True
    assert payload["settlement"]["status"] == "green"
    assert payload["worktree_settlement"]["refreshable_handoff_preview_count"] == 1
    assert payload["worktree_settlement"]["refreshable_admissibility_preview_count"] == 1
    assert (
        payload["dream_weekly_alignment_line"] == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity"
    )
    assert payload["worktree_settlement"]["weekly_host_status_preview"] == {
        "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
        "queue_shape": "weekly_host_status",
        "requires_operator_action": "false",
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "anchor_status_line": (
            "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
        ),
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=observed_history_grounding "
            "repair=anchor_and_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
        "dream_weekly_alignment_line": (
            "dream_weekly_alignment | alignment=aligned "
            "weekly=F1_grounding_evidence_integrity "
            "dream=F1_grounding_evidence_integrity"
        ),
        "artifact_policy_status_line": (
            "host_trigger_mode=single_tick | experiment_summary=ignored "
            "reason=host_tick_single_tick_mode"
        ),
        "scribe_status_line": (
            "scribe | status=generated mode=template_assist "
            "posture=pressure_without_counterweight"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
    }
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] is None
    assert payload["worktree_settlement"]["handoff_previews"] == [
        {
            "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
            "queue_shape": "weekly_host_status",
            "requires_operator_action": "false",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "runtime_status_line": (
                "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                "failures=1 max_failure=1 tension=breached"
            ),
            "anchor_status_line": (
                "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
            ),
            "problem_route_status_line": (
                "route | family=F1_grounding_evidence_integrity "
                "invariant=observed_history_grounding "
                "repair=anchor_and_boundary_guardrail"
            ),
            "problem_route_secondary_labels": (
                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
            ),
            "dream_weekly_alignment_line": (
                "dream_weekly_alignment | alignment=aligned "
                "weekly=F1_grounding_evidence_integrity "
                "dream=F1_grounding_evidence_integrity"
            ),
            "artifact_policy_status_line": (
                "host_trigger_mode=single_tick | experiment_summary=ignored "
                "reason=host_tick_single_tick_mode"
            ),
            "scribe_status_line": (
                "scribe | status=generated mode=template_assist "
                "posture=pressure_without_counterweight"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
        }
    ]
    assert "Refreshable handoff previews: `1`" in markdown
    assert "Weekly host status" in markdown
    assert "Weekly runtime posture" in markdown
    assert "Weekly anchor posture" in markdown
    assert "Weekly problem route" in markdown
    assert "Weekly problem route secondary" in markdown
    assert "Weekly artifact policy" in markdown
    assert "Weekly admissibility" in markdown
    assert "Weekly Scribe posture" in markdown
    assert "Dream weekly alignment" in markdown
    assert "## Weekly Host Status Mirror" in markdown
    assert "weekly_host_status" in markdown
    assert "- queue_shape: `weekly_host_status`" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "dream_weekly_alignment_line" in markdown
    assert "artifact_policy_status_line" in markdown
    assert "admissibility_primary_status_line" in markdown
    assert "scribe_status_line" in markdown


def test_build_report_mirrors_scribe_focus_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 1,
            },
            "subjectivity_focus_preview": None,
            "scribe_focus_preview": {
                "path": "docs/status/scribe_status_latest.json",
                "queue_shape": "scribe_chronicle_ready",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "generated | mode=llm_chronicle model=gemma3:4b fallback_mode=bootstrap_reflection "
                    "attempts=2 latest=chronicle_pair"
                ),
                "runtime_status_line": (
                    "state_document | tensions=0 collisions=0 crystals=0 posture=anchor_only"
                ),
                "anchor_status_line": (
                    "anchor | [M0] tension: quiet readiness without a named external event..."
                ),
                "problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=observed_history_grounding "
                    "repair=anchor_and_boundary_guardrail"
                ),
                "problem_route_secondary_labels": (
                    "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
                ),
                "artifact_policy_status_line": (
                    "artifact_source=chronicle_pair | chronicle=yes companion=yes"
                ),
                "admissibility_primary_status_line": "",
            },
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/scribe_status_latest.json",
                            "queue_shape": "scribe_chronicle_ready",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "generated | mode=llm_chronicle model=gemma3:4b fallback_mode=bootstrap_reflection "
                                "attempts=2 latest=chronicle_pair"
                            ),
                            "runtime_status_line": (
                                "state_document | tensions=0 collisions=0 crystals=0 posture=anchor_only"
                            ),
                            "anchor_status_line": (
                                "anchor | [M0] tension: quiet readiness without a named external event..."
                            ),
                            "problem_route_status_line": (
                                "route | family=F1_grounding_evidence_integrity "
                                "invariant=observed_history_grounding "
                                "repair=anchor_and_boundary_guardrail"
                            ),
                            "problem_route_secondary_labels": (
                                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
                            ),
                            "artifact_policy_status_line": (
                                "artifact_source=chronicle_pair | chronicle=yes companion=yes"
                            ),
                            "admissibility_primary_status_line": "",
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["overall_ok"] is True
    assert payload["settlement"]["status"] == "green"
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] is None
    assert payload["worktree_settlement"]["scribe_focus_preview"] == {
        "path": "docs/status/scribe_status_latest.json",
        "queue_shape": "scribe_chronicle_ready",
        "requires_operator_action": "false",
        "primary_status_line": (
            "generated | mode=llm_chronicle model=gemma3:4b fallback_mode=bootstrap_reflection "
            "attempts=2 latest=chronicle_pair"
        ),
        "runtime_status_line": (
            "state_document | tensions=0 collisions=0 crystals=0 posture=anchor_only"
        ),
        "anchor_status_line": (
            "anchor | [M0] tension: quiet readiness without a named external event..."
        ),
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=observed_history_grounding "
            "repair=anchor_and_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
        "artifact_policy_status_line": (
            "artifact_source=chronicle_pair | chronicle=yes companion=yes"
        ),
        "admissibility_primary_status_line": "",
    }
    assert "## Scribe Focus Mirror" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "scribe_chronicle_ready" in markdown
    assert "scribe_status_latest.json" in markdown


def test_build_report_mirrors_dream_observability_focus_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 0,
            },
            "subjectivity_focus_preview": None,
            "weekly_host_status_preview": {
                "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
                "queue_shape": "weekly_host_status",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                    "runtime_source=host_tick session=weekly-session resumed=yes"
                ),
                "runtime_status_line": (
                    "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                    "failures=1 max_failure=1 tension=breached"
                ),
                "problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=observed_history_grounding "
                    "repair=anchor_and_boundary_guardrail"
                ),
                "problem_route_secondary_labels": (
                    "F4_execution_contract_integrity,F7_representation_localization_integrity"
                ),
                "artifact_policy_status_line": "",
                "scribe_status_line": (
                    "scribe | status=generated mode=template_assist "
                    "posture=pressure_without_counterweight"
                ),
                "admissibility_primary_status_line": (
                    "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                ),
            },
            "dream_observability_focus_preview": {
                "path": "docs/status/dream_observability_latest.json",
                "queue_shape": "dream_observability_ready",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "dream_observability_ready | cycles=8 collisions=3 councils=3 "
                    "scribe=generated"
                ),
                "runtime_status_line": (
                    "wakeup_dashboard | session=wakeup-session resumed=yes "
                    "posture=pressure_without_counterweight"
                ),
                "anchor_status_line": "anchor | [T1] tension: observed grounding...",
                "problem_route_status_line": (
                    "route | family=F6_semantic_role_boundary_integrity "
                    "invariant=chronicle_self_scope "
                    "repair=semantic_boundary_guardrail"
                ),
                "problem_route_secondary_labels": (
                    "F4_execution_contract_integrity,F7_representation_localization_integrity"
                ),
                "artifact_policy_status_line": (
                    "dashboard_artifacts_ready | html=yes json=yes recent_rows=8"
                ),
                "admissibility_primary_status_line": "",
            },
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/dream_observability_latest.json",
                            "queue_shape": "dream_observability_ready",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "dream_observability_ready | cycles=8 collisions=3 councils=3 "
                                "scribe=generated"
                            ),
                            "runtime_status_line": (
                                "wakeup_dashboard | session=wakeup-session resumed=yes "
                                "posture=pressure_without_counterweight"
                            ),
                            "anchor_status_line": "anchor | [T1] tension: observed grounding...",
                            "problem_route_status_line": (
                                "route | family=F6_semantic_role_boundary_integrity "
                                "invariant=chronicle_self_scope "
                                "repair=semantic_boundary_guardrail"
                            ),
                            "problem_route_secondary_labels": (
                                "F4_execution_contract_integrity,F7_representation_localization_integrity"
                            ),
                            "artifact_policy_status_line": (
                                "dashboard_artifacts_ready | html=yes json=yes recent_rows=8"
                            ),
                            "admissibility_primary_status_line": "",
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["overall_ok"] is True
    assert payload["settlement"]["status"] == "green"
    assert payload["dream_weekly_alignment_line"] == (
        "dream_weekly_alignment | alignment=diverged "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F6_semantic_role_boundary_integrity "
        "shared_secondary=F4_execution_contract_integrity,F7_representation_localization_integrity"
    )
    assert payload["worktree_settlement"]["dream_observability_focus_preview"] == {
        "path": "docs/status/dream_observability_latest.json",
        "queue_shape": "dream_observability_ready",
        "requires_operator_action": "false",
        "primary_status_line": (
            "dream_observability_ready | cycles=8 collisions=3 councils=3 " "scribe=generated"
        ),
        "runtime_status_line": (
            "wakeup_dashboard | session=wakeup-session resumed=yes "
            "posture=pressure_without_counterweight"
        ),
        "anchor_status_line": "anchor | [T1] tension: observed grounding...",
        "problem_route_status_line": (
            "route | family=F6_semantic_role_boundary_integrity "
            "invariant=chronicle_self_scope "
            "repair=semantic_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F4_execution_contract_integrity,F7_representation_localization_integrity"
        ),
        "artifact_policy_status_line": (
            "dashboard_artifacts_ready | html=yes json=yes recent_rows=8"
        ),
        "admissibility_primary_status_line": "",
    }
    assert "Dream observability" in markdown
    assert "Dream runtime posture" in markdown
    assert "Dream anchor posture" in markdown
    assert "Dream problem route" in markdown
    assert "Dream problem route secondary" in markdown
    assert "Dream artifact policy" in markdown
    assert "Dream weekly alignment" in markdown
    assert "alignment=diverged" in markdown
    assert "## Weekly Host Status Mirror" in markdown
    assert "## Dream Observability Focus Mirror" in markdown
    assert "dream_observability_ready" in markdown
    assert "- anchor_status_line:" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "dream_observability_latest.json" in markdown


def test_build_report_mirrors_agent_integrity_focus_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 0,
            },
            "subjectivity_focus_preview": None,
            "weekly_host_status_preview": None,
            "dream_observability_focus_preview": None,
            "agent_integrity_focus_preview": {
                "path": "docs/status/agent_integrity_latest.json",
                "queue_shape": "agent_integrity_guarded",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "agent_integrity_warning | errors=0 warnings=1 "
                    "review_dirs=2 protected_files=3"
                ),
                "runtime_status_line": (
                    "integrity_contract | contract=agent_integrity_contract.py "
                    "checker=check_agent_integrity.py workflow=agent-integrity-check.yml"
                ),
                "problem_route_status_line": (
                    "integrity | family=G1_integrity_contract_drift "
                    "invariant=embedded_expected_hash_metadata "
                    "repair=protected_file_documentation"
                ),
                "artifact_policy_status_line": (
                    "protected_hashes=blocking | hidden_chars=blocking | "
                    "embedded_metadata=warning | watched_dirs=review_only"
                ),
            },
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/agent_integrity_latest.json",
                            "queue_shape": "agent_integrity_guarded",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "agent_integrity_warning | errors=0 warnings=1 "
                                "review_dirs=2 protected_files=3"
                            ),
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["worktree_settlement"]["agent_integrity_focus_preview"] == {
        "path": "docs/status/agent_integrity_latest.json",
        "queue_shape": "agent_integrity_guarded",
        "requires_operator_action": "false",
        "primary_status_line": (
            "agent_integrity_warning | errors=0 warnings=1 review_dirs=2 protected_files=3"
        ),
        "runtime_status_line": (
            "integrity_contract | contract=agent_integrity_contract.py "
            "checker=check_agent_integrity.py workflow=agent-integrity-check.yml"
        ),
        "anchor_status_line": "",
        "problem_route_status_line": (
            "integrity | family=G1_integrity_contract_drift "
            "invariant=embedded_expected_hash_metadata "
            "repair=protected_file_documentation"
        ),
        "artifact_policy_status_line": (
            "protected_hashes=blocking | hidden_chars=blocking | "
            "embedded_metadata=warning | watched_dirs=review_only"
        ),
        "admissibility_primary_status_line": "",
    }
    assert "Agent integrity" in markdown
    assert "Agent integrity runtime" in markdown
    assert "Agent integrity problem route" in markdown
    assert "Agent integrity artifact policy" in markdown
    assert "## Agent Integrity Focus Mirror" in markdown


def test_build_report_mirrors_repo_semantic_atlas_focus_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 0,
            },
            "subjectivity_focus_preview": None,
            "weekly_host_status_preview": None,
            "dream_observability_focus_preview": None,
            "repo_semantic_atlas_focus_preview": {
                "path": "docs/status/repo_semantic_atlas_latest.json",
                "queue_shape": "repo_semantic_atlas_ready",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
                    "chronicles=19 doc_threads=431 rules=8 graph_edges=7"
                ),
                "runtime_status_line": (
                    "entrypoints | atlas=repo_semantic_atlas_latest.json "
                    "repo=repo_healthcheck_latest.json "
                    "dream=dream_observability_latest.json "
                    "weekly=true_verification_task_status_latest.json "
                    "scribe=scribe_status_latest.json protocol=alias_first"
                ),
                "artifact_policy_status_line": (
                    "semantic_map=domain_level | aliases=source_declared "
                    "graph=passive_no_reparse protocol=backend_agnostic"
                ),
            },
            "agent_integrity_focus_preview": None,
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/repo_semantic_atlas_latest.json",
                            "queue_shape": "repo_semantic_atlas_ready",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
                                "chronicles=19 doc_threads=431 rules=8 graph_edges=7"
                            ),
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["worktree_settlement"]["repo_semantic_atlas_focus_preview"] == {
        "path": "docs/status/repo_semantic_atlas_latest.json",
        "queue_shape": "repo_semantic_atlas_ready",
        "requires_operator_action": "false",
        "primary_status_line": (
            "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
            "chronicles=19 doc_threads=431 rules=8 graph_edges=7"
        ),
        "runtime_status_line": (
            "entrypoints | atlas=repo_semantic_atlas_latest.json "
            "repo=repo_healthcheck_latest.json "
            "dream=dream_observability_latest.json "
            "weekly=true_verification_task_status_latest.json "
            "scribe=scribe_status_latest.json protocol=alias_first"
        ),
        "anchor_status_line": "",
        "artifact_policy_status_line": (
            "semantic_map=domain_level | aliases=source_declared "
            "graph=passive_no_reparse protocol=backend_agnostic"
        ),
        "admissibility_primary_status_line": "",
    }
    assert "Repo semantic atlas" in markdown
    assert "Repo semantic retrieval" in markdown
    assert "Repo semantic artifact policy" in markdown
    assert "## Repo Semantic Atlas Focus Mirror" in markdown


def test_build_report_mirrors_repo_intelligence_focus_preview_from_worktree_settlement(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": True,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "no_switch_needed",
            "tree_equal": True,
            "current_missing_count": 0,
            "backfill_missing_count": 0,
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 4,
                    "sample_paths": ["scripts/run_repo_governance_settlement_report.py"],
                    "recommended_actions": ["keep settlement mirrors readable"],
                }
            ]
        },
    )
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 1,
                "refreshable_admissibility_preview_count": 0,
            },
            "subjectivity_focus_preview": None,
            "weekly_host_status_preview": None,
            "dream_observability_focus_preview": None,
            "repo_semantic_atlas_focus_preview": None,
            "repo_intelligence_focus_preview": {
                "path": "docs/status/repo_intelligence_latest.json",
                "queue_shape": "repo_intelligence_ready",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "repo_intelligence_ready | available_surfaces=5/5 "
                    "protected_files=5 watched_dirs=3 adoption=sidecar_only"
                ),
                "runtime_status_line": (
                    "entrypoints | repo=repo_healthcheck_latest.json "
                    "settlement=repo_governance_settlement_latest.json "
                    "review=runtime_source_change_groups_latest.json "
                    "weekly=true_verification_task_status_latest.json "
                    "scribe=scribe_status_latest.json"
                ),
                "semantic_retrieval_protocol": (
                    "alias_first -> neighborhood_before_file -> status_surface_before_source"
                ),
                "semantic_preferred_neighborhood": "repo_governance",
                "artifact_policy_status_line": (
                    "external_repo_intelligence=sidecar_only | "
                    "main_repo_install=no hooks=no protected_files=no"
                ),
            },
            "agent_integrity_focus_preview": None,
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/repo_intelligence_latest.json",
                            "queue_shape": "repo_intelligence_ready",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "repo_intelligence_ready | available_surfaces=5/5 "
                                "protected_files=5 watched_dirs=3 adoption=sidecar_only"
                            ),
                        }
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["worktree_settlement"]["repo_intelligence_focus_preview"] == {
        "path": "docs/status/repo_intelligence_latest.json",
        "queue_shape": "repo_intelligence_ready",
        "requires_operator_action": "false",
        "primary_status_line": (
            "repo_intelligence_ready | available_surfaces=5/5 "
            "protected_files=5 watched_dirs=3 adoption=sidecar_only"
        ),
        "runtime_status_line": (
            "entrypoints | repo=repo_healthcheck_latest.json "
            "settlement=repo_governance_settlement_latest.json "
            "review=runtime_source_change_groups_latest.json "
            "weekly=true_verification_task_status_latest.json "
            "scribe=scribe_status_latest.json"
        ),
        "anchor_status_line": "",
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "artifact_policy_status_line": (
            "external_repo_intelligence=sidecar_only | "
            "main_repo_install=no hooks=no protected_files=no"
        ),
        "admissibility_primary_status_line": "",
    }
    assert "Repo intelligence" in markdown
    assert "Repo intelligence semantic protocol" in markdown
    assert "Repo intelligence first neighborhood" in markdown
    assert "## Repo Intelligence Focus Mirror" in markdown
