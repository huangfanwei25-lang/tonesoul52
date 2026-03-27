# ToneSoul Claim Authority Matrix

> Status: architectural boundary contract
> Purpose: tell later agents, for each major ToneSoul claim or term, what its current authority and implementation status is
> Last Updated: 2026-03-27
> Produced By: Claude Opus (deep scan of 1,755 repo files)
> Scope: 75 terms across AXIOMS, runtime, law/, spec/, tests/, docs/

## How To Use This Document

If you are an AI agent entering this repo:

1. Look up the term you are about to rely on
2. Check the **Status** column
3. If it says `hard runtime` or `test-backed` — you may rely on it for engineering decisions
4. If it says `runtime-adjacent` — verify the integration point before assuming it fires
5. If it says `doc-only`, `research/theory`, or `projection-only` — do not treat it as current runtime truth

## Authority Role Legend

| Role | Meaning |
|------|---------|
| `canonical` | In AXIOMS.json or canonical architecture contracts |
| `runtime` | Wired into tonesoul/ code that executes |
| `operational` | In AI_QUICKSTART / AI_REFERENCE (guide, not constitution) |
| `law` | In law/ directory (governance design, may or may not be implemented) |
| `spec` | In spec/ directory (formal specification) |
| `deep_map` | In ANATOMY or architecture docs (panoramic map) |
| `interpretive` | In narrative/reading docs (meaning layer) |
| `research` | In research/ or theory docs (not current runtime) |
| `projection` | Dashboard/world-map/visual layer |

## Implementation Status Legend

| Status | Meaning | Can an agent rely on it? |
|--------|---------|--------------------------|
| `hard runtime` | Executes in load/commit/process pipeline | Yes |
| `runtime-adjacent` | Code exists, integration varies | Only with verification |
| `test-backed` | Has dedicated tests but integration point unclear | Only with verification |
| `doc-only` | Described in docs, no matching runtime code | No |
| `research/theory` | Theoretical framework, not current dependency | No |
| `projection-only` | Dashboard/visual layer, not governance truth | No |

---

## Matrix: Core Governance (Axioms & Posture)

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 1 | **Axiom 1: Continuity** | canonical | hard runtime | AXIOMS.json, runtime_adapter.py (load/commit), time_island.py | Yes |
| 2 | **Axiom 2: Responsibility Threshold** | canonical | hard runtime | AXIOMS.json, aegis_shield.py (hash chain + sign), runtime_adapter.py (commit) | Yes |
| 3 | **Axiom 3: Governance Gate (POAV ≥ 0.92)** | canonical | hard runtime | AXIOMS.json, time_island.py (POAV weights tracked), yss_gates.py (poav_gate), unified_pipeline.py, test_poav.py, test_unified_pipeline_v2_runtime.py | Yes — bounded runtime gate exists: unified_pipeline enforces ≥ 0.92 on high-risk paths and records baseline POAV on low-risk paths |
| 4 | **Axiom 4: Non-Zero Tension** | canonical | hard runtime | AXIOMS.json, runtime_adapter.py (tension decay never drops to zero), tension_engine.py | Yes |
| 5 | **Axiom 5: Mirror Recursion** | canonical | doc-only | AXIOMS.json | No — no reflection cycle code found |
| 6 | **Axiom 6: User Sovereignty / Harm Block** | canonical | runtime-adjacent | AXIOMS.json, benevolence.py (INTERCEPT/REJECT), resistance.py (CircuitBreaker) | Only with verification — filters exist, enforcement path varies |
| 7 | **Axiom 7: Semantic Field Conservation** | canonical | doc-only | AXIOMS.json | No — conceptual only |
| 8 | **GovernancePosture** | runtime | hard runtime | runtime_adapter.py:44-77 | Yes |
| 9 | **SessionTrace** | runtime | hard runtime | runtime_adapter.py:80-106 | Yes |
| 10 | **Soul Integral (Ψ)** | runtime | hard runtime | runtime_adapter.py:205-215, test_runtime_adapter.py | Yes |
| 11 | **Baseline Drift** | runtime | hard runtime | runtime_adapter.py:176-197, test_runtime_adapter.py | Yes |
| 12 | **Tension Decay** | runtime | hard runtime | runtime_adapter.py:152-168 (alpha=0.05, ~14h half-life) | Yes |
| 13 | **Commit Lock (Mutex)** | runtime | hard runtime | runtime_adapter.py:519+ (30s TTL), store.py COMMIT_LOCK_KEY | Yes |
| 14 | **Agent Footprints** | runtime | hard runtime | runtime_adapter.py:260-286 (last 100 visits) | Yes |
| 15 | **R-Memory Packet** | runtime | hard runtime | runtime_adapter.py:731-893, spec/governance/r_memory_packet_v1.schema.json | Yes |

