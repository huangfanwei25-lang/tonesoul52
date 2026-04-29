# Memory Subjectivity Grouping Handoff Surface Addendum (2026-03-11)

> Purpose: align grouping artifacts with the same handoff surface shape already exposed by the review-batch artifact.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The review-batch artifact already had a compact handoff surface.

The grouping artifact did not.

That left an awkward mismatch:

- one artifact started with queue posture and handoff state
- the other still started with raw counts

## Core Rule

The grouping artifact may expose the same top-level handoff shape as the batch,
but it must speak in triage language, not review language.

This means grouping may expose:

- `handoff`
- `primary_status_line`
- `status_lines`
- per-group `group_shape`

It must not claim reviewed stability that only the batch layer can know.

## Guardrails

Grouping handoff must remain grounded in unresolved triage facts:

- recommendation
- same-source loop shape
- duplicate pressure
- producer follow-up

It must **not**:

- emit `stable_deferred_history`
- infer reviewed settlement
- collapse review and triage into one layer

## Architectural Conclusion

The operator should now be able to open either artifact and still get the same
kind of answer first:

- what shape of queue is this
- does it need action now
- what is the shortest truthful line that summarizes it
