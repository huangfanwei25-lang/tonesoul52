# Memory Subjectivity Deferred-Pending Reporting Addendum (2026-03-10)

> Purpose: define how deferred reviews should appear in reporting without falsely collapsing unresolved rows into settled memory.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already allows an operator to mark an unresolved semantic group as
`deferred`.

That does **not** settle the underlying tension rows.

It keeps them unresolved on purpose.

The missing piece was observability:

after a `deferred` review, the latest subjectivity report still read those rows
mostly as raw `candidate` payloads unless an operator manually inspected the
review ledger.

This addendum settles that reporting boundary.

## Core Rule

For unresolved tensions, the public report should expose an **effective pending
status**:

1. first from the latest review ledger decision, if one exists
2. otherwise from the row's own `promotion_gate.status`

This keeps `candidate` and `deferred` visible as different operator states even
when the original tension payload is unchanged.

## Minimum Reporting Surface

The latest subjectivity report should expose at least:

- `deferred_tension_count`
- unresolved counts grouped by effective pending status
- per-row `pending_status` alongside existing `promotion_status`

## Guardrails

This phase remains:

- report-only
- schema-free
- retrieval-neutral

It must **not**:

- change the meaning of `deferred`
- settle tension rows automatically
- widen `SoulDB`
- introduce live reranking

## Architectural Conclusion

Once `deferred` becomes a real operator action, it must also become a real
operator-visible state.

Otherwise the branch can record discernment without being able to see it.
