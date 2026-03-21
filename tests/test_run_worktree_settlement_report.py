from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_worktree_settlement_report as settlement_runner


def _dirty_plan() -> dict[str, object]:
    return {
        "recommendation": "defer_until_worktree_clean",
        "rationale": "worktree is dirty",
        "tree_equal": True,
        "current_missing_count": 5,
        "backfill_missing_count": 0,
        "cleanup_priority": [
            {"category": "generated_status", "count": 2, "reason": "refresh later"},
            {"category": "memory", "count": 1, "reason": "private review"},
            {"category": "tests", "count": 1, "reason": "pair with code"},
        ],
        "worktree": {
            "dirty": True,
            "entry_count": 4,
            "staged_count": 0,
            "unstaged_count": 2,
            "untracked_count": 2,
            "category_counts": {
                "generated_status": 2,
                "memory": 1,
                "tests": 1,
            },
        },
    }


def _dirty_entries() -> list[dict[str, object]]:
    return [
        {
            "status": " M",
            "path": "docs/status/repo_healthcheck_latest.json",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "reports/model_comparison_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "reports",
        },
        {
            "status": " M",
            "path": "memory/architecture_reflection_2026-03-07.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "memory",
        },
        {
            "status": "??",
            "path": "tests/test_run_worktree_settlement_report.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "tests",
        },
    ]


