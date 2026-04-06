# ToneSoul Compact Self-Improvement Result Cue Design (2026-04-07)

> Purpose: define the smallest safe way a later shell may reference current self-improvement posture without turning trial history into first-hop runtime truth.
> Status: phase design note for `Phase 796`.
> Authority: planning aid. Runtime truth remains in code, tests, accepted contracts, and dedicated status artifacts.

---

## Why This Exists

ToneSoul now has:

- a bounded self-improvement loop v0 spec
- a first trial wave
- a promotion-ready result-surface contract
- dedicated status artifacts for the latest trial wave

So the next question is no longer:

`should trial outcomes exist?`

It is:

`does any compact cue belong in later shells, and if so where can it appear without polluting first-hop operator truth?`

This design exists to answer that before any runtime payload grows.

---

## Compressed Thesis

The primary home of self-improvement outcomes should remain:

- dedicated status artifacts

Any compact cue must be:

- opt-in
- secondary
- operator-facing
- clearly labeled as trial posture

It must not become:

- a new Tier 0 gate
- a new Tier 1 orientation pillar
- a packet truth field
- an observer-window stability signal

---

## Current Surface Survey

## 1. `session-start --tier 0`

Current job:

- readiness
- task track
- deliberation mode
- canonical center summary
- hook chain
- bounded mutation preflight

Assessment:

- **do not place the cue here**

Why:

- Tier 0 is instant gate
- self-improvement posture is not needed to decide whether immediate work is safe
- any extra cue here would compete with the main bounded move

---

## 2. `session-start --tier 1`

Current job:

- canonical center
- subsystem parity
- closeout attention
- observer shell
- hook chain
- mutation preflight

Assessment:

- **do not place the cue in default Tier 1 payload**

Why:

- Tier 1 already carries the minimum current-story shell
- trial posture would be easy to misread as part of current runtime truth
- the likely value is lower than the risk of authority flattening

---

## 3. `observer-window`

Current job:

- stable / contested / stale
- canonical center
- hot-memory ladder
- closeout attention
- mutation preflight

Assessment:

- **do not place the cue in stable/contested/stale buckets**

Why:

- those buckets are about current orientation and bounded handoff
- trial outcomes are experiment lineage, not current-state truth
- mixing them would blur:
  - runtime posture
  - experiment posture

---

## 4. `packet / runtime adapter`

Assessment:

- **forbid direct cue insertion in v0**

Why:

- packet surfaces are transport and coordination truth
- self-improvement results should not travel as if they were live coordination state

---

## 5. `dashboard operator shell`

Assessment:

- **best future candidate for a compact cue**

Why:

- operator-facing
- already secondary to CLI/runtime truth
- can render a small, clearly bounded cue without changing transport or first-hop shell payload

Best likely location:

- dashboard status panel secondary block
- or Tier 2 drawer accessory card

Not:

- top hero area
- first metric row
- Tier 0 start strip

---

## Primary / Secondary Rule

Primary result surface:

- `docs/status/self_improvement_trial_wave_latest.json`
- `docs/status/self_improvement_trial_wave_latest.md`

Secondary compact cue:

- may appear only after explicit design and bounded implementation
- must point back to the dedicated status surface
- must remain subordinate to runtime truth

This means:

- read status artifact first
- compact cue later, if needed

not the reverse.

---

## Recommended Cue Shape

If a compact cue is implemented later, its shape should stay very small:

- `present`
- `summary_text`
- `latest_result_posture`
- `top_promotion_limit`
- `next_action`
- `source_path`
- `receiver_rule`

Recommended `summary_text` example:

`self-improvement posture: 1 promoted, 1 parked; status surface only`

Recommended `receiver_rule`:

`Trial posture is secondary. Open the dedicated status surface before treating any result as guidance for a new candidate.`

---

## Explicit Non-Goals

This cue must not do any of these:

- show raw trial artifacts inline
- summarize multiple historical waves as one score
- appear in Tier 0 by default
- appear in packet/import posture
- override `closeout_attention`, `canonical_center`, or `subsystem_parity`
- teach a new authority tier

---

## Best Next Move

If ToneSoul implements this later, the safest next step is:

- dashboard-only pilot
- collapsed by default
- one-line summary plus source-path link/copy cue

That is enough to test usefulness without contaminating first-hop shells.

---

## Decision

For now:

- keep dedicated status artifacts as the primary result surface
- do **not** add a cue to Tier 0, Tier 1, observer buckets, or packet
- treat dashboard operator shell as the only plausible future compact-cue pilot

---

## One-Sentence Summary

`ToneSoul should surface self-improvement posture through dedicated status artifacts first, and only later consider a tiny dashboard-only cue that points back to those artifacts without entering first-hop runtime truth.`
