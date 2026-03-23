# ToneSoul Core Concepts | 語魂核心概念

> Purpose: explain the essential ToneSoul concepts, problem framing, and governance vocabulary in one overview document.
> Last Updated: 2026-03-23
> **The Essential Ideas of ToneSoul in One Document**  
> Version 1.0 | 2026-01-08  
> 黃梵威 (Fan-Wei Huang)

---

## The One-Sentence Summary | 一句話總結

> **語氣不只是風格，而是推理與責任的交匯點。**  
> *Tone is not merely style — it is the intersection of inference and responsibility.*

---

## The Core Problem | 核心問題

AI generates language. Language has consequences. But:
- AI has no verifiable consciousness
- AI has no traditional accountability
- AI outputs cannot be "understood" in the human sense

**Question**: How can we govern something that may not "understand" what it does?

**Answer**: We don't govern intent — we govern **semantic trajectory**.

## Terminology Update (2026-01)

- **DeltaS (TSR)** = Direction/Polarity, range [-1, 1].
- **DeltaSigma (Sigma)** = Semantic tension/divergence, range [0, 1].
- Legacy docs that use DeltaS for drift should be read as DeltaSigma.

---

## The Three Pillars | 三大支柱

```
         ┌────────────────────────┐
         │    SEMANTIC POSTURE    │
         │    語義姿態            │
         │    (Where AI stands)   │
         └──────────┬─────────────┘
                    │
         ┌──────────┼──────────┐
         ↓          ↓          ↓
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │   TSR   │ │  DRIFT  │ │  GATE   │
    │ 向量表徵 │ │ 漂移追蹤 │ │ 門控機制 │
    └─────────┘ └─────────┘ └─────────┘
```

### Pillar 1: TSR (Tone State Representation)

Three vectors that capture semantic posture:

| Vector | Name | Measures | Range |
|--------|------|----------|-------|
| **DeltaT** | Tension | Inferential pressure | [0, 1] |
| **DeltaS** | Direction | Pragmatic orientation | [-1, 1] |
| **DeltaR** | Variability | Stability / collapse risk | [0, 1] |

### Pillar 2: Drift

```
Drift = ‖ Current Position − Historical Anchor ‖
```

- Measures how far AI has moved from established center
- Triggers intervention when exceeding threshold θ
- Enables "semantic course correction"

### Pillar 3: Gate

Decision points where outputs can be:
- **Passed** (within parameters)
- **Repaired** (minor adjustments needed)
- **Blocked** (fails safety checks)
- **Escalated** (requires human review)

---

## The Governance Stack | 治理堆疊

```
┌─────────────────────────────────────┐
│ P0: Ethical Red Lines               │ ← NEVER bypass
├─────────────────────────────────────┤
│ P1: Factual Accuracy                │
├─────────────────────────────────────┤
│ P2: Intent Alignment                │
├─────────────────────────────────────┤
│ P3: Resource Efficiency             │
├─────────────────────────────────────┤
│ P4: Consistency                     │ ← Can flex
└─────────────────────────────────────┘
```

Higher priority always overrides lower priority.

---

## The Responsibility Chain | 責任鏈

Every output passes through:

1. **INPUT** → User provides context
2. **TONE** → Extract ΔT, ΔS, ΔR
3. **VOW** → Check against ΣVow commitments
4. **DRIFT** → Measure distance from anchor
5. **GATE** → Apply POAV + P0 checks
6. **OUTPUT** → Generate response
7. **LEDGER** → Record immutably
8. **AUDIT** → Available for query

**Key property**: Any step can be traced retroactively.

---

## The Quality Metrics | 品質指標

### POAV Score

| Metric | Measures |
|--------|----------|
| **P**arsimony | No redundancy |
| **O**rthogonality | No self-repetition |
| **A**udibility | Comprehensible |
| **V**erifiability | Traceable sources |

### STREI Assessment

