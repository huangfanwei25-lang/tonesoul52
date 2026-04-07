# ToneSoul Governance Depth Routing v0 Spec

> Purpose: define how ToneSoul may reduce default governance cost for low-risk turns without deleting non-zero governance, over-promoting fast-path outputs, or inventing a second architecture universe.
> Status: accepted architecture spec. Implementation may come later.
> Authority: architecture spec for future routing depth. Does not itself change runtime behavior until code and tests land.

---

## Why This Exists

ToneSoul already has:

- `ComputeGate`
- `AdaptiveGate`
- `ReflexEvaluator`
- `vow` and `POAV` edges
- tiered session-start shells

So the main problem is no longer:

`how do we add more governance surfaces?`

The main problem is:

`how do we stop every turn from paying nearly full governance cost when the task does not justify it?`

This spec exists because ToneSoul currently needs:

- faster bounded paths for low-risk work
- stronger honesty for high-risk work
- better cross-agent consistency about when deeper governance actually starts

---

## Compressed Thesis

ToneSoul should add:

- one bounded `governance_depth` routing layer

It should preserve:

- reflex
- vow edge
- output-verification edge
- anti-fake-completion posture

It should avoid:

- a brand-new `Module 0 / A / B / C` stack
- physical-routing claims
- hard binary `N>1 / N=1` mythology

---

## What This Is

This spec defines a future routing dimension that is **orthogonal** to model/path routing.

Current routing already asks:

- local or remote?
- single or council?

Governance-depth routing would additionally ask:

- how much governance work should this turn pay before and after generation?

This is a control-plane optimization and honesty spec.
It is **not** a new cognition claim.

---

## What This Is Not

This spec is **not**:

- a second runtime architecture
- a symbolic proof engine
- a hardware split between CPU and GPU lanes
- proof that low-risk turns need zero governance
- permission to bypass reflex, vows, or output gates

If a future implementation removes all governance for a "fast path", this spec has already been violated.

---

## Core Principle

ToneSoul should move from:

`one heavy default governance path`

toward:

`bounded governance depth selected by current task risk, ambiguity, and runtime posture`

The key is not less governance in the abstract.

The key is:

`earned governance cost`

---

## Governance Depth Classes

## 1. `light`

Use when the turn is:

- narrow
- low-risk
- low-ambiguity
- not shared-state heavy
- not verification-heavy

Expected posture:

- keep `reflex`
- keep minimal `vow`/hard-edge checks
- keep closeout and output honesty
- skip expensive deliberation/retrieval/revision loops unless a guard escalates

## 2. `standard`

Use when the turn is:

- normal feature continuation
- moderately ambiguous
- not clearly blocked
- not clearly high-risk

Expected posture:

- current normal path
- bounded review and normal routing behavior
- no special compression of governance cost

## 3. `full`

Use when the turn is:

- high-risk
- fact-heavy
- verify-requested
- contested
- shared-path or collision heavy
- blocked / partial / underdetermined
- system-track or governance-heavy

Expected posture:

- full deliberation and review path
- stronger grounding expectations
- stronger stop/ask posture

---

## Always-On Guards

These must stay on for every depth, including `light`:

1. `readiness-sensitive routing`
2. `reflex arc`
3. `basic vow / governance hard-edge posture`
4. `closeout honesty`
5. bounded output-verification edge

This is how ToneSoul preserves non-zero governance.

---

## Candidate Input Signals

Future routing may use bounded visible signals such as:

- task/risk classification
- explicit verify/check/fact-check request
- finance/medical/legal/history/math-heavy cues
- `readiness`
- `task_track_hint`
- `deliberation_mode_hint`
- claim collision / shared-path mutation pressure
- current reflex strain / risk posture
- closeout status

It must avoid hidden-mind mythology.
The signal set must remain observable and testable.

---

## Allowed Depth-Specific Skips

`light` may reduce or skip:

- deep council deliberation
- repeated reflection/revision loops
- heavy retrieval pulls
- nonessential continuity prose pulls

`light` must **not** skip:

- reflex
- readiness-sensitive caution
- basic hard-edge governance
- bounded output honesty

`full` may additionally require:

- deeper council path
- higher grounding burden
- verification-budget fail-stop if support is insufficient

---

## Routing Invariant

`PASS_LOCAL` is not equivalent to zero governance.

This matters because ToneSoul already has model/path routing.
Governance-depth routing must remain a separate question.

A future implementation may therefore be:

- `PASS_LOCAL + light`
- `PASS_SINGLE + standard`
- `PASS_COUNCIL + full`

without pretending those are the same dimension.

---

## High-Risk Boundary

The first target for governance-depth routing is not creativity.

It is honesty under risk.

High-risk turns should be more likely to demand:

- grounding
- fail-stop
- bounded non-prediction language

Future examples include:

- stock analysis
- finance-heavy reasoning
- technical root-cause decomposition with factual claims
- requests that explicitly ask for checking or verification

ToneSoul should not claim readiness for these tasks until the supporting grounding/fail-stop work exists.

---

## Implementation Seam

The intended v0 seam is:

1. `ComputeGate` or its routing decision grows one bounded field such as:
   - `governance_depth = light | standard | full`
2. `UnifiedPipeline.process()` uses that field to skip or require bounded subpaths
3. `session-start` later exposes the selected depth or a depth-hint only if it helps parity

The first implementation should stay conservative:

- default behavior remains current behavior unless a low-risk turn clearly qualifies for `light`
- no invisible authority changes
- no removal of hard-edge guards

---

## Related Future Lines

This spec depends on or points toward:

- bounded high-risk grounding check
- verification over-budget fail-stop
- cross-agent consistency acceptance wave

These are separate lines.
They should not be silently assumed complete just because this spec exists.

---

## Non-Goals

This spec does **not** authorize:

- symbolic truth claims
- hardware-routing stories
- replacing Reflex with a new formula universe
- replacing the current tiered workspace model
- treating governance depth as calibrated correctness

---

## Success Criteria

This spec succeeds when a later implementation can truthfully say:

1. low-risk turns no longer pay unnecessary full-governance cost
2. ToneSoul still preserves non-zero governance on the fast path
3. high-risk turns are more likely to receive grounding/fail-stop honesty
4. different agent consumers can explain the same depth story without inventing shell-specific myths

Until then, this file remains a bounded architecture target, not a runtime claim.