def test_build_report_groups_dirty_entries_into_lanes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
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
                ]
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    assert payload["overall_ok"] is False
    assert payload["planner"]["recommendation"] == "defer_until_worktree_clean"
    assert payload["worktree"]["entry_count"] == 4
    assert payload["summary"]["active_lane_count"] == 3

    refresh_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "refreshable_artifacts"
    )
    assert refresh_lane["active"] is True
    assert refresh_lane["entry_count"] == 2
    assert refresh_lane["categories"][0]["category"] == "generated_status"
    assert refresh_lane["handoff_preview_count"] == 2
    assert refresh_lane["admissibility_preview_count"] == 2
    assert payload["summary"]["refreshable_handoff_preview_count"] == 2
    assert payload["summary"]["refreshable_admissibility_preview_count"] == 2
    assert payload["subjectivity_focus_preview"] == {
        "path": "docs/status/subjectivity_report_latest.json",
        "queue_shape": "deferred_monitoring",
        "requires_operator_action": "false",
        "primary_status_line": (
            "deferred_monitoring | records=195 unresolved=50 deferred=50 "
            "settled=31 reviewed_vows=0 | top_unresolved_status=deferred"
        ),
        "runtime_status_line": "",
        "anchor_status_line": "",
        "artifact_policy_status_line": "",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
    }
    assert refresh_lane["handoff_previews"][0]["queue_shape"] == "deferred_monitoring"
    assert (
        refresh_lane["handoff_previews"][1]["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert refresh_lane["handoff_previews"][1]["requires_operator_action"] == "false"

    memory_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "private_memory_review"
    )
    assert memory_lane["active"] is True
    assert memory_lane["entry_count"] == 1
    assert "private" in memory_lane["recommended_actions"][0].lower()

    assert "Private memory paths remain governed by the dual-track boundary" in markdown
    assert "Subjectivity focus" in markdown
    assert "Subjectivity admissibility" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "Refreshable Artifacts" in markdown
    assert "Handoff previews: `2`" in markdown
    assert "requires_operator_action" in markdown
    assert "deferred_monitoring" in markdown
    assert "stable_history_only" in markdown
    assert "runtime_status_line" in markdown
    assert "scribe_status_line" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "dream_weekly_alignment_line" in markdown
    assert "artifact_policy_status_line" in markdown
    assert "admissibility_primary_status_line" in markdown


def test_build_report_returns_clean_status_when_worktree_is_clean(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clean_plan = {
        "recommendation": "no_switch_needed",
        "rationale": "clean",
        "tree_equal": True,
        "current_missing_count": 0,
        "backfill_missing_count": 0,
        "cleanup_priority": [],
        "worktree": {
            "dirty": False,
            "entry_count": 0,
            "staged_count": 0,
            "unstaged_count": 0,
            "untracked_count": 0,
            "category_counts": {},
        },
    }
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: clean_plan
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {"handoff_previews": [], "subjectivity_focus_preview": None},
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, _ = settlement_runner.build_report(tmp_path)

    assert payload["overall_ok"] is True
    assert payload["issues"] == []
    assert payload["summary"]["active_lane_count"] == 0
    assert payload["summary"]["refreshable_handoff_preview_count"] == 0
    assert payload["summary"]["refreshable_admissibility_preview_count"] == 0
    assert payload["subjectivity_focus_preview"] == payload["weekly_host_status_preview"]


def test_build_report_passes_through_weekly_host_status_preview_without_subjectivity_focus(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
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
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    refresh_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "refreshable_artifacts"
    )
    assert payload["summary"]["refreshable_handoff_preview_count"] == 1
    assert payload["summary"]["refreshable_admissibility_preview_count"] == 1
    assert (
        payload["dream_weekly_alignment_line"] == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity"
    )
    assert payload["weekly_host_status_preview"] == {
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
    assert payload["subjectivity_focus_preview"] == payload["weekly_host_status_preview"]
    assert refresh_lane["handoff_preview_count"] == 1
    assert refresh_lane["handoff_previews"] == [
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
    assert "true_verification_task_status_latest.json" in markdown


def test_build_report_selects_scribe_focus_preview_from_refreshable_handoffs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
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
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    refresh_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "refreshable_artifacts"
    )
    assert payload["subjectivity_focus_preview"] is None
    assert payload["scribe_focus_preview"] == {
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
    assert refresh_lane["handoff_previews"] == [
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
    ]
    assert "## Scribe Focus Mirror" in markdown
    assert "scribe_chronicle_ready" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "scribe_status_latest.json" in markdown


def test_build_report_selects_dream_observability_focus_preview_from_refreshable_handoffs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
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
                        "admissibility_primary_status_line": "",
                    },
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
                    },
                ],
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    refresh_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "refreshable_artifacts"
    )
    assert payload["dream_weekly_alignment_line"] == (
        "dream_weekly_alignment | alignment=diverged "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F6_semantic_role_boundary_integrity "
        "shared_secondary=F4_execution_contract_integrity,F7_representation_localization_integrity"
    )
    assert payload["dream_observability_focus_preview"] == {
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
    assert len(refresh_lane["handoff_previews"]) == 2
    assert refresh_lane["handoff_previews"][1] == {
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
    assert "## Dream Observability Focus Mirror" in markdown
    assert "Dream observability" in markdown
    assert "Dream runtime posture" in markdown
    assert "Dream anchor posture" in markdown
    assert "Dream problem route" in markdown
    assert "Dream problem route secondary" in markdown
    assert "Dream artifact policy" in markdown
    assert "Dream weekly alignment" in markdown
    assert "alignment=diverged" in markdown
    assert "## Weekly Host Status Mirror" in markdown
    assert "dream_observability_ready" in markdown
    assert "- anchor_status_line:" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "dream_observability_latest.json" in markdown


def test_build_report_selects_agent_integrity_focus_preview_from_refreshable_handoffs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
                "handoff_previews": [
                    {
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
                        "admissibility_primary_status_line": "",
                    }
                ],
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    assert payload["agent_integrity_focus_preview"] == {
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
    assert "## Agent Integrity Focus Mirror" in markdown
    assert "agent_integrity_warning" in markdown
    assert "agent_integrity_latest.json" in markdown


def test_build_report_selects_repo_semantic_atlas_focus_preview_from_refreshable_handoffs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
                "handoff_previews": [
                    {
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
                        "admissibility_primary_status_line": "",
                    }
                ],
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    assert payload["repo_semantic_atlas_focus_preview"] == {
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
    assert "repo_semantic_atlas_latest.json" in markdown


def test_build_report_selects_repo_intelligence_focus_preview_from_refreshable_handoffs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
                "handoff_previews": [
                    {
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
                            "alias_first -> neighborhood_before_file -> "
                            "status_surface_before_source"
                        ),
                        "semantic_preferred_neighborhood": "repo_governance",
                        "artifact_policy_status_line": (
                            "external_repo_intelligence=sidecar_only | "
                            "main_repo_install=no hooks=no protected_files=no"
                        ),
                        "admissibility_primary_status_line": "",
                    }
                ],
                "subjectivity_focus_preview": None,
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    assert payload["repo_intelligence_focus_preview"] == {
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


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "planner": {"recommendation": "defer_until_worktree_clean"},
        "worktree": {"dirty": True},
        "settlement_lanes": [],
        "summary": {"active_lane_count": 1},
        "next_checkpoint": {
            "command": "python scripts/plan_commit_attribution_base_switch.py --strict"
        },
        "boundary_notes": {"public_scope": [], "private_scope": []},
        "issues": ["dirty_worktree_blocks_branch_movement"],
        "warnings": [],
    }
    monkeypatch.setattr(
        settlement_runner,
        "build_report",
        lambda repo_root, sample_limit=5, backfill_ref="": (
            payload,
            "# Worktree Settlement Latest\n",
        ),
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_worktree_settlement_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = settlement_runner.main()

    assert exit_code == 1
    json_path = out_dir / settlement_runner.JSON_FILENAME
    md_path = out_dir / settlement_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["planner"]["recommendation"] == "defer_until_worktree_clean"
