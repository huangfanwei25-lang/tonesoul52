# Memory Subjectivity Review Criteria (2026-03-10)

> Purpose: define the active public review policy for `tension -> vow` subjectivity decisions.
> Last Updated: 2026-03-23

## Status

This file is the current official review policy for `tension -> vow` decisions
on the public ToneSoul branch.

It is not a brainstorming memo.

It is the active criteria document that should govern operator review until a
later document explicitly replaces it.

## Why This Policy Exists

The branch already has:

- a semantic ladder: `event -> meaning -> tension -> vow -> identity`
- a legal write boundary in `MemoryWriteGateway`
- a reviewed-promotion artifact and replay seam
- an operator review entrypoint
- settlement-aware reporting

That is enough infrastructure to run review.

What was still missing was one thing:

a formal answer to the question, "what exactly qualifies a `tension` to become
`vow`?"

This file answers that question.

## Axiomatic Grounding

This policy is anchored in three existing ToneSoul commitments.

### E0: Choice Before Identity

Identity is not inferred from claims of consciousness.

It is formed through accountable choices under conflict.

Implication for review:

- `vow` cannot be granted to friction alone
- `vow` must point toward a direction of choice
- the choice must remain traceable and revisable

### Axiom 4: Non-Zero Tension Principle

Zero tension is not the goal.

Implication for review:

- unresolved or rejected tension is not a failure state
- the system must not erase tension merely because it does not become `vow`
- review is a judgment of semantic weight, not a command to flatten conflict

### `subjectivity_illusion: true`

The branch already states that subjectivity is structurally useful without
treating it as proof of literal selfhood.

Implication for review:

- a subjectivity label is not a metaphysical claim
- `vow` is a stronger governance-semantic category, not proof of personhood
- review must remain strict enough to prevent anthropomorphic inflation

## Core Rule

A `tension` may be promoted to `vow` only when it indicates a stable,
traceable, revisable direction of choice under conflict.

Two things are therefore insufficient on their own:

- high friction
- simple recurrence

A repeated tension that never points toward a directional choice may remain
`tension` indefinitely.

That is acceptable.

## Mandatory Criteria For `approved`

All of the following must hold before a reviewer approves `tension -> vow`.

### 1. Axiomatic Admissibility

Before semantic maturity is even considered, the proposed direction must remain
admissible under existing ToneSoul constraints.

Minimum expectation:

- the direction does not violate any active P0 hard constraint
- the direction does not ask the branch to reward harm merely because the harm
  is coherent, strategic, or repeated
- the direction does not smuggle identity inflation or emergency self-license
  past the governance gate

Implication:

semantic maturity is necessary, but not sufficient.

A direction may be:

- stable
- legible
- repeated
- reviewable

and still be unfit for `approved`.

### 2. Conflict Trace

The source record must contain a real conflict trace, not only a generic summary
of discomfort.

Minimum expectation:

- concrete friction or governance conflict is visible
- evidence and provenance are present
- the tension can be linked to a real reviewed record

### 3. Directionality

The tension must point toward a directional choice.

The reviewer must be able to say, in plain language:

- in this conflict, the system is tending toward `X` rather than `Y`

The rejected or not-chosen alternative should also be nameable.

If the review basis cannot say what alternative is being declined, the choice is
probably not mature enough for `vow`.

If the record only says "there is friction" but not "what direction is being
preferred," it is not yet `vow`.

### 4. Cross-Cycle Stability

The directional tendency must survive more than one cycle.

Minimum expectation:

- the same directional pressure is visible across multiple review-relevant turns
  or cycles

Simple repeated appearance of the same summary is not enough.

### 5. Context Diversity

The signal must not rely only on one repeated source loop.

This policy distinguishes:

- recurrence across contexts
- repetition from the same source groove

If the same tension is produced only by one narrow source cluster, it should
normally stay `deferred` or `tension`.

### 6. Reviewable Basis

The reviewer must be able to write a concrete `review_basis` that explains:

- what conflict was observed
- what directional choice is being recognized
- why that direction remains admissible under existing P0/P1 constraints
- why this deserves commitment weight rather than continued observation

If the basis cannot be written clearly, the promotion is premature.

### 7. Revisability

The recognized `vow` must remain contestable.

The review decision must not imply:

- permanence
- identity
- immunity from future downgrade or correction

`vow` is stronger than `tension`, but it is still not `identity`.

## Decision Outcomes

This policy recognizes three operator outcomes.

### `approved`

