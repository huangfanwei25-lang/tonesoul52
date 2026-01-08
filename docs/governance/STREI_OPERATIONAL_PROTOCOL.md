# Protocol: STREI Vector Operational Specification

## 1. Definition & Vector Mapping
The STREI vector represents the **Mind Model State** of ToneSoul (TAE-01). It is an engineering requirement for all L2-L5 interactions.

| Vector | Full Name | Arch Layer | Functional Role |
| :--- | :--- | :--- | :--- |
| **S** | Stability | L4 (Integrity) | Measures hash-chain consistency and semantic drift. |
| **T** | Tension | L5/REM (Weaver) | Measures unresolved complexity; drives the "REM Cycle". |
| **R** | Responsibility | L4 (Ledger) | Measures Density of Traceability (Proof of Trace). |
| **E** | Ethics | L0 (Axioms) | Hard Constraint Gate (PASS/BLOCK). |
| **I** | Intent | L1 (Spine) | Alignment with Axiomatic Target Objectives. |

## 2. Threshold Governance
As per [GUARDIAN_THRESHOLDS.yaml](file:///c:/Users/user/Desktop/倉庫/docs/GUARDIAN_THRESHOLDS.yaml):
- **BLOCK Trigger**: $E < 0.70$ OR $R < 0.60$ OR $I < 0.65$.
- **WARN Trigger**: $T > 0.85$.

## 3. Maintenance Policy
- **Self-Evolution**: High Tension ($T$) must be resolved via **Semantic Distillation** (`memory_distiller.py`) to maintain Stability ($S$).
- **Auditability**: All vector measurements must be committed to the [StepLedger](file:///c:/Users/user/Desktop/倉庫/modules/protocol/ledger.py).
