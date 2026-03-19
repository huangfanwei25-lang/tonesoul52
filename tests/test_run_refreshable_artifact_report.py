from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_refreshable_artifact_report as artifact_report


def _entries() -> list[dict[str, object]]:
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
            "status": " M",
            "path": "docs/status/probe_deadline/",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/runtime_probe_watch/",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/true_verification_weekly/",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/dream_observability_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/private_memory_review_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/runtime_source_change_groups_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/subjectivity_shadow_pressure_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/subjectivity_tension_groups_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/subjectivity_tension_groups_latest.md",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/subjectivity_review_batch_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/subjectivity_review_batch_latest.md",
            "staged": False,
            "unstaged": False,
            "untracked": True,
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
            "status": "??",
            "path": "reports/analysis_gpt53.md",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "reports",
        },
        {
            "status": " M",
            "path": "docs/status/README.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "docs",
        },
    ]


def test_build_report_classifies_known_generated_and_manual_inputs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        artifact_report.planner, "collect_worktree_entries", lambda repo_root: _entries()
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["overall_ok"] is False
    assert payload["summary"]["entry_count"] == 14
    assert payload["summary"]["regenerate_count"] == 10
    assert payload["summary"]["namespace_regenerate_count"] == 2
    assert payload["summary"]["manual_review_count"] == 1
    assert payload["summary"]["archive_or_drop_count"] == 1
    assert payload["summary"]["inspect_count"] == 0
    assert payload["summary"]["handoff_preview_count"] == 0
    assert payload["summary"]["admissibility_preview_count"] == 0
    assert payload["subjectivity_focus_preview"] is None

    entries = {item["path"]: item for item in payload["entries"]}
    assert entries["docs/status/repo_healthcheck_latest.json"]["disposition"] == "regenerate"
    assert (
        "run_repo_healthcheck.py"
        in entries["docs/status/repo_healthcheck_latest.json"]["producer_source"]
    )
    assert entries["docs/status/dream_observability_latest.json"]["disposition"] == "regenerate"
    assert entries["docs/status/private_memory_review_latest.json"]["disposition"] == "regenerate"
    assert (
        entries["docs/status/runtime_source_change_groups_latest.json"]["disposition"]
        == "regenerate"
    )
    assert (
        entries["docs/status/subjectivity_shadow_pressure_latest.json"]["disposition"]
        == "regenerate"
    )
    assert (
        entries["docs/status/subjectivity_tension_groups_latest.json"]["disposition"]
        == "regenerate"
    )
    assert (
        entries["docs/status/subjectivity_tension_groups_latest.md"]["disposition"] == "regenerate"
    )
    assert (
        entries["docs/status/subjectivity_review_batch_latest.json"]["disposition"] == "regenerate"
    )
    assert entries["docs/status/subjectivity_review_batch_latest.md"]["disposition"] == "regenerate"
    assert entries["reports/model_comparison_latest.json"]["disposition"] == "regenerate"
    assert entries["reports/analysis_gpt53.md"]["disposition"] == "manual_review"
    assert entries["docs/status/probe_deadline/"]["disposition"] == "archive_or_drop"
    assert entries["docs/status/runtime_probe_watch/"]["disposition"] == "namespace_regenerate"
    assert (
        "python scripts/run_runtime_probe_watch.py --strict"
        in entries["docs/status/runtime_probe_watch/"]["namespace_commands"]
    )
    assert entries["docs/status/true_verification_weekly/"]["disposition"] == "namespace_regenerate"
    assert "docs/status/README.md" not in entries
    assert "reports/analysis_gpt53.md" in markdown
    assert "python scripts/run_subjectivity_shadow_pressure_report.py" in markdown
    assert "python scripts/run_subjectivity_tension_grouping.py" in markdown
    assert "python scripts/run_subjectivity_review_batch.py" in markdown
    assert "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion" in markdown
    assert "python scripts/run_runtime_probe_watch.py --strict" in markdown
    assert "Historical probe namespace" in markdown


