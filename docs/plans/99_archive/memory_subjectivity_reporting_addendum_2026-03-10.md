# Memory Subjectivity Reporting Addendum (2026-03-10)

> Purpose: define the operator reporting surfaces used to inspect accumulated subjectivity layers in public memory.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch can now:

- express `subjectivity_layer`
- validate it at write time
- keep `tension -> vow` promotion reviewable

But that still leaves one operator gap:

How do we inspect what kind of subjectivity the system is actually accumulating?

Without a read/report surface, the branch can write subjectivity-aware payloads but cannot explain their distribution in a legible way.

## Core Rule

Phase C should stay observational.

It should help operators see:

- how many records remain at `event`
- how many become `meaning`
- which traces are still unresolved `tension`
- which commitments have passed review into `vow`

It should **not** widen external API contracts or introduce subjectivity-ranked recall yet.

## Minimal Public-Safe Surface

This phase adds two internal helpers under `tonesoul/memory/subjectivity_reporting.py`:

- `summarize_subjectivity_distribution(...)`
- `list_subjectivity_records(...)`

They are intentionally narrow:

- they work off existing `SoulDB` records
- they read payload-first storage without requiring schema widening
- they produce operator-facing summaries rather than user-facing policy changes

## What Counts As Unresolved Tension

`tension` is still unresolved when:

- `subjectivity_layer == tension`
- and its `promotion_gate` is absent or still below review-strength status

That means reviewed or approved promotion metadata stops a tension record from being reported as unresolved, even if the original trace remains visible in storage.

## Guardrail

These helpers are reporting surfaces, not retrieval policy.

This phase deliberately does **not**:

- rank recall by `subjectivity_layer`
- add new HTTP endpoints
- auto-promote `tension` into `vow`
- move private memory corpus concerns into the public repository

## Architectural Conclusion

The first job of subjectivity-aware retrieval is not to steer generation.

It is to make the branch's own semantic accumulation inspectable.

Only after that inspection surface exists should the project consider whether query/ranking pressure justifies a deeper retrieval or persistence upgrade.
