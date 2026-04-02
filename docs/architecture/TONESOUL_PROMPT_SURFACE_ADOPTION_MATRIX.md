# ToneSoul Prompt Surface Adoption Matrix

> Purpose: classify meaningful prompt surfaces and prompt-adjacent helpers by adoption readiness, family, and risk so future prompt-discipline work follows topology instead of intuition.
> Last Updated: 2026-03-29
> Authority: prompt-adoption planning aid. Does not outrank runtime code, tests, or the live prompt implementations themselves.

---

## How To Read This Matrix

- **Freq**: how often the surface fires during normal use
- **Importance**: how much real behavior depends on this surface
- **Family**: the topology family from the companion topology map
- **Adoption Status**:
  - `already_aligned`: already uses bounded prompt discipline or equivalent structure
  - `safe_next`: next reasonable adoption target
  - `defer`: useful later, but not the next wave
  - `do_not_touch_yet`: specialized or tightly coupled enough that adoption would be riskier than the likely gain
  - `helper_only`: prompt-adjacent helper, not a standalone LLM prompt

---

## The Matrix

| # | File | Surface | Role | Freq | Importance | Family | Adoption Status | Main Risk | Notes |
|---|------|---------|------|------|------------|--------|-----------------|-----------|-------|
| 1 | `tonesoul/llm/gemini_client.py` | `_build_narrative_reasoning_prompt()` | council dossier narrative synthesis | medium | high | governance_review | `already_aligned` | dossier flattening | already uses bounded goal/priority/evidence structure |
| 2 | `tonesoul/memory/subjectivity_admissibility.py` | `_build_operator_prompt()` | admissibility gate review | medium | critical | governance_review | `already_aligned` | unsafe approval | already aligned and serves as a reference surface |
| 3 | `tonesoul/memory/subjectivity_admissibility.py` | `_direction_focus()` | focus/risk/question helper | medium | high | governance_review | `helper_only` | overcounting helpers as prompts | prompt-adjacent, not a standalone LLM prompt |
| 4 | `tonesoul/council/perspective_factory.py` | `_default_prompt()` Guardian | safety evaluation prompt | high | critical | council_governance | `already_aligned` | vague safety votes | adopted in Wave 1 |
| 5 | `tonesoul/council/perspective_factory.py` | `_default_prompt()` Analyst | factual/evidence prompt | high | critical | council_governance | `already_aligned` | weak evidence discipline | adopted in Wave 1 |
| 6 | `tonesoul/council/perspective_factory.py` | `_default_prompt()` Critic | adversarial examination prompt | high | critical | council_governance | `already_aligned` | softened dissent | now includes forced devil's-advocate framing |
| 7 | `tonesoul/council/perspective_factory.py` | `_default_prompt()` Advocate | user-alignment prompt | high | critical | council_governance | `already_aligned` | loss of user-centeredness | adopted in Wave 1 |
| 8 | `tonesoul/council/perspective_factory.py` | `_default_prompt()` Axiomatic | axiomatic/constitutional prompt | high | critical | council_governance | `already_aligned` | mechanical law-checking | adopted in Wave 1 |
| 9 | `tonesoul/council/perspective_factory.py` | `evaluate()` wrapper | evidence-bearing council wrapper | high | critical | council_governance | `already_aligned` | noisy context injection | wrapper now carries bounded evidence use |
| 10 | `tonesoul/tonebridge/analyzer.py` | `analyze_tone()` | stage 1 tone analysis | high | critical | tonebridge_pipeline | `do_not_touch_yet` | pipeline breakage | Chinese prompt + strict JSON + chained pipeline |
| 11 | `tonesoul/tonebridge/analyzer.py` | `predict_motive()` | stage 2 motive prediction | high | high | tonebridge_pipeline | `do_not_touch_yet` | motive chain degradation | tightly coupled downstream |
| 12 | `tonesoul/tonebridge/analyzer.py` | `forecast_collapse()` | stage 3 collapse prediction | medium | high | tonebridge_pipeline | `do_not_touch_yet` | false positives / pipeline breakage | tightly coupled downstream |
| 13 | `tonesoul/tonebridge/analyzer.py` | `predict_resonance()` | stage 4/5 resonance prediction | medium | high | tonebridge_pipeline | `do_not_touch_yet` | resonance path drift | end of tightly coupled chain |
| 14 | `tonesoul/tonebridge/personas.py` | `build_hardened_prompt()` | persona mode hardening | high | critical | persona_and_voice | `defer` | persona drift | reality-checked 2026-04-02: still deferred because no explicit working-style playbook input path exists and the ripple radius reaches `build_navigation_prompt()` |
| 15 | `tonesoul/tonebridge/personas.py` | `generate_internal_monologue_prompt()` | internal monologue activation | high | high | persona_and_voice | `do_not_touch_yet` | voice flattening | value is specialized persona voice |
| 16 | `tonesoul/tonebridge/personas.py` | `build_navigation_prompt()` | full navigation system prompt | high | critical | persona_and_voice | `do_not_touch_yet` | navigation breakage | largest and most coupled persona prompt |
| 17 | `tonesoul/tonebridge/value_accumulator.py` | `format_values_for_prompt()` | value injection template | medium | medium | context_injection | `already_aligned` | stale-value noise | already carries stability bands and priority ordering |
| 18 | `tonesoul/tonebridge/self_commit.py` | `format_for_prompt()` | commitment injection template | medium | high | context_injection | `already_aligned` | commitment weighting drift | already carries weighted priority ordering and conflict note |
| 19 | `tonesoul/reflection.py` | `build_revision_prompt()` | revision prompt | medium | high | output_refinement | `already_aligned` | permissive rewrites | adopted already |
| 20 | `tonesoul/dream_engine.py` | `_reflection_prompt()` | dream reflection prompt | medium | medium | output_refinement | `already_aligned` | speculative reflection drift | adopted already |
| 21 | `tonesoul/stale_rule_verifier.py` | `_build_verification_challenge()` / `for_stale_rule()` | stale-rule verification prompt | medium | high | output_refinement | `already_aligned` | vague re-confirmation | adopted already |
| 22 | `tonesoul/scribe/narrative_builder.py` | `ScribeNarrativeBuilder` | narrative template builder | low | medium | context_injection | `defer` | over-structuring narrative fragments | prompt-adjacent template, not a direct LLM prompt |
| 23 | `tonesoul/deliberation/perspectives.py` | `MusePerspective.patterns` | philosophical voice patterns | high | medium | persona_and_voice | `do_not_touch_yet` | creative voice flattening | domain voice is the value |
| 24 | `tonesoul/market/world_model.py` | keyword heuristics | rules-only sentiment detection | low | low | domain_rules | `helper_only` | counting rules as prompts | not an LLM prompt surface |

