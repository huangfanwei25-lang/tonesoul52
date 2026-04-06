# ToneSoul Knowledge Layer Boundary Contract

> Purpose: define where a future ToneSoul knowledge layer begins and ends, so retrieval does not collapse into R-memory, identity, or exploratory residue.
> Last Updated: 2026-04-06
> Authority: architecture boundary aid. Does not outrank runtime code, canonical anchors, tests, or current hot-state coordination surfaces.

---

## Why This Exists

ToneSoul currently has strong hot coordination:

- session-start
- observer window
- packet
- claims / checkpoints / compactions
- subject snapshot / working-style continuity

What it still does not have is a real knowledge layer.

Without a boundary contract, later agents over-collapse four different things:

- hot coordination state
- canonical design truth
- compiled knowledge
- exploratory residue

This contract exists to stop that collapse.

## Compressed Thesis

`R-memory is hot coordination, not a retrieval index.`

`retrieval is not memory, and memory is not identity.`

ToneSoul therefore needs a future knowledge layer that stays separate from:

- canonical anchors
- hot-state coordination
- working identity
- parked drafts and external residue

## The 5-Layer Knowledge Boundary

### 1. Canonical Anchors

Examples:

- `DESIGN.md`
- `task.md.current_short_board`
- canonical architecture contracts
- `AXIOMS.json`

What it is:

- parent truth for current design center and current accepted direction

What it is not:

- a searchable knowledge dump
- runtime hot state

### 2. Hot Coordination State

Examples:

- session-start bundle
- observer window
- packet
- claims / checkpoints / compactions
- closeout grammar

What it is:

- current working-state transport and bounded continuation support

What it is not:

- long-lived retrieval corpus
- durable knowledge index

### 3. Compiled Knowledge

Examples:

- future queryable architecture distillations
- future structured research syntheses
- future health-checked collection/index surfaces

What it is:

- explicit, queryable, health-checked knowledge assembled from source materials

What it is not:

- raw source corpus
- subject continuity
- identity

### 4. Exploratory Residue

Examples:

- parked `docs/plans/` drafts
- `external_research/`
- local clones / sidecar comparisons
- unratified external framework analysis

What it is:

- material that may still yield useful ideas

What it is not:

- runtime truth
- canonical design
- retrieval-ready compiled knowledge

### 5. Operator Retrieval Surfaces

Examples:

- future bounded query tools
- future graph/query operator panes
- future collection-aware knowledge shell

What it is:

- the operator-facing retrieval seam for asking bounded questions against compiled knowledge

What it is not:

- a substitute for session-start
- a replacement for mutation or closeout preflight

## Current Reality

ToneSoul today already has:

- strong hot coordination
- strong canonical anchors
- growing research distillation

ToneSoul does **not** yet have:

- a real compiled knowledge index
- health-checked collections
- bounded operator retrieval tools over that layer

So the present rule is:

`do not pretend R-memory is already the knowledge layer.`

## Source Flow

The intended future flow is:

1. `raw sources`
   - papers
   - repos
   - external docs
   - historical specs
2. `compiled knowledge`
   - distilled, structured, queryable, health-checked
3. `operator retrieval surfaces`
   - bounded shell/query tools
4. `runtime use`
   - only after bounded retrieval results are explicitly pulled

This means:

- raw sources should not be read as already compiled
- compiled knowledge should not be confused with live continuity
- retrieval results should not silently mutate identity or runtime truth

## Interaction With R-Memory

R-memory should remain responsible for:

- current coordination
- resumability
- current bounded continuity
- mutation / closeout discipline

The future knowledge layer should remain responsible for:

- historical and conceptual retrieval
- research lookup
- design lineage lookup
- operator question answering over compiled sources

These layers may collaborate, but they must not merge.

## Non-Goals

This contract is not:

- a vector-db commitment
- a qmd adoption promise
- proof that every useful repo document must enter the future index
- permission to treat exploratory residue as if it were verified knowledge

It is only a boundary contract.
