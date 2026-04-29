# Memory Subjectivity Tension Grouping Addendum (2026-03-10)

## Why This Addendum Exists

The branch now has a formal review policy and an operator review lane.

That solved the question of what `approved / deferred / rejected` mean.

It did **not** yet solve one practical problem:

what exactly is the review unit when unresolved tensions arrive as repeated
Dream-collision rows rather than as clean, one-record semantic candidates?

The current `32 unresolved tensions` result is the first clear case where row
volume and review volume are not the same thing.

This addendum settles that boundary.

## Core Rule

The default review unit is a semantic tension group, not an individual row.

Rows remain the storage unit.

Groups become the triage and review-preparation unit.

This keeps the branch from mistaking:

- duplicate operational bursts

for:

- distinct subjectivity candidates

## Minimum Grouping Axes

Every unresolved tension grouping pass should expose at least:

### 1. Collision Lineage

- which `source_record_ids` / `stimulus_record_id` values produced the rows

### 2. Topic Surface

- what topic or collision title the rows are about

### 3. Normative Direction

- what kind of governance direction the tension appears to point toward
- for example: governance escalation, safety boundary, provenance discipline,
  resource discipline

### 4. Friction Band

- low: `< 0.30`
- medium: `0.30 - 0.50`
- high: `> 0.50`

### 5. Temporal Spread

- how many distinct cycles the pattern survives
- whether it is a burst from one run or a signal recurring across runs

## Output Expectation

The grouping layer should answer three operator questions before any review is
attempted:

1. How many unresolved rows exist?
2. How many semantic groups do those rows collapse into?
3. Which groups deserve:
   - likely reject
   - likely defer
   - candidate for manual review

This phase is triage, not promotion.

It should not mutate memory by itself.

## Guardrails

This grouping phase must remain:

- read-only
- explainable
- compatible with the existing review criteria

It must **not**:

- auto-approve or auto-reject memory records
- widen `SoulDB`
- alter live retrieval policy
- depend on UI-first review tooling

## Architectural Conclusion

The branch now has enough review semantics that the next bottleneck is no longer
"what does approval mean?"

It is:

"what should be reviewed together?"

This addendum answers that by making semantic grouping the bridge between raw
candidate tension rows and explicit operator judgment.
