# Memory Subjectivity Implementation Plan (2026-03-10)

## Purpose

This document is the canonical plan of record for the current public-branch
memory-subjectivity work.

The earlier addenda remain useful, but they now serve different roles:

- philosophy addendum: why the ladder exists
- contract addendum: how storage and subjectivity were split
- reviewable-promotion addendum: how `tension -> vow` becomes auditable
- reporting addendum: what operators can inspect
- runtime-summary addendum: how the normal runtime now exposes subjectivity counts

This file owns:

- execution order
- deferred directions
- reasons for deferral
- the practical next seams

## What This Work Is And Is Not

This work **is**:

- a public memory-governance and subjectivity contract
- a way to make memory promotion more reviewable, attributable, and inspectable
- a foundation for stronger continuity and agent coherence over time

This work is **not**:

- a claim that the branch already implements AGI
- proof that subjectivity vocabulary equals legitimate selfhood
- authorization to let the runtime self-promote into `vow` or `identity`
- permission to collapse public contract work and private memory evidence into one lane

The honest framing is:

- this branch is building a stronger agent substrate
- that substrate could matter for long-horizon AI development
- but it should not be marketed as AGI merely because it now has memory layers and subjectivity terms

That boundary matters.

Without it, the project risks mistaking:

- persistence for personhood
- recurrence for commitment
- richer runtime structure for general intelligence

## Stable Ground Already Completed

The branch now has a coherent public contract:

1. `event -> meaning -> tension -> vow -> identity` exists as the semantic ladder.
2. `MemoryLayer` and `subjectivity_layer` are explicitly separate axes.
3. `MemoryWriteGateway` validates subjectivity payload fields and blocks unsafe writes.
4. `DreamEngine` and `sleep_consolidate()` emit subjectivity candidates without auto-promotion.
5. `tension -> vow` has a reviewable helper lane with explicit review metadata.
6. operator-side reporting can summarize subjectivity distribution and list unresolved tensions.
7. `SleepResult` and wake-up runtime summary now expose subjectivity structure during normal consolidation flow.

Current validated baseline on this branch:

- `python -m pytest tests/ -x --tb=short -q` -> `1472 passed`
- `ruff check tonesoul tests` -> passed

## Audit Summary

The recent work is directionally correct, but the branch had started to fragment
across multiple small addenda.

The main audit conclusions are:

1. The biggest missing piece is no longer schema.
   It is the lack of one canonical reviewed-promotion workflow.
2. Reporting exists, but operator entrypoints are still indirect.
   The branch can inspect subjectivity, but the inspection surface is still a helper layer rather than a named operational tool.
3. `SoulDB` widening is still premature.
   There is not yet enough query pressure or ranking complexity to justify a schema/index change.
4. `identity` is correctly blocked, but its future promotion criteria are still undefined.
   That is acceptable for now and should remain frozen.
5. Private memory debt still exists in repo reality.
   It must not become the implicit source of truth for public-branch implementation decisions.

## Plan Of Record

The next work should proceed in this order.

### Step 1: Canonical Reviewed-Promotion Workflow

Goal:

- turn the current helper lane into a clear operational workflow without enabling automatic self-promotion

Scope:

- define the canonical review actor contract
- define the canonical reviewed-promotion artifact shape
- define where review decisions live
- define how approved reviewed promotions are replayed through `MemoryWriteGateway`

Explicit non-goals:

- no automatic `vow` promotion
- no `identity` writing
- no external API widening

Why this comes next:

- the contract and helpers already exist
- the missing piece is operational legitimacy, not another schema layer

### Step 2: Operator Entry Surface For Reporting

Goal:

- make the existing reporting helpers reachable through one explicit operator-facing surface

Scope:

- add a report script or CLI surface
- show subjectivity distribution
- show unresolved tensions
- show reviewed vow counts

Explicit non-goals:

