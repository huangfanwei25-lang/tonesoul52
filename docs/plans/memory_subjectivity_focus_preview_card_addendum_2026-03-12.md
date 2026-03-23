# Memory Subjectivity Focus Preview Card Addendum (2026-03-12)

> Purpose: add a compact focus-preview card so higher mirrors can show live deferred posture and admissibility blockers at a glance.
> Last Updated: 2026-03-23

## Why This Addendum Exists

Once queue posture and admissibility posture both reached the higher mirrors,
the next operator problem was no longer missing data.

It was scan cost.

The higher layers could already show three subjectivity previews:

- report
- grouping
- review batch

But only one of them actually carried the branch's most important unresolved
truth:

- the live deferred queue posture
- and the live admissibility blocker

That meant the operator still had to visually search the preview list to find
the one line that mattered most.

## What This Phase Adds

This phase adds one compact mirror-only focus card:

- `subjectivity_focus_preview`

The rule is still conservative:

- select from already mirrored preview objects
- prefer the preview that already carries `admissibility_primary_status_line`
- do not recompute review semantics
- do not infer a new blocker

So the higher layers now expose not just a list of previews, but one explicit
focus card for interruption recovery.

## New Surface

This phase adds:

- `subjectivity_focus_preview` on `refreshable_artifact_report_latest.json`
- `subjectivity_focus_preview` on `worktree_settlement_latest.json`
- `worktree_settlement.subjectivity_focus_preview` on
  `repo_governance_settlement_latest.json`

And markdown mirrors now render:

- `## Subjectivity Focus`
- `## Subjectivity Focus Mirror`

## Boundary

This remains mirror-only.

It does not:

- change review criteria
- change settlement logic
- change writer behavior
- auto-classify admissibility

It only surfaces the already-published subjectivity/admissibility line in a
shorter recovery path.

## Focused Validation

- `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- result: `10 passed`
- `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`

## Live Mirror Result

Latest live refresh after this phase:

- `refreshable_artifact_report_latest.json` at `2026-03-11T16:11:52Z`
- `worktree_settlement_latest.json` at `2026-03-11T16:12:04Z`
- `repo_governance_settlement_latest.json` at `2026-03-11T16:12:10Z`

The shared focus card currently resolves to:

- path:
  `docs/status/subjectivity_review_batch_latest.json`
- queue posture:
  `stable_history_only`
- queue line:
  `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility line:
  `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
