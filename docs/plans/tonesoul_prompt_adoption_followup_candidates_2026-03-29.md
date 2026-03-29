# ToneSoul Prompt Adoption Follow-Up Candidates (2026-03-29)

> Purpose: bounded next implementation candidates for prompt-surface adoption after the already-completed council and refinement waves.
> Last Updated: 2026-03-29

---

## Candidate 1: Add Stability Bands To Value Injection

**Target**
- `tonesoul/tonebridge/value_accumulator.py::format_values_for_prompt()`

**Why next**
- high leverage
- not tightly coupled like ToneBridge analysis
- aligns with existing working-style / continuity discipline

**Goal**
- distinguish durable versus decaying versus ephemeral injected values
- preserve current visual-strength output

---

## Candidate 2: Add Priority Ordering To Self-Commit Injection

**Target**
- `tonesoul/tonebridge/self_commit.py::format_for_prompt()`

**Why next**
- commitments already carry weight semantics
- prompt-adjacent ordering discipline is a natural next adoption step

**Goal**
- make the most binding commitments survive compression first
- keep irreversibility weight legible

---

## Candidate 3: Review Scribe Narrative Builder As Prompt-Adjacent Context Supplier

**Target**
- `tonesoul/scribe/narrative_builder.py::ScribeNarrativeBuilder`

**Why later**
- lower frequency
- not a direct LLM prompt
- still useful as a context-supplier discipline surface

**Goal**
- decide whether it only needs helper labeling and ordering hints, or no adoption at all

---

## Candidate 4: Revisit Persona Hardening Only After Context Injection Wave

**Target**
- `tonesoul/tonebridge/personas.py::build_hardened_prompt()`

**Why deferred**
- higher risk than context injection
- persona drift cost is real

**Goal**
- check whether a bounded stability/priority framing helps without flattening persona voice

---

## Explicitly Closed Candidates

Do not reopen these as follow-up work:

- council perspective family
- `perspective_factory.py::evaluate()`
- `tonesoul/reflection.py::build_revision_prompt()`
- `tonesoul/dream_engine.py::_reflection_prompt()`
- `tonesoul/stale_rule_verifier.py::_build_verification_challenge()`

Those are already aligned enough to stop being the current short board.

---

## Recommended Order

1. value injection
2. self-commit injection
3. optional scribe review
4. only then consider persona hardening

That keeps adoption on the shortest remaining board instead of reopening finished waves.
