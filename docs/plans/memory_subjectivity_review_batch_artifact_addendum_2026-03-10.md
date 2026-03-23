# Memory Subjectivity Review Batch Artifact Addendum (2026-03-10)

> Purpose: define the canonical pending-queue artifact for grouped subjectivity review work.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch now has two different but complementary operator needs:

1. a way to **apply** one reviewed decision across a semantic tension group
2. a way to **see the whole pending queue** before deciding what to apply

`scripts/run_subjectivity_group_review.py` already covers the first need.

This addendum settles the second.

## Core Rule

The branch should expose one read-only review-batch artifact that turns the
current unresolved semantic groups into an operator queue.

This queue is not a second review engine.

It is a preparation surface.

## What The Batch Artifact Must Contain

For each pending semantic group, the artifact should show at least:

- topic
- inferred direction
- triage recommendation
- default review status if the operator confirms the recommendation
- representative record ids across lineages
- a reusable review-basis template

## Why This Layer Matters

Grouping artifacts answer:

- what should be reviewed together?

The review-batch artifact answers:

- what should the operator look at next?

That keeps the branch from forcing operators to manually translate:

- semantic groups

into:

- concrete review work items

every time the queue changes.

## Guardrails

This artifact must remain:

- read-only
- explainable
- downstream of the canonical grouping logic

It must **not**:

- settle review state by itself
- bypass `scripts/run_subjectivity_group_review.py`
- invent new review semantics outside the formal criteria

## Architectural Conclusion

The branch now has three distinct review surfaces:

- grouping: what belongs together
- review batch: what deserves attention next
- group review apply: what decision actually gets written

That separation keeps the workflow inspectable without collapsing planning and
mutation into the same step.
