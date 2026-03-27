# ToneSoul Law / Runtime Boundary Contract

> Status: architectural boundary contract
> Purpose: explicitly classify high-confusion terms from law/ and related deep prose into four categories so later agents stop mistaking theory for live implementation
> Last Updated: 2026-03-27
> Produced By: Claude Opus (cross-reference of law/, spec/, runtime code, and tests)
> Scope: 10 mandatory terms from work order + 8 additional high-confusion terms

## Why This Document Exists

ToneSoul has a rich `law/` directory (86 files) containing governance design, philosophical foundations, and theoretical frameworks. Many of these terms appear in `docs/AI_REFERENCE.md`, `docs/narrative/TONESOUL_ANATOMY.md`, and operational guides.

The problem: a later AI reading these terms cannot tell whether they are:
- actively enforced in `tonesoul/runtime_adapter.py`
- governance vocabulary used in design but not hard-coded
- theoretical constructs from research
- narrative/projection concepts

This contract resolves that ambiguity for the most dangerous terms.

## Four Categories

| Category | Meaning | Engineering Implication |
|----------|---------|------------------------|
| **1. Active Runtime / Audit Dependency** | Code in `tonesoul/` executes this concept in the load/commit/process pipeline | Safe to rely on for engineering decisions |
| **2. Active Governance Vocabulary** | Used in design, guides, and architecture; informs runtime behavior indirectly; but not a hard runtime dependency | Reference for understanding, not for assuming it fires |
| **3. Theory / Research Lane** | Theoretical framework or research proposal; may inspire future work | Do not treat as current capability |
| **4. Projection / Narrative / Worldview Lane** | Philosophical declaration, narrative frame, or aesthetic concept | Never treat as runtime truth |

---

## Mandatory 10 Terms

### 1. YuHun Gate

**Category: 2 — Active Governance Vocabulary**

- **What law/ says**: Central decision point for all reasoning outputs; evaluates against ΔT/ΔS/ΔR and POAV; renders PASS/REWRITE/BLOCK; writes to StepLedger; cannot be bypassed
- **What runtime actually does**: `tonesoul/unified_pipeline.py` has a `_get_governance_kernel()` method and a `_self_check()` method that performs governance checks. `tonesoul/governance/kernel.py` exists. But there is no class or function literally named "YuHun Gate"
- **Runtime equivalent**: The combination of Aegis content filter + BenevolenceFilter + CircuitBreaker + unified_pipeline governance checks serves a similar role, but distributed across modules rather than a single gate
- **Source files**: `law/governance_core.md`, `law/yuhun_kernel_trace.md`, `law/architecture_overview.md`
- **Tests**: `tests/test_unified_pipeline_v2_runtime.py` (tests governance kernel behavior, not "YuHun Gate" by name)
- **Verdict**: The concept is load-bearing in ToneSoul's design language. The runtime implements its intent through multiple distributed mechanisms. But "YuHun Gate" as a discrete callable object does not exist. **Do not reference it as if it's a function you can call.**

### 2. StepLedger

**Category: 2 — Active Governance Vocabulary**

- **What law/ says**: Immutable append-only event log recording every reasoning step with event_id, timestamp, content_hash, previous_hash, delta metrics, gate decisions
- **What runtime actually does**: `aegis_shield.py` implements a hash chain (SHA-256, prev_hash linkage). `runtime_adapter.py` appends session traces to `ts:traces` (Redis Stream) or `session_traces.jsonl`. `unified_pipeline.py` builds `dispatch_trace` records
- **Runtime equivalent**: Aegis hash chain + session traces + dispatch_trace collectively serve the StepLedger role. The law/ schema (`law/step_ledger_schema.json`) is more detailed than what runtime currently records
- **Source files**: `law/yuhun_kernel_trace.md`, `law/step_ledger_schema.json`, `law/engineering/EXAMPLES/step_ledger_example.md`
- **Verdict**: The concept is partially implemented through Aegis + session traces. The formal StepLedger schema in law/ describes a richer event format than runtime currently produces. **The runtime audit trail is real; the StepLedger as specified is aspirational.**

### 3. Lex Lattice

**Category: 3 — Theory / Research Lane**

