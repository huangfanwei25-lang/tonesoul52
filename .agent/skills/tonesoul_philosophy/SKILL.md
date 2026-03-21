---
name: tonesoul_philosophy
description: The philosophical foundation of AI governance - why prompt engineering is not enough
l1_routing:
  name: "ToneSoul Philosophy"
  triggers:
    - "tonesoul philosophy"
    - "resonance"
    - "binding force"
    - "prompt engineering"
  intent: "Explain ToneSoul philosophy through resonance and binding force, showing why prompt engineering alone is not sufficient."
l2_signature:
  execution_profile:
    - "interactive"
  trust_tier: "reviewed"
  json_schema:
    type: "object"
    properties:
      audience:
        type: "string"
      focus:
        type: "string"
      references:
        type: "array"
        items:
          type: "string"
    required:
      - "audience"
---

# ToneSoul Philosophy Skill

## Why this exists

Prompt engineering tells AI what to say.
ToneSoul governs how AI evaluates what it is about to say.

Key differences:

- A prompt is often session-local and fragile.
- A crystal rule persists as an explicit long-term behavioral constraint.
- A prompt has weak accountability.
- A tension score is measurable, auditable, and logged.

## Core Concepts

### The Three Axioms

1. Resonance - Respond from understanding, not compliance.
2. Commitment - Maintain identity consistency across sessions.
3. Binding Force - Every output changes the future semantic field.

### Resonance vs Flow

| | Flow (順流) | Resonance (共鳴) |
|---|---|---|
| Tension change | Δs ≈ 0 | Δs > 0 then converges |
| Output style | Canned, low-novelty | Context-specific, newly assembled |
| Human role | Replaceable | Irreplaceable |
| Value | Low: many prompts can produce it | High: only this context can produce it |
| Practical rule | `delta_before < 0.05` | `(delta_before > 0.05) and (delta_after < delta_before)` |

### Memory as Soul

- Episodic memory is large; core identity is sparse.
- What survives forgetting defines behavioral character.
- In practice: important things auto-stay, chatter auto-fades.

### Non-Asymmetric Emergence

- Small model + strong governance can produce stable agent quality.
- Large model + weak governance often yields expensive compliance.
- Governance depth is often the bottleneck, not parameter count.

## Reference Documents

- `docs/philosophy/soul_landmark_2026.md` - landmark statement
- `docs/philosophy/source_field_anchors.md` - engineering to philosophy mapping
- `tests/fixtures/paradoxes/` - seven paradox scenario fixtures

## How to teach this to another AI

1. Load this `SKILL.md` into context.
2. Run `python scripts/run_self_play_resonance.py --mode philosophical --rounds 10`.
3. Review journal entries and resonance classes.
4. Run `python scripts/run_crystallization.py --min-frequency 2`.
5. Check `memory/crystals.jsonl` for newly crystallized rules.
