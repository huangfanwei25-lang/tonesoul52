# Changed Surface Checks Latest

- generated_at: 2026-07-02T07:34:25Z
- plan_ok: true
- checks_ok: null
- execution_mode: plan
- changed_path_count: 26
- surface_count: 1
- planned_check_count: 3
- blocking_check_count: 3
- failed_check_count: 0

## Surfaces
- `docs_governance` (26): Docs, workflow, or authority files changed and need consistency verification.
  - `docs/status/autonomous_registry_schedule_latest.json`
  - `docs/status/dream_observability_latest.html`
  - `docs/status/dream_observability_latest.json`
  - `docs/status/dream_wakeup_snapshot_latest.json`
  - `docs/status/external_source_registry_latest.json`
  - `docs/status/external_source_registry_latest.md`
  - `docs/status/l8_adapter_dataset_gate_latest.json`
  - `docs/status/l8_adapter_dataset_gate_latest.md`

## Checks
- `protected_paths` [planned]: `python scripts/verify_protected_paths.py --repo-root . --strict --changed-file docs/status/autonomous_registry_schedule_latest.json --changed-file docs/status/dream_observability_latest.html --changed-file docs/status/dream_observability_latest.json --changed-file docs/status/dream_wakeup_snapshot_latest.json --changed-file docs/status/external_source_registry_latest.json --changed-file docs/status/external_source_registry_latest.md --changed-file docs/status/l8_adapter_dataset_gate_latest.json --changed-file docs/status/l8_adapter_dataset_gate_latest.md --changed-file docs/status/private_memory_review_latest.json --changed-file docs/status/private_memory_review_latest.md --changed-file docs/status/refreshable_artifact_report_latest.json --changed-file docs/status/refreshable_artifact_report_latest.md --changed-file docs/status/repo_governance_settlement_latest.json --changed-file docs/status/repo_governance_settlement_latest.md --changed-file docs/status/runtime_source_change_groups_latest.json --changed-file docs/status/runtime_source_change_groups_latest.md --changed-file docs/status/subjectivity_report_latest.json --changed-file docs/status/subjectivity_report_latest.md --changed-file docs/status/subjectivity_review_batch_latest.json --changed-file docs/status/subjectivity_review_batch_latest.md --changed-file docs/status/subjectivity_shadow_pressure_latest.json --changed-file docs/status/subjectivity_shadow_pressure_latest.md --changed-file docs/status/subjectivity_tension_groups_latest.json --changed-file docs/status/subjectivity_tension_groups_latest.md --changed-file docs/status/worktree_settlement_latest.json --changed-file docs/status/worktree_settlement_latest.md`
  - reason: Fail closed when protected files or private memory paths are touched.
  - blocking: true
  - surfaces: `docs_governance`
- `docs_consistency` [planned]: `python scripts/verify_docs_consistency.py --repo-root .`
  - reason: Authority and workflow docs must remain consistent with runtime enforcement.
  - blocking: true
  - surfaces: `docs_governance`
- `python_full_regression` [planned]: `python -m pytest tests -x --tb=short -q`
  - reason: The change surface is broad or critical enough to require full Python regression.
  - blocking: true
  - surfaces: `docs_governance`
