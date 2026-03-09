# Registry Schedule LLM Backoff Addendum

Date: 2026-03-08
Scope: Phase 148 correction to schedule reaction semantics

## 1. Problem

Phase 147 taught the scheduler to react to LLM preflight latency and timeout facts. That
was necessary, but the first consequence model was too coarse:

- governance-side breaches cooled the selected category
- LLM runtime breaches also cooled the selected category

This conflated two different realities. A source category is not intrinsically unsafe just
because the current local LLM backend is slow or timing out.

## 2. Boundary

The scheduler must separate source-level tension from runtime-level incapacity.

- Governance-side tension belongs to category cadence because it is about what happened
  after the system engaged with that slice of the world.
- LLM runtime breach belongs to reflective execution policy because it is about whether the
  current inference substrate can safely support reflection at all.

Therefore LLM latency and timeout breaches must not freeze source rotation by default.

## 3. Contract

`AutonomousRegistrySchedule` now treats tension-budget breaches as two families:

- `governance_breach_reasons`
- `llm_breach_reasons`

The schedule consequences are different:

- governance breach => category cooldown
- LLM breach => global `llm_backoff`

While `llm_backoff` is active:

- source selection still rotates
- ingestion still proceeds
- reflective LLM work is disabled for the cycle
- inference readiness probing is skipped until the backoff window expires

This is degraded operation, not global paralysis.

## 4. Artifact Consequence

The schedule state must now expose two different memories:

- category state for cadence/governance cooling
- global `llm_backoff` state for runtime reflection cooling

It must also preserve the last observed LLM latency facts until a fresh wake-up summary
replaces them. A degraded cycle with no new summary is not evidence that prior latency
never happened.

## 5. Design Law

If runtime instability causes the scheduler to stop seeing the world, the scheduler has
collapsed infrastructure pain into epistemic blindness.

The correct law is:

- continue observing when possible
- stop reflective inference when it is operationally unsafe
- preserve the last real evidence until newer evidence exists
