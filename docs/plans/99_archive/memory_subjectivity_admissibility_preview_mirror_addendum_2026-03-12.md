# Memory Subjectivity Admissibility Preview Mirror Addendum (2026-03-12)

> Purpose: mirror admissibility status upward into preview surfaces so interruption recovery preserves gate context.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The review batch now exposes a compact admissibility handoff line:

- `admissibility_primary_status_line`

That solved review-batch interruption recovery.

But the higher mirror layers still only previewed queue posture.

That meant an operator could see:

- `stable_history_only`

without seeing the second half of the truth:

- which admissibility gate the same queue was still blocked behind

## What This Phase Adds

This phase mirrors the existing admissibility handoff line upward through the
already-existing preview chain:

- `subjectivity_review_batch_latest.json`
- `refreshable_artifact_report_latest.json`
- `worktree_settlement_latest.json`
- `repo_governance_settlement_latest.json`

The rule is strict:

copy the preview field upward unchanged.

Do not recompute subjectivity state.

Do not rebuild admissibility logic in settlement scripts.

## New Preview Surface

Preview objects may now include:

- `admissibility_primary_status_line`

And the higher layers now also expose:

- `summary.admissibility_preview_count` on the refreshable report
- `summary.refreshable_admissibility_preview_count` on the worktree settlement
- `worktree_settlement.refreshable_admissibility_preview_count` on repo
  governance settlement

## Boundary

This remains a mirror-only phase.

It does not:

- change review semantics
- invent a new governance gate
- recompute or reinterpret admissibility state

The higher layers simply become more honest mirrors of what review batch
already knows.

## Focused Validation

- `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- result: `10 passed`
- `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`

## Live Mirror Result

Latest live refresh after this phase:

- `refreshable_artifact_report_latest.json` at `2026-03-11T16:06:45Z`
- `summary.handoff_preview_count = 3`
- `summary.admissibility_preview_count = 1`
- `worktree_settlement_latest.json` at `2026-03-11T16:06:56Z`
- `summary.refreshable_handoff_preview_count = 3`
- `summary.refreshable_admissibility_preview_count = 1`
- `repo_governance_settlement_latest.json` at `2026-03-11T16:06:59Z`
- `worktree_settlement.refreshable_handoff_preview_count = 3`
- `worktree_settlement.refreshable_admissibility_preview_count = 1`

The mirrored admissibility preview now resolves to the review-batch lane:

- queue posture:
  `stable_history_only`
- queue line:
  `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility line:
  `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
