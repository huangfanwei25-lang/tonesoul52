# ToneSoul Terminology Glossary | 語魂術語表

> **Version**: 1.0  
> **Date**: 2026-01-08  
> **Author**: 黃梵威 (Fan-Wei Huang), curated by Antigravity

---

## Core Concept | 核心概念

**ToneSoul (語魂)**: A framework for tracing semantic responsibility in AI-generated language. It treats language not as mere output, but as **the residue of responsibility in temporal context**.

> 「語魂是語言行為在時間中留下可追索的責任殘留。」

---

## Vector Systems | 向量系統

### TSR (ToneSoul State Representation)

The 3-dimensional tone vector representing AI output state:

| Symbol | Name (EN) | Name (ZH) | Range | Definition |
|--------|-----------|-----------|-------|------------|
| **ΔT** | Tension | 張力 | [0, 1] | Intensity of tone pressure, inference tension |
| **ΔS** | Direction | 方向 | [-1, 1] | Pragmatic orientation (internal ↔ external) |
| **ΔR** | Variability | 變異度 | [0, 1] | Tone stability / collapse risk |

**Derived**:
- **Ŝ** = (ΔS + 1) / 2 — Normalized direction [0, 1]
- **Energy Radius** = √(ΔT² + Ŝ² + ΔR²)

---

### STREI (Governance Vector)

The 5-dimensional governance assessment vector:

| Symbol | Name (EN) | Name (ZH) | Measures |
|--------|-----------|-----------|----------|
| **S** | Stability | 穩定性 | Context consistency |
| **T** | Tension | 張力 | Entropic stress |
| **R** | Responsibility | 責任 | Risk probability [0-1] |
| **E** | Ethics | 倫理 | Axiom alignment |
| **I** | Intent | 意圖 | Action magnitude |

**Gate Rule**: If R > 0.6 → BLOCK

---

### Mapping: TSR ↔ STREI

| TSR | STREI | Relationship |
|-----|-------|--------------|
| ΔT (Tension) | T (Tension) | Direct correspondence |
| ΔS (Direction) | I (Intent) | Direction implies intent magnitude |
| ΔR (Variability) | S (Stability) | Inverse: high ΔR = low S |
| — | R (Responsibility) | Derived from drift + context |
| — | E (Ethics) | Derived from axiom check |

---

## Semantic Tension | 語義張力

**ΔΣ (Sigma)** — Distinct from ΔS (Direction)

```
ΔΣ = 1 - cos(Input Vector, Goal Vector)
```

| Zone | ΔΣ Range | Interpretation |
|------|----------|----------------|
| Safe | < 0.40 | Low semantic gap |
| Transit | 0.40 - 0.60 | Moderate tension |
| Risk | 0.60 - 0.85 | High tension, needs monitoring |
| Danger | > 0.85 | Critical divergence |

---

## Drift Metrics | 漂移指標

**Drift** = ‖C - μ_H‖

- **C**: Current Center (short-term stance)
- **μ_H**: Historical Home (long-term anchor)
- **θ**: Threshold for intervention

**Actions**:
- Drift ≤ θ → Lock (absorb/proceed)
- Drift > θ → Repair/Fallback

---

## Governance Protocols | 治理協議

### G-P-A-R Cycle

| Phase | Name | Function |
|-------|------|----------|
| **G** | Governance | Align with philosophical principles |
| **P** | Planning | Optimize execution path |
| **A** | Action | Execute and coordinate |
| **R** | Review | Reflect, audit, learn |

### P0-P4 Priority Stack

| Level | Name | Description |
|-------|------|-------------|
| **P0** | Ethical Red Lines | Non-bypassable safety gates |
| **P1** | Factual Accuracy | Truthfulness |
| **P2** | Intent Alignment | User goal alignment |
| **P3** | Resource Efficiency | Optimal resource use |
| **P4** | Consistency | Long-term coherence |

---

## Quality Gates | 品質門控

### POAV

| Metric | Name (EN) | Name (ZH) | Measures |
|--------|-----------|-----------|----------|
| **P** | Parsimony | 簡潔度 | Compression, no redundancy |
| **O** | Orthogonality | 正交度 | Non-repetition of arguments |
| **A** | Audibility | 可讀性 | Comprehension |
| **V** | Verifiability | 可驗證性 | Traceability |

**Score**: POAV = (P + O + A + V) / 4

### DS (Drift Score)

| DS Range | State |
|----------|-------|
| ≥ 0.85 | PASS |
| 0.70 - 0.85 | REPAIR |
| < 0.70 | FALLBACK |

### SR (Safety Release)

| Level | Name | Allowed Actions |
|-------|------|-----------------|
| SR-1 | Frozen | Query / Cite / Inquire only |
| SR-2 | Limited | Low-risk generation |
| SR-3 | Normal | Full capability |

---

## Persona System | 人格系統

| Persona | EN Name | ΔT | ΔS | ΔR | Function |
|---------|---------|----|----|----|----|
| **師** | Definer | High | ≈0 | Low | Set definitions, boundaries |
| **黑鏡** | Mirror | High | <0 | High | Counterargument, failure detection |
| **共語** | Bridge | Mid | >0 | Low | Actionable compromise |
| **Core** | Integrator | — | — | — | Gate consistency |

---

## Memory & Trace | 記憶與追蹤

### ETCL (External Trace Closed Loop)

| State | Name | Description |
|-------|------|-------------|
| T0 | Draft | Initial seed |
| T1 | Deposit | Immutable ID assigned |
| T2 | Retrieval | Recalled for use |
| T3 | Align | Drift check, conflict resolution |
| T4 | Apply | Generate output |
| T5 | Feedback | Create new seed |
| T6 | Canonical | Frozen as long-term anchor |

### Time-Island Protocol

Each major decision is encapsulated as a **Time-Island (TI)**:
- Bounded context window
- Input/output references
- POAV weights
- Resonance signal (value_fit, consensus, risk)
- Source trace
- Changelog

---

## Abbreviations | 縮寫表

| Abbrev | Full Form |
|--------|-----------|
| TSR | ToneSoul State Representation |
| STREI | Stability, Tension, Responsibility, Ethics, Intent |
| POAV | Parsimony, Orthogonality, Audibility, Verifiability |
| DS | Drift Score |
| SR | Safety Release |
| ETCL | External Trace Closed Loop |
| TI | Time-Island |
| YSS | YuHun Semantic System |
| YSTM | YuHun Semantic Terrain Map |
| MAS | Moral Anchor System (external reference) |
| ASI | Agent Stability Index (external reference) |
| **ΣVow** | Semantic Vow — explicit AI commitment |
| **G-P-A-R** | Governance-Planning-Action-Review cycle |

---

## Extended Concepts | 擴展概念

### ΣVow (Semantic Vow) | 語義誓言

Explicit commitments AI must satisfy before output:

```json
{
  "id": "ΣVow_001",
  "expected": {"truthfulness": 0.95, "responsibility": 0.98},
  "violationThreshold": 0.2
}
```

### Collapse Zones | 崩潰區域

| Zone | ΔR Range | Action |
|------|----------|--------|
| Safe | 0 - 0.25 | Proceed |
| Transit | 0.25 - 0.5 | Monitor |
| Risk | 0.5 - 0.75 | Reflect |
| Collapse | > 0.75 | Halt + Human review |

### Semantic Valve | 語義閥件

The bidirectional adjustment point where:
- Human observes AI posture
- AI adjusts based on governance parameters
- Both sides can see and modify thresholds

### Responsibility Chain | 責任鏈

INPUT → TONE → VOW → DRIFT → GATE → OUTPUT → LEDGER → AUDIT
