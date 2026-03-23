# Protocol: STREI Vector Operational Specification

> Purpose: specify the operational meaning, thresholds, and maintenance rules for the STREI vector in ToneSoul governance.
> Last Updated: 2026-03-23
## 1. Definition & Vector Mapping
The STREI vector represents the **Mind Model State** of ToneSoul (TAE-01). It is an
engineering requirement for all L2-L5 interactions.

| Vector | Full Name | Arch Layer | Functional Role |
| --- | --- | --- | --- |
| **S** | Stability | L4 (Integrity) | Measures hash-chain consistency and semantic drift. |
| **T** | Tension | L5/REM (Weaver) | Measures unresolved complexity; drives the REM cycle. |
| **R** | Responsibility | L4 (Ledger) | Measures density of traceability (Proof of Trace). |
| **E** | Ethics | L0 (Axioms) | Hard constraint gate (PASS/BLOCK). |
| **I** | Intent | L1 (Spine) | Alignment with axiomatic target objectives. |

## 2. Threshold Governance
As per `docs/GUARDIAN_THRESHOLDS.yaml`:
- **BLOCK Trigger**: E < 0.70 OR R < 0.60 OR I < 0.65
- **WARN Trigger**: T > 0.85

## 3. Maintenance Policy
- **Self-Evolution**: High Tension (T) must be resolved via **Semantic Distillation**
  (`memory_distiller.py`) to maintain Stability (S).
- **Auditability**: All vector measurements must be committed to the StepLedger
  specification (`docs/STEP_LEDGER_SPEC.md`).
