# Memory Subjectivity Carry-Forward Queue Annotation Addendum (2026-03-11)

> Purpose: define how prior review outcomes are carried forward as queue annotations without inheriting decisions blindly.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already had:

1. semantic grouping
2. explicit `deferred` / `rejected` review writes
3. revisit-aware queue reporting

That still left one technical debt seam:

new unresolved rows could re-enter the queue as if the branch had no memory of
earlier operator decisions.

This addendum defines the carry-forward boundary.

## Core Rule

Carry-forward is queue annotation, not decision inheritance.

The read-only review batch may say:

- this group matches a prior reject
- this group matches a prior deferred decision
- this group matches a prior approved/reviewed decision
- this group has mixed historical decisions

It may **not** silently settle, reject, defer, or promote the new rows.

Until the branch has a first-class `review_batch_id`, historical carry-forward
still uses the best available reviewed evidence rather than a perfect batch
cohort identity. That is acceptable for queue annotation, but not for hidden
automation.

## Matching Rule

A current semantic group may only inherit carry-forward context when it matches
prior reviewed rows on:

- `topic`
- `direction`
- at least one provenance overlap signal:
  - overlapping `source_url`, or
  - overlapping `stimulus_lineage`

`friction_band` remains visible for triage, but it is **not** a hard
carry-forward key. Small score movement must not erase operator history.

## Active vs Historical Decision Rule

The queue should expose two different truths at once:

- the active carry-forward decision that currently governs operator reading
- the broader historical decision mix that explains how the queue got here

So the review batch should surface:

- `prior_decision_status_counts`
- `historical_prior_decision_status_counts`

and the carry-forward annotation should follow the active decision, not the
entire mixed history blob.

## Minimum Annotation States

The read-only batch surface should distinguish at least:

- `fresh_group`
- `prior_reject_match`
- `prior_deferred_match`
- `prior_deferred_match_needs_revisit`
- `prior_approved_match`
- `mixed_prior_decisions`

## Guardrails

This phase remains:

- read-only
- report-first
- downstream of canonical review logs

It must **not**:

- auto-reapply prior decisions
- auto-settle new unresolved rows
- auto-promote to `vow`
- widen `SoulDB`

## Architectural Conclusion

The queue should stop being memoryless.

But it should not become a hidden autopilot.

Carry-forward therefore means:

- remember prior judgment
- expose current recurrence
- keep the final decision with the operator
