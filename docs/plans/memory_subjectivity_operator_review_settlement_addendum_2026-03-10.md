# Memory Subjectivity Operator Review + Settlement Addendum (2026-03-10)

> Purpose: define the operator review-and-settlement flow for subjectivity decisions and replayable outcomes.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already has:

- candidate `tension` records
- a canonical reviewed-promotion artifact
- a replay seam that can write reviewed `vow` records through `MemoryWriteGateway`

But one practical gap remained:

the operator still had no first-class way to run a review, and the reporting
lane still could not tell when a specific unresolved tension had already been
settled by an explicit review.

That left the branch with a real reviewed-promotion contract, but only in unit
tests.

## Core Rule

`review -> replay -> report` must become one visible operator lane.

That means three things must happen together:

1. an operator can select a concrete unresolved `tension` record
2. the review decision is preserved as an auditable artifact
3. the reporting lane can tell whether that tension is still unresolved

If the third step is missing, the queue never settles.

## Review Artifact Rule

The canonical reviewed-promotion decision stays the semantic artifact.

But the operational review event should also be recorded in a durable review
ledger so both approved and rejected reviews remain inspectable.

For this phase, `action_logs` is the narrowest acceptable ledger:

- it already exists in `SoulDB`
- it can carry manual review metadata
- it can record approve / reject / defer decisions without polluting memory rows

Approved review still replays through `MemoryWriteGateway`.

Rejected or deferred review should still leave an audit trace even when no `vow`
record is written.

## Settlement Rule

An unresolved `tension` should remain unresolved only while no explicit review
artifact has settled that exact record.

The settlement boundary should therefore be based on the reviewed tension record
id, not only on shared stimulus ids or vague textual similarity.

The narrow rule for this phase is:

- the operator review decision references the reviewed tension record id
- approved replay keeps that linkage in the resulting `vow` payload
- reporting treats a tension as settled when an explicit review artifact points
  at that tension record id

This avoids mutating historical tension rows in place while still letting the
queue shrink honestly.

## Guardrails

This phase still does **not**:

- auto-promote tension into vow
- widen HTTP/API contracts
- widen `SoulDB` memory schema for `subjectivity_layer`
- claim that one reviewed vow implies `identity`

The goal is not to make review cheaper.

It is to make review usable and auditable.

## Architectural Conclusion

The branch no longer needs only a promotion contract.

It needs a settlement contract.

Once an operator has reviewed a concrete tension, the system should be able to
answer all three questions:

- what was reviewed?
- what decision was made?
- does that tension still belong in the unresolved queue?
