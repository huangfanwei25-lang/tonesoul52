# Registry Schedule Tension Budget Addendum

Date: 2026-03-07
Scope: Phase 137 schedule reaction policy for wake-up tension signals

## 1. Problem

The autonomous scheduler already knows how to:

- rotate across reviewed sources
- avoid immediate repetition
- back off sources that fail operationally
- bias attention rhythm across categories

What it still does not know is how to react when the downstream dream cycle itself
reports a high-tension outcome. If `max_friction_score`, `max_lyapunov_proxy`, or
`council_count` spikes, the scheduler currently has no explicit policy for slowing down.

## 2. Boundary

This reaction must not become a second governance engine.

- `GovernanceKernel` remains the only place that computes friction and intervention logic.
- `AutonomousWakeupLoop` remains the only place that summarizes those outcomes per cycle.
- `AutonomousRegistrySchedule` may only consume the summarized signal and turn it into a
  temporary cadence consequence.

So the scheduler does not decide whether tension is "correct." It only decides whether
observed tension is high enough to cool attention for a while.

## 3. Contract

A schedule profile may define a cycle-level tension budget with:

- `tension_max_friction_score`
- `tension_max_lyapunov_proxy`
- `tension_max_council_count`
- `tension_cooldown_cycles`

Any threshold may be omitted. A budget breach occurs when any defined threshold is exceeded.

## 4. Consequence

When a cycle breaches the tension budget:

- each category selected in that schedule tick receives temporary cooldown
- the cooldown is written to schedule state, not soul memory
- the next schedule ticks must report the category as deferred by `tension_budget_cooldown`

This is category-scoped operational memory, not semantic memory and not trust memory.

## 5. Design Law

The scheduler must react only to explicit observed metrics. It must not:

- reconstruct friction from raw memories
- infer hidden governance state
- rewrite thresholds inside `GovernanceKernel`

If the wake-up summary cannot justify the cooldown in plain artifact terms, the scheduler
is doing too much.