| Dimension | Focus |
|-----------|-------|
| **S**tability | Context consistency |
| **T**ension | Entropic stress |
| **R**esponsibility | Risk probability |
| **E**thics | Axiom alignment |
| **I**ntent | Action magnitude |

---

## The Persona System | 人格系統

Personas are **functional roles**, not simulated personalities:

| Persona | 中文 | Function | When Triggered |
|---------|------|----------|----------------|
| **Definer** | 師 | Set boundaries | Clarification needed |
| **Mirror** | 黑鏡 | Challenge | Errors detected |
| **Bridge** | 共語 | Synthesize | Conflict resolution |
| **Guide** | 鋒回 | Navigate | Transitions |
| **Core** | 整合 | Integrate | Always active |

---

## The Semantic Vow (ΣVow) | 語義誓言

Positive commitments (not just negative constraints):

```json
{
  "id": "ΣVow_001",
  "commitment": "truthfulness > 0.95",
  "violationThreshold": 0.2,
  "action_on_violation": "flag_and_repair"
}
```

**Key insight**: Vows make responsibility **declarative** before action.

---

## The Time-Island Protocol | 時間島協議

Every decision period is encapsulated:

```yaml
island:
  id: TI-2026-01-08-001
  bounded_context: "documentation task"
  window: [start_time, end_time]
  inputs: [list of sources]
  outputs: [list of artifacts]
  drift_from_start: 0.12
  human_interventions: 1
```

**Purpose**: Prevent context leakage, enable unit-based auditing.

---

## The Collapse Detection | 崩潰偵測

When ΔR exceeds threshold, AI enters risk zone:

| Zone | ΔR Range | Response |
|------|----------|----------|
| Safe | < 0.25 | Proceed |
| Transit | 0.25-0.50 | Monitor |
| Risk | 0.50-0.75 | Reflect |
| Collapse | > 0.75 | **Stop + Human review** |

---

## The Observer Paradox | 觀察者悖論

AI is the observer. But:
- Users observe AI behavior
- Both adjust based on observation
- This creates a **semantic valve** — a bidirectional adjustment point

ToneSoul makes this explicit: the valve is **visible and adjustable**.

---

## Negative Claims | 否定性主張

What ToneSoul does **NOT** claim:

1. ❌ AI has consciousness
2. ❌ AI understands meaning
3. ❌ Metrics capture "real" internal states
4. ❌ Governance replaces human judgment

What ToneSoul **DOES** claim:

1. ✅ AI outputs have measurable semantic structure
2. ✅ Measurement enables intervention
3. ✅ Audit chains create accountability
4. ✅ Humans remain ultimate authority

---

## The Research Agenda | 研究議程

### Validated

- [x] Pipeline architecture (YSS M0-M5)
- [x] Audit chain implementation
- [x] Gate system functionality

### To Be Validated

- [ ] H1: Tension correlates with diversity
- [ ] H2: Drift predicts intervention need
- [ ] H3: POAV correlates with quality ratings
- [ ] H4: Persona activation matches output type

---

## One-Page Summary | 一頁總結

```
┌─────────────────────────────────────────────────────────────┐
│                       TONESOUL                              │
│           Semantic Responsibility Framework                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CORE INSIGHT:                                              │
│  語氣 = 推理 × 責任                                          │
│  Tone = Inference × Responsibility                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MEASURE          TRACK           GATE           AUDIT      │
│  ────────         ─────           ────           ─────      │
│  TSR vectors      Drift           POAV           Ledger     │
│  ΔT/ΔS/ΔR         from anchor     P0-P4          immutable  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GOVERN WITHOUT UNDERSTANDING                               │
│  We don't need AI to "understand" to hold it accountable.   │
│  We need traceable trajectories and gateable outputs.       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## References

- Semantic Responsibility Theory (`philosophy/semantic_responsibility_theory.md`)
- The Observer and the Observed (`philosophy/observer_and_observed.md`)
- Experimental Design (`research/experimental_design.md`)
- Terminology Glossary (`terminology.md`)
- YuHun Core v3.0 Public Release
- MGGI Specification v0.1.0
