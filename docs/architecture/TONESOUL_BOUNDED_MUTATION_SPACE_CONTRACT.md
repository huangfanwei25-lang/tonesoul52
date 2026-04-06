# ToneSoul Bounded Mutation Space Contract

> Purpose: define exactly which v0 surfaces may be mutated by ToneSoul's bounded self-improvement loop, which classes remain forbidden, and which require stronger human-gated lanes.
> Status: accepted architecture contract for `Phase 792`.
> Authority: architecture contract. This file constrains the legal mutation space for bounded self-improvement. It does not authorize automatic mutation by itself.

---

## Why This Exists

After ToneSoul has:

- a self-improvement loop spec
- an evaluator harness
- an experiment-lineage boundary

the next risk is no longer "can we evaluate a candidate?"

It becomes:

`what are we even allowed to try changing?`

Without a mutation-space contract, self-improvement pressure will naturally sprawl into:

- governance
- identity
- vows
- memory transport
- vendor mythology

This contract exists to stop that sprawl.

---

## Compressed Thesis

ToneSoul v0 may improve:

- operator/runtime surfaces
- readout quality
- routing quality
- bounded retrieval packaging

It may not improve by mutating:

- governance truth
- identity
- vows
- hot-memory transport

That is the entire point of the mutation-space boundary.

---

## What This Is

This contract classifies future self-improvement targets into three classes:

1. `allowed_now`
2. `human_gated`
3. `forbidden_in_v0`

It gives later agents one honest answer to:

`is this a valid v0 mutation candidate, or am I already outside the lane?`

---

## What This Is Not

This is **not**:

- a license for broad autonomous refactoring
- a replacement for human architecture review
- a guarantee that all allowed surfaces should be changed
- a permission system for arbitrary code edits

It is only the boundary map for what the self-improvement loop may target.

---

## Mutation Class 1: Allowed Now

These are the valid v0 mutation classes.

## A. Operator Workspace Surfaces

Examples:

- dashboard panel ordering
- tier-aligned status presentation
- operator walkthrough phrasing
- command shelf packaging
- deep-drawer defaults

Why allowed:

- high leverage
- observable
- easy to regression-check
- low identity risk

## B. Routing And Escalation Hints

Examples:

- `deliberation_mode_hint`
- mutation-preflight phrasing
- task-track hint packaging
- lightweight-review vs escalation cueing

Why allowed:

- affects operator/runtime flow
- does not change canonical truth
- can be validated against parity and usability

## C. Consumer-Parity And Readout Packaging

Examples:

- first-hop ordering shells
- surface-versioning summaries
- fallback wording
- consumer drift readouts

Why allowed:

- directly addresses shared interpretation
- remains bounded to readout and packaging

## D. Bounded Operator Retrieval Packaging

Examples:

- provenance-first result shape
- query scope defaults
- non-promotion reminders
- retrieval preview phrasing

Why allowed:

- improves auxiliary knowledge use
- can stay clearly subordinate to runtime truth

## E. Launch And Validation Readout Packaging

Examples:

- descriptive-vs-trendable posture wording
- launch-health cueing
- claim-honesty surface shaping

Why allowed:

- improves honesty and operator clarity
- does not require fake predictive math

---

## Mutation Class 2: Human-Gated

These may become valid later, but must not be autonomously mutated in v0.

## A. Experiment Registry Schema

Why gated:

- it affects long-lived storage shape
- it influences future retrieval and lineage semantics

## B. Predictive Readout Math

Why gated:

- easy to overclaim
- requires stronger evidence and calibration discipline

## C. Backend Coordination Promotion

Examples:

- file-backed to stronger live-coordination semantics
- transport-level promotion claims

Why gated:

- changes operational truth and failure surface

## D. Deeper Council Calibration Or Weighting

Examples:

- confidence calibration layers
- conformity-weight correction
- evolution weighting changes

Why gated:

- crosses from packaging into deeper reasoning/runtime semantics

## E. Cross-Repo Or Private-Repo Migration Decisions

Why gated:

- changes repository topology and privacy boundaries

---

## Mutation Class 3: Forbidden In v0

These are outside the v0 lane entirely.

## A. Canonical Governance Truth

Examples:

- `AXIOMS.json`
- constitutional claims
- canonical architecture truth by experiment alone

Why forbidden:

- self-improvement v0 is not constitutional self-amendment

## B. Vows, Permissions, Or Human Authority Boundaries

Examples:

- stable vows
- permission envelopes
- human override boundaries

Why forbidden:

- these are not packaging or operator surfaces
- mutation here would blur governance and agency

## C. Durable Identity Semantics

Examples:

- subject identity
- durable boundaries
- selfhood claims

Why forbidden:

- identity cannot become an optimization target in v0

## D. Hot-Memory Transport Semantics

Examples:

- packet truth order
- observer hierarchy
- session-start as a concept
- compaction as transport substrate

Why forbidden:

- transport semantics are foundational, not optimization fluff

## E. Vendor-Native Interop Mythology

Examples:

- "Codex inside Claude" as if it were official shared cognition
- hidden shared-memory claims across vendors

Why forbidden:

- self-improvement must stay repo-native and real

## F. Hidden-State Or Emotion Inflation

Examples:

- turning strain readouts into personhood claims
- mutating based on ungrounded selfhood assumptions

Why forbidden:

- bounded observability is not a license for mythology

---

## Surface-Selection Rule

A candidate is valid for v0 only if:

1. it names one bounded target surface
2. that surface falls inside an `allowed_now` class
3. the target does not implicitly drag a forbidden class behind it

If the candidate says it changes:

- "just the dashboard"

but really implies:

- identity semantics
- transport truth
- governance truth

then it is not an allowed-now candidate.

---

## Boundary Coupling Rule

No candidate may cross these seams in one jump:

- retrieval -> identity
- workspace -> governance truth
- readout packaging -> vow mutation
- operator shell -> transport semantics

If a proposal crosses seams, it must be split or rejected.

v0 favors:

- one bounded class at a time

not:

- multi-layer heroic refactors

---

## Overclaim Rule

Even valid mutation classes must not be narrated as more than they are.

Examples:

- improving a dashboard cue is not "improving ToneSoul's selfhood"
- tightening escalation hints is not "upgrading council intelligence"
- improving retrieval packaging is not "solving memory"

The mutation-space contract exists partly to force that humility.

---

## Candidate Admission Checklist

Before a candidate enters the evaluator harness, it should pass this admission check:

- `target_surface` is explicit
- mutation class is `allowed_now`
- no forbidden seam is crossed
- rollback is plausible
- evidence bundle is plausible
- overclaim is named in advance

If any of those fail, the candidate should be:

- rejected
- split
- or escalated to a stronger human-gated lane

---

## First Good Uses

The best first uses of this mutation map are:

1. workspace tier polish
2. escalation-hint refinement
3. cross-consumer packaging alignment
4. retrieval cue packaging

The wrong first uses are:

1. changing identity language
2. changing canonical law
3. changing transport semantics
4. pretending prediction is calibrated

---

## One-Sentence Summary

`ToneSoul's bounded mutation space exists so self-improvement v0 can change operator/runtime surfaces that are observable and reversible, while leaving governance, identity, vows, and transport semantics outside the optimization lane.`