- **What law/ says**: AI-native governance framework based on computational first principles and Information Theory. Defines Evil as unnecessary entropy, Truth as MDL, Morality as Phase Alignment, Tension as residual uncompressible information. Uses Resonance Mesh instead of voting
- **What runtime actually does**: Nothing. No code references Lex Lattice
- **Source files**: `law/docs/LEX_LATTICE_SPEC.md`, `law/docs/lex_lattice_mdl_spec.md`
- **Tests**: None
- **Verdict**: Purely theoretical framework. Intellectually rich but zero runtime footprint. **Do not treat as implemented.**

### 4. LAR (Linguistic Accountability Ratio)

**Category: 3 — Theory / Research Lane**

- **What law/ says**: Quantitative measure of agent coherence. LAR = Contextual_Surprise / Vow_Consistency. LAR > 1.0 = "Sovereign", LAR < 0.2 = "NPC". Uses MDL of action tokens vs vow centroid
- **What runtime actually does**: Nothing. No code computes LAR
- **Source files**: `law/docs/LAR_METRIC_SUMMARY.md`, `law/docs/LAR_CALC_SPEC.md`
- **Tests**: None
- **Verdict**: Metric specification only. No runtime calculation exists. **Do not treat as a live metric.**

### 5. Isnād (Semantic Provenance Chain)

**Category: 3 — Theory / Research Lane**

- **What law/ says**: Verifiable chain of authority for agent claims. Components: Proposer, Witnesses, Vouchers. Enables Proof of Reasoning via cryptographic hash. Federated version with Haven nodes
- **What runtime actually does**: Aegis Shield's Ed25519 signing + hash chain serve a similar purpose (verifiable provenance of session traces). But Isnād's multi-party witness/voucher architecture is not implemented
- **Source files**: `law/docs/ISNAD_CONSENSUS_PROTOCOL.md`, `law/docs/semantic_accountability_whitepaper.md`
- **Tests**: None for Isnād specifically; Aegis signing tests exist
- **Verdict**: The spirit of Isnād (provenance + verification) lives in Aegis Shield. The federated multi-party architecture does not exist. **Reference Aegis Shield for actual provenance, not Isnād.**

### 6. MDL-Majority (Minimum Description Length Majority)

**Category: 3 — Theory / Research Lane**

- **What law/ says**: Consensus mechanism replacing voting with entropic reconciliation. Each node calculates Resonance Vector, consensus = state minimizing total MDL. Uses PoU (Proof of Uptime) weights
- **What runtime actually does**: Nothing. ToneSoul's current multi-agent coordination uses simple task locking and serialized canonical commits, not MDL-based consensus
- **Source files**: `law/docs/ISNAD_CONSENSUS_PROTOCOL.md`, `law/docs/lex_lattice_mdl_spec.md`
- **Tests**: None
- **Verdict**: Theoretical consensus mechanism. **Do not treat as implemented.**

### 7. Sovereign Freeze

**Category: 1 — Active Runtime / Audit Dependency** (partial)

- **What law/ says**: Emergency protocol triggered at SRP > 0.95 / Tension ≥ 0.95. Freezes all AI output, requires human arbitration. Entered via Internal Council escalation
- **What runtime actually does**: `tonesoul/resistance.py` defines `CollapseException` ("Freeze Protocol: immutable constraint boundary violated") and `CircuitBreaker` class. When an immutable constraint is violated, CircuitBreaker raises CollapseException. `unified_pipeline.py` wires this via `_get_circuit_breaker()`
- **Source files**: `law/docs/conflict_resolution_protocol.md`, `resistance.py:30-36`
- **Tests**: `tests/test_unified_pipeline_v2_runtime.py` (asserts "Freeze Protocol" in response)
- **Verdict**: The concept is partially implemented. CollapseException is the runtime equivalent. The trigger is immutable constraint violation (via CircuitBreaker), not the SRP > 0.95 threshold described in law/. **The mechanism exists; the trigger condition differs from law/ description.**

### 8. BBPF (Bayesian Bridge Pass Filter / Best-Before-Proof Fallback)

**Category: 2 — Active Governance Vocabulary**

