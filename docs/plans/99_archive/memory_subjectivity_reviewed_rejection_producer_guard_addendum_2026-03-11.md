# Memory Subjectivity Reviewed Rejection Producer Guard Addendum (2026-03-11)

## Why This Addendum Exists

The first DreamEngine duplicate guard proved one thing correctly:

- if the same source loop is still actively unresolved, producer writes should
  be skipped instead of stacked

Live verification then exposed the next gap:

- once a same-source loop has already been explicitly `rejected`, the producer
  can still reopen that exact same topic/source/lineage as a fresh `candidate`

That is not a review-lane problem anymore.

It is repeated producer churn against an already-reviewed same-lineage pattern.

## Core Rule

DreamEngine may skip a fresh `dream_collision` write when all of these are true:

- the latest reviewed decision for the same collision signature is `rejected`
- the collision matches the same normalized `topic`
- the collision matches the same normalized `source_url`
- the collision matches the same lineage (`stimulus_record_id` / `source_record_ids`)

This is narrower than global source-loop suppression.

It does **not** block:

- a different source loop
- a new lineage on the same source loop
- unresolved `deferred` handling, which remains owned by the active-unresolved guard

## Guardrails

This phase must remain:

- producer-side
- narrow
- audit-friendly

It must **not**:

- reinterpret every historical decision as permanent silence
- suppress new source diversity
- suppress a second independent lineage cluster
- auto-settle or auto-promote anything

## Architectural Conclusion

There are now two different producer dampeners:

1. `active_unresolved_signature`
   This prevents live unresolved loops from stacking.

2. `prior_rejected_signature`
   This prevents an already-rejected same-lineage pattern from reopening as a
   fresh candidate.

The first protects the live queue.
The second protects the queue from pointless re-entry after explicit rejection.
