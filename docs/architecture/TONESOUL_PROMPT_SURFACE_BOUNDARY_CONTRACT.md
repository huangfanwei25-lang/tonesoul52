# ToneSoul Prompt Surface Boundary Contract

> Purpose: define when a prompt surface deserves starter-card adoption, when it only needs wording cleanup, and when it must remain specialized.
> Last Updated: 2026-03-29
> Authority: prompt-adoption boundary aid. Does not outrank runtime code, tests, or live prompt behavior.

---

## Compressed Thesis

Prompt discipline is for surfaces whose failure mode involves lost evidence, false confidence, weak recovery behavior, or governance bypass.

It is not for:
- domain pipelines whose value is schema-stable analysis
- persona/voice surfaces whose value is distinctive expression
- rules-only heuristics that are not prompts

---

## Adoption Levels

### Level 0: No Change

Use when the surface is:
- already aligned
- not actually an LLM prompt
- domain-specific enough that adoption would only add noise

### Level 1: Wording Cleanup

Use when the structure is fine but wording is misleading, contradictory, or ambiguous.

Do not change:
- output schema
- variable interpolation shape
- language choice

### Level 2: Starter-Card Adoption

Use when the surface benefits from explicit:
- goal function
- P0 / P1 / P2
- evidence discipline
- recovery instructions
- bounded output expectation

Do not change:
- functional purpose
- downstream schema assumptions
- load-bearing domain vocabulary

### Level 3: Structural Rewrite

Use only when one prompt mixes incompatible concerns or its schema no longer fits any receiver.

This should be rare.

---

## Decision Criteria

### 1. Governance Or Evidence Responsibility

If a prompt contributes to approval, blocking, escalation, dossier carry, or evidence a later agent will rely on, it is a strong Level 2 candidate.

### 2. Tightly Coupled Pipeline Risk

If the prompt sits in a strict multi-stage pipeline where one output feeds the next, default to Level 0 or Level 1.

### 3. Specialized Voice Value

If the prompt's value is its voice, mood, or persona-specific texture, leave it alone unless there is a documented quality failure.

### 4. Prompt-Adjacent Helper Status

If the surface is really a helper, template builder, or rules-only heuristic, do not treat it as a full prompt surface.

### 5. Frequency And Leverage

High-frequency governance prompts deserve earlier adoption than low-frequency or local-only prompts.

### 6. Already-Finished Work

Do not keep recommending surfaces that are already aligned in runtime. Reclassify them and move to the next short board.

---

## Boundary Rules

### Rule 1: Adopt Families, Not Fragments

When a family shares one structure, adopt it together. Partial adoption inside one family creates worse inconsistency than waiting.

### Rule 2: Preserve Adversarial And Protective Stance

Critic must remain adversarial.
Guardian must remain conservative.
Axiomatic must remain constitutional rather than merely procedural.

Prompt discipline must not neutralize these roles.

### Rule 3: Domain Prompts Stay Domain

Do not force governance-shaped prompt discipline onto:
- ToneBridge multi-stage analysis prompts
- persona navigation prompts
- Muse voice patterns

### Rule 4: Prompt-Adjacent Helpers Must Be Named Honestly

Helpers such as `_direction_focus()` or rules-only keyword detectors may appear in topology maps, but they should be labeled as helpers, not counted as full LLM prompts.

### Rule 5: Follow Water-Bucket Prioritization

Once a family reaches baseline:
- discoverable
- bounded
- tested
- at least one live adoption wave complete

move to the next short board instead of refining the same family indefinitely.

---

## Current Safe Boundary

### Already At Baseline

- council governance prompt family
- governance review prompt family
- reflection / dream / stale-rule output-refinement prompts

### Safest Next Adoption

- context injection templates:
  - `format_values_for_prompt()`
  - `format_for_prompt()`

### Explicitly Not Next

- ToneBridge analysis pipeline
- persona navigation / internal monologue
- Muse voice patterns

---

## Handoff Line

The prompt-discipline question is no longer "should we adopt council prompts?" That wave is done. The live boundary now is simpler: adopt context-injection templates next, and keep persona/domain prompts outside the wave unless there is a documented failure.