## Matrix: Defense & Integrity

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 16 | **Aegis Shield** | runtime | hard runtime | aegis_shield.py (3-layer: hash chain + Ed25519 + content filter) | Yes |
| 17 | **Hash Chain** | runtime | hard runtime | aegis_shield.py:78-124 (SHA-256, prev_hash linkage) | Yes |
| 18 | **Ed25519 Signing** | runtime | hard runtime | aegis_shield.py:140-236 (.aegis/keys/) | Yes |
| 19 | **Content Filter (Poison Patterns)** | runtime | hard runtime | aegis_shield.py:251-298 (13 injection patterns) | Yes |
| 20 | **CircuitBreaker / Freeze Protocol** | runtime | runtime-adjacent | resistance.py:30-36 (CollapseException), unified_pipeline.py | Only with verification — code exists, trigger path via unified_pipeline |
| 21 | **PainEngine** | runtime | runtime-adjacent | resistance.py (FrictionCalculator + throttle: temp spike, top-p crash, delay) | Only with verification — test coverage minimal |
| 22 | **FrictionCalculator** | runtime | test-backed | resistance.py:42-60 (tension_delta + wave_distance) | Only with verification |

## Matrix: Monitoring & Quality

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 23 | **TSR (ΔT, ΔS, ΔR)** | runtime, canonical | hard runtime | Multiple files, test_tsr_metrics_comprehensive.py | Yes |
| 24 | **DriftMonitor** | runtime | hard runtime | drift_monitor.py (EMA alpha=0.3, WARNING≥0.35, CRISIS≥0.60) | Yes |
| 25 | **EscapeValve** | runtime | hard runtime | escape_valve.py (max_retries=3, circuit_breaker=5), test_escape_valve.py + red_team | Yes |
| 26 | **BenevolenceFilter** | runtime | hard runtime | benevolence.py (3-layer: attribute + shadow + benevolence audit), test_benevolence.py | Yes |
| 27 | **ContractObserver** | runtime | hard runtime | contract_observer.py (4 output contracts, zone-triggered), unified_pipeline.py (CRITICAL violations block), test_unified_pipeline_v2_runtime.py | Yes — CRITICAL violations block in unified_pipeline; warning-level violations remain observable without blocking |
| 28 | **MultiScaleObserver** | runtime | test-backed | contract_observer.py:237-314 (instant/short/medium trends) | Only with verification |
| 29 | **QualityTracker** | runtime | test-backed | contract_observer.py:328-393 | Only with verification |
| 30 | **LongTermQualityMonitor** | runtime | test-backed | council_capability.py:171-246 (trend detection, degradation alerts) | Only with verification |

## Matrix: Council & Persona

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 31 | **Council (Multi-Persona Deliberation)** | runtime, spec | hard runtime | unified_pipeline.py, 128+ test files, spec/council_spec.md | Yes |
| 32 | **PersonaStack** | runtime | test-backed | test_persona_dimension.py, test_persona_audit.py | Only with verification |
| 33 | **CouncilWeights (Guardian/Analyst/Critic/Advocate)** | runtime | runtime-adjacent | council_capability.py:26-98 (zone threshold adjustment) | Only with verification — weights exist, no voting aggregation |
| 34 | **CapabilityBoundary** | runtime | test-backed | council_capability.py:101-168 (skill coverage → tolerance) | Only with verification |
| 35 | **InterSoul Bridge** | runtime | test-backed | test_inter_soul_bridge.py, test_inter_soul_negotiation.py | Only with verification |
| 36 | **SovereigntyGuard** | runtime | test-backed | test_inter_soul_sovereignty.py (P0 boundary protection) | Only with verification |

## Matrix: Decision Context & State

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 37 | **TimeIsland** | runtime | hard runtime | time_island.py (lifecycle: DRAFT→ACTIVE→COMPLETED→ARCHIVED), test_time_island.py | Yes |
| 38 | **POAV Weights** | runtime | hard runtime (data) | time_island.py:89 (default {P:0.25, O:0.25, A:0.25, V:0.25}), unified_pipeline.py (bounded gate consumes POAV score at inference) | Yes — tracked as runtime data; bounded high-risk enforcement now exists in unified_pipeline |
| 39 | **Vow System** | runtime | hard runtime | test_vow_system.py, test_vow_system_properties.py, runtime_adapter.py (reconcile) | Yes |
| 40 | **TensionEngine** | runtime | hard runtime | tension_engine.py, test_tension_engine.py, test_property_tension_engine.py | Yes |
| 41 | **ResistanceVector** | runtime | test-backed | test_tension_engine.py (fact/logic/ethics weighted sum) | Only with verification |
| 42 | **Zone Classification** | runtime | runtime-adjacent | council_capability.py (safe/transit/risk/danger thresholds), spec/wfgy_semantic_control_spec.md | Only with verification |

