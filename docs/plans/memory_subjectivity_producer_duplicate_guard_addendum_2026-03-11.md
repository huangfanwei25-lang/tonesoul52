# Memory Subjectivity Producer Duplicate Guard Addendum (2026-03-11)

> Purpose: define the duplicate-guard expectations for upstream subjectivity producers that keep rewriting the same source loop.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The queue work proved something important:

- review batching can now settle or defer the current pressure honestly
- carry-forward can now annotate whether a fresh group matches prior judgment
- deferred context is now visible on the main operator surfaces

But none of that changes the upstream fact that DreamEngine can keep writing new
`tension` rows for the same live source loop.

That is producer noise, not retrieval debt.

## Core Rule

DreamEngine should not persist a fresh `dream_collision` tension when the same
unresolved collision signature is already live.

The first guard is intentionally narrow:

- signature = normalized `topic` + normalized `source_url`
- if `source_url` is absent, fall back to `topic` + source lineage
- only unresolved `dream_collision` tensions participate in the guard

Practical meaning:

- if the branch is already holding one unresolved OSV homepage tension, a later
  cycle should not keep stacking more rows for the same topic/source loop
- if the same topic appears from a different source loop, the new row should
  still be admissible

## Guardrails

This phase must not:

- rewrite or delete existing tension rows
- reinterpret historical `rejected` decisions as permanent suppression
- auto-settle anything
- change retrieval behavior
- widen `SoulDB` schema

It is a producer-side duplicate guard, not a semantic reclassification layer.

## Architectural Conclusion

The branch has now learned two separate truths:

- review decides what a live tension means
- producer noise control decides how many times the same unresolved tension gets
  written

Those are related, but they are not the same job.
