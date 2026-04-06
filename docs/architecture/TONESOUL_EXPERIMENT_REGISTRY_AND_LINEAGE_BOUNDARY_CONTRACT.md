# ToneSoul Experiment Registry And Lineage Boundary Contract

> Purpose: define where bounded self-improvement trial outputs belong, how experiment lineage should be classified, and why experiment memory must stay separate from hot coordination, canonical identity, and general compiled knowledge.
> Status: accepted architecture contract for `Phase 791`.
> Authority: architecture contract. This file defines the boundary for future experiment lineage. It does not create a live registry runtime.

---

## Why This Exists

Once ToneSoul has:

- a self-improvement loop spec
- an evaluator harness
- a future compiled-knowledge landing zone

the next risk becomes obvious:

`where do the outcomes of bounded trials go?`

If that answer is vague, the repo drifts toward three bad defaults:

1. experiment outputs get stuffed back into `R-memory`
2. promotion-ready results get mixed with exploratory failure notes
3. compiled knowledge gets polluted by transient trial artifacts

This contract exists to stop that collapse before a runtime registry is built.

---

## Compressed Thesis

Experiment lineage should have its own bounded lane.

It must stay separate from:

- hot coordination
- canonical governance truth
- durable identity
- generic compiled knowledge

ToneSoul needs experiment memory.
It does not need experiment sprawl.

---

## What This Is

This contract defines the boundary for future experiment-registry content produced by bounded self-improvement work.

It answers:

- what counts as a trial artifact
- what counts as a distilled lesson
- what counts as a promotion-ready result
- what must never be stored as experiment lineage

---

## What This Is Not

This is **not**:

- a replacement for `R-memory`
- a generic telemetry warehouse
- a hidden reasoning archive
- a direct compiled-knowledge corpus
- a durable identity archive

It is only the future home for bounded self-improvement lineage.

---

## Three Registry Classes

Future experiment lineage should be split into three classes.

### 1. `raw_run`

What it is:

- the immediate record of one bounded trial run
- candidate metadata
- evaluator inputs
- evidence bundle references
- outcome classification

What it is not:

- a durable lesson
- a promoted rule

Typical posture:

- short retention
- review-oriented
- high volatility

### 2. `distilled_lesson`

What it is:

- a reusable lesson derived from one or more raw runs
- the smallest stable takeaway that still preserves failure context

What it is not:

- raw run logs
- canonical governance truth

Typical posture:

- medium retention
- compiled but still bounded
- reusable across similar future candidates

### 3. `promotion_ready_result`

What it is:

- a trial outcome strong enough to justify a concrete bounded adoption step
- the bridge between experimental lineage and a real patch or contract update

What it is not:

- a blanket authorization to rewrite adjacent surfaces
- a canonical architectural law

Typical posture:

- narrow scope
- strong evidence bundle
- explicit rollback path

---

## Boundary Against R-Memory

`R-memory` remains for:

- hot coordination
- current task orientation
- bounded handoff
- current closeout and import posture

Experiment lineage must not be stored as if it were:

- session-start truth
- observer truth
- packet/operator guidance truth
- subject continuity

At most, hot coordination may reference:

- that a bounded trial exists
- where to look for it
- whether a result is promoted, parked, or retired

But not the whole experiment narrative itself.

---

## Boundary Against Compiled Knowledge

Compiled knowledge is broader than experiment lineage.

Compiled knowledge may contain:

- research distillations
- architecture distillations
- operator-safe summaries

Experiment lineage is narrower:

- it records how ToneSoul tested candidate changes against itself

The right relation is:

- experiment lineage may later feed compiled lessons
- compiled knowledge must not absorb raw runs by default

This prevents general retrieval from surfacing noisy trial artifacts as if they were stable reference material.

---

## Boundary Against Canonical Governance

No experiment-registry class may be treated as canonical governance truth by default.

Not even `promotion_ready_result`.

Promotion-ready means:

- ready for a bounded patch or contract update

It does not mean:

- now part of the constitution
- now part of identity
- now stronger than code/tests/contracts already in force

If a result changes governance truth, that promotion must still happen through stronger surfaces.

---

## Boundary Against Identity

Experiment lineage must never become:

- subject identity memory
- stable vow history
- durable-boundary archive

Even if a candidate touches operator style or workspace preference, its lineage remains:

- experiment memory

not:

- selfhood memory

This is a hard line.

---

## Proposed Future Landing Zone

When implemented, experiment lineage should live in a dedicated bounded root such as:

`knowledge/experiments/`

with at least:

1. `knowledge/experiments/raw_runs/`
2. `knowledge/experiments/lessons/`
3. `knowledge/experiments/promotions/`
4. `knowledge/experiments/status/`

This keeps it distinct from:

- `knowledge/compiled/`
- `docs/research/`
- hot coordination surfaces

This is a boundary proposal, not a migration command.

---

## Minimum Metadata For `raw_run`

Every future raw run should eventually declare:

- `run_id`
- `candidate_id`
- `target_surface`
- `started_at`
- `finished_at`
- `status`
- `success_metric_summary`
- `failure_watch_summary`
- `evidence_bundle_refs`
- `rollback_path_summary`
- `consumer_scope`

Without those, a raw run is not useful enough to keep.

---

## Minimum Metadata For `distilled_lesson`

Every future distilled lesson should eventually declare:

- `lesson_id`
- `derived_from_runs`
- `lesson_scope`
- `applies_when`
- `does_not_apply_when`
- `overclaim_to_avoid`
- `freshness_posture`

This keeps lessons reusable but bounded.

---

## Minimum Metadata For `promotion_ready_result`

Every future promotion-ready result should eventually declare:

- `promotion_id`
- `derived_from_runs`
- `candidate_id`
- `target_surface`
- `promotion_scope`
- `required_patch_or_contract`
- `rollback_path`
- `parity_surfaces_checked`
- `promotion_limit`

This prevents "promotion-ready" from becoming vague optimism.

---

## Retention Rule

The registry should keep different retention postures by class:

- `raw_run`
  - shortest retention
  - prunable after distillation or supersession

- `distilled_lesson`
  - medium retention
  - keep while still useful and unchallenged

- `promotion_ready_result`
  - keep until promoted, retired, or invalidated

Retention should be explicit, not accidental.

---

## Parking And Retirement Rule

Not all experiment outputs deserve continued presence.

The registry must support:

- `active`
- `parked`
- `retired`

Definitions:

### `active`

Still relevant for current or near-future bounded work.

### `parked`

Potentially useful later, but blocked by prerequisites or not yet worth current attention.

### `retired`

No longer a good candidate, or superseded by a better lesson/result.

This allows experiment memory to remain useful without becoming a permanent junk drawer.

---

## Query Rule

Future operator retrieval may reference experiment lineage only under bounded conditions:

- lineage lookup
- promotion trace
- health/status check

It must not default to surfacing raw runs in operator-facing retrieval.

The default operator retrieval priority should stay:

- compiled references first
- experiment raw runs only when explicitly asked

This prevents noisy experiment history from crowding out cleaner operator knowledge.

---

## Human-Gate Rule

The registry may support bounded self-improvement work.

It must not silently authorize:

- governance mutation
- identity mutation
- vow mutation
- vendor-native interop claims

Those still require stronger lanes and often human judgment.

---

## One-Sentence Summary

`ToneSoul's experiment registry must remember bounded self-improvement lineage without letting trial artifacts leak back into hot coordination, compiled knowledge, canonical governance, or identity.`