## Matrix: Storage & Communication

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 43 | **Store (Redis + FileStore)** | runtime | hard runtime | store.py, backends/redis_store.py, backends/file_store.py | Yes |
| 44 | **Perspective Lane** | runtime | hard runtime | runtime_adapter.py:377-421 (ts:perspectives:*) | Yes (write/read works) |
| 45 | **Checkpoint Lane** | runtime | hard runtime | runtime_adapter.py:424-464 (ts:checkpoints:*) | Yes (write/read works) |
| 46 | **Compaction Lane** | runtime | hard runtime | runtime_adapter.py:467-511 (ts:compacted, limit=20, ttl=7d) | Yes (write/read works) |
| 47 | **Semantic Field (ts:field)** | runtime | doc-only | store.py:37 (key exists), never populated | No |
| 48 | **Gateway (HTTP)** | runtime | hard runtime | scripts/gateway.py, test_gateway_integration.py | Yes |
| 49 | **Zone Registry** | runtime | hard runtime | runtime_adapter.py (rebuilt on commit), ts:zones | Yes |
| 50 | **Pub/Sub Events** | runtime | hard runtime | store.py CHANNEL_EVENTS, ts:events | Yes (Redis only) |

## Matrix: Unified Pipeline (Full Inference Path)

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 51 | **UnifiedPipeline** | runtime | hard runtime | unified_pipeline.py (3000+ lines, wires council+tonebridge+trajectory+drift+escape+benevolence) | Yes |
| 52 | **ToneBridge** | runtime | runtime-adjacent | unified_pipeline.py:224 (lazy-loaded) | Only with verification |
| 53 | **Trajectory Analysis** | runtime | runtime-adjacent | unified_pipeline.py:246 (lazy-loaded) | Only with verification |
| 54 | **Semantic Graph** | runtime | runtime-adjacent | unified_pipeline.py:357 (lazy-loaded) | Only with verification |
| 55 | **Perturbation Recovery** | runtime | runtime-adjacent | unified_pipeline.py:430 (lazy-loaded) | Only with verification |

## Matrix: Law/ Terms (HIGH CONFUSION ZONE)

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 56 | **YuHun Gate** | law | runtime-adjacent | law/governance_core.md, law/yuhun_kernel_trace.md; unified_pipeline.py has governance kernel but no class named "YuHun Gate" | No — concept informs architecture, not a callable runtime object |
| 57 | **StepLedger** | law | runtime-adjacent | law/step_ledger_schema.json (formal JSON schema), unified_pipeline.py (dispatch_trace); Aegis hash chain serves similar role | No — law/ schema exists, runtime equivalent is Aegis chain + session traces |
| 58 | **Lex Lattice** | law, research | research/theory | law/docs/LEX_LATTICE_SPEC.md, law/docs/lex_lattice_mdl_spec.md | No — theoretical framework only |
| 59 | **LAR (Linguistic Accountability Ratio)** | law, research | research/theory | law/docs/LAR_METRIC_SUMMARY.md, law/docs/LAR_CALC_SPEC.md | No — metric spec only, no runtime calculation |
| 60 | **Isnād** | law, research | research/theory | law/docs/ISNAD_CONSENSUS_PROTOCOL.md | No — consensus protocol design, not implemented |
| 61 | **MDL-Majority** | law, research | research/theory | law/docs/ISNAD_CONSENSUS_PROTOCOL.md, law/docs/lex_lattice_mdl_spec.md | No — theoretical consensus mechanism |
| 62 | **Sovereign Freeze** | law, runtime | runtime-adjacent | law/docs/conflict_resolution_protocol.md; resistance.py CollapseException is the runtime equivalent | Only with verification — exists as CollapseException, trigger path via CircuitBreaker |
| 63 | **BBPF** | spec, law | runtime-adjacent | spec/wfgy_semantic_control_spec.md (Bridge Guard), PARADOXES/paradox_006.json | Only with verification — spec describes trigger condition, unified_pipeline may wire it |
| 64 | **Digital Sovereignty Manifesto** | law | doc-only | law/docs/digital_sovereignty_manifesto.md | No — philosophical declaration, not runtime |
| 65 | **Honesty Contract (10 Rules)** | law | runtime-adjacent | law/honesty_contract.md; benevolence.py implements key principles (γ·Honesty > β·Helpfulness) | Only with verification — principles inform benevolence filter |
| 66 | **Semantic Spine (12-Layer)** | law | doc-only | law/semantic_spine_schema.json | No — architectural model, not runtime layers |
| 67 | **Constitution.json** | law | doc-only | law/constitution.json | No — governance design document |
| 68 | **Accountability Guild (AGS-1)** | law, research | research/theory | law/docs/AG_STANDARDS.md | No — federated governance proposal |
| 69 | **Haven Nodes** | law, research | research/theory | law/docs/LAR_CALC_SPEC.md | No — distributed architecture proposal |

