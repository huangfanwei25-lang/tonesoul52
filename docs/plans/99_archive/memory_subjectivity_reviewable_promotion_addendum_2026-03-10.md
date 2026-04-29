# Memory Subjectivity Reviewable Promotion Addendum (2026-03-10)

> Purpose: define the reviewed-promotion lane and artifact requirements for promoting `tension` into `vow`.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already had two important constraints:

- `subjectivity_layer` exists as a public contract
- direct `vow` / `identity` writes are blocked unless a review-strength `promotion_gate` is present

That was enough to prevent unsafe auto-promotion, but it still left one gap:

What does a legitimate reviewed promotion actually look like?

Without that answer, the system can block unsafe writes, but it still cannot express a proper reviewed lane for `tension -> vow`.

## Core Rule

`vow` is not a stronger `tension` record.

It is a reviewed commitment derived from tension.

That means promotion into `vow` must carry review metadata that is auditable, not just an approval-like flag.

## Required Review Metadata

For a `vow` write to be legitimate, the promotion lane now requires:

- a review-strength `promotion_gate.status`
- `reviewed_by`
- `review_basis`

The important addition is `review_basis`.

`reviewed` without an explanation is not a meaningful accountability trace.

The system must be able to answer:

- who reviewed this?
- on what basis was this promoted?

## Narrow Runtime Effect

This phase deliberately does **not** introduce automatic vow promotion.

Instead it adds a reviewable helper lane:

- `build_reviewed_vow_payload(...)`
- `promote_reviewed_tension_to_vow(...)`

Both live in `tonesoul/memory/consolidator.py`.

They keep the phase narrow by requiring explicit caller intent and by rejecting non-tension sources.

## Storage / Subjectivity Alignment

This phase keeps the contract split intact:

- `subjectivity_layer` moves from `tension` to `vow`
- operational `layer` is set to `factual`

That choice is deliberate.

Once a commitment has passed explicit review, it should no longer live as a purely working-memory trace.

But this still does not make it identity.

## Guardrail

The reviewed lane must remain explicit:

- no Dream cycle may self-promote to `vow`
- no sleep consolidation pass may auto-promote to `vow`
- reviewed promotion is a separate act, not a side effect of retention

That separation prevents the system from mistaking recurrence for endorsement.

## Architectural Conclusion

The purpose of the reviewable lane is not to make promotion easier.

It is to make the transition from unresolved tension to commitment legible, attributable, and contestable.

That is the minimum standard for any memory system that claims `vow` is a stronger category than ordinary tension.
