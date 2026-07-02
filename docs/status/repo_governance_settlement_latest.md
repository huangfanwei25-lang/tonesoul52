# Repo Governance Settlement Latest

- Generated at: `2026-07-02T07:34:20Z`
- Overall OK: `false`
- Settlement status: `runtime_blocked`
- Healthcheck generated at: `2026-06-01T12:52:32Z`
- Healthcheck pass/fail: `17` / `4`
- Failing checks: `python_lint, python_format, git_hygiene, skill_registry`
- Metadata-only blocker: `false`
- Runtime green except attribution: `false`

## Attribution

- Planner recommendation: `defer_until_worktree_clean`
- Tree equal: `true`
- Missing trailers: current=`5`, backfill=`0`

## Repo Governance Group

- Dirty entries in repo governance group: `24`
- Sample: `.github/workflows/test.yml`
- Sample: `scripts/healthcheck.py`
- Sample: `scripts/run_repo_healthcheck.py`
- Sample: `scripts/verify_7d.py`
- Sample: `scripts/verify_command_registry.py`
- Sample: `scripts/verify_docs_consistency.py`
- Sample: `tests/test_agent_discussion_tool.py`
- Sample: `tests/test_run_repo_healthcheck.py`

## Worktree Settlement Mirror

- Worktree dirty: `true`
- Planner recommendation: `manual_review_required`
- Refreshable handoff previews: `3`
- Refreshable admissibility previews: `1`
- Subjectivity focus: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- Subjectivity admissibility: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Subjectivity Focus Mirror

- path: `docs/status/subjectivity_review_batch_latest.json`
- queue_shape: `stable_history_only`
- requires_operator_action: `false`
- primary_status_line: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

- `docs/status/subjectivity_report_latest.json` (`deferred_monitoring`): `deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`
  - requires_operator_action: `false`
- `docs/status/subjectivity_review_batch_latest.json` (`stable_history_only`): `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
  - requires_operator_action: `false`
  - admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
- `docs/status/subjectivity_tension_groups_latest.json` (`monitoring_queue`): `high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate`
  - requires_operator_action: `false`

## Next Actions

- Resolve the non-attribution blocking checks before treating repo governance as converged.
- Use the healthcheck artifact as the source of truth for which blocking gates still fail.
