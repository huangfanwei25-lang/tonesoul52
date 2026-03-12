# Refreshable Artifact Report Latest

- Generated at: `2026-03-11T16:16:35Z`
- Overall OK: `false`
- Dirty refreshable entries: `23`
- Known regenerators: `14`
- Namespace regenerators: `9`
- Manual review items: `0`
- Archive-or-drop probe namespaces: `0`
- Inspect items: `0`
- Handoff previews: `3`
- Admissibility previews: `1`

## Subjectivity Focus

- path: `docs/status/subjectivity_review_batch_latest.json`
- queue_shape: `stable_history_only`
- requires_operator_action: `false`
- primary_status_line: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Handoff Previews

- `docs/status/subjectivity_report_latest.json`
  - queue_shape: `deferred_monitoring`
  - requires_operator_action: `false`
  - primary_status_line: `deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`
- `docs/status/subjectivity_review_batch_latest.json`
  - queue_shape: `stable_history_only`
  - requires_operator_action: `false`
  - primary_status_line: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
  - admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
- `docs/status/subjectivity_tension_groups_latest.json`
  - queue_shape: `monitoring_queue`
  - requires_operator_action: `false`
  - primary_status_line: `high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate`

## Regenerate

- `python scripts/run_refreshable_artifact_report.py`
  - count: `2`
  - source: `scripts/run_refreshable_artifact_report.py`
  - path: `docs/status/refreshable_artifact_report_latest.json`
  - path: `docs/status/refreshable_artifact_report_latest.md`
- `python scripts/run_repo_governance_settlement_report.py`
  - count: `2`
  - source: `scripts/run_repo_governance_settlement_report.py`
  - path: `docs/status/repo_governance_settlement_latest.json`
  - path: `docs/status/repo_governance_settlement_latest.md`
- `python scripts/run_subjectivity_report.py --strict`
  - count: `2`
  - source: `scripts/run_subjectivity_report.py`
  - path: `docs/status/subjectivity_report_latest.json`
  - path: `docs/status/subjectivity_report_latest.md`
- `python scripts/run_subjectivity_review_batch.py`
  - count: `2`
  - source: `scripts/run_subjectivity_review_batch.py`
  - path: `docs/status/subjectivity_review_batch_latest.json`
  - path: `docs/status/subjectivity_review_batch_latest.md`
- `python scripts/run_subjectivity_shadow_pressure_report.py`
  - count: `2`
  - source: `scripts/run_subjectivity_shadow_pressure_report.py`
  - path: `docs/status/subjectivity_shadow_pressure_latest.json`
  - path: `docs/status/subjectivity_shadow_pressure_latest.md`
- `python scripts/run_subjectivity_tension_grouping.py`
  - count: `2`
  - source: `scripts/run_subjectivity_tension_grouping.py`
  - path: `docs/status/subjectivity_tension_groups_latest.json`
  - path: `docs/status/subjectivity_tension_groups_latest.md`
- `python scripts/run_worktree_settlement_report.py`
  - count: `2`
  - source: `scripts/run_worktree_settlement_report.py`
  - path: `docs/status/worktree_settlement_latest.json`
  - path: `docs/status/worktree_settlement_latest.md`

## Namespace Regenerate

- `docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/dream_observability_latest.html` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/dream_observability_latest.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/dream_wakeup_snapshot.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/preflight/autonomous_registry_schedule_latest.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/preflight/dream_observability_latest.html` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/preflight/dream_observability_latest.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/preflight/dream_wakeup_snapshot.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`
- `docs/status/true_verification_weekly/true_verification_host_tick_latest.json` (`operational_namespace`)
  - notes: `Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.`
  - command: `python scripts/run_true_verification_host_tick.py --strict`
  - command: `python scripts/report_true_verification_task_status.py --strict`
  - command: `python scripts/render_true_verification_task_scheduler.py --strict`
  - command: `python scripts/install_true_verification_task_scheduler.py --strict`
  - source: `scripts/run_true_verification_host_tick.py`
  - source: `scripts/report_true_verification_task_status.py`
  - source: `scripts/render_true_verification_task_scheduler.py`
  - source: `scripts/install_true_verification_task_scheduler.py`

## Manual Review

- None

## Archive Or Drop

- None

## Inspect

- None
