# Memory Subjectivity Group Review Pending-Filter Addendum (2026-03-11)

> Purpose: let group-review actions focus on only the fresh pending slice instead of replaying the whole semantic group.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The group review lane can already settle an entire semantic group.

That is good for first-pass review.

It is too blunt for revisit work.

Once a group already contains a mix such as:

- older `deferred` rows
- newer `candidate` rows

an operator often needs to review only the fresh unresolved slice.

## Core Rule

Group review may optionally filter by current pending state before applying the
batch decision.

The first required case is:

- apply a revisit decision only to rows whose current `pending_status` is
  `candidate`

## Guardrails

This filter changes selection scope, not review semantics.

It must **not**:

- change the meaning of `deferred` / `rejected`
- auto-carry decisions forward
- hide older unresolved rows from reporting

It only narrows which rows receive the explicit operator write.

## Architectural Conclusion

Revisit review should be surgical.

The group remains the semantic unit.

But the write scope may need to target only the fresh unresolved slice inside
that group.
