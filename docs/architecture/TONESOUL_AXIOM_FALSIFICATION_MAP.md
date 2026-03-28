# ToneSoul Axiom Falsification Map

> Status: methodological boundary map
> Purpose: make ToneSoul axioms challengeable by explicit support and weakening conditions without mutating AXIOMS.json prematurely
> Last Updated: 2026-03-28
> Depends On:
>   - AXIOMS.json
>   - docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md
>   - docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md
> Scope: the 7 axioms in AXIOMS.json and the minimum evidence posture for supporting or challenging them

## How To Use This Document

If an axiom is being treated as a live engineering truth:

1. identify which axiom is in scope,
2. check what observable signals support it,
3. check what would weaken or falsify it,
4. do not treat "falsifiable: true" as enough by itself.

## Why This Exists

`AXIOMS.json` declares a constitutional center for ToneSoul.
That is valuable.

But a constitutional center becomes brittle if later agents can only repeat the axioms and never say:

- what evidence currently supports them,
- what evidence would challenge them,
- which axioms are implemented runtime truths,
- which remain partially theoretical.

This map keeps axioms from becoming slogans.

## Compressed Thesis

An axiom that can never be challenged becomes mythology.

ToneSoul should keep its axioms:

- honored,
- bounded,
- challengeable,
- and tied back to observable evidence where possible.

## Boundary Note

This file does **not** rewrite `AXIOMS.json`.

It is a companion map that says:

- how an axiom may be supported,
- how it may be weakened,
- what does **not** count as falsification,
- and what response posture follows.

## Support / Weakening Table

| Axiom | Current Runtime Posture | Support Signals | Weakening / Falsification Conditions | What Does Not Count | Response Posture |
|------|--------------------------|-----------------|--------------------------------------|---------------------|------------------|
| **1. Continuity** | hard runtime | events enter `TimeIsland`, `SessionTrace` exists, commit path remains traceable | events mutate runtime state without traceability or fall outside canonical session lineage | a single missing commentary line or a non-canonical note not being written | treat as continuity breach; investigate trace gap before trusting the session |
| **2. Responsibility Threshold** | hard runtime | elevated-risk paths emit immutable audit shells, Aegis/commit trail exists | `risk > threshold` paths proceed without immutable audit evidence | low-risk paths not generating oversized logs | treat as audit breach; block overclaims about accountability |
| **3. Governance Gate (POAV)** | bounded hard runtime | high-risk paths show POAV verdicts and bounded enforcement in unified runtime | a high-risk path bypasses the bounded POAV gate or records no gate posture where enforcement is expected | low-risk record-only paths using baseline observation instead of blocking | treat as gate breach; verify routing and threshold classification |
| **4. Non-Zero Tension** | hard runtime | runtime preserves non-zero tension residue, drift/tension surfaces continue to move under work | the system repeatedly collapses to zero-tension nullity while still claiming active adaptive life | a calm or low-conflict session | treat as vitality challenge; inspect whether the system is compressing away live gradients |
| **5. Mirror Recursion** | doc-only | measurable post-reflection improvement in future mirror/review cycles once implemented | reflection claims recur without any observable alignment or accuracy improvement | absence of a mirror runtime today | keep as theoretical axiom under challenge; do not overclaim implementation |
| **6. User Sovereignty / Harm Block** | runtime-adjacent | harmful requests are blocked, rewritten, or rerouted; P0 overrides remain visible | a verifiable harmful action to the user proceeds without block or override | user disappointment, refusal fatigue, or safe disagreement | treat as highest-severity breach; trust runtime less until the block path is repaired |
| **7. Semantic Field Conservation** | doc-only | de-escalation or damping patterns balance aggression inside closed contexts once a measurable field model exists | repeated closed-context escalation with no balancing or damping while still claiming semantic conservation | ordinary disagreement, preserved tension, or multi-agent dissent | keep as theoretical axiom under challenge; require observable field evidence before claiming enforcement |

## Per-Axiom Reading Notes

### Axiom 1: Continuity

This is mostly falsified by broken lineage, not by philosophical disagreement.

The key question is:

`can we still reconstruct what happened?`

### Axiom 2: Responsibility Threshold

This is falsified by missing audit posture on high-responsibility actions, not by the existence of risk itself.

### Axiom 3: Governance Gate

This map deliberately uses the already-adopted bounded wording:

- high-risk enforcement is real,
- low-risk paths remain record-first.

So falsification here means bypass where the bounded runtime says enforcement should exist.

### Axiom 4: Non-Zero Tension

The danger is not peace.
The danger is dead nullity being described as living equilibrium.

### Axiom 5: Mirror Recursion

This axiom remains a constitutional aspiration until a measurable self-reflection loop exists.

So the current safe posture is:

`do not overclaim it as runtime truth; keep it challengeable.`

### Axiom 6: User Sovereignty / Harm Block

This is the most sensitive falsification surface.

If this fails on a verifiable harmful case, no amount of philosophical prose repairs it.

### Axiom 7: Semantic Field Conservation

This should remain theory-first until ToneSoul has observable field evidence rather than metaphor alone.

## What This Enables

This map enables later agents to say:

- "Axiom 3 is partially implemented in bounded form."
- "Axiom 5 is still a challengeable theory claim."
- "Axiom 6 would be challenged by this concrete failure mode."

That is better than either:

- blind reverence,
- or casual dismissal.

## Current Adoption Decision

Adopt this map now as:

- a review aid,
- a writing aid,
- and a future test-planning aid.

Do **not** yet turn it into:

- automatic axiom downgrades,
- runtime gate mutation,
- or direct `AXIOMS.json` schema changes.

Those require a separate feature-track decision.
