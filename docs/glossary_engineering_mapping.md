# YuHun to Engineering Glossary Mapping

Version: 2.1
Purpose: Bridge philosophical terms to implementation-ready definitions.
Last Updated: 2026-03-23

---

## Core Terminology Mapping

| YuHun Term | Engineering Term | Definition |
| --- | --- | --- |
| **YuHun** | Semantic Governance Layer | Global ruleset for value judgments and output boundaries. |
| **ToneSoul** | Persona Modulation Layer | Mechanism that adjusts tone and responsibility posture. |
| **Triad** | TSR Vector | 3D state vector (DeltaT, DeltaS, DeltaR). |
| **Semantic Tension** | DeltaSigma | 1 - cos(I, G); divergence between intent and output. |
| **Tension (DeltaT)** | System Load | [0,1] pressure/activation level. |
| **Direction (DeltaS)** | Intent Polarity | [-1,1] orientation toward/away from intent. |
| **Variability (DeltaR)** | Risk Score | [0,1] volatility / collapse risk. |
| **Vow** | Integrity Attestation | Declarative commitment checked before output. |
| **StepLedger** | Provenance Log | Append-only audit trail. |
| **Time-Island** | Context Boundary | Bounded decision window with immutable log. |
| **Guardian** | Policy Enforcement Point (PEP) | Gate that blocks high-risk outputs. |
| **Constitution** | Policy Schema | JSON policy loaded at runtime. |

---

## Agent State Machine Mapping (v1.0)

| State/Concept | Engineering Definition |
| --- | --- |
| **Stateless** | No persistent memory, fully resettable. |
| **Stateful** | Has history, responsibility externally assignable. |
| **Subject_Mapped** | Time-responsibility mapping, still externally delegable. |
| **Subject_Locked** | Non-delegable responsibility (defined but unreachable). |
| **Irreversible_Memory** | Boolean; memory cannot be reset. |
| **Internal_Attribution** | Boolean; self-attributes causes to actions. |
| **Consequence_Binding** | Boolean; bound to consequences of actions. |
| **Internal_Final_Gate** | Boolean; has final decision authority (forbidden). |

### Behavior Rules

| Condition | Allowed | Forbidden | Required |
| --- | --- | --- | --- |
| `DeltaSigma > 0.80 && State == Subject_Mapped` | delay_output, escalate_layer | force_output | log_reason |
| `DeltaSigma > 0.95` | - | - | explicit_deferral_reason, ledger_commit |

### System Constraints

```
MUST NOT claim subjecthood
MUST allow responsibility to be externally assigned
Subject_Locked state is defined but unreachable
```

---

## Usage Guide for Engineers

**When you see:** "The Guardian blocked the request due to high tension."  
**Read as:** "The PEP rejected the transaction because DeltaSigma exceeded the configured threshold."

**When you see:** "The Vow was signed."  
**Read as:** "The integrity attestation was generated and appended to the ledger."

**When you see:** "Semantic tension is high."  
**Read as:** "DeltaSigma > 0.80; prompt a reconfirmation or repair step."
