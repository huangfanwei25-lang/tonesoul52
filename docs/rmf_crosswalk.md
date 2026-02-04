# NIST AI RMF Crosswalk (Draft)

Date: 2026-02-04
Scope: High-level mapping of ToneSoul components to NIST AI RMF 1.0 functions (Govern/Map/Measure/Manage).
Note: This is a working crosswalk, not a compliance claim.

## Mapping Table
| RMF Function | Intent (Summary) | ToneSoul Artifacts | Evidence Outputs | Gaps / Next Actions |
| --- | --- | --- | --- | --- |
| Govern | Establish policies, accountability, and oversight for AI systems. | `law/AXIOMS.json`, CouncilRuntime, `docs/STRUCTURE.md`, handoff drift_log discipline. | AXIOMS, Council structured verdicts, Isnad ledger entries. | Formal human authorization gate, explicit governance roles. |
| Map | Identify context, intended use, and risk boundaries. | CouncilRequest context, STREI metrics, risk model in README. | Structured verdict sections A/B/C, risk labels, context keys. | System card + use-case statements; formal data statements. |
| Measure | Assess performance, reliability, and risk impact. | Test suite, coherence metrics, MemoryObserver logs, Council votes. | `tests/`, structured verdicts, action_logs, provenance ledger. | Define metric thresholds and monitoring cadence. |
| Manage | Mitigate and respond to risks; lifecycle controls. | Council `BLOCK`/`REFINE`, Orchestrator gating, Isn?d hash chain. | Ledger with hash/prev_hash, drift_log continuity, incident notes. | Incident response playbook; red-team protocols. |

## GenAI Profile Alignment (High-Level)
The NIST GenAI Profile extends RMF 1.0 with generative-specific considerations (content integrity, data provenance, misuse risks). ToneSoul aligns via:
- **Content integrity**: structured verdicts + Isnad hash chain.
- **Data provenance**: `provenance_ledger.jsonl` + planned PROV-DM mapping.
- **Misuse risk control**: Council safety veto + risk-specific refinement.

## References
- NIST AI RMF 1.0 (NIST AI 100-1)
- NIST GenAI Profile (NIST AI 600-1)
