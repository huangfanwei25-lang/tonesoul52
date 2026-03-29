# ToneSoul Prompt Surface Topology Map

> Purpose: group prompt surfaces into families so adoption can happen in bounded waves instead of one-off patches.
> Last Updated: 2026-03-29
> Authority: prompt-adoption topology aid. Does not outrank runtime code, tests, or live prompt behavior.

---

## Family 1: Council Governance

**Representative surfaces**
- `tonesoul/council/perspective_factory.py::_default_prompt()` for all five perspectives
- `tonesoul/council/perspective_factory.py::evaluate()`

**Why they belong together**
- same deliberation family
- same output object family
- same governance stakes
- same failure mode: bad votes and weak evidence handling

**Current posture**
- already adopted
- keep as baseline reference family

---

## Family 2: Governance Review

**Representative surfaces**
- `tonesoul/memory/subjectivity_admissibility.py::_build_operator_prompt()`
- `tonesoul/llm/gemini_client.py::_build_narrative_reasoning_prompt()`
- prompt-adjacent helper: `tonesoul/memory/subjectivity_admissibility.py::_direction_focus()`

**Why they belong together**
- they shape admissibility review or dossier-facing governance review
- they already use bounded goal / priority / evidence framing

**Current posture**
- already aligned
- use as reference implementations

---

## Family 3: Context Injection

**Representative surfaces**
- `tonesoul/tonebridge/value_accumulator.py::format_values_for_prompt()`
- `tonesoul/tonebridge/self_commit.py::format_for_prompt()`
- prompt-adjacent builder: `tonesoul/scribe/narrative_builder.py::ScribeNarrativeBuilder`

**Why they belong together**
- they inject prior state into later prompts
- they benefit from stability, freshness, and priority ordering
- they are not as tightly coupled as ToneBridge analysis

**Current posture**
- next adoption family
- highest-value short board after the council wave

---

## Family 4: Output Refinement

**Representative surfaces**
- `tonesoul/reflection.py::build_revision_prompt()`
- `tonesoul/dream_engine.py::_reflection_prompt()`
- `tonesoul/stale_rule_verifier.py::_build_verification_challenge()`

**Why they belong together**
- all are post-generation or post-detection refinement/evaluation prompts
- all benefit from bounded goal / recovery / evidence handling

**Current posture**
- already adopted
- use as auxiliary reference family

---

## Family 5: ToneBridge Analysis Pipeline

**Representative surfaces**
- `tonesoul/tonebridge/analyzer.py::analyze_tone()`
- `tonesoul/tonebridge/analyzer.py::predict_motive()`
- `tonesoul/tonebridge/analyzer.py::forecast_collapse()`
- `tonesoul/tonebridge/analyzer.py::predict_resonance()`

**Why they belong together**
- strict chained pipeline
- schema coupling across stages
- Chinese-domain analysis prompts

**Current posture**
- do not touch yet

**Why**
- one stage cannot be safely changed without validating the full chain

---

## Family 6: Persona And Voice

**Representative surfaces**
- `tonesoul/tonebridge/personas.py::build_hardened_prompt()`
- `tonesoul/tonebridge/personas.py::generate_internal_monologue_prompt()`
- `tonesoul/tonebridge/personas.py::build_navigation_prompt()`
- `tonesoul/deliberation/perspectives.py::MusePerspective.patterns`

**Why they belong together**
- their value is expressive / persona-specific
- they depend on persona state and mode locking
- they are not governance-first surfaces

**Current posture**
- mostly do not touch
- only `build_hardened_prompt()` is a later defer candidate

---

## Family 7: Domain Rules And Non-Prompt Helpers

**Representative surfaces**
- `tonesoul/market/world_model.py` keyword heuristics
- other rules-only detectors that may look prompt-like in topology scans

**Why they belong together**
- not LLM prompts
- should not consume adoption effort meant for actual prompt surfaces

**Current posture**
- helper-only

---

## Family Summary

| Family | Posture | Short Note |
|--------|---------|------------|
| Council Governance | complete baseline | already adopted |
| Governance Review | complete baseline | already aligned reference family |
| Context Injection | next wave | current short board |
| Output Refinement | complete baseline | already adopted |
| ToneBridge Analysis Pipeline | do not touch yet | tightly coupled |
| Persona And Voice | mostly do not touch | voice is the value |
| Domain Rules And Helpers | helper-only | not prompt-adoption targets |

---

## Adoption Direction

Use this order:

1. governance families
2. context-injection families
3. only then consider specialized persona/domain families

That means the next real implementation wave should not reopen council or reflection work. It should move into context injection.

---

## Handoff Line

The repo no longer needs another council prompt wave. Topology now points to one clear next step: context injection templates. Everything else in the prompt layer is either already aligned, helper-only, or still too specialized to justify adoption.
