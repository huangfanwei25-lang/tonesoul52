# Memory Subjectivity Operator Lens View Addendum (2026-03-11)

> Purpose: define the compressed operator lens used to read subjectivity queue posture and revisit triggers quickly.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The history-density surface made one thing clearer:

- the remaining OSV homepage branch is historically dense
- it is already `deferred`
- it has no fresh rows since the latest review

But the operator still has to read several low-level fields before that shape
becomes obvious.

That means the branch still lacks one final compression layer:

- a short operator lens that says what kind of queue this is
- why it should or should not be acted on now
- what would actually cause revisit

## Core Rule

The review-batch artifact may add one short operator lens per review group.

This lens may surface:

- `queue_posture`
- `revisit_trigger`
- `operator_lens_summary`

These fields must remain:

- derived
- read-only
- subordinate to the existing semantic fields

## Guardrails

This phase must **not**:

- replace `revisit_readiness`
- replace `carry_forward_annotation`
- replace the reviewed status model
- create a new decision category

It is a view, not a semantic rewrite.

## Architectural Conclusion

The batch should first answer the operator's real question:

- is this an active queue
- a deferred history stack
- a reopen that needs attention now

Only after that should the operator read the denser supporting fields.
