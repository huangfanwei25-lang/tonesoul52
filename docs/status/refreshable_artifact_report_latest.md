# Refreshable Artifact Report Latest

- Generated at: `2026-07-02T07:34:20Z`
- Overall OK: `false`
- Dirty refreshable entries: `10`
- Known regenerators: `8`
- Namespace regenerators: `0`
- Manual review items: `0`
- Archive-or-drop probe namespaces: `0`
- Inspect items: `2`
- Handoff previews: `2`
- Admissibility previews: `0`

## Subjectivity Focus

- None

## Handoff Previews

- `docs/status/dream_observability_latest.json`
  - queue_shape: `dream_observability_ready`
  - requires_operator_action: `false`
  - primary_status_line: `dream_observability_ready | wakeup_cycles=1 schedule_cycles=1 warnings=1 overall_ok=yes`
  - runtime_status_line: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
  - problem_route_status_line: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
  - artifact_policy_status_line: `dashboard_inputs | wakeup=yes schedule=yes invalid_json=0`
- `docs/status/l8_adapter_dataset_gate_latest.json`
  - queue_shape: ``
  - requires_operator_action: `false`
  - primary_status_line: `l8_dataset_gate_ready | records=1 approved=1 rejected=0 load_issues=0`
  - runtime_status_line: `entrypoints | input=spec/governance/adapter_dataset_record_v1.example.json schema=spec/governance/adapter_dataset_record_v1.schema.json contract=docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
  - artifact_policy_status_line: `adapter_rows=public_safe_only | min_verifier_pass_rate_floor=0.90 private_memory=forbidden`

## Regenerate

- `python scripts/run_autonomous_registry_schedule.py --strict`
  - count: `2`
  - source: `scripts/run_autonomous_registry_schedule.py`
  - path: `docs/status/autonomous_registry_schedule_latest.json`
  - path: `docs/status/dream_wakeup_snapshot_latest.json`
- `python scripts/run_dream_observability_dashboard.py --strict`
  - count: `2`
  - source: `scripts/run_dream_observability_dashboard.py`
  - path: `docs/status/dream_observability_latest.html`
  - path: `docs/status/dream_observability_latest.json`
- `python scripts/run_external_source_registry_check.py --strict`
  - count: `2`
  - source: `scripts/run_external_source_registry_check.py`
  - path: `docs/status/external_source_registry_latest.json`
  - path: `docs/status/external_source_registry_latest.md`
- `python scripts/run_private_memory_review_report.py`
  - count: `2`
  - source: `scripts/run_private_memory_review_report.py`
  - path: `docs/status/private_memory_review_latest.json`
  - path: `docs/status/private_memory_review_latest.md`

## Namespace Regenerate

- None

## Manual Review

- None

## Archive Or Drop

- None

## Inspect

- `docs/status/l8_adapter_dataset_gate_latest.json` (`generated_status_artifact`)
- `docs/status/l8_adapter_dataset_gate_latest.md` (`generated_status_artifact`)
