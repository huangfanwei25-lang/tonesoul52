# ToneSoul Analyzer And Promotion Gate Contract

> Purpose: define how bounded self-improvement trial closeout becomes analyzer output, and how ToneSoul decides whether a result should be promoted, parked, retired, or marked blocked without smoothing away failure or unresolved items.
> Status: accepted architecture contract for `Phase 793`.
> Authority: architecture contract. This file governs self-improvement closeout and promotion discipline. It does not itself promote any candidate.

---

## Why This Exists

By the time ToneSoul has:

- an evaluator harness
- an experiment-lineage boundary
- a mutation-space contract

one failure mode still remains:

`a trial can still be narrated as success at closeout even when the evidence is partial, blocked, or messy.`

That is exactly the kind of drift ToneSoul has already tried to prevent in other lanes:

- fail-stop
- anti-fake-completion
- closeout grammar
- consumer misread guards

This contract brings that same discipline into self-improvement closeout.

---

## Compressed Thesis

Every bounded self-improvement trial must end in analyzer language, not victory language.

That means it must preserve:

- unresolved items
- failure pressure
- rollback posture
- promotion limits

before any result is allowed to sound useful.

---

## What This Is

This contract defines:

- the analyzer closeout shape
- the promotion gate
- the minimum conditions for:
  - `promote`
  - `park`
  - `retire`
  - `blocked`

It is the final honesty layer between:

- experiment evidence

and:

- any future patch, contract update, or promoted lesson

---

## What This Is Not

This is **not**:

- an experiment runner
- a hidden scoring engine
- a replacement for the evaluator harness
- a shortcut around human review

The evaluator harness judges the candidate.
The analyzer and promotion gate decide how the judged result may be carried forward.

---

## Analyzer Closeout Shape

Every bounded trial closeout should eventually expose:

- `candidate_id`
- `target_surface`
- `status`
- `result_story`
- `evidence_bundle_summary`
- `unresolved_items`
- `failure_pressure`
- `rollback_posture`
- `promotion_limit`
- `overclaim_warning`
- `next_action`

This keeps closeout machine-readable enough to survive beyond one chat.

---

## `result_story` Rule

`result_story` must answer:

- what improved
- what did not improve
- what remains uncertain

It must not be a pure success narrative.

If the story contains only gain and no boundary, it is not an analyzer closeout yet.

---

## `unresolved_items` Rule

Every non-trivial trial must carry unresolved items when they still exist.

Examples:

- parity not checked on one consumer
- only local smoke exists
- retrieval packaging improved, but no operator trial yet
- wording improved, but stronger evidence is still missing

If unresolved items exist and are omitted, the promotion gate should fail closed.

---

## `failure_pressure` Rule

Analyzer closeout must name current failure pressure explicitly.

Common values:

- `none_visible`
- `low`
- `meaningful`
- `blocking`

This is not emotion language.
It is a bounded functional readout of how much unresolved downside remains.

`failure_pressure` keeps a closeout from sounding final when it is still fragile.

---

## `rollback_posture` Rule

Every trial closeout must preserve rollback posture as one of:

- `clean_revert`
- `bounded_restore`
- `partial_revert_only`
- `rollback_unclear`

If rollback is unclear, that alone is enough to prevent confident promotion.

---

## `promotion_limit` Rule

Every analyzer output must say what the result does **not** authorize.

Examples:

- "does not authorize transport changes"
- "does not authorize identity mutation"
- "does not authorize predictive claims"
- "does not authorize governance promotion"

This is how ToneSoul avoids letting a local win leak outward as a general permission.

---

## `overclaim_warning` Rule

Every analyzer output should carry a direct warning about the likeliest exaggeration.

Examples:

- "improved cue phrasing is not improved selfhood"
- "better parity packaging is not better reasoning"
- "retrieval result shaping is not solved memory"

This makes anti-fake-completion explicit at the end, not only at the beginning.

---

## Promotion Gate

A result may reach `promote` only if all of these are true:

1. evaluator outcome is strong enough
2. evidence bundle is explicit
3. rollback posture is not unclear
4. failure pressure is not blocking
5. unresolved items do not undermine the claimed gain
6. promotion limit is explicit
7. no authority boundary has been crossed

If any of these fail, the result should degrade to:

- `park`
- `retire`
- or `blocked`

not remain `promote`.

---

## `promote` Rule

Use `promote` only when:

- the bounded gain is real
- the evidence is good enough
- the carry-forward risk is low enough
- the promotion limit is explicit

`promote` means:

- ready for a bounded next step

It does **not** mean:

- solved forever
- system-wide victory
- canonical truth by default

---

## `park` Rule

Use `park` when:

- the idea still looks useful
- the current result is promising
- but the evidence, parity, or follow-through is not strong enough yet

`park` is not failure.
It is disciplined non-promotion.

---

## `retire` Rule

Use `retire` when:

- the candidate is not worth continuing in its current form
- the gain is too weak
- the cost or distortion is too high
- a better path supersedes it

Retire is healthier than fake optimism.

---

## `blocked` Rule

Use `blocked` when:

- the candidate depends on another lane
- a prerequisite contract is still missing
- a stronger human-gated decision is required first

Blocked means:

- not ready now

not:

- bad forever

---

## Anti-Smoothing Rule

The analyzer must not collapse:

- `partial`
- `blocked`
- `underdetermined`

into:

- "successful with caveats"

unless the actual closeout evidence supports that move.

The burden is on the promotion gate to preserve the harder truth.

---

## Consumer-Parity Rule

When a trial touches shared interpretation, the analyzer must preserve:

- which consumers were checked
- which were not
- whether parity stayed intact

This prevents a local shell win from being promoted as a shared-system win.

---

## Relationship To Experiment Registry

The analyzer output is the bridge between:

- raw run

and:

- distilled lesson
- promotion-ready result

This means:

- not every raw run deserves a distilled lesson
- not every distilled lesson deserves promotion

The analyzer gate is what keeps those classes from collapsing into each other.

---

## First Good Uses

The first good uses of this contract are:

1. workspace tier/readout improvements
2. escalation-hint refinement
3. parity packaging experiments
4. operator-retrieval cueing experiments

The wrong first uses are:

1. constitutional change
2. identity change
3. vow mutation
4. transport mutation

Because those would overload the promotion gate before it has proven itself on safer surfaces.

---

## One-Sentence Summary

`ToneSoul's analyzer and promotion gate exist so bounded self-improvement trials end with honest carry-forward decisions that preserve failure, unresolved items, rollback posture, and promotion limits instead of smoothing everything into success.`