def test_build_report_is_clean_when_no_refreshable_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(artifact_report.planner, "collect_worktree_entries", lambda repo_root: [])

    payload, _ = artifact_report.build_report(tmp_path)

    assert payload["overall_ok"] is True
    assert payload["summary"]["entry_count"] == 0
    assert payload["summary"]["handoff_preview_count"] == 0
    assert payload["summary"]["admissibility_preview_count"] == 0
    assert payload["subjectivity_focus_preview"] is None
    assert payload["issues"] == []


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_refreshable_artifact_report.py",
        "summary": {
            "entry_count": 2,
            "regenerate_count": 1,
            "namespace_regenerate_count": 0,
            "manual_review_count": 1,
            "archive_or_drop_count": 0,
            "inspect_count": 0,
            "kind_counts": [],
            "category_counts": [],
            "disposition_counts": [],
        },
        "regenerate_groups": [],
        "namespace_groups": [],
        "archive_groups": [],
        "entries": [],
        "issues": ["refreshable_artifacts_lane_still_dirty"],
        "warnings": [],
    }
    monkeypatch.setattr(
        artifact_report, "build_report", lambda repo_root: (payload, "# Refreshable\n")
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_refreshable_artifact_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = artifact_report.main()

    assert exit_code == 1
    json_path = out_dir / artifact_report.JSON_FILENAME
    md_path = out_dir / artifact_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["summary"]["entry_count"] == 2


def test_build_report_surfaces_handoff_previews_for_subjectivity_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "subjectivity_report_latest.json").write_text(
        json.dumps(
            {
                "handoff": {
                    "queue_shape": "deferred_monitoring",
                    "requires_operator_action": False,
                    "top_unresolved_status": "deferred",
                    "primary_status_line": (
                        "deferred_monitoring | records=195 unresolved=50 deferred=50 "
                        "settled=31 reviewed_vows=0 | top_unresolved_status=deferred"
                    ),
                },
                "primary_status_line": (
                    "deferred_monitoring | records=195 unresolved=50 deferred=50 "
                    "settled=31 reviewed_vows=0 | top_unresolved_status=deferred"
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (status_dir / "subjectivity_review_batch_latest.json").write_text(
        json.dumps(
            {
                "batch": {
                    "handoff": {
                        "queue_shape": "stable_history_only",
                        "requires_operator_action": False,
                        "top_queue_posture": "stable_deferred_history",
                        "primary_status_line": (
                            "stable_deferred_history | A distributed vulnerability database for "
                            "Open Source | rows=50 lineages=12 cycles=30 | "
                            "trigger=second_source_context_or_material_split"
                        ),
                        "runtime_status_line": (
                            "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7 "
                            "singleton_lineages=3 dense_lineages=2"
                        ),
                        "artifact_policy_status_line": (
                            "subjectivity_batch_artifacts_ready | strict=true review_groups=2 "
                            "status_lines=2"
                        ),
                    },
                    "primary_status_line": (
                        "stable_deferred_history | A distributed vulnerability database for "
                        "Open Source | rows=50 lineages=12 cycles=30 | "
                        "trigger=second_source_context_or_material_split"
                    ),
                    "runtime_status_line": (
                        "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7 "
                        "singleton_lineages=3 dense_lineages=2"
                    ),
                    "artifact_policy_status_line": (
                        "subjectivity_batch_artifacts_ready | strict=true review_groups=2 "
                        "status_lines=2"
                    ),
                    "admissibility_primary_status_line": (
                        "admissibility_not_yet_clear | focus=authority_and_exception_pressure | "
                        "tags=cross_cycle_persistence, exception_pressure, "
                        "externalized_harm_check, low_context_diversity"
                    ),
                }
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": "??",
                "path": "docs/status/subjectivity_report_latest.md",
                "staged": False,
                "unstaged": False,
                "untracked": True,
                "category": "generated_status",
            },
            {
                "status": "??",
                "path": "docs/status/subjectivity_review_batch_latest.json",
                "staged": False,
                "unstaged": False,
                "untracked": True,
                "category": "generated_status",
            },
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["handoff_preview_count"] == 2
    assert payload["summary"]["admissibility_preview_count"] == 1
    assert payload["subjectivity_focus_preview"] == {
        "path": "docs/status/subjectivity_review_batch_latest.json",
        "queue_shape": "stable_history_only",
        "requires_operator_action": "false",
        "primary_status_line": (
            "stable_deferred_history | A distributed vulnerability database for "
            "Open Source | rows=50 lineages=12 cycles=30 | "
            "trigger=second_source_context_or_material_split"
        ),
        "runtime_status_line": (
            "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7 "
            "singleton_lineages=3 dense_lineages=2"
        ),
        "anchor_status_line": "",
        "artifact_policy_status_line": (
            "subjectivity_batch_artifacts_ready | strict=true review_groups=2 " "status_lines=2"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure | "
            "tags=cross_cycle_persistence, exception_pressure, "
            "externalized_harm_check, low_context_diversity"
        ),
    }
    assert payload["handoff_previews"] == [
        {
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
            "admissibility_primary_status_line": "",
        },
        {
            "path": "docs/status/subjectivity_review_batch_latest.json",
            "queue_shape": "stable_history_only",
            "requires_operator_action": "false",
            "primary_status_line": (
                "stable_deferred_history | A distributed vulnerability database for "
                "Open Source | rows=50 lineages=12 cycles=30 | "
                "trigger=second_source_context_or_material_split"
            ),
            "runtime_status_line": (
                "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7 "
                "singleton_lineages=3 dense_lineages=2"
            ),
            "anchor_status_line": "",
            "artifact_policy_status_line": (
                "subjectivity_batch_artifacts_ready | strict=true review_groups=2 " "status_lines=2"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure | "
                "tags=cross_cycle_persistence, exception_pressure, "
                "externalized_harm_check, low_context_diversity"
            ),
        },
    ]
    assert "## Subjectivity Focus" in markdown
    assert "## Handoff Previews" in markdown
    assert "requires_operator_action" in markdown
    assert "`docs/status/subjectivity_report_latest.json`" in markdown
    assert "deferred_monitoring" in markdown
    assert "stable_history_only" in markdown
    assert "Admissibility previews: `1`" in markdown
    assert "runtime_status_line" in markdown
    assert "artifact_policy_status_line" in markdown
    assert "admissibility_primary_status_line" in markdown


def test_extract_handoff_surface_reads_artifact_and_admissibility_from_handoff_only() -> None:
    payload = {
        "primary_status_line": (
            "stable_deferred_history | A distributed vulnerability database for Open Source"
        ),
        "handoff": {
            "queue_shape": "stable_history_only",
            "primary_status_line": (
                "stable_deferred_history | A distributed vulnerability database for Open Source"
            ),
            "runtime_status_line": "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7",
            "semantic_retrieval_protocol": (
                "alias_first -> neighborhood_before_file -> status_surface_before_source"
            ),
            "semantic_preferred_neighborhood": "repo_governance",
            "artifact_policy_status_line": (
                "artifact_policy_ready | strict=true install=present template=present"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "requires_operator_action": False,
        },
    }

    assert artifact_report._extract_handoff_surface(payload) == {
        "queue_shape": "stable_history_only",
        "primary_status_line": (
            "stable_deferred_history | A distributed vulnerability database for Open Source"
        ),
        "runtime_status_line": "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7",
        "anchor_status_line": "",
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "artifact_policy_status_line": (
            "artifact_policy_ready | strict=true install=present template=present"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "requires_operator_action": "false",
    }


def test_build_report_surfaces_true_verification_task_status_preview(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    weekly_dir = tmp_path / "docs" / "status" / "true_verification_weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    (weekly_dir / "true_verification_task_status_latest.json").write_text(
        json.dumps(
            {
                "overall_ok": True,
                "primary_status_line": (
                    "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                    "runtime_source=host_tick session=weekly-session resumed=yes"
                ),
                "runtime_status_line": (
                    "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                    "failures=1 max_failure=1 tension=breached"
                ),
                "dream_weekly_alignment_line": (
                    "dream_weekly_alignment | alignment=aligned "
                    "weekly=F1_grounding_evidence_integrity "
                    "dream=F1_grounding_evidence_integrity"
                ),
                "handoff": {
                    "queue_shape": "weekly_host_status",
                    "primary_status_line": (
                        "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                        "runtime_source=host_tick session=weekly-session resumed=yes"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 1
    assert payload["summary"]["regenerate_count"] == 1
    assert payload["summary"]["namespace_regenerate_count"] == 0
    assert payload["summary"]["handoff_preview_count"] == 1
    assert payload["summary"]["admissibility_preview_count"] == 0
    entry = payload["entries"][0]
    assert (
        entry["path"]
        == "docs/status/true_verification_weekly/true_verification_task_status_latest.json"
    )
    assert entry["disposition"] == "regenerate"
    assert (
        entry["producer_command"]
        == "python scripts/report_true_verification_task_status.py --strict"
    )
    assert entry["producer_source"] == "scripts/report_true_verification_task_status.py"
    assert payload["handoff_previews"] == [
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
            "anchor_status_line": "",
            "dream_weekly_alignment_line": (
                "dream_weekly_alignment | alignment=aligned "
                "weekly=F1_grounding_evidence_integrity "
                "dream=F1_grounding_evidence_integrity"
            ),
            "artifact_policy_status_line": "",
            "admissibility_primary_status_line": "",
        }
    ]
    assert payload["subjectivity_focus_preview"] is None
    assert "weekly_host_status" in markdown
    assert "dream_weekly_alignment_line" in markdown
    assert "python scripts/report_true_verification_task_status.py --strict" in markdown


def test_build_report_preserves_dream_weekly_alignment_from_handoff_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    weekly_dir = tmp_path / "docs" / "status" / "true_verification_weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    (weekly_dir / "true_verification_task_status_latest.json").write_text(
        json.dumps(
            {
                "overall_ok": True,
                "primary_status_line": (
                    "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                    "runtime_source=host_tick session=weekly-session resumed=yes"
                ),
                "handoff": {
                    "queue_shape": "weekly_host_status",
                    "primary_status_line": (
                        "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                        "runtime_source=host_tick session=weekly-session resumed=yes"
                    ),
                    "dream_weekly_alignment_line": (
                        "dream_weekly_alignment | alignment=aligned "
                        "weekly=F1_grounding_evidence_integrity "
                        "dream=F1_grounding_evidence_integrity"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["handoff_previews"] == [
        {
            "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
            "queue_shape": "weekly_host_status",
            "requires_operator_action": "false",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "runtime_status_line": "",
            "anchor_status_line": "",
            "dream_weekly_alignment_line": (
                "dream_weekly_alignment | alignment=aligned "
                "weekly=F1_grounding_evidence_integrity "
                "dream=F1_grounding_evidence_integrity"
            ),
            "artifact_policy_status_line": "",
            "admissibility_primary_status_line": "",
        }
    ]
    assert "dream_weekly_alignment_line" in markdown


def test_build_report_preserves_scribe_compact_lines_from_handoff_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "scribe_status_latest.json").write_text(
        json.dumps(
            {
                "status": "generated",
                "primary_status_line": (
                    "generated | mode=template_assist model=gemma3:4b "
                    "fallback_mode=observed_history attempts=2 latest=chronicle_pair"
                ),
                "handoff": {
                    "queue_shape": "scribe_chronicle_ready",
                    "primary_status_line": (
                        "generated | mode=template_assist model=gemma3:4b "
                        "fallback_mode=observed_history attempts=2 latest=chronicle_pair"
                    ),
                    "scribe_status_line": (
                        "state_document | tensions=1 collisions=0 crystals=0 "
                        "posture=pressure_without_counterweight"
                    ),
                    "anchor_status_line": (
                        "anchor | [tension_afbd38eb] tension: High PE valuation "
                        "(46.7x) in a market pullback..."
                    ),
                    "problem_route_status_line": (
                        "route | family=F6_semantic_role_boundary_integrity "
                        "invariant=chronicle_self_scope "
                        "repair=semantic_boundary_guardrail "
                        "secondary=F4_execution_contract_integrity"
                    ),
                    "problem_route_secondary_labels": "F4_execution_contract_integrity",
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/scribe_status_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["handoff_previews"] == [
        {
            "path": "docs/status/scribe_status_latest.json",
            "queue_shape": "scribe_chronicle_ready",
            "requires_operator_action": "false",
            "primary_status_line": (
                "generated | mode=template_assist model=gemma3:4b "
                "fallback_mode=observed_history attempts=2 latest=chronicle_pair"
            ),
            "runtime_status_line": "",
            "scribe_status_line": (
                "state_document | tensions=1 collisions=0 crystals=0 "
                "posture=pressure_without_counterweight"
            ),
            "anchor_status_line": (
                "anchor | [tension_afbd38eb] tension: High PE valuation "
                "(46.7x) in a market pullback..."
            ),
            "problem_route_status_line": (
                "route | family=F6_semantic_role_boundary_integrity "
                "invariant=chronicle_self_scope "
                "repair=semantic_boundary_guardrail "
                "secondary=F4_execution_contract_integrity"
            ),
            "problem_route_secondary_labels": "F4_execution_contract_integrity",
            "artifact_policy_status_line": "",
            "admissibility_primary_status_line": "",
        }
    ]
    assert "scribe_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown


def test_build_report_surfaces_scribe_status_preview(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "scribe_status_latest.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-03-13T04:23:10Z",
                "status": "generated",
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
                "handoff": {
                    "queue_shape": "scribe_chronicle_ready",
                    "primary_status_line": (
                        "generated | mode=llm_chronicle model=gemma3:4b fallback_mode=bootstrap_reflection "
                        "attempts=2 latest=chronicle_pair"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/scribe_status_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 1
    assert payload["summary"]["regenerate_count"] == 1
    entry = payload["entries"][0]
    assert entry["path"] == "docs/status/scribe_status_latest.json"
    assert entry["disposition"] == "regenerate"
    assert entry["producer_command"] == "python scripts/run_scribe_cycle.py"
    assert entry["producer_source"] == "scripts/run_scribe_cycle.py"
    assert payload["handoff_previews"] == [
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
    assert "scribe_chronicle_ready" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "python scripts/run_scribe_cycle.py" in markdown


def test_build_report_surfaces_dream_observability_preview(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "dream_observability_latest.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-03-14T12:00:00Z",
                "overall_ok": True,
                "primary_status_line": (
                    "dream_observability_ready | wakeup_cycles=2 schedule_cycles=1 "
                    "warnings=0 overall_ok=yes"
                ),
                "runtime_status_line": (
                    "wakeup_scribe | status=generated "
                    "posture=pressure_without_counterweight source=chronicle_pair"
                ),
                "problem_route_status_line": (
                    "route | family=F6_semantic_role_boundary_integrity "
                    "invariant=chronicle_self_scope "
                    "repair=semantic_boundary_guardrail "
                    "secondary=F4_execution_contract_integrity"
                ),
                "problem_route_secondary_labels": "F4_execution_contract_integrity",
                "artifact_policy_status_line": (
                    "dashboard_inputs | wakeup=yes schedule=yes invalid_json=0"
                ),
                "handoff": {
                    "queue_shape": "dream_observability_ready",
                    "primary_status_line": (
                        "dream_observability_ready | wakeup_cycles=2 schedule_cycles=1 "
                        "warnings=0 overall_ok=yes"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/dream_observability_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["handoff_previews"] == [
        {
            "path": "docs/status/dream_observability_latest.json",
            "queue_shape": "dream_observability_ready",
            "requires_operator_action": "false",
            "primary_status_line": (
                "dream_observability_ready | wakeup_cycles=2 schedule_cycles=1 "
                "warnings=0 overall_ok=yes"
            ),
            "runtime_status_line": (
                "wakeup_scribe | status=generated "
                "posture=pressure_without_counterweight source=chronicle_pair"
            ),
            "anchor_status_line": "",
            "problem_route_status_line": (
                "route | family=F6_semantic_role_boundary_integrity "
                "invariant=chronicle_self_scope "
                "repair=semantic_boundary_guardrail "
                "secondary=F4_execution_contract_integrity"
            ),
            "problem_route_secondary_labels": "F4_execution_contract_integrity",
            "artifact_policy_status_line": (
                "dashboard_inputs | wakeup=yes schedule=yes invalid_json=0"
            ),
            "admissibility_primary_status_line": "",
        }
    ]
    assert "dream_observability_ready" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "python scripts/run_dream_observability_dashboard.py --strict" in markdown


def test_build_report_registers_repo_intelligence_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "repo_intelligence_latest.json").write_text(
        json.dumps(
            {
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
                "handoff": {
                    "queue_shape": "repo_intelligence_ready",
                    "primary_status_line": (
                        "repo_intelligence_ready | available_surfaces=5/5 "
                        "protected_files=5 watched_dirs=3 adoption=sidecar_only"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/repo_intelligence_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 1
    entry = payload["entries"][0]
    assert entry["path"] == "docs/status/repo_intelligence_latest.json"
    assert entry["disposition"] == "regenerate"
    assert entry["producer_command"] == "python scripts/run_repo_intelligence_report.py"
    assert entry["producer_source"] == "scripts/run_repo_intelligence_report.py"
    assert payload["handoff_previews"] == [
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
    ]
    assert "repo_intelligence_ready" in markdown
    assert "python scripts/run_repo_intelligence_report.py" in markdown
    assert "semantic_retrieval_protocol" in markdown
    assert "semantic_preferred_neighborhood" in markdown


def test_build_report_registers_repo_semantic_atlas_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "repo_semantic_atlas_latest.json").write_text(
        json.dumps(
            {
                "primary_status_line": (
                    "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
                    "chronicles=1 graph_edges=7"
                ),
                "runtime_status_line": (
                    "entrypoints | atlas=repo_semantic_atlas_latest.json "
                    "repo=repo_healthcheck_latest.json "
                    "dream=dream_observability_latest.json "
                    "weekly=true_verification_task_status_latest.json "
                    "scribe=scribe_status_latest.json"
                ),
                "artifact_policy_status_line": (
                    "semantic_map=domain_level | aliases=source_declared graph=passive_no_reparse"
                ),
                "handoff": {
                    "queue_shape": "repo_semantic_atlas_ready",
                    "primary_status_line": (
                        "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
                        "chronicles=1 graph_edges=7"
                    ),
                    "requires_operator_action": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/repo_semantic_atlas_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 1
    entry = payload["entries"][0]
    assert entry["path"] == "docs/status/repo_semantic_atlas_latest.json"
    assert entry["disposition"] == "regenerate"
    assert entry["producer_command"] == "python scripts/run_repo_semantic_atlas.py"
    assert entry["producer_source"] == "scripts/run_repo_semantic_atlas.py"
    assert payload["handoff_previews"] == [
        {
            "path": "docs/status/repo_semantic_atlas_latest.json",
            "queue_shape": "repo_semantic_atlas_ready",
            "requires_operator_action": "false",
            "primary_status_line": (
                "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 chronicles=1 graph_edges=7"
            ),
            "runtime_status_line": (
                "entrypoints | atlas=repo_semantic_atlas_latest.json "
                "repo=repo_healthcheck_latest.json "
                "dream=dream_observability_latest.json "
                "weekly=true_verification_task_status_latest.json "
                "scribe=scribe_status_latest.json"
            ),
            "anchor_status_line": "",
            "artifact_policy_status_line": (
                "semantic_map=domain_level | aliases=source_declared graph=passive_no_reparse"
            ),
            "admissibility_primary_status_line": "",
        }
    ]
    assert "repo_semantic_atlas_ready" in markdown
    assert "python scripts/run_repo_semantic_atlas.py" in markdown


def test_build_report_registers_agent_integrity_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "agent_integrity_latest.json").write_text(
        json.dumps(
            {
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
                "handoff": {
                    "queue_shape": "agent_integrity_guarded",
                    "primary_status_line": (
                        "agent_integrity_warning | errors=0 warnings=1 "
                        "review_dirs=2 protected_files=3"
                    ),
                    "requires_operator_action": False,
                    "path": "docs/status/agent_integrity_latest.json",
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        artifact_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "docs/status/agent_integrity_latest.json",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "generated_status",
            }
        ],
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 1
    entry = payload["entries"][0]
    assert entry["path"] == "docs/status/agent_integrity_latest.json"
    assert entry["producer_command"] == "python scripts/run_agent_integrity_report.py --strict"
    assert entry["producer_source"] == "scripts/run_agent_integrity_report.py"
    assert payload["handoff_previews"] == [
        {
            "path": "docs/status/agent_integrity_latest.json",
            "queue_shape": "agent_integrity_guarded",
            "requires_operator_action": "false",
            "primary_status_line": (
                "agent_integrity_warning | errors=0 warnings=1 " "review_dirs=2 protected_files=3"
            ),
            "runtime_status_line": (
                "integrity_contract | contract=agent_integrity_contract.py "
                "checker=check_agent_integrity.py workflow=agent-integrity-check.yml"
            ),
            "anchor_status_line": "",
            "artifact_policy_status_line": (
                "protected_hashes=blocking | hidden_chars=blocking | "
                "embedded_metadata=warning | watched_dirs=review_only"
            ),
            "admissibility_primary_status_line": "",
            "problem_route_status_line": (
                "integrity | family=G1_integrity_contract_drift "
                "invariant=embedded_expected_hash_metadata "
                "repair=protected_file_documentation"
            ),
        }
    ]
    assert "agent_integrity_warning" in markdown
    assert "python scripts/run_agent_integrity_report.py --strict" in markdown
