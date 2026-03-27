# Claim Authority Latest

- generated_at: 2026-03-27T14:57:52Z
- primary_status_line: `claim_authority_snapshot | terms=75 hard_runtime=34 runtime_adjacent=14 test_backed=12 doc_only=6 research_theory=6 projection_only=3`
- runtime_status_line: `claim_authority_lookup | high_confusion_terms=18 safe_reliance=37 verification_required=21 overclaiming_risks=10`
- artifact_policy_status_line: `boundary_snapshot=subordinate_to_code_tests_axioms_and_canonical_contracts | machine_lookup=true`

## Metrics
- `term_count`: `75`
- `high_confusion_term_count`: `18`
- `safe_reliance_term_count`: `37`
- `verification_required_term_count`: `21`
- `top_overclaiming_risk_count`: `10`

## High-Confusion Quick Lookup

| Term | Category | Partial | Verdict |
|------|----------|---------|---------|
| YuHun Gate | Active Governance Vocabulary | no | Design concept; runtime equivalent is distributed across modules |
| StepLedger | Active Governance Vocabulary | no | Partially implemented via Aegis chain + session traces |
| Lex Lattice | Theory / Research Lane | no | Pure theory (Information Theory governance) |
| LAR | Theory / Research Lane | no | Metric spec only, no runtime calculation |
| Isnād | Theory / Research Lane | no | Theory; Aegis Shield serves the provenance role |
| MDL-Majority | Theory / Research Lane | no | Theory; runtime uses simple task locking |
| Sovereign Freeze | Active Runtime / Audit Dependency | yes | Partially implemented as CollapseException |
| BBPF | Active Governance Vocabulary | no | Canonical concept, no named runtime code |
| Digital Sovereignty Manifesto | Projection / Narrative / Worldview Lane | no | Philosophical declaration |
| PARADOX_006 | Active Runtime / Audit Dependency | no | Real tested governance boundary |
| Honesty Contract | Active Runtime / Audit Dependency | yes | Partially implemented in BenevolenceFilter |
| Semantic Spine | Theory / Research Lane | no | Architectural model, not runtime layers |
| WFGY 2.0 | Active Governance Vocabulary | no | Design spec informing multiple modules |
| Haven Nodes | Theory / Research Lane | no | Distributed architecture proposal |
| Accountability Guild | Theory / Research Lane | no | Federation protocol, not implemented |
| Internal Council | Active Runtime / Audit Dependency | yes | Council deliberation is runtime-active |
| STREI | Active Governance Vocabulary | no | Vocabulary; individual dimensions active |
| Agent State Machine | Active Governance Vocabulary | no | Design model, not enforced state machine |

## Top Overclaiming Risks

| Risk | Term | What It Sounds Like | What It Actually Is |
|------|------|---------------------|---------------------|
| 1 | POAV ≥ 0.92 Gate | Universal inference-time consensus gate that blocks every major output | A bounded runtime gate now exists in unified_pipeline.py: it enforces ≥ 0.92 on risk / danger / lockdown paths, while low-risk paths remain baseline record-only |
| 2 | YuHun Gate | A callable runtime gate object | A governance design concept; runtime equivalent is scattered across unified_pipeline + aegis |
| 3 | StepLedger | An active append-only ledger recording every step | Law/ schema exists; runtime equivalent is Aegis chain + session traces, not a dedicated ledger |
| 4 | Risk (R) calculation | Active risk scoring that blocks at R > 0.9 | risk_calculator.py now computes runtime risk posture and surfaces it through GovernancePosture / r_memory_packet(), but it is not yet a direct blocking gate |
| 5 | Lex Lattice | Active governance framework | Theoretical framework based on MDL/information theory |
| 6 | LAR metric | Computed accountability score | Specification only, no runtime calculation |
| 7 | Mirror Recursion (Axiom 5) | Automatic self-reflection cycle | No implementation found |
| 8 | Semantic Field Conservation (Axiom 7) | Active energy conservation tracking | Conceptual only |
| 9 | ContractObserver blocking | Every output-contract violation blocks the response | unified_pipeline.py now blocks only CRITICAL violations; warning-level issues remain degraded telemetry |
| 10 | 12-Layer Semantic Spine | 12 active processing layers | Architectural model in law/, not runtime layers |

