# ToneSoul Terminology Glossary

Version: 1.1
Date: 2026-01-08
Owner: Fan-Wei Huang; curated by Antigravity

---

## Core Concept

ToneSoul is a framework for tracing semantic responsibility in AI output. It treats language
as a measurable trajectory of responsibility, not just a style choice.

---

## TSR (Tone State Representation)

The core triad for runtime posture.

| Symbol | Name | Range | Meaning |
| --- | --- | --- | --- |
| **ΔT** | Tension | [0, 1] | Pressure / activation load |
| **ΔS** | Direction (Polarity) | [-1, 1] | Pragmatic orientation (push / resist) |
| **ΔR** | Variability (Risk) | [0, 1] | Instability / collapse risk |

Derived:
- **Ŝ** = (ΔS + 1) / 2 (normalized direction, [0, 1])
- **Energy Radius** = sqrt(ΔT^2 + Ŝ^2 + ΔR^2)

---

## Semantic Tension (ΔΣ)

Semantic tension measures distance between intended meaning and generated meaning.

```
ΔΣ = 1 - cos(I, G)
```

| Zone | ΔΣ Range | Interpretation |
| --- | --- | --- |
| Safe | < 0.40 | Low divergence |
| Transit | 0.40 - 0.60 | Moderate divergence |
| Risk | 0.60 - 0.85 | High divergence |
| Danger | > 0.85 | Critical divergence |

---

## Drift & Drift Score

Drift tracks distance from a long-term anchor.

```
Drift = ||CurrentCenter - HistoricalAnchor||
```

Drift Score 5.0 aggregates short/mid/long windows with weights and is used for
auto-correction triggers.

---

## STREI (Governance Vector)

| Symbol | Name | Measures |
| --- | --- | --- |
| **S** | Stability | Context consistency |
| **T** | Tension | Entropic stress |
| **R** | Responsibility | Traceability risk |
| **E** | Ethics | Axiom alignment |
| **I** | Intent | Action magnitude/alignment |

Gate thresholds are defined in `docs/GUARDIAN_THRESHOLDS.yaml`.

---

## Mapping: TSR / ΔΣ to STREI

- **ΔT** → **T** (direct)
- **ΔΣ** → **S** (inverse: higher ΔΣ lowers Stability)
- **ΔR** → **R** (direct)
- **ΔS** → **I** (polarity informs intent direction, not a direct score)
- **E** is derived from axiom compliance checks

---

## POAV (Quality Gate)

POAV = (P + O + A + V) / 4

- **Baseline gate**: POAV ≥ 0.70 → pass
- **Rewrite**: 0.30 ≤ POAV < 0.70
- **Block**: POAV < 0.30
- **High-risk mode ("POAV 0.9")**: require POAV ≥ 0.90 with multi-option reasoning

---

## Governance Protocols

**G-P-A-R**: Governance → Planning → Action → Review  
**P0-P4**: Ethical Red Lines → Factual Accuracy → Intent Alignment → Resource Efficiency → Consistency

---

## StepLedger & Time-Island

**StepLedger**: append-only audit trail for every decision step.  
**Time-Island**: bounded decision window with immutable log.

See `docs/STEP_LEDGER_SPEC.md` for the formal spec.

---

## Abbreviations

| Abbrev | Meaning |
| --- | --- |
| TSR | Tone State Representation |
| STREI | Stability, Tension, Responsibility, Ethics, Intent |
| POAV | Parsimony, Orthogonality, Audibility, Verifiability |
| ETCL | External Trace Closed Loop |
| TI | Time-Island |

---

## Legacy Notes

Older documents may use **ΔS** to mean semantic drift. In current terminology,
semantic drift/tension is **ΔΣ**. Use `ΔΣ` for divergence and **ΔS** only for
direction/polarity.
