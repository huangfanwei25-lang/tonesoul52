# Worktree Settlement Latest

- Generated at: `2026-03-11T16:16:46Z`
- Overall OK: `false`
- Worktree dirty: `true`
- Planner recommendation: `manual_review_required` (`tree_equal=false`)
- Attribution debt: current=`34`, backfill=`0`

## Subjectivity Focus Mirror

- path: `docs/status/subjectivity_review_batch_latest.json`
- queue_shape: `stable_history_only`
- requires_operator_action: `false`
- primary_status_line: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Settlement Order

1. **Refreshable Artifacts** (`entries=23`, `active=true`)
   - Goal: Separate reproducible outputs from authored source edits before any branch movement.
   - Exit criteria: No remaining dirty paths in generated outputs or reports, or an explicit decision to preserve them.
   - Action: Do not let generated status snapshots and derived reports drive branch-base decisions.
   - Action: Refresh, discard, or restage reproducible artifacts only after the authored source set is stable.
   - `generated_status`: count=`23`, staged=`0`, unstaged=`15`, untracked=`8`
     samples: `docs/status/refreshable_artifact_report_latest.json`, `docs/status/refreshable_artifact_report_latest.md`, `docs/status/repo_governance_settlement_latest.json`, `docs/status/repo_governance_settlement_latest.md`, `docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json`
   - Handoff previews: `3`
     - `docs/status/subjectivity_report_latest.json` (`deferred_monitoring`): `deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`
       requires_operator_action: `false`
     - `docs/status/subjectivity_review_batch_latest.json` (`stable_history_only`): `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
       requires_operator_action: `false`
       admissibility: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
     - `docs/status/subjectivity_tension_groups_latest.json` (`monitoring_queue`): `high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate`
       requires_operator_action: `false`

2. **Private Memory Review** (`entries=1`, `active=true`)
   - Goal: Review private memory artifacts outside the public-branch settlement path.
   - Exit criteria: Private memory changes are either archived to the private path or consciously excluded from branch movement.
   - Action: Treat raw memory artifacts as private-evolution evidence, not ordinary public repo edits.
   - Action: Mirror only public-safe learnings into task/reflection/status artifacts when needed.
   - `memory`: count=`1`, staged=`0`, unstaged=`1`, untracked=`0`
     samples: `memory/crystals.jsonl`

3. **Public Contract Docs** (`entries=35`, `active=true`)
   - Goal: Group public documentation and spec edits by owning implementation phase.
   - Exit criteria: Docs/spec edits are paired with their implementation or intentionally deferred.
   - Action: Settle docs and specs after generated artifacts are separated, but before final branch movement.
   - Action: Keep public docs aligned with the actual runtime and governance artifacts they describe.
   - `docs`: count=`35`, staged=`0`, unstaged=`2`, untracked=`33`
     samples: `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`, `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`, `docs/experiments/historical_viewpoint_audit_seed_2026-03-11.json`, `docs/plans/memory_subjectivity_admissibility_preview_mirror_addendum_2026-03-12.md`, `docs/plans/memory_subjectivity_admissibility_status_line_addendum_2026-03-11.md`

4. **Runtime Source Changes** (`entries=42`, `active=true`)
   - Goal: Review high-signal code and contract changes as cohesive change groups.
   - Exit criteria: Core source edits are grouped into reviewable changesets with matching tests and docs.
   - Action: Keep tests paired with the code paths they validate instead of settling them independently.
   - Action: Treat scripts, runtime apps, and core `tonesoul` changes as the public source-of-truth lane.
   - `scripts`: count=`16`, staged=`0`, unstaged=`4`, untracked=`12`
     samples: `scripts/run_refreshable_artifact_report.py`, `scripts/run_repo_governance_settlement_report.py`, `scripts/run_subjectivity_report.py`, `scripts/run_worktree_settlement_report.py`, `scripts/hunt_margin_safe_live.py`
   - `tests`: count=`16`, staged=`0`, unstaged=`8`, untracked=`8`
     samples: `tests/test_dream_engine.py`, `tests/test_reviewed_promotion.py`, `tests/test_run_refreshable_artifact_report.py`, `tests/test_run_repo_governance_settlement_report.py`, `tests/test_run_subjectivity_report.py`
   - `tonesoul`: count=`10`, staged=`0`, unstaged=`5`, untracked=`5`
     samples: `tonesoul/dream_engine.py`, `tonesoul/memory/__init__.py`, `tonesoul/memory/reviewed_promotion.py`, `tonesoul/memory/subjectivity_reporting.py`, `tonesoul/schemas.py`

5. **Experimental and Misc Review** (`entries=2`, `active=true`)
   - Goal: Resolve root-level drift and experimental assets deliberately instead of letting them hitchhike.
   - Exit criteria: Experimental and miscellaneous paths have an explicit keep/defer/drop decision.
   - Action: Decide whether experimental files belong to the public repo, a follow-up branch, or should be dropped.
   - Action: Review uncategorized root-level files manually before any git history movement.
   - `repo_misc`: count=`2`, staged=`0`, unstaged=`2`, untracked=`0`
     samples: `CODEX_TASK.md`, `task.md`

## Notes

- Private memory paths remain governed by the dual-track boundary; settle them as private evidence, not as ordinary public branch content.
- Generated status artifacts and derived reports should be refreshed only after the authored source set is stable.
- Re-check branch movement readiness with `python scripts/plan_commit_attribution_base_switch.py --current-ref HEAD --backfill-ref feat/env-perception-attribution-backfill --strict` after settlement.
