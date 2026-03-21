# Registry Schedule Category Policy Addendum

Date: 2026-03-07
Scope: Phase 136 follow-up to `registry_schedule_profile_theory_2026-03-07.md`

## 1. Why Another Layer Is Needed

Phase 135 gave the scheduler memory, but not rhythm. The scheduler can now avoid
immediate repetition and temporarily back off unstable entries, yet it still treats
all eligible categories as rhythmically flat unless the operator manually narrows the
filter set.

That leaves one missing policy seam:

- source registry decides what is admissible
- schedule profile decides how often each category should reappear
- governance kernel decides what to do with the resulting tension

The new work belongs strictly in the schedule profile layer.

## 2. Deterministic Weighted Cadence

Category weight must not become random sampling.

If a profile says `vulnerability-intel` matters more than `research-archive`, the
scheduler should not roll dice. Probabilistic selection would make two identical runs
produce different histories from the same state, which weakens:

- testability
- replayability
- artifact explanation

The correct design is deterministic weighted cadence:

1. Expand category weights into a stable cadence ring.
2. Advance through that ring with a persisted category cursor.
3. Inside each category, keep entry selection round-robin.

This means weight expresses attention rhythm, not truth ranking.

## 3. Category-Scaled Failure Cooling

Failure backoff also needs one more degree of freedom. A feed category that is expected
to be volatile may deserve a different cooling slope than a slower research category.

The clean decomposition is:

- `failure_backoff_cycles`: the base cooling unit
- `category_backoff_multipliers`: category-specific scaling
- `backoff_until_cycle`: concrete per-entry result written into scheduler state

This keeps trust and cadence separate. A longer backoff does not mean the source is
less trustworthy; it only means the scheduler should stop spending immediate attention
there for a while.

## 4. Boundary Law

The following separations must stay intact:

- `source_registry` owns admissibility, host allowlist, and review freshness.
- `schedule_profile` owns cadence, category weights, and operational cooling.
- `AutonomousRegistrySchedule` executes resolved primitives and persists artifact state.
- `GovernanceKernel` owns friction, council escalation, and intervention semantics.

Therefore category weights and backoff multipliers must not leak into `soul.db`,
`self_journal.jsonl`, or governance memory.

## 5. Artifact Consequence

If this policy is implemented correctly, schedule artifacts should be able to answer:

- which category slot was selected this cycle
- which weight caused that category to appear again sooner
- which entries were deferred by revisit cooldown or failure backoff
- which category multiplier extended the backoff window

If an operator cannot reconstruct those answers from the artifact, the scheduler is
still too implicit.
