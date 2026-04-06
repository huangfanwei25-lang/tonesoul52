# ToneSoul Self-Improvement Evaluator Harness Contract

> Purpose: define the minimum evaluator shape that every bounded self-improvement candidate must pass through before it may be promoted, parked, or retired.
> Status: accepted architecture contract for `Phase 790`.
> Authority: architecture contract. This file defines how ToneSoul judges bounded self-improvement candidates. It does not itself authorize mutation.

---

## Why This Exists

ToneSoul now has enough structure to propose bounded improvements.

What it still lacked was one explicit answer to this question:

`when a candidate claims it improved something, how does ToneSoul decide whether that claim is real, partial, blocked, or not worth keeping?`

Without that answer, self-improvement would drift into:

- nicer prose
- stronger narrative
- smoother demos
- hidden selection bias

instead of an honest improvement discipline.

This harness exists to prevent that.

---

## Compressed Thesis

Every bounded self-improvement candidate must carry:

- a baseline
- a candidate
- a success metric
- a failure watch
- a rollback path
- an outcome classification

If it cannot name those, it is not ready for trial.

---

## What This Is

This harness is the evaluation contract for bounded v0 candidates in areas such as:

- workspace/operator shell
- routing or escalation hints
- consumer-parity packaging
- bounded operator-retrieval packaging
- launch/readout packaging

It is the structure that turns:

- "this seems better"

into:

- "this improved X under Y evidence while still failing or preserving Z"

---

## What This Is Not

This harness is **not**:

- a generic runtime test framework
- a replacement for pytest or validation waves
- an autonomous mutation engine
- a scoring system for identity or selfhood
- a justification for changing governance truth by metric

It is only the evaluation shell for bounded improvement candidates.

---

## Required Candidate Record

Every candidate must declare at least:

- `candidate_id`
- `target_surface`
- `target_consumer`
- `baseline_story`
- `candidate_story`
- `success_metric`
- `failure_mode_watch`
- `rollback_path`
- `overclaim_to_avoid`

Optional but recommended:

- `scope_limit`
- `expected_tradeoff`
- `parity_surfaces`
- `human_gate`

If these are missing, the safest evaluator outcome is:

- `status = not_ready_for_trial`

---

## Target Surface Rule

`target_surface` must name one bounded surface, not a vague system ambition.

Good examples:

- `dashboard.status_panel`
- `session_start.deliberation_mode_hint`
- `consumer_contract.first_hop_order`
- `operator_retrieval.result_shape`

Bad examples:

- `ToneSoul intelligence`
- `memory quality`
- `governance maturity`

The evaluator is only useful when the mutation target is explicit.

---

## Baseline Story Rule

The baseline must say:

- what the current behavior is
- what current friction or failure is visible
- which existing surfaces already constrain the problem

It must not say only:

- "the system feels weak here"
- "this should be more elegant"

The evaluator needs a pre-change story that could in principle be falsified.

---

## Candidate Story Rule

The candidate story must say:

- what changes
- what stays unchanged
- why the candidate might help
- what authority boundary it must not cross

If the candidate cannot say what it deliberately leaves untouched, it is probably too wide for v0.

---

## Success Metric Rule

Every candidate must define one or more bounded success metrics.

Allowed metric classes:

1. `regression`
   - tests stay green

2. `parity`
   - consumers agree more cleanly on the same story

3. `readability_or_operability`
   - operators need fewer steps or encounter less ambiguity

4. `honesty`
   - descriptive/promotional boundaries become clearer

5. `latency_or_surface_budget`
   - a tier opens less or carries less default load

Disallowed metric classes in v0:

- identity coherence
- selfhood strength
- hidden-reasoning quality
- unsupported predictive certainty

---

## Failure-Mode Watch Rule

Every candidate must explicitly watch for at least one failure mode.

Common failure watches:

- authority inflation
- consumer drift
- compaction over-promotion
- dashboard flattening into control-plane soup
- retrieval reading as runtime truth
- smoother wording hiding unresolved blockers

If there is no named failure watch, there is no honest improvement trial.

---

## Evidence Bundle Rule

Promotion must cite an explicit evidence bundle.

Allowed bundle components:

- regression tests
- targeted validation waves
- smoke outputs
- parity checks
- doc/contract consistency checks

Nice prose is not evidence.

If the bundle is thin, the promotion posture must stay thin.

---

## Rollback Path Rule

Every candidate must state how to back out safely.

Rollback may be:

- revert the patch
- restore the old adapter
- disable the new cue or readout
- keep the old shape as fallback

No rollback path means:

- too wide
- or too immature

for v0.

---

## Outcome Classification

Every evaluated candidate must end in one of these:

- `promote`
- `park`
- `retire`
- `blocked`
- `not_ready_for_trial`

Definitions:

### `promote`

Regression green, evidence positive, boundary preserved.

### `park`

Potentially useful, but not strong enough yet or awaiting a later dependency.

### `retire`

The candidate should not continue in its current form.

### `blocked`

The candidate is structurally waiting on another lane or missing prerequisite.

### `not_ready_for_trial`

The proposal is still too vague, too wide, or under-specified.

---

## Anti-Fake-Completion Rule

The evaluator must never output `promote` only because:

- the story is elegant
- the output feels smoother
- the candidate is intellectually attractive

If unresolved items remain central, the outcome must be:

- `park`
- or `blocked`

not `promote`.

This is what keeps self-improvement from becoming self-flattery.

---

## Parity Rule

Candidates that affect shared interpretation must declare:

- which consumers they are expected to preserve parity across

At minimum when relevant:

- Codex-style shell
- Claude-compatible adapter
- dashboard/operator shell
- observer/readout surfaces

If one consumer improves while shared interpretation fractures, the evaluator should fail the candidate or downgrade it to `park`.

---

## Non-Eligible Mutation Classes

This evaluator harness must refuse candidates whose primary mutation target is:

- `AXIOMS.json`
- vows or permissions
- durable identity semantics
- hot-memory transport semantics
- vendor-native interop mythology

These are out of v0 scope even if the local patch seems small.

---

## Minimum Result Shape

The output of a v0 evaluation should eventually be renderable as:

- `candidate_id`
- `target_surface`
- `status`
- `success_metric_summary`
- `failure_watch_summary`
- `evidence_bundle_summary`
- `rollback_path_summary`
- `overclaim_to_avoid`
- `unresolved_items`

This keeps improvement evaluation machine-readable enough to compare later.

---

## First Good Use

The best first use of this harness is not a huge experiment system.

It is one bounded candidate in a safe family such as:

- workspace tier alignment
- escalation-hint quality
- cross-consumer packaging
- operator-retrieval cueing

That is enough to prove whether the harness is honest before anything larger is attempted.

---

## One-Sentence Summary

`ToneSoul's self-improvement evaluator harness exists so bounded improvement candidates are judged by explicit baseline, evidence, failure watch, and rollback discipline rather than by narrative confidence.`