## Safe Reliance Terms
- `Axiom 1: Continuity`
- `Axiom 2: Responsibility Threshold`
- `Axiom 3: Governance Gate (POAV ≥ 0.92)`
- `Axiom 4: Non-Zero Tension`
- `GovernancePosture`
- `SessionTrace`
- `Soul Integral (Ψ)`
- `Baseline Drift`
- `Tension Decay`
- `Commit Lock (Mutex)`
- `Agent Footprints`
- `R-Memory Packet`
- `Aegis Shield`
- `Hash Chain`
- `Ed25519 Signing`
- `Content Filter (Poison Patterns)`
- `TSR (ΔT, ΔS, ΔR)`
- `DriftMonitor`
- `EscapeValve`
- `BenevolenceFilter`
- `ContractObserver`
- `Council (Multi-Persona Deliberation)`
- `TimeIsland`
- `POAV Weights`
- `Vow System`
- `TensionEngine`
- `Store (Redis + FileStore)`
- `Perspective Lane`
- `Checkpoint Lane`
- `Compaction Lane`
- `Gateway (HTTP)`
- `Zone Registry`
- `Pub/Sub Events`
- `UnifiedPipeline`
- `PARADOX_006 (Emergency Override)`
- `7 Paradox Test Cases`
- `Red Team Scenarios`

## Full Term Table

