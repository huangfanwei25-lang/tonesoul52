# ToneSoul Observability And Axiom Adoption Review (2026-03-28)

> Purpose: review extracted external-theory proposals and translate the adoptable parts into ToneSoul-native architecture decisions
> Last Updated: 2026-03-28
> Status: reviewed adoption note; not a runtime change log

## Decision Summary

ToneSoul should adopt two ideas now, but only after translating them into existing repository language:

1. `blackbox boundary` -> **observable-shell opacity contract**
2. `falsifiability conditions` -> **axiom falsification map**

The other proposals should remain deferred:

- `impact tracking`
- `path semantic marking`
- `tension-delayed commit`

## Adoption Table

| Source Proposal | ToneSoul-Aligned Name | Decision | Why |
|----------------|-----------------------|----------|-----|
| blackbox boundary marking | `observable-shell opacity` | adopt now | fits A/B/C firewall, externalized cognition, and epistemic honesty with low implementation pressure |
| falsifiability conditions | `axiom falsification map` | adopt now | keeps axioms challengeable without mutating `AXIOMS.json` prematurely |
| path semantic marking | `decision-path lane marking` | defer | likely to become after-the-fact narration unless generation timing is tightly bounded |
| impact tracking | `downstream consequence linkage` | defer | high attribution ambiguity; current git + trace + compaction posture is still sufficient |
| tension delayed commit | `commit readiness under unresolved tension` | defer to later feature track | valuable idea, but too easy to turn into coordination paralysis if introduced early |

## Why The Two Adopted Ideas Fit ToneSoul

### 1. Observable-Shell Opacity

ToneSoul already speaks the language of:

- mechanism,
- observability,
- interpretation,
- epistemic honesty,
- externalized cognition.

So it should not import a foreign "blackbox" term as a new constitutional object.

The ToneSoul-native question is:

`which parts of a decision path are truly observable at the shell, and which remain opaque?`

### 2. Axiom Falsification

ToneSoul already has a constitutional center in `AXIOMS.json`.

What it lacked was a bounded way to say:

- what supports an axiom,
- what would weaken it,
- which axioms are runtime-backed,
- which remain theory-backed.

That gap is methodological, not philosophical.

## Why The Other Three Stay Deferred

### Path Semantic Marking

Useful in theory, but dangerous if agents start backfilling:

- `PRIMARY`
- `CONSTRAINT`
- `REJECTED`

after the decision already happened.

That would create narrative polish, not stronger truth.

### Impact Tracking

ToneSoul absolutely cares about downstream effect, including effect on the user.

But a new consequence-linking surface would currently create too much false causality risk:

- weak attribution,
- backward blame inflation,
- noisy maintenance.

### Tension-Delayed Commit

This is the strongest deferred candidate.

It aligns with ToneSoul's "preserve tension" instinct, but it should not enter runtime until the system can prove it will:

- preserve unresolved conflict,
- without creating endless delay loops,
- and without teaching agents to avoid finishing work.

## Safe Next Step

The next safe step is documentation-level adoption only:

- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`

No runtime gate, no packet field, no trace schema change is required yet.

## Result

ToneSoul absorbs the good part of the external theory:

- more honesty about opacity,
- more honesty about what could disprove an axiom,

without absorbing the parts most likely to create ceremony, false causality, or commit paralysis.