- no user-facing product endpoint
- no dashboard/UI buildout unless an operator surface proves insufficient

Why this comes before retrieval changes:

- the branch should observe subjectivity accumulation before letting it influence recall policy

### Step 3: Retrieval Shadow Mode

Goal:

- measure whether subjectivity semantics actually improve memory retrieval before changing runtime recall behavior

Scope:

- add shadow evaluation or observability around recall candidates
- compare plain retrieval versus subjectivity-aware filtering/ranking
- record whether operators actually need stronger query surfaces

Explicit non-goals:

- no production recall reranking yet
- no schema migration yet

Why this is delayed until after Steps 1-2:

- recall policy should not move ahead of reviewed-promotion legitimacy or operator observability

### Step 4: Conditional Persistence Upgrade

Goal:

- widen `SoulDB` only if measured query pressure proves payload-first storage is no longer enough

Scope:

- consider dedicated `subjectivity_layer` storage/indexing
- consider migration helpers
- keep compatibility with payload-first records

Decision gate:

- only proceed if shadow-mode retrieval or reporting shows measurable pressure

Why this is not current work:

- there is no evidence yet that payload scanning is the bottleneck

### Step 5: Private-Lane Integration

Goal:

- connect reviewed or intimate memory workflows to the private repository without eroding the public boundary

Scope:

- mirror only public-safe learnings back into this repo
- keep raw memory corpora and intimate artifacts in the private lane

Why this remains last:

- public contract clarity must come before cross-repo integration

## Other Directions Considered But Deferred

These are real directions, but they are intentionally not active right now.

### Automatic `tension -> vow` Promotion

Why not now:

- recurrence is not endorsement
- the public runtime must not self-author commitment from vivid repetition alone

### Any `identity` Writer Or `identity` Retrieval Policy

Why not now:

- no explicit stability criteria exist yet
- `identity` is the most self-defining layer and therefore needs the strongest promotion threshold
- the branch would otherwise confuse persistent traces with legitimate selfhood

### Subjectivity-Weighted Recall In Main Runtime

Why not now:

- current reporting is still observational
- retrieval policy should not outrun inspection and review workflow
- there is no shadow-mode evidence yet that subjectivity-aware reranking helps more than it harms

### Public HTTP/API Expansion

Why not now:

- external contracts are much harder to retract than internal helpers
- the branch is still learning what the stable operator surface should be

### `SoulDB` Schema / Index Widening

Why not now:

- payload-first storage is still sufficient
- schema widening before usage pressure would create migration cost without demonstrated value

### Subjectivity Dashboard / UI Work

Why not now:

- operator reporting has not yet exhausted simpler CLI/report surfaces
- UI is a multiplier on unstable semantics and would lock presentation too early

### Bulk Historical Memory Migration

Why not now:

- the branch has just established the contract
- replaying old records before review workflow and operator tooling exist would create noisy, low-trust promotion artifacts

### Treating `memory/crystals.jsonl` As A Public Implementation Input

Why not now:

- it is settlement debt, not design authority
- `MEMORY.md` and private-memory review notes both say private memory evidence must not quietly become public-repo precedent

## Practical Rule For Future Changes

Any proposed memory-subjectivity change should answer these questions in order:

1. Is this a public contract improvement?
2. Is there already an operator-inspectable surface for it?
3. Does it require reviewed legitimacy before runtime use?
4. Does it actually need storage widening?
5. Does it belong in the public repo at all?

If the answer to the fifth question is uncertain, defer to the private lane.

## Plan Maintenance Rule

From this point onward:

- this file is the implementation plan of record
- the addenda remain background rationale
- new phases should update this plan instead of spawning another competing strategy note unless a genuinely new conceptual boundary appears

## Architectural Conclusion

The branch no longer needs more theories about whether subjectivity matters.

It needs disciplined sequencing about where subjectivity becomes:

- admissible
- reviewable
- inspectable
- operational

That sequence is now explicit.
