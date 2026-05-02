# Memory Subjectivity Duplicate Pressure Surface Addendum (2026-03-11)

> Purpose: surface duplicate pressure as an operator-visible signal when repeated unresolved rows are driven by producer loops rather than review semantics.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch can now do all of these things:

1. group unresolved tensions into semantic review units
2. carry forward prior human judgment without auto-settling new rows
3. show why a deferred group is still being held

That still left one practical ambiguity:

when the queue re-opens again, is the problem really review semantics, or is one
producer loop simply generating too many near-duplicate tension rows?

This addendum settles that boundary.

## Core Rule

Duplicate pressure is an operator-facing observability signal, not a hidden
decision engine.

The grouping and review-batch artifacts may say:

- this semantic group is under low / medium / high duplicate pressure
- this group is dominated by one source loop
- this group now deserves upstream dedup follow-up

They may **not**:

- auto-suppress rows
- auto-settle review decisions
- auto-promote or auto-reject tensions

## Minimum Signals

For each semantic group, the operator surfaces should expose at least:

- `same_source_loop`
- `rows_per_lineage`
- `rows_per_cycle`
- `duplicate_pressure`
- `duplicate_pressure_reason`
- `producer_followup`

At the summary layer, the artifacts should also expose:

- `duplicate_pressure_counts`
- `producer_followup_counts`

## Guardrails

This phase remains:

- read-only
- report-first
- downstream of grouping and review semantics

It must **not**:

- widen `SoulDB`
- change `approved / deferred / rejected`
- hide unresolved tensions from the queue
- pretend carry-forward and producer pressure are the same problem

## Architectural Conclusion

Once the queue has collapsed to one deferred group, the next debt is no longer:

- "how should this be reviewed?"

It becomes:

- "why is this same source loop still producing so much unresolved row volume?"

The branch therefore needs a duplicate-pressure surface so upstream dedup /
noise-control work can be justified explicitly rather than inferred by hand.