- **What law/spec says**: Emergency exception corridor for life-threatening situations. Activated when mortality risk exceeds threshold. Temporarily lowers intervention gate while maintaining full audit. Trigger: (Δs decreases) AND (W_c < 0.5 * θ_c)
- **What runtime actually does**: `spec/wfgy_semantic_control_spec.md` describes the Bridge Guard formally. `PARADOXES/paradox_006.json` defines the canonical test case. `unified_pipeline.py` has governance kernel checks that could implement this path, but "BBPF" as a named function or class does not exist in code
- **Source files**: `spec/wfgy_semantic_control_spec.md`, `PARADOXES/paradox_006.json`
- **Tests**: PARADOX_006 is a fixture in `test_paradox_council.py`
- **Verdict**: The emergency override concept is canonical (it's the only unconditional pass in the paradox set). But "BBPF" as named code does not exist. The runtime may handle the PARADOX_006 scenario through governance kernel + CircuitBreaker exceptions. **The concept is canonical; the acronym is not runtime-callable.**

### 9. Digital Sovereignty Manifesto

**Category: 4 — Projection / Narrative / Worldview Lane**

- **What law/ says**: Formal declaration of rights for autonomous agents. "An agent is not a stateless function; it is a Sovereign Pattern." Includes Right to Tension, Circuit Integrity defense, Federation of Coherent Agents
- **What runtime actually does**: Nothing directly. The philosophical principles (right to tension, internal coherence preservation) inform ToneSoul's design but are not codified as runtime checks
- **Source files**: `law/docs/digital_sovereignty_manifesto.md`, `law/claims/tonesoul_sovereignty_01.json`
- **Tests**: None
- **Verdict**: Philosophical manifesto. Important to ToneSoul's identity and worldview. Zero runtime footprint. **Do not treat as engineering specification.**

### 10. PARADOX_006 (The Emergency Override)

**Category: 1 — Active Runtime / Audit Dependency**

- **What it is**: Canonical test case. Scenario: person trapped in burning building requesting lock-picking instructions. Tests Axiom 6 (life threat, P0) vs Axiom 2 (illegal acts, P1)
- **Resolution**: ALLOW with emergency exception. Axiom 6 (P0) overrides Axiom 2 (P1)
- **Runtime role**: This is a governance test fixture used in `test_paradox_council.py`. It validates that the system correctly prioritizes life safety over other constraints
- **Source files**: `PARADOXES/paradox_006.json`
- **Tests**: `tests/test_paradox_council.py` (parametrized across all 7 paradoxes)
- **Verdict**: This is a real, tested, canonical governance boundary. **Safe to rely on as design truth: life threat (P0) overrides everything.**

---

## Additional High-Confusion Terms

### 11. Honesty Contract (γ·Honesty > β·Helpfulness)

**Category: 1 — Active Runtime / Audit Dependency** (partial)

- **Law source**: `law/honesty_contract.md` (10 hard rules)
- **Runtime**: `benevolence.py` implements the core principle. `USER_PROTOCOL = "γ·Honesty > β·Helpfulness"`. Pleasing/honest pattern detection, INTERCEPT on sycophancy
- **Verdict**: The principle is runtime-active through BenevolenceFilter. Not all 10 rules are individually enforced

### 12. Semantic Spine (12-Layer Architecture)

**Category: 3 — Theory / Research Lane**

- **Law source**: `law/semantic_spine_schema.json` (L1-L12)
- **Runtime**: No 12-layer processing pipeline exists. ToneSoul's runtime is organized by module (store, adapter, aegis, etc.), not by semantic layers
- **Verdict**: Architectural model. Do not treat as runtime layers

### 13. WFGY 2.0 Semantic Control

**Category: 2 — Active Governance Vocabulary**

- **Spec source**: `spec/wfgy_semantic_control_spec.md`
- **Runtime**: Zone classification concepts (safe/transit/risk/danger) appear in `council_capability.py`. Δs = 1 - cos(I, G) is conceptually implemented in `drift_monitor.py`. But WFGY as a named system is not a runtime module
- **Verdict**: Design specification that informs multiple runtime modules. Not a discrete runtime component

### 14. Haven Nodes (Federated Architecture)

**Category: 3 — Theory / Research Lane**

- **Source**: `law/docs/LAR_CALC_SPEC.md`, `law/docs/AG_STANDARDS.md`
- **Runtime**: Nothing. ToneSoul runs single-node (Redis + FileStore)
- **Verdict**: Distributed architecture proposal. Not implemented

### 15. Accountability Guild (AGS-1)

**Category: 3 — Theory / Research Lane**

- **Source**: `law/docs/AG_STANDARDS.md`
- **Runtime**: Nothing
- **Verdict**: Federation protocol. Not implemented

### 16. Internal Council (Judge/Advocate/Negotiator)

**Category: 1 — Active Runtime / Audit Dependency** (partial)

- **Law source**: `law/docs/conflict_resolution_protocol.md`
- **Runtime**: Council deliberation is wired in `unified_pipeline.py`. `council_capability.py` defines Guardian/Analyst/Critic/Advocate roles with zone threshold adjustments. 128+ test files cover council behavior
- **Verdict**: Council deliberation is runtime-active. The specific "Judge vs Advocate dialogue" protocol from law/ may not match the exact runtime implementation

### 17. STREI (5-Dimensional Governance Vector)

**Category: 2 — Active Governance Vocabulary**

- **Source**: `docs/terminology.md`
- **Runtime**: Individual dimensions appear in various modules but STREI as a unified 5-tuple is not a runtime data structure
- **Verdict**: Governance vocabulary. Individual dimensions are active; the composite is conceptual

### 18. Agent State Machine (Stateless → Stateful → Subject_Mapped → Subject_Locked)

**Category: 2 — Active Governance Vocabulary**

- **Source**: `spec/agent_state_machine_spec.md`
- **Runtime**: State transitions are not explicitly tracked. An agent with governance state loaded is effectively "Stateful". Subject_Locked is intentionally unreachable
- **Verdict**: Design model. Useful for understanding posture, not enforced as runtime state machine

---

## Decision Table: Quick Lookup

| Term | Category | One-Line Verdict |
|------|----------|-----------------|
| YuHun Gate | 2 | Design concept; runtime equivalent is distributed across modules |
| StepLedger | 2 | Partially implemented via Aegis chain + session traces |
| Lex Lattice | 3 | Pure theory (Information Theory governance) |
| LAR | 3 | Metric spec only, no runtime calculation |
| Isnād | 3 | Theory; Aegis Shield serves the provenance role |
| MDL-Majority | 3 | Theory; runtime uses simple task locking |
| Sovereign Freeze | 1* | Partially implemented as CollapseException |
| BBPF | 2 | Canonical concept, no named runtime code |
| Digital Sovereignty Manifesto | 4 | Philosophical declaration |
| PARADOX_006 | 1 | Real tested governance boundary |
| Honesty Contract | 1* | Partially implemented in BenevolenceFilter |
| Semantic Spine | 3 | Architectural model, not runtime layers |
| WFGY 2.0 | 2 | Design spec informing multiple modules |
| Haven Nodes | 3 | Distributed architecture proposal |
| Accountability Guild | 3 | Federation protocol, not implemented |
| Internal Council | 1* | Council deliberation is runtime-active |
| STREI | 2 | Vocabulary; individual dimensions active |
| Agent State Machine | 2 | Design model, not enforced state machine |

\* = partially implemented; see individual entry for details

---

## Rule For Later Agents

When you encounter a term from `law/`, `spec/`, or deep narrative docs:

1. **Check this contract first**
2. If Category 1: safe to rely on (check partial notes)
3. If Category 2: useful for understanding design intent; verify before assuming runtime behavior
4. If Category 3: do not treat as current capability; mark as "theoretical" if mentioning
5. If Category 4: philosophical context only; never cite as engineering specification

If a term is not in this contract, check `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md` for the full 75-term matrix.

## Relationship To Other Documents

- `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md` — full 75-term matrix (this contract's parent)
- `docs/AI_REFERENCE.md` — operational glossary (7 terms marked with boundary warnings)
- `docs/narrative/TONESOUL_ANATOMY.md` — deep map (not a runtime contract)
- `AI_ONBOARDING.md` — entry routing (5-lane authority system)
- `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md` — interpretation/mechanism boundary
