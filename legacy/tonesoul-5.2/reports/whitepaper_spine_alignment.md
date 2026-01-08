# Whitepaper vs Semantic Spine Alignment

Scope:
- Whitepaper source: `5.2/reports/WHITEPAPER_cleaned.md`
- Semantic Spine source: `docs/SEMANTIC_SPINE_SPEC.md`

All terms listed below are the readable/cleaned English names for alignment.

---

## Term Alignment Table

| Whitepaper term | Semantic Spine term | Notes |
| --- | --- | --- |
| Wave Layer | L6 Narrative & Identity | Both carry tone/emotion vectors; Whitepaper focuses on tone dynamics. |
| Structure Layer | L10 Value & Norm Field + L12 Governance Gates | Value anchoring + POAV-like gating align to L10/L12. |
| Physics Layer | L1 Stable World Layer | Both encode invariant constraints and verifiable structure. |
| Semantic Seed | L9 Provenance & Accountability | Seed metadata aligns with provenance and traceability. |
| LTM (Long-Term Memory) | L9 Provenance & Accountability | Spine stores source chains; Whitepaper defines lifecycle. |
| T0-T6 Lifecycle | L9 Provenance & Accountability | Spine does not name T0-T6; closest match is provenance tracking. |
| ToneSoul (Delta T/S/R) | L6 Narrative & Identity + L12 Gates | Tone metrics map to narrative state + governance gate inputs. |
| REL (Responsibility Echo Level) | L9 Provenance & Accountability | Responsibility scoring aligns with accountability tracking. |
| Mercy-based Objective | L10 Value & Norm Field | Both define value-weighted optimization. |
| Multi-point governance | L11 Multi-Perspective Engine | Multiple perspectives and arbitration align directly. |
| Chronos/Kairos/Trace | L6 Narrative & Identity + L9 Provenance | Time hooks + traceability map to L6/L9. |
| Time Fold | L3 Temporal Drift Layer | Time-sliced meanings and drift handling are shared concepts. |
| DCS (Dynamic Closure System) | L12 Governance & Soul Gates | DCS is a control gate; aligns to governance gating. |
| Quarantine Zone | L4 Meme & Volatile Layer | Isolation policy matches volatile containment. |
| JUMP Engine | L12 Gates + L13 Semantic Drive | JUMP is a high-risk transition under gate control. |
| Minimal Action Set | L12 Governance Gates + L8 Epistemic | Verify/Cite/Inquire align with epistemic discipline. |

---

## Whitepaper -> 5.2 Implementation Mapping

| Whitepaper topic | 5.2 implementation | Status |
| --- | --- | --- |
| Chronos/Kairos/Trace | `5.2/tonesoul52/context_compiler.py` | implemented |
| ToneSoul (Delta T/S/R) | `5.2/tonesoul52/tsr_metrics.py`, `5.2/spec/metrics/tsr_policy.yaml` | implemented (heuristic TSR metrics + deltas) |
| POAV / Quality gating | `5.2/tonesoul52/poav.py`, `5.2/tonesoul52/yss_gates.py` | implemented (minimal POAV metric + gate) |
| ETCL memory loop | `5.2/tonesoul52/memory_manager.py`, `5.2/spec/memory/memory_policy.yaml`, `5.2/tonesoul52/etcl_lifecycle.py` | implemented (minimal T0-T6 transitions + seed state history) |
| Semantic Seed schema | `5.2/memory/seeds/*.json` | partial (seed snapshot + metadata/provenance/governance/anchor) |
| LTM provenance tracking | `5.2/tonesoul52/memory_manager.py`, `5.2/memory/graph_index.json` | implemented (artifact index + hashes) |
| T0-T6 lifecycle | `5.2/tonesoul52/etcl_lifecycle.py` | implemented (state transitions) |
| Mercy-based objective | `5.2/tonesoul52/mercy_objective.py` | implemented (objective snapshot + audit wiring) |
| Multi-point governance | `5.2/tonesoul52/role_council.py`, `5.2/spec/frames/frame_registry.json`, `5.2/spec/governance/role_catalog.yaml` | implemented (lightweight council summary) |
| Chronos/Kairos/Trace gates | `5.2/tonesoul52/yss_gates.py` (context_lint) | implemented |
| DCS (Dynamic Closure System) | `5.2/tonesoul52/dcs.py`, `5.2/tonesoul52/yss_gates.py`, `5.2/spec/governance/dcs_policy.yaml` | implemented (record-only gate + artifact) |
| Quarantine Zone | `5.2/tonesoul52/escalation.py`, `5.2/tonesoul52/yss_gates.py` | implemented (escalation gate + ledger) |
| JUMP Engine | `5.2/tonesoul52/escalation.py`, `5.2/tonesoul52/yss_gates.py` | implemented (jump decision path) |
| Minimal Action Set (Verify/Cite/Inquire) | `5.2/tonesoul52/action_set.py` | implemented (action set policy + constraints wiring) |
| Evidence + Audit chain | `5.2/tonesoul52/evidence_collector.py`, `5.2/tonesoul52/audit_interface.py` | implemented |
| YSTM terrain (what/where + drift) | `5.2/tonesoul52/ystm/*`, `5.2/reports/ystm_demo/*` | implemented |

---

## Notes

- This mapping is conservative: it only marks “implemented” where runnable code exists.
- “partial” means scaffolding exists but not a complete life cycle or metric system.
