# ToneSoul Promotion-Ready Result Surface Contract

> Purpose: define how bounded self-improvement trial outcomes may surface to later agents without bloating first-hop shells, impersonating runtime truth, or leaving raw trial residue as a new hidden swamp.
> Status: accepted architecture contract for `Phase 795`.
> Authority: architecture contract. This file governs how self-improvement results may be surfaced after analyzer closeout. It does not itself promote any candidate.

---

## Why This Exists

After ToneSoul has:

- an evaluator harness
- an experiment-registry boundary
- a bounded mutation-space contract
- an analyzer and promotion gate
- a first bounded trial wave

one practical gap remains:

`how should later agents see the result of those trials without rereading raw run artifacts or mistaking trial outcomes for runtime truth?`

Without this contract, two bad outcomes become likely:

- trial results stay too hidden, so later agents reopen the same lane blindly
- trial results surface too aggressively, so session-start or observer-window start sounding like experiment dashboards

This contract exists to prevent both.

---

## Compressed Thesis

Bounded self-improvement results should surface in a dedicated result layer:

- visible enough to orient later work
- narrow enough to stay secondary
- explicit enough to preserve supersession and residue posture

They must not become:

- canonical governance truth
- runtime coordination truth
- identity truth
- a new default packet or observer tier

---

## What This Is

This contract defines:

- the allowed result-surface classes
- where those results may appear first
- what replay rule later agents should follow
- how supersession should work
- how parked, retired, and blocked results should remain visible without polluting first-hop shells

It is the surfacing boundary for post-analyzer trial outcomes.

---

## What This Is Not

This is **not**:

- a replacement for the experiment registry
- a replacement for raw run artifacts
- a new first-hop authority lane
- a promotion license by itself
- a justification for stuffing self-improvement history into `session-start`, `observer-window`, or packet defaults

The result surface is a bounded readout layer, not a new truth tier.

---

## Result Surface Classes

Every surfaced trial outcome must map to one of these classes:

- `promoted_result`
- `parked_result`
- `retired_result`
- `blocked_result`
- `not_ready_result`

These are surfacing classes, not authority classes.

They describe how a later agent should interpret the analyzer outcome.

---

## Primary Landing Rule

The first legitimate home for surfaced trial outcomes is:

- a dedicated status surface

For v0, that means artifacts like:

- `docs/status/self_improvement_trial_wave_latest.json`
- `docs/status/self_improvement_trial_wave_latest.md`

This is deliberate.

It lets later agents inspect trial outcomes without forcing those outcomes into:

- `session-start`
- `observer-window`
- `packet`
- dashboard Tier 0 or Tier 1 defaults

---

## First-Hop Non-Bloat Rule

Self-improvement results must not become default first-hop payload.

Specifically:

- `session-start` must not expand into a trial-history bundle
- `observer-window` must not become an experiment timeline
- packet/readiness surfaces must not carry raw trial results as if they were live coordination truth

If a future shell wants a compact cue, it must be:

- opt-in
- bounded
- clearly secondary

---

## Minimum Surfaced Result Shape

Every surfaced result should preserve at least:

- `candidate_id`
- `target_surface`
- `status`
- `result_surface.surface_status`
- `evidence_bundle_summary`
- `promotion_limit`
- `replay_rule`
- `supersession_posture`
- `residue_posture`
- `next_action`

This is enough for later agents to know what happened without opening raw artifacts first.

---

## Replay Rule

Later agents should follow this read order:

1. read the dedicated result surface
2. check the analyzer closeout summary
3. open raw run artifacts only when the outcome is:
   - disputed
   - blocked in a surprising way
   - or relevant to a new closely related trial

This keeps result surfacing lightweight while still preserving drilldown.

---

## Supersession Rule

Every surfaced result must declare one of these supersession postures:

- `active_until_superseded`
- `superseded_by_newer_trial`
- `historical_only`

Supersession must be scoped by mutation family or target surface.

A new result about:

- `consumer_contract.first_hop_order`

may supersede an older result about the same family.

It must not silently supersede unrelated surfaces such as:

- dashboard tier alignment
- operator retrieval cueing
- launch-health packaging

---

## Residue Posture Rule

Every surfaced result must declare where its residue belongs.

Allowed residue postures include:

- `keep_visible_in_latest_status_surface`
- `park_in_status_surface`
- `historical_only`
- `retired_from_first_hop`

This is what prevents old experiments from piling up as a new hidden swamp.

The rule is:

- recent, active, bounded results may stay visible
- older or superseded results should decay into history
- raw run artifacts should stay in lineage storage, not in first-hop shells

---

## Carry-Forward Rule

Surfaced self-improvement results may inform:

- future candidate selection
- operator expectation-setting
- supersession and parking decisions

They may **not** by themselves authorize:

- governance promotion
- identity or vow mutation
- transport-semantics change
- retrieval or council authority inflation

The result surface is advisory to future improvement work, not a shortcut to runtime truth.

---

## Promoted Result Rule

`promoted_result` means:

- the bounded gain was strong enough to carry forward
- the promotion gate passed
- the result may stay visible in the latest bounded result surface

It does **not** mean:

- canonical truth
- solved forever
- runtime superiority across unrelated consumers

Promoted results still carry promotion limits.

---

## Parked, Retired, And Blocked Result Rule

These classes must remain visible enough to stop repeated confusion.

- `parked_result`
  - useful idea, not strong enough yet
- `retired_result`
  - not worth continuing in its current form
- `blocked_result`
  - waiting on another lane or prerequisite

These should usually surface as:

- bounded status records
- clear next action
- clear residue posture

not as hidden leftovers inside raw experiments.

---

## Overclaim Rule

Result surfaces must carry one explicit overclaim warning.

Examples:

- better packaging is not better reasoning
- promoted retrieval cueing is not solved memory
- promoted parity alignment is not predictive calibration

This keeps surfaced trial results from re-entering the system as mythology.

---

## Consumer Rule

If future consumers render self-improvement results, they must keep them:

- secondary to runtime truth
- clearly labeled as trial outcomes
- bounded to recent and relevant results only

They must not flatten:

- promoted results
- parked results
- blocked results

into one generic "improvement history" pane without posture labels.

---

## First Good Use

The first good use of this contract is simple:

- keep `self_improvement_trial_wave_latest.*` as the primary surfaced result
- let later agents read that status first
- avoid pulling result history into session-start or observer-window until a stronger compact-cue design exists

That is enough for v0.

---

## One-Sentence Summary

`ToneSoul's promotion-ready result surface exists so self-improvement outcomes stay visible, replayable, and supersedable without turning trial history into a new authority tier or a new first-hop status swamp.`