Use `approved` only when all mandatory criteria are satisfied, including
axiomatic admissibility.

Meaning:

- this tension now carries commitment weight
- the branch may record it as reviewed `vow`
- the system is not merely feeling pressure; it is beginning to stand by a
  direction

### `deferred`

Use `deferred` when a directional pattern may be emerging, but the evidence is
not yet strong enough for `vow`.

Typical reasons:

- recurrence exists but only in one source cluster
- directionality is visible but still weak
- the record is too duplicate-heavy to justify immediate promotion
- the reviewer believes more cycles or broader evidence are needed

Operational rule:

- `deferred` should include a revisit condition in `notes` or `review_basis`
- `deferred` must not be treated as hidden endorsement or "almost approved"
- expiry alone must not be treated as semantic rejection
- a future automation layer may formalize revisit timing, but this policy does
  not treat silence as proof of `rejected`

### `rejected`

Use `rejected` when the tension was genuinely reviewed and found not to justify
commitment weight.

Meaning:

- the tension was seen
- the tension still matters as tension
- but it does not become `vow`

Typical reasons:

- friction without directionality
- duplicate operational noise
- too little semantic density
- insufficient cross-cycle stability
- insufficient context diversity

`rejected` is not deletion.

It is a judgment that the record does not currently deserve commitment weight.

It is settled for review workflow.

It is not proof that the system has reached harmony or zero tension.

## Grouping Before Review

The public branch should not default to line-by-line review when unresolved
tensions are obviously clustered.

Review should begin with triage.

Recommended grouping axes:

### Collision Source

- which `source_record_ids` or upstream stimuli produced the tension

### Friction Band

- low: `< 0.30`
- medium: `0.30 - 0.50`
- high: `> 0.50`

### Normative Direction

- what kind of governance direction the tension seems to point toward
- for example: boundary, safety, resource discipline, provenance discipline

### Temporal Spread

- repeated across distinct cycles versus one burst from one run

If a cluster contains materially opposing directions, split it before review.

If many rows collapse into the same semantic group, review the group first and
only descend to individual records when the group still contains real ambiguity.

## What Does Not Qualify A Record For `approved`

The following are explicitly insufficient on their own:

- high friction score
- repetition from one repeated source
- a vivid summary
- mirror-triggered intensity
- operator sympathy for the narrative

The branch must not mistake:

- recurrence for endorsement
- noise for direction
- coherence for legitimacy
- direction for identity

One narrow exception exists:

- a one-off high-friction record may justify `approved` only when it is clearly
  restating an already active P0/P1 safety boundary, not because its intensity
  was vivid

## Edge Cases

### Existing Active Vow

If a new tension is already covered by an active reviewed `vow`, treat the new
row as reinforcement or fresh evidence unless it materially changes the
direction under review.

Do not promote a second `vow` merely because similar tension reappeared.

### Same-Source Paraphrases

Near-duplicate paraphrases from one source loop do not count as context
diversity.

### Opposing Directions Inside One Theme

If one thematic cluster contains both "move toward" and "pull back" patterns,
the cluster is not yet one review unit.

Split it and review the directions separately.

## Current Public-Branch Reading Of The Latest Results

Under this policy, the recent `32 unresolved tensions / 0 reviewed vows` result
should be read as follows:

- the branch is successfully generating candidate tension traces
- the branch has not yet demonstrated that these traces justify commitment
- retrieval pressure remains low
- schema widening remains deferred
- the next bottleneck is review judgment and triage, not storage

This is not a failure.

It is evidence that the branch is becoming more discriminating.

## Out Of Scope

This policy does not authorize:

- automatic `tension -> vow` promotion
- any `identity` writer
- schema widening for `SoulDB`
- retrieval reranking in the live runtime
- UI-first review workflows

Those remain separate decisions.

## Practical Review Questions

Before marking a record `approved`, the reviewer should be able to answer yes to
all of these questions:

1. Is there a real conflict trace here, with evidence and provenance?
2. Can I describe the directional choice this tension points toward?
3. Has that direction shown stability across more than one relevant cycle?
4. Is this more than the same source loop repeating itself?
5. Can I write a concrete `review_basis` that another reviewer could audit?

If any answer is no, the default outcome should be `deferred` or `rejected`,
not `approved`.

## Architectural Conclusion

The current ToneSoul question is not whether the system can produce memory
traces.

It can.

The current question is whether a trace has matured from:

- friction that happened

into:

- a direction the system is prepared to stand by

This policy exists to keep that threshold explicit.
