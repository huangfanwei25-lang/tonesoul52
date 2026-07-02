# Worktree Settlement Latest

- Generated at: `2026-07-02T07:34:25Z`
- Overall OK: `false`
- Worktree dirty: `true`
- Planner recommendation: `no_switch_needed` (`tree_equal=false`)
- Attribution debt: current=`0`, backfill=`0`
- Subjectivity focus: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- Subjectivity admissibility: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`
- Dream observability: `dream_observability_ready | wakeup_cycles=1 schedule_cycles=1 warnings=1 overall_ok=yes`
- Dream runtime posture: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
- Dream problem route: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
- Dream artifact policy: `dashboard_inputs | wakeup=yes schedule=yes invalid_json=0`

## Weekly Host Status Mirror

- None

## Subjectivity Focus Mirror

- path: `docs/status/subjectivity_review_batch_latest.json`
- queue_shape: `monitoring_queue`
- requires_operator_action: `false`
- primary_status_line: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- admissibility_primary_status_line: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`

## Dream Observability Focus Mirror

- path: `docs/status/dream_observability_latest.json`
- queue_shape: `dream_observability_ready`
- requires_operator_action: `false`
- primary_status_line: `dream_observability_ready | wakeup_cycles=1 schedule_cycles=1 warnings=1 overall_ok=yes`
- runtime_status_line: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
- problem_route_status_line: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
- artifact_policy_status_line: `dashboard_inputs | wakeup=yes schedule=yes invalid_json=0`

## Repo Semantic Atlas Focus Mirror

- None

## Repo Intelligence Focus Mirror

- None

## Scribe Focus Mirror

- None

## Agent Integrity Focus Mirror

- None

## Settlement Order

1. **Refreshable Artifacts** (`entries=24`, `active=true`)
   - Goal: Separate reproducible outputs from authored source edits before any branch movement.
   - Exit criteria: No remaining dirty paths in generated outputs or reports, or an explicit decision to preserve them.
   - Action: Do not let generated status snapshots and derived reports drive branch-base decisions.
   - Action: Refresh, discard, or restage reproducible artifacts only after the authored source set is stable.
   - `generated_status`: count=`24`, staged=`0`, unstaged=`24`, untracked=`0`
     samples: `docs/status/autonomous_registry_schedule_latest.json`, `docs/status/dream_observability_latest.html`, `docs/status/dream_observability_latest.json`, `docs/status/dream_wakeup_snapshot_latest.json`, `docs/status/external_source_registry_latest.json`
   - Handoff previews: `5`
     - `docs/status/dream_observability_latest.json` (`dream_observability_ready`): `dream_observability_ready | wakeup_cycles=1 schedule_cycles=1 warnings=1 overall_ok=yes`
       runtime_status_line: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
       problem_route_status_line: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
       artifact_policy_status_line: `dashboard_inputs | wakeup=yes schedule=yes invalid_json=0`
       requires_operator_action: `false`
     - `docs/status/l8_adapter_dataset_gate_latest.json` (``): `l8_dataset_gate_ready | records=1 approved=1 rejected=0 load_issues=0`
       runtime_status_line: `entrypoints | input=spec/governance/adapter_dataset_record_v1.example.json schema=spec/governance/adapter_dataset_record_v1.schema.json contract=docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
       artifact_policy_status_line: `adapter_rows=public_safe_only | min_verifier_pass_rate_floor=0.90 private_memory=forbidden`
       requires_operator_action: `false`
     - `docs/status/subjectivity_report_latest.json` (`action_required`): `action_required | records=4 unresolved=2 deferred=0 settled=0 reviewed_vows=0 | top_unresolved_status=candidate`
       requires_operator_action: `true`
     - `docs/status/subjectivity_review_batch_latest.json` (`monitoring_queue`): `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
       requires_operator_action: `false`
       admissibility_primary_status_line: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`
     - `docs/status/subjectivity_tension_groups_latest.json` (`multi_group`): `same_source_loop_monitor | A distributed vulnerability database for Open Source | recommendation=reject_review | rows=1 lineages=1 cycles=1 | density=1r x1`
       requires_operator_action: `false`

2. **Private Memory Review** (`entries=0`, `active=false`)
   - Goal: Review private memory artifacts outside the public-branch settlement path.
   - Exit criteria: Private memory changes are either archived to the private path or consciously excluded from branch movement.
   - Action: Treat raw memory artifacts as private-evolution evidence, not ordinary public repo edits.
   - Action: Mirror only public-safe learnings into task/reflection/status artifacts when needed.

3. **Public Contract Docs** (`entries=0`, `active=false`)
   - Goal: Group public documentation and spec edits by owning implementation phase.
   - Exit criteria: Docs/spec edits are paired with their implementation or intentionally deferred.
   - Action: Settle docs and specs after generated artifacts are separated, but before final branch movement.
   - Action: Keep public docs aligned with the actual runtime and governance artifacts they describe.

4. **Runtime Source Changes** (`entries=0`, `active=false`)
   - Goal: Review high-signal code and contract changes as cohesive change groups.
   - Exit criteria: Core source edits are grouped into reviewable changesets with matching tests and docs.
   - Action: Keep tests paired with the code paths they validate instead of settling them independently.
   - Action: Treat scripts, runtime apps, and core `tonesoul` changes as the public source-of-truth lane.

5. **Experimental and Misc Review** (`entries=0`, `active=false`)
   - Goal: Resolve root-level drift and experimental assets deliberately instead of letting them hitchhike.
   - Exit criteria: Experimental and miscellaneous paths have an explicit keep/defer/drop decision.
   - Action: Decide whether experimental files belong to the public repo, a follow-up branch, or should be dropped.
   - Action: Review uncategorized root-level files manually before any git history movement.

## Notes

- Private memory paths remain governed by the dual-track boundary; settle them as private evidence, not as ordinary public branch content.
- Generated status artifacts and derived reports should be refreshed only after the authored source set is stable.
- Re-check branch movement readiness with `python scripts/plan_commit_attribution_base_switch.py --current-ref HEAD --backfill-ref feat/env-perception-attribution-backfill --strict` after settlement.