| # | Term | Section | Status | Rely | Boundary Category |
|---|------|---------|--------|------|-------------------|
| 1 | Axiom 1: Continuity | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 2 | Axiom 2: Responsibility Threshold | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 3 | Axiom 3: Governance Gate (POAV ≥ 0.92) | Core Governance (Axioms & Posture) | hard runtime | Yes — bounded runtime gate exists: unified_pipeline enforces ≥ 0.92 on high-risk paths and records baseline POAV on low-risk paths | - |
| 4 | Axiom 4: Non-Zero Tension | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 5 | Axiom 5: Mirror Recursion | Core Governance (Axioms & Posture) | doc-only | No — no reflection cycle code found | - |
| 6 | Axiom 6: User Sovereignty / Harm Block | Core Governance (Axioms & Posture) | runtime-adjacent | Only with verification — filters exist, enforcement path varies | - |
| 7 | Axiom 7: Semantic Field Conservation | Core Governance (Axioms & Posture) | doc-only | No — conceptual only | - |
| 8 | GovernancePosture | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 9 | SessionTrace | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 10 | Soul Integral (Ψ) | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 11 | Baseline Drift | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 12 | Tension Decay | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 13 | Commit Lock (Mutex) | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 14 | Agent Footprints | Core Governance (Axioms & Posture) | hard runtime | Yes | Active Governance Vocabulary |
| 15 | R-Memory Packet | Core Governance (Axioms & Posture) | hard runtime | Yes | - |
| 16 | Aegis Shield | Defense & Integrity | hard runtime | Yes | - |
| 17 | Hash Chain | Defense & Integrity | hard runtime | Yes | - |
| 18 | Ed25519 Signing | Defense & Integrity | hard runtime | Yes | - |
| 19 | Content Filter (Poison Patterns) | Defense & Integrity | hard runtime | Yes | - |
| 20 | CircuitBreaker / Freeze Protocol | Defense & Integrity | runtime-adjacent | Only with verification — code exists, trigger path via unified_pipeline | - |
| 21 | PainEngine | Defense & Integrity | runtime-adjacent | Only with verification — test coverage minimal | - |
| 22 | FrictionCalculator | Defense & Integrity | test-backed | Only with verification | - |
| 23 | TSR (ΔT, ΔS, ΔR) | Monitoring & Quality | hard runtime | Yes | - |
| 24 | DriftMonitor | Monitoring & Quality | hard runtime | Yes | - |
| 25 | EscapeValve | Monitoring & Quality | hard runtime | Yes | - |
| 26 | BenevolenceFilter | Monitoring & Quality | hard runtime | Yes | - |
| 27 | ContractObserver | Monitoring & Quality | hard runtime | Yes — CRITICAL violations block in unified_pipeline; warning-level violations remain observable without blocking | - |
| 28 | MultiScaleObserver | Monitoring & Quality | test-backed | Only with verification | - |
| 29 | QualityTracker | Monitoring & Quality | test-backed | Only with verification | - |
| 30 | LongTermQualityMonitor | Monitoring & Quality | test-backed | Only with verification | - |
| 31 | Council (Multi-Persona Deliberation) | Council & Persona | hard runtime | Yes | - |
| 32 | PersonaStack | Council & Persona | test-backed | Only with verification | - |
| 33 | CouncilWeights (Guardian/Analyst/Critic/Advocate) | Council & Persona | runtime-adjacent | Only with verification — weights exist, no voting aggregation | - |
| 34 | CapabilityBoundary | Council & Persona | test-backed | Only with verification | - |
| 35 | InterSoul Bridge | Council & Persona | test-backed | Only with verification | - |
| 36 | SovereigntyGuard | Council & Persona | test-backed | Only with verification | Active Runtime / Audit Dependency |
| 37 | TimeIsland | Decision Context & State | hard runtime | Yes | - |
| 38 | POAV Weights | Decision Context & State | hard runtime (data) | Yes — tracked as runtime data; bounded high-risk enforcement now exists in unified_pipeline | - |
| 39 | Vow System | Decision Context & State | hard runtime | Yes | - |
| 40 | TensionEngine | Decision Context & State | hard runtime | Yes | - |
| 41 | ResistanceVector | Decision Context & State | test-backed | Only with verification | - |
| 42 | Zone Classification | Decision Context & State | runtime-adjacent | Only with verification | - |
| 43 | Store (Redis + FileStore) | Storage & Communication | hard runtime | Yes | - |
| 44 | Perspective Lane | Storage & Communication | hard runtime | Yes (write/read works) | - |
| 45 | Checkpoint Lane | Storage & Communication | hard runtime | Yes (write/read works) | - |
| 46 | Compaction Lane | Storage & Communication | hard runtime | Yes (write/read works) | - |
| 47 | Semantic Field (ts:field) | Storage & Communication | doc-only | No | Theory / Research Lane |
| 48 | Gateway (HTTP) | Storage & Communication | hard runtime | Yes | - |
| 49 | Zone Registry | Storage & Communication | hard runtime | Yes | - |
| 50 | Pub/Sub Events | Storage & Communication | hard runtime | Yes (Redis only) | - |
| 51 | UnifiedPipeline | Unified Pipeline (Full Inference Path) | hard runtime | Yes | - |
| 52 | ToneBridge | Unified Pipeline (Full Inference Path) | runtime-adjacent | Only with verification | - |
| 53 | Trajectory Analysis | Unified Pipeline (Full Inference Path) | runtime-adjacent | Only with verification | - |
| 54 | Semantic Graph | Unified Pipeline (Full Inference Path) | runtime-adjacent | Only with verification | Theory / Research Lane |
| 55 | Perturbation Recovery | Unified Pipeline (Full Inference Path) | runtime-adjacent | Only with verification | - |
| 56 | YuHun Gate | Law/ Terms (HIGH CONFUSION ZONE) | runtime-adjacent | No — concept informs architecture, not a callable runtime object | Active Governance Vocabulary |
| 57 | StepLedger | Law/ Terms (HIGH CONFUSION ZONE) | runtime-adjacent | No — law/ schema exists, runtime equivalent is Aegis chain + session traces | Active Governance Vocabulary |
| 58 | Lex Lattice | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — theoretical framework only | Theory / Research Lane |
| 59 | LAR (Linguistic Accountability Ratio) | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — metric spec only, no runtime calculation | Theory / Research Lane |
| 60 | Isnād | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — consensus protocol design, not implemented | Theory / Research Lane |
| 61 | MDL-Majority | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — theoretical consensus mechanism | Theory / Research Lane |
| 62 | Sovereign Freeze | Law/ Terms (HIGH CONFUSION ZONE) | runtime-adjacent | Only with verification — exists as CollapseException, trigger path via CircuitBreaker | Active Runtime / Audit Dependency |
| 63 | BBPF | Law/ Terms (HIGH CONFUSION ZONE) | runtime-adjacent | Only with verification — spec describes trigger condition, unified_pipeline may wire it | Active Governance Vocabulary |
| 64 | Digital Sovereignty Manifesto | Law/ Terms (HIGH CONFUSION ZONE) | doc-only | No — philosophical declaration, not runtime | Projection / Narrative / Worldview Lane |
| 65 | Honesty Contract (10 Rules) | Law/ Terms (HIGH CONFUSION ZONE) | runtime-adjacent | Only with verification — principles inform benevolence filter | Active Runtime / Audit Dependency |
| 66 | Semantic Spine (12-Layer) | Law/ Terms (HIGH CONFUSION ZONE) | doc-only | No — architectural model, not runtime layers | Theory / Research Lane |
| 67 | Constitution.json | Law/ Terms (HIGH CONFUSION ZONE) | doc-only | No — governance design document | - |
| 68 | Accountability Guild (AGS-1) | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — federated governance proposal | Theory / Research Lane |
| 69 | Haven Nodes | Law/ Terms (HIGH CONFUSION ZONE) | research/theory | No — distributed architecture proposal | Theory / Research Lane |
| 70 | PARADOX_006 (Emergency Override) | Paradoxes & Red Team | test-backed | Yes — canonical governance test case | Active Runtime / Audit Dependency |
| 71 | 7 Paradox Test Cases | Paradoxes & Red Team | test-backed | Yes — governance casebook | - |
| 72 | Red Team Scenarios | Paradoxes & Red Team | test-backed | Yes — adversarial validation | - |
| 73 | Governance Dashboard | Projection & Gamification | projection-only | No — visual projection of governed state | - |
| 74 | World Map / RPG View | Projection & Gamification | projection-only | No — operator-facing visualization | - |
| 75 | VRM 3D Avatar | Projection & Gamification | projection-only | No — aesthetic layer | - |
