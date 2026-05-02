# Memory Subjectivity Requires-Operator-Action Preview Mirror Addendum (2026-03-12)

> Purpose: define higher-level preview mirrors that expose whether subjectivity artifacts require operator action.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The higher mirrors already knew:

- queue posture
- admissibility posture
- one compact focus card

But they still lacked one small truth that already existed at the leaf
artifact level:

- `requires_operator_action`

Without that field, a higher mirror could tell you what the queue looked like,
yet still force you to infer whether the leaf artifact itself thought human
intervention was needed.

That is unnecessary ambiguity.

## What This Phase Adds

This phase mirrors the existing `handoff.requires_operator_action` field upward
through the same preview chain:

- `refreshable_artifact_report_latest.json`
- `worktree_settlement_latest.json`
- `repo_governance_settlement_latest.json`

The rule stays strict:

- copy the field upward unchanged
- do not infer it from `queue_shape`
- do not recompute subjectivity semantics

## New Surface

Preview objects now carry:

- `requires_operator_action`

And the same field now appears on:

- `subjectivity_focus_preview`
- `worktree_settlement.subjectivity_focus_preview`
- mirrored preview rows in governance markdown

## Boundary

This remains mirror-only.

It does not:

- change review state
- create a new operator gate
- recalculate action readiness

It only preserves the leaf artifact's own statement about whether operator
intervention is currently required.

## Focused Validation

- `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- result: `10 passed`
- `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`

## Live Mirror Result

Latest live refresh after this phase:

- `refreshable_artifact_report_latest.json` at `2026-03-11T16:16:35Z`
- `worktree_settlement_latest.json` at `2026-03-11T16:16:46Z`
- `repo_governance_settlement_latest.json` at `2026-03-11T16:16:51Z`

The currently mirrored subjectivity truth is consistent at every layer:

- focus path:
  `docs/status/subjectivity_review_batch_latest.json`
- `requires_operator_action = false`
- queue posture:
  `stable_history_only`
- admissibility posture:
  `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