## Matrix: Paradoxes & Red Team

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 70 | **PARADOX_006 (Emergency Override)** | canonical | test-backed | PARADOXES/paradox_006.json, test_paradox_council.py | Yes — canonical governance test case |
| 71 | **7 Paradox Test Cases** | canonical | test-backed | PARADOXES/*.json, tests/fixtures/paradoxes/ | Yes — governance casebook |
| 72 | **Red Team Scenarios** | runtime | test-backed | tests/red_team/ (7 files: escape_valve_seed_abuse, etc.) | Yes — adversarial validation |

## Matrix: Projection & Gamification

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 73 | **Governance Dashboard** | projection | projection-only | apps/dashboard/ | No — visual projection of governed state |
| 74 | **World Map / RPG View** | projection | projection-only | apps/world/ | No — operator-facing visualization |
| 75 | **VRM 3D Avatar** | projection | projection-only | apps/dashboard/ (kurisu.vrm) | No — aesthetic layer |

---

## Top 10 Overclaiming Risks

These are the terms most likely to mislead a later AI into thinking something is runtime-hard when it is not:

| Risk | Term | What It Sounds Like | What It Actually Is |
|------|------|---------------------|---------------------|
| 1 | **POAV ≥ 0.92 Gate** | Universal inference-time consensus gate that blocks every major output | A bounded runtime gate now exists in `unified_pipeline.py`: it enforces ≥ 0.92 on `risk` / `danger` / lockdown paths, while low-risk paths remain baseline record-only |
| 2 | **YuHun Gate** | A callable runtime gate object | A governance design concept; runtime equivalent is scattered across unified_pipeline + aegis |
| 3 | **StepLedger** | An active append-only ledger recording every step | Law/ schema exists; runtime equivalent is Aegis chain + session traces, not a dedicated ledger |
| 4 | **Risk (R) calculation** | Active risk scoring that blocks at R > 0.9 | `risk_calculator.py` now computes runtime risk posture and surfaces it through `GovernancePosture` / `r_memory_packet()`, but it is not yet a direct blocking gate |
| 5 | **Lex Lattice** | Active governance framework | Theoretical framework based on MDL/information theory |
| 6 | **LAR metric** | Computed accountability score | Specification only, no runtime calculation |
| 7 | **Mirror Recursion (Axiom 5)** | Automatic self-reflection cycle | No implementation found |
| 8 | **Semantic Field Conservation (Axiom 7)** | Active energy conservation tracking | Conceptual only |
| 9 | **ContractObserver blocking** | Every output-contract violation blocks the response | `unified_pipeline.py` now blocks only `CRITICAL` violations; warning-level issues remain degraded telemetry |
| 10 | **12-Layer Semantic Spine** | 12 active processing layers | Architectural model in law/, not runtime layers |

## Terms Safe For Engineering Reliance

These are confirmed hard runtime, test-backed, and safe to treat as current truth:

- GovernancePosture, SessionTrace, load(), commit()
- Soul Integral, Baseline Drift, Tension Decay
- Aegis Shield (hash chain + Ed25519 + content filter)
- Agent Footprints, Task Locking, Commit Mutex
- DriftMonitor (EMA, WARNING/CRISIS alerts)
- EscapeValve (circuit breaker, graceful degradation)
- BenevolenceFilter (3-layer audit)
- TimeIsland (lifecycle, POAV weights as data)
- Vow System (create/retire/enforce)
- TensionEngine (ResistanceVector, zone classification)
- Store (Redis + FileStore dual-backend)
- Perspective / Checkpoint / Compaction lanes
- Gateway (HTTP), R-Memory Packet
- UnifiedPipeline (full inference path)
- 7 Paradox test cases, Red team scenarios
