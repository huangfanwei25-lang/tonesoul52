# Memory Subjectivity Deferred Context Surface Addendum (2026-03-11)

> Purpose: expose the latest deferred reason and revisit condition on the main operator-facing subjectivity surfaces.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch can already say:

- which tensions are still unresolved
- which ones are explicitly `deferred`
- which group currently needs re-review

That is still not enough for good operator judgment.

The remaining gap is simple:

the latest deferred reason and revisit condition are still buried in review
logs instead of being visible on the main operator surfaces.

## Core Rule

If a tension is still unresolved and its active review status is `deferred`, the
main reporting surfaces should expose the latest reviewed context that keeps it
there.

Minimum fields:

- latest `review_basis`
- latest `notes`
- latest review actor identity

For semantic-group review batches, the latest active deferred context should be
visible at the group level, not only per row.

## Observed Live Outcome

The new surface became useful immediately because the live queue did not stay
still.

First refresh after the context surface landed:

- report artifact at `2026-03-11T10:05:08Z`
- `53 unresolved tension`
- `45 deferred tension`
- `8 candidate tension`
- `27 settled tension`
- `0 reviewed vow`
- `2 semantic groups`
- `13 lineage groups`
- `revisit_readiness_counts = {n/a: 1, needs_revisit: 1}`
- `carry_forward_annotation_counts = {prior_reject_match: 1, prior_deferred_match_needs_revisit: 1}`

Later same-session refresh:

- report artifact at `2026-03-11T10:07:29Z`
- review-batch artifact at `2026-03-11T10:07:32Z`
- `50 unresolved tension`
- `50 deferred tension`
- `0 candidate tension`
- `30 settled tension`
- `0 reviewed vow`
- `1 semantic group`
- `12 lineage groups`
- `revisit_readiness_counts = {holding_deferred: 1}`
- `carry_forward_annotation_counts = {prior_deferred_match: 1}`

This matters because the branch should now treat queue counts as timestamped
live observations, not as timeless plan facts.

## Guardrails

This phase remains:

- read-only
- report-first
- downstream of canonical review logs

It must **not**:

- reinterpret review semantics
- invent synthetic revisit criteria
- auto-promote or auto-settle based on notes text

The reporting surface only makes the operator's existing judgment legible.

## Architectural Conclusion

`deferred` should not feel like a black box.

If the queue keeps one live deferred group, the branch should show:

- why it is still deferred
- who deferred it
- what would justify waking it up again

That remains true even when the live queue grows or contracts within the same
session.
