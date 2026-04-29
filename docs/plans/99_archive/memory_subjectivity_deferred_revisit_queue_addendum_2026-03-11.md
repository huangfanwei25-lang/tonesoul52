# Memory Subjectivity Deferred Revisit Queue Addendum (2026-03-11)

> Purpose: define how deferred semantic groups re-enter an explicit revisit queue instead of silently disappearing or auto-settling.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch can now do two things correctly:

1. write `deferred` onto an unresolved semantic group
2. make that deferred-pending state visible in the latest subjectivity report

That still leaves one operational gap:

how does an operator know when a deferred group should be looked at again?

This addendum settles that queue boundary.

## Core Rule

Deferred groups should not auto-settle and should not auto-reject.

Instead, the read-only review-batch artifact should expose whether a deferred
group is:

- ready for its first deferred write
- still being held in deferred observation
- ready for revisit because new unresolved evidence has appeared

## Minimum Queue Signals

For deferred-capable groups, the review batch should expose at least:

- `pending_status_counts`
- `latest_review_timestamp`
- `latest_row_timestamp`
- `rows_after_latest_review`
- one explicit `revisit_readiness` field

## Guardrails

This phase remains:

- read-only
- report-first
- downstream of canonical grouping and review ledgers

It must **not**:

- auto-apply deferred or rejected decisions
- auto-promote to `vow`
- widen `SoulDB`

## Architectural Conclusion

`deferred` is not a dead end.

It is a waiting state.

The branch therefore needs a queue that can distinguish:

- waiting
- drifting
- recurring

without collapsing those cases into silent background noise.