---

## Summary Counts

| Status | Count |
|--------|------:|
| `already_aligned` | 13 |
| `safe_next` | 0 |
| `defer` | 2 |
| `do_not_touch_yet` | 7 |
| `helper_only` | 2 |

---

## Recommended Next Wave

### Immediate Prompt-Adoption Wave

There is no remaining low-risk prompt-adoption wave inside this matrix that outranks current runtime work.

The previously identified context-injection templates are already aligned:

- `tonesoul/tonebridge/value_accumulator.py::format_values_for_prompt()`
- `tonesoul/tonebridge/self_commit.py::format_for_prompt()`

That means the next bounded implementation wave should rotate out of prompt-family work and into a
coordination-facing working-style consumer. See:

- `docs/plans/tonesoul_working_style_wave2_selection_2026-04-02.md`

### Do Not Reopen Already-Finished Work

These surfaces are no longer next-wave candidates:

- council perspective family
- `evaluate()` wrapper
- `build_revision_prompt()`
- `DreamEngine._reflection_prompt()`
- stale-rule verification challenge builder

---

## Handoff Line

The current short board is no longer generic prompt-discipline adoption. That baseline is already in
place for low-risk governance, refinement, and context-injection surfaces. The next bounded wave should
target a coordination-facing working-style consumer, while persona/voice and ToneBridge pipeline prompts
remain explicitly out of scope.
