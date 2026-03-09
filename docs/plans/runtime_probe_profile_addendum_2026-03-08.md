# Runtime Probe Profile Addendum

## Why A Profile

Phase 150 proved a real runtime pattern in the field:

- cycle 1 can request global `llm_backoff`
- cycle 2 can execute under that backoff
- the same period does not necessarily imply governance distrust of the selected source category

Keeping that scenario as a long CLI recipe is operationally weak. It forces humans and agents to remember an accidental threshold bundle instead of reusing a declared policy surface.

## Design Intent

`runtime_probe_watch` exists to answer one question cleanly:

Can ToneSoul still distinguish runtime incapacity from epistemic/source distrust when reflective LLM work times out?

So the profile is intentionally biased:

- governance thresholds are relaxed
- runtime thresholds stay tight
- cadence and source scope remain small and reproducible

## Contract

- `runtime_probe_watch` is not a new scheduler behavior
- it is a named composition of existing behaviors
- passing this profile means:
  - `llm_backoff_requested` and `llm_backoff_active` can be observed as separate states
  - governance cooldown remains at zero for the same sample unless a genuine governance breach appears

## Operational Meaning

This profile turns a verification story into a repeatable ritual.

That matters because a governance system should not depend on operator memory of last week's successful command. If a runtime-only verification matters architecturally, it deserves a stable name in the schedule contract.
