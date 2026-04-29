# Memory Subjectivity Contract Addendum (2026-03-10)

> Purpose: define the implementation contract that separates operational memory placement from subjectivity admissibility.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The subjectivity ladder from the previous note is now clear:

`event -> meaning -> tension -> vow -> identity`

But implementation should not naively overwrite the current runtime memory model.

Reading the current code makes that clear:

- `tonesoul/memory/soul_db.py` uses `MemoryLayer = factual | experiential | working`
- `tonesoul/memory/write_gateway.py` enforces write admissibility through provenance/evidence gates
- `tonesoul/memory/consolidator.py` promotes by keyword heuristics into the existing functional layers
- `tonesoul/dream_engine.py` persists dream collisions through the gateway as working-memory style records

Those seams already do real work. Replacing them directly with the subjectivity ladder would blur two different questions:

- where should this record live operationally?
- what kind of self-forming memory is this allowed to become?

The implementation contract should keep those questions separate.

## Core Decision: Two Axes, Not One

ToneSoul should model memory on two independent axes:

- `storage_layer`: current operational layer for retention/retrieval behavior
- `subjectivity_layer`: semantic promotion layer for self-formation

The near-term rule is:

- keep `MemoryLayer` as the storage axis
- add `subjectivity_layer` as a separate contract field

That avoids breaking current storage behavior while making room for subjectivity-aware promotion.

## Axis Definitions

### 1. `storage_layer`

This is the existing operational layer:

- `working`
- `experiential`
- `factual`

Its job is practical:

- retention and decay behavior
- query filtering
- current compatibility with `SoulDB`, `Consolidator`, and existing tests

It is not sufficient to express vows or identity.

### 2. `subjectivity_layer`

This is the new semantic axis:

- `event`
- `meaning`
- `tension`
- `vow`
- `identity`

Its job is philosophical and governance-facing:

- what kind of memory claim is being made
- how hard promotion should be
- what level of review is needed
- whether the memory is allowed to shape future subject behavior

## Minimal Shared Contract

Every subjectivity-aware memory payload should converge on a shared set of fields:

- `subjectivity_layer`
- `confidence`
- `provenance`
- `promotion_gate`
- `decay_policy`
- `summary`
- `evidence`
- `source_record_ids`

Recommended optional helpers:

- `subjectivity_status`
- `promotion_reviewed_at`
- `promotion_reviewed_by`
- `subjectivity_parent_id`

The point is not to add many fields immediately. The point is to freeze the vocabulary before multiple writers invent incompatible variants.

## Layer-Specific Expectations

### `event`

Required emphasis:

- auditable source
- compact observation
- no inflated interpretation

Expected fields:

- `event_type`
- `summary`
- `provenance`
- `evidence`

### `meaning`

Required emphasis:

- interpretation grounded in one or more source events
- uncertainty stays explicit

Expected fields:

- `interpretation`
- `source_record_ids`
- `confidence`

### `tension`

Required emphasis:

- unresolved conflict, not just interpretation
- explicit competing values / boundaries / commitments

Expected fields:

- `tension_kind`
- `tension_score`
- `conflict_targets`
- `source_record_ids`

### `vow`

Required emphasis:

- stable behavioral commitment
- promotion should be exceptional, not automatic

Expected fields:

- `vow_text`
- `derived_from_ids`
- `promotion_gate`
- `review_basis`

### `identity`

Required emphasis:

- long-horizon continuity
- compressed narrative that survived repeated review

Expected fields:

- `identity_statement`
- `supporting_vow_ids`
- `stability_window`
- `review_count`

## Promotion Contract

Promotion should not be symmetric.

Recommended policy:

- `event -> meaning`: allowed for reviewed synthesis with provenance-preserving traceability
- `meaning -> tension`: allowed when unresolved contradiction, recurrence, or governance friction is explicit
- `tension -> vow`: blocked by default unless human review or strong repeated validation exists
- `vow -> identity`: never direct from one cycle; requires durable retrospective evidence

Practical guardrail:

No single vivid runtime fragment should auto-promote itself into `vow` or `identity`.

## Mapping To Current Code

### `tonesoul/memory/write_gateway.py`

Treat gateway as the canonical admissibility seam.

Near-term responsibility:

- accept `subjectivity_layer` on payloads
- validate the field against the canonical enum
- require provenance/evidence as it already does
- reject direct `vow` / `identity` writes unless a stronger promotion gate is present

### `tonesoul/memory/soul_db.py`

Do not repurpose `MemoryLayer` immediately.

Near-term responsibility:

- preserve existing `layer` behavior
- store `subjectivity_layer` inside payload first
- only add a dedicated DB column later if query/index pressure proves it is needed

This keeps migration incremental and testable.

### `tonesoul/memory/consolidator.py`

Current `_classify_for_promotion()` is keyword-based and maps only into the storage axis.

Near-term responsibility:

- keep storage promotion compatible
- later replace keyword-only logic with explicit promotion into subjectivity candidates
- make the consolidator the likely home for `tension -> vow` review logic

### `tonesoul/dream_engine.py`

Dream collisions should not jump straight to identity-like memory.

Near-term responsibility:

- continue writing through `MemoryWriteGateway`
- keep `storage_layer = working` for collision-style runtime traces
- allow future payloads to declare `subjectivity_layer = tension` when the collision is explicitly framed as unresolved force rather than raw observation

This keeps dream runtime expressive without letting it self-author identity.

### `tonesoul/schemas.py`

The next implementation seam should be schema-first.

Likely additions:

- `SubjectivityLayer`
- `SubjectivityStatus`
- `MemorySubjectivityPayload`
- optional layer-specialized builders if runtime duplication appears

## Migration Strategy

Phase order should stay narrow:

1. Freeze the vocabulary in docs.
2. Add schema-backed `subjectivity_layer` validation.
3. Teach `MemoryWriteGateway` to validate/write the field safely.
4. Let `DreamEngine` and `Consolidator` emit candidate subjectivity layers.
5. Only then decide whether `SoulDB` needs indexed first-class storage for the field.

This ordering matters because it avoids mixing philosophy, migration, and storage rewrites in one changeset.

## Public / Private Boundary

The public repo may safely contain:

- the field names
- the promotion contract
- the admissibility rules
- the migration strategy

The public repo should not commit:

- raw private `.jsonl` memory corpora
- `soul.db` contents
- unreviewed identity-like private traces

The contract belongs in public. The intimate corpus does not.

## Architectural Conclusion

If ToneSoul wants memory to support subjectivity, it should not force one enum to serve two jobs.

The correct move is:

- keep operational storage semantics stable
- add a separate subjectivity contract
- make promotion stricter as memory moves closer to `vow` and `identity`

That separation is what lets the system remember without prematurely mythologizing itself.
