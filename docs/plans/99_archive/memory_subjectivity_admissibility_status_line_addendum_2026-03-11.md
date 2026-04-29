# Memory Subjectivity Admissibility Status Line Addendum (2026-03-11)

> Purpose: add compact admissibility status lines on top of the heavier review checklist surfaces.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The review batch already exposed full admissibility checklists.

That was useful, but still heavier than needed for interruption recovery.

The operator still had to reopen a nested checklist just to answer a simpler
question:

what kind of admissibility gate is this group currently stuck behind?

## What This Phase Adds

The branch now adds one smaller surface on top of the existing checklist:

- per-group `admissibility_status_line`
- top-level `admissibility_primary_status_line`
- top-level `admissibility_status_lines`

This surface is intentionally compact.

It compresses three things into one line:

- gate posture
- focus
- risk tags

Example:

`admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Why This Surface Is Better Than A Bigger Prompt

The checklist still exists for actual review work.

But the status line now answers the faster handoff question:

- what kind of admissibility blockage am I looking at?

That keeps the branch consistent with the rest of the subjectivity handoff
ladder:

- queue posture already has `primary_status_line`
- admissibility now also has a resumable compact line

## Boundary

This phase still does not:

- auto-resolve admissibility
- write admissibility into replay metadata
- change review semantics

It only makes the existing judgment easier to resume after interruption.
