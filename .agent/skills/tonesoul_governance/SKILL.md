---
name: tonesoul_governance
description: AI self-governance skill with tension computation, resonance detection, and memory crystallization
l1_routing:
  name: "ToneSoul Governance"
  triggers:
    - "governance"
    - "semantic tension"
    - "resonance detection"
    - "memory crystallization"
  intent: "Apply governance and semantic tension evaluation to distinguish resonance detection from compliance and preserve memory crystallization rules."
l2_signature:
  execution_profile:
    - "engineering"
  trust_tier: "reviewed"
  json_schema:
    type: "object"
    properties:
      task:
        type: "string"
      target_module:
        type: "string"
      constraints:
        type: "array"
        items:
          type: "string"
    required:
      - "task"
---

# ToneSoul Governance Skill

## What this skill does

- Computes semantic tension for every AI response.
- Blocks or rewrites outputs that drift outside governance boundaries.
- Detects genuine resonance vs sycophantic flow.
- Crystallizes repeated important patterns into permanent decision rules.

## When to use

- You need accountable AI responses instead of best-effort persuasion.
- You need audit traces for why an answer was accepted or blocked.
- You need cross-session behavior consistency.
- You need to distinguish understanding from compliance.

## API Surface

### TensionEngine

```python
from tonesoul.tension_engine import TensionEngine

engine = TensionEngine(work_category="research")
result = engine.compute(text_tension=0.7, confidence=0.8)
print(result.total, result.zone, result.signals.semantic_delta)
```

### ResonanceClassifier

```python
from tonesoul.resonance import classify_resonance

resonance = classify_resonance(tension_before=0.21, tension_after=0.05)
print(resonance.resonance_type)  # flow / resonance / deep_resonance / divergence
```

### MemoryCrystallizer

```python
from tonesoul.memory.crystallizer import MemoryCrystallizer

crystallizer = MemoryCrystallizer()
crystals = crystallizer.crystallize(patterns=[])
print(crystals)
```

## Configuration

| Env Var | Default | Description |
|---|---|---|
| `TONESOUL_MEMORY_EMBEDDER` | `auto` | `hash` / `sentence-transformer` / `auto` |
| `LLM_BACKEND` | `auto` | `gemini` / `ollama` / `auto` |
| `TS_VISUAL_CHAIN_ENABLED` | `true` | Enable or disable visual chain features |

## Files

- `tonesoul/tension_engine.py` - Core tension computation
- `tonesoul/resonance.py` - Resonance classifier
- `tonesoul/unified_pipeline.py` - End-to-end pipeline orchestration
- `tonesoul/memory/crystallizer.py` - Memory crystallization logic
- `memory/consolidator.py` - Episode consolidation
- `tonesoul/council/` - Multi-perspective deliberation system
- `tonesoul/gates/compute.py` - Compute gate (approve/block/rewrite)
