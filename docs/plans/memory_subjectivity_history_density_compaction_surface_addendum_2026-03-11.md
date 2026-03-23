# Memory Subjectivity History Density Compaction Surface Addendum (2026-03-11)

> Purpose: define a compact operator-facing surface for historically dense deferred subjectivity queues.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch has already done the important semantic work:

- the remaining OSV homepage loop is explicitly `deferred`
- the queue is no longer reopening with fresh `candidate` rows
- the live review lane is not the bottleneck anymore

What still reads badly is the artifact surface.

`50 unresolved tension` by itself still makes the remaining loop look larger
and more active than it really is.

The real shape is narrower:

- one same-source deferred loop
- twelve lineages
- a heavily repeated historical stack
- zero fresh rows since the latest review

That is not a new review problem.

It is an observability compression problem.

## Core Rule

The operator-facing batch and grouping artifacts may surface read-only history
density signals that compress repeated same-source lineage stacks into a more
truthful shape.

This phase may add:

- lineage repeat counts
- lineage density histograms
- first/last seen time windows
- one derived `history_density_summary`
- one derived `density_compaction_candidate` / `operator_followup`

These signals must remain derived from existing rows.

## Guardrails

This phase must remain:

- read-only
- operator-facing
- semantically conservative

It must **not**:

- rewrite historical deferred rows
- auto-settle a holding group
- change `approved / deferred / rejected`
- change producer write rules
- reinterpret density as a new commitment signal

## Architectural Conclusion

Once a same-source deferred loop is stable, the next honest improvement is not
another review write.

It is an artifact surface that shows the loop as:

- historically dense
- currently settled
- operationally a compaction candidate rather than an active queue crisis
