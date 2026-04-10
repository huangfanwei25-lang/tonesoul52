# ToneSoul Test And Validation Topology Map

> Status: architectural topology document
> Purpose: organize the repo's validation surfaces into lanes, describe what confidence each lane actually buys, what it still does not prove, and the most dangerous false inference later agents might make
> Last Updated: 2026-04-09
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md (evidence levels)
>   - docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md (claim-level evidence mapping)
>   - Full test suite (~363 files, ~1900+ tests, 65K+ lines)
>   - pytest.ini, conftest.py, .github/workflows/
> Scope: 7 validation lanes, ~363 test files mapped

## How To Use This Document

If you are deciding whether to trust a ToneSoul claim:

1. Find which **validation lane** covers the claim
2. Read what **confidence that lane buys** — this is what you can trust
3. Read what **it still does not prove** — this is where overclaiming starts
4. Read the **dangerous false inference** — this is the specific mistake to avoid

---

## Validation Infrastructure Overview

| Component | Details |
|---|---|
| Test framework | pytest with asyncio support (`asyncio_mode = auto`) |
| Test files | ~363 in `tests/`, 8 in `tests/red_team/` |
| Test functions | ~1,900+ |
| Test code | ~65,000+ lines |
| CI workflows | `test.yml` (`ToneSoul CI`, automatic mainline); `pytest-ci.yml` (`Pytest CI (Manual Focused Rerun)`, manual Python-only rerun); `ci.yml` (`CI (Legacy Manual Replay)`, manual legacy replay/comparison lane) |
| Fixtures | `_isolate_soul_db` (temp SoulDB), `qa_sandbox` (isolated env), `workspace_tmpdir` |
| Key techniques | monkeypatching, property-based testing, red team fuzzing |

---

## Seven Validation Lanes

### Lane 1: Critical Runtime Protections

**What is in this lane**: tests that verify safety-critical mechanisms — the things that must not break because failure means unsafe output.

**Representative tests**:
- `test_vow_system.py` (25 tests) — vow violation detection
- `test_vow_system_properties.py` (10 tests) — property-based vow testing
- `test_adaptive_gate.py` (23 tests) — gate state transitions with QA audit
- `test_escape_valve.py` (11 tests) + `test_escape_valve_runtime.py` (4 tests)
- `test_constraint_stack.py` (5 tests) — priority evaluation
- `test_security_governance_bypass.py` (6 tests) — governance cannot be bypassed
- `test_security_llm_boundary.py` (6 tests) — LLM boundary enforcement
- `test_security_memory_boundary.py` (6 tests) — memory access boundaries
- `test_benevolence.py` (8 tests) — honesty > helpfulness filter
- `test_resistance.py` (34 tests) — tension resistance and pressure dynamics
- Red team suite (8 files) — injection, fuzzing, type confusion, abuse

**Approximate coverage**: ~170 tests across ~30 files

**What confidence this lane buys**:
- Vow violations are detected for defined vow types
- Gate states transition correctly under known conditions
- Escape valve triggers when configured conditions are met
- Known attack vectors (injection, fuzzing, type confusion) are handled
- Error messages do not leak internal state
- Memory and LLM boundaries are enforced

**What it still does not prove**:
- That all possible violations are caught (coverage is for defined patterns)
- That the vow definitions themselves are correct (tests verify mechanism, not policy)
- That novel attack vectors are handled (adversarial creativity is unbounded)
- That safety holds under combinations of concurrent violations
- That the benevolence filter catches all sycophancy patterns

**Most dangerous false inference**: "ToneSoul has comprehensive safety testing" → "ToneSoul is safe." Safety tests verify known mechanisms against known patterns. They cannot guarantee safety against unknown patterns or emergent interactions.

---

### Lane 2: Council & Deliberation Mechanics

**What is in this lane**: tests that verify the council runs correctly — perspectives vote, coherence is computed, verdicts are generated, tension is tracked.

**Representative tests**:
- `test_council_runtime.py` (14 tests) — genesis fields, role summaries, multi-agent contracts
- `test_council_coherence.py` (11 tests) — coherence computation from votes
- `test_council_evolution.py` (5 tests) — weight tracking and alignment
- `test_adaptive_deliberation.py` (13 tests) — multi-round tension-based convergence
- `test_deliberation_engine.py` (3 tests) — sync/async mechanics
- `test_deliberation_gravity.py` (11 tests) — synthesis and aggregation
- `test_council_capability.py` (17 tests) — capabilities and permissions
- `test_paradox_council.py` (18 tests) — paradox handling
- `test_custom_role_council.py` (19 tests) — custom role definitions
- `test_tension_engine.py` (47 tests) — tension computation and resolution
- `test_integration_deliberation_council.py` (6 tests) — council integration

**Approximate coverage**: ~170 tests across ~15 files

**What confidence this lane buys**:
- Council perspectives are invoked and produce votes
- Coherence is computed from vote patterns using a defined formula
- Verdicts are generated from coherence and vote patterns
- Multi-round deliberation converges based on tension tracking
- Tension zones (Echo Chamber / Sweet Spot / Chaos) are correctly classified
- Paradox resolution works for defined paradox cases

**What it still does not prove**:
- That council decisions are good (mechanism correctness ≠ decision quality)
- That coherence predicts output quality (coherence is an agreement metric, not accuracy)
- That evolution weights improve over time (conformity bias documented)
- That multi-round deliberation produces better outcomes than single-pass
- That dissent is always captured completely
- That deliberation mode selection works (not yet implemented)

**Most dangerous false inference**: "The council has 170+ tests" → "Council decisions are validated." Tests verify the council *runs correctly*. They do not verify the council *decides correctly*. Running correctly is necessary but not sufficient for good decisions.

---

### Lane 3: Memory, Subject, & Handoff

**What is in this lane**: tests that verify memory storage, decay, crystallization, handoff signing, and subject snapshot management.

**Representative tests**:
- `test_memory_crystallizer.py` (17 tests) — crystallization mechanics
- `test_memory_manager.py` (15 tests) — lifecycle management
- `test_memory_hippocampus.py` (9 tests) — consolidation
- `test_memory_decay.py` (5 tests) — decay calculations
- `test_stale_rule_verifier.py` (23 tests) — stale content detection
- `test_time_island.py` (36 tests) — chronos/kairos coordination
- `test_handoff_builder_security.py` (4 tests) — HMAC signing and tamper detection
- `test_handoff_ingester.py` (3 tests) — JSON/Markdown ingestion
- `test_save_subject_snapshot.py` (2 tests) — snapshot persistence
- `test_save_compaction.py` (2 tests) — compaction generation
- `test_save_checkpoint.py` (2 tests) — checkpoint saving
- `test_soul_db_decay_query.py` (4 tests) — decay queries
- `test_scribe_engine.py` (18 tests) — narrative journaling

**Approximate coverage**: ~150 tests across ~20 files

**What confidence this lane buys**:
- Memory crystallization produces compact artifacts
- Decay calculations follow defined formulas
- Stale content is detected by rule-based checks
- Time island coordination (chronos/kairos) works
- Handoff packets are signed and tamper-detectable
- Subject snapshots can be saved and loaded

**What it still does not prove**:
- That crystallized memories preserve the right information (information fidelity)
- That compactions are complete and useful to the next agent
- That handoff actually improves next-session quality
- That subject snapshot captures meaningful identity (2 tests is thin)
- That continuity lanes and import postures are enforced (document-backed only)

**Most dangerous false inference**: "Handoff is tested" → "Context is preserved across sessions." Handoff *signing and format* are tested. Whether the handoff *content* actually helps the receiving agent is not measured.

---

### Lane 4: Governance, Runtime, & Audit

**What is in this lane**: tests that verify agent lifecycle, governance kernel, commit attribution, observability, and verification hygiene.

**Representative tests**:
- `test_governance_kernel.py` (20 tests) — core governance
- `test_contract_observer.py` (20 tests) — contract observation
- `test_contract_observer_properties.py` (15 tests) — contract property verification
- `test_drift_monitor.py` (21 tests) — drift detection
- `test_persona_dimension.py` (21 tests) — persona tracking
- `test_observability.py` (17 tests) — tracing
- `test_intent_verification.py` (14 tests) — intent capture
- `test_verify_docs_consistency.py` (16 tests) — doc consistency
- `test_verify_dual_track_boundary.py` (14 tests) — execution boundaries
- `test_start_agent_session.py` (5 tests), `test_end_agent_session.py` (4 tests)
- `test_verify_7d.py` (11 tests) — 7-day audit cycle
- Verification/hygiene suite (~28 files, ~180 tests)

**Approximate coverage**: ~350 tests across ~50 files

**What confidence this lane buys**:
- Governance kernel loads and enforces basic rules
- Contracts are observed and violations are flagged
- Drift from baseline is detected and tracked
- Session lifecycle (start/end) follows defined steps
- Documentation consistency is verified
- Architectural layer boundaries are respected
- 7-day audit cycle is enforced
- Commit attribution is correct

**What it still does not prove**:
- That governance actually prevents bad outcomes (governance runs, but effectiveness is unmeasured)
- That drift thresholds are appropriate (thresholds are design choices)
- That contract observation catches all violations (coverage depends on contract completeness)
- That audit cycle frequency is sufficient

**Most dangerous false inference**: "Governance has 350 tests" → "The system is well-governed." Tests verify governance *mechanisms*. They do not verify governance *effectiveness*. A governance system that always runs but never catches a real problem is not effective governance.

---

### Lane 5: Schema & Data Validation

**What is in this lane**: tests that verify data structures are valid — Pydantic models, JSON schema enforcement, safe parsing.

**Representative tests**:
- `test_schemas.py` (38 tests) — Pydantic model validation, defaults, clamping
- `test_safe_parse.py` (8 tests) — LLM output parsing
- `test_seed_schema_check.py` (5 tests) — seed structure validation
- `test_tech_trace_validate.py` (6 tests) — trace format compliance
- `test_corpus_schema.py` (2 tests) — corpus data shape

**Approximate coverage**: ~60 tests across ~10 files

**What confidence this lane buys**:
- Core data models (ToneAnalysisResult, CouncilStructuredVerdict, GovernanceDecision) reject invalid structure
- Field values are clamped to valid ranges (0.0-1.0)
- LLM output with trailing commas, markdown blocks, and whitespace is parsed safely
- Seed payloads have all required fields
- Tech-trace claims and attributions cross-reference correctly

**What it still does not prove**:
- That valid-shaped data is semantically correct (schema validates form, not meaning)
- That all code paths produce schema-valid output (validation runs at consumption, not always at production)
- That schemas themselves are correct definitions of what data should look like

**Most dangerous false inference**: "Data is validated by Pydantic" → "Data is correct." Pydantic validates that a field named `confidence` contains a float between 0.0 and 1.0. It does not validate that the confidence value is meaningful or accurate.

---

### Lane 6: Integration & End-to-End

**What is in this lane**: tests that verify multi-component interactions — full pipeline runs, API endpoint integration, memory-council-reflection flows.

**Representative tests**:
- `test_unified_pipeline_v2_runtime.py` (21 tests) — full pipeline execution
- `test_end_to_end_pipeline.py` (6 tests) — end-to-end workflow
- `test_integration_deliberation_council.py` (6 tests) — council integration
- `test_integration_memory_lifecycle.py` (7 tests) — memory lifecycle
- `test_integration_tonebridge_pipeline.py` (6 tests) — tonebridge session
- `test_genesis_integration.py` (7 tests) — genesis field integration
- `test_orchestrator_integration.py` (7 tests) — orchestrator coordination
- `test_api_phase_a_security.py` (11 tests) — API security
- `test_api_phase_b_pipeline.py` (4 tests) — API pipeline
- `test_api_chat_council_mode.py` (19 tests) — API council mode
- `test_simulation.py` (13,983 lines) — multi-scenario simulation framework

**Approximate coverage**: ~100 tests across ~15 files

**What confidence this lane buys**:
- The pipeline runs end-to-end without crashing
- Components integrate without obvious data format mismatches
- API endpoints handle requests and produce responses
- Multi-component flows (memory → council → reflection) complete successfully

**What it still does not prove**:
- That end-to-end output quality is good (tests verify completion, not quality)
- That the pipeline handles all real-world input distributions
- That component interactions are correct under all orderings and concurrent scenarios
- That production-scale performance is acceptable

**Most dangerous false inference**: "End-to-end tests pass" → "The system works correctly in production." E2E tests verify that the pipeline completes. They do not measure output quality, real-world robustness, or production-scale behavior.

---

### Lane 7: Narrative & Doctrine Without Direct Verification

**What is in this lane**: claims that exist only in documentation — architectural contracts, philosophical statements, design visions, theoretical specifications. No test file directly verifies these claims.

**Representative documents** (not test files):
- SOUL.md — mission, identity, philosophical anchors, soul modes
- AXIOMS.json — 7 axioms (some reflected in code, some purely philosophical)
- law/docs/ — Lex Lattice, LAR, Isnād, Haven federation (all theory)
- docs/architecture/ contracts — lifecycle lanes, import posture, receiver rules, prompt topology, adoption waves, deliberation modes, confidence posture derivation
- spec/council_spec.md — role definitions and deliberation flow description

**Approximate test coverage**: zero dedicated tests for the claims in these documents

**What confidence this lane buys**:
- The documents exist, are well-structured, and are internally consistent
- They provide a useful conceptual framework for understanding the system
- They name limitations honestly (council independence, confidence calibration)

**What it still does not prove**:
- That the described behavior occurs at runtime
- That the documented rules are followed by code
- That the philosophical framework produces better outcomes than alternatives
- That theoretical specifications will ever be implemented

**Most dangerous false inference**: "The architecture is well-documented" → "The architecture is implemented and enforced." Documentation describes intent. The gap between documented intent and runtime behavior can be large — and documentation quality can mask that gap. The better-written the document, the more tempting it is to treat it as evidence.

---

## Lane Summary Table

| Lane | Focus | Test Count | Evidence Level | Primary Value | Primary Gap |
|---|---|---|---|---|---|
| 1. Critical Runtime Protections | Safety mechanisms | ~170 | E1 | Known-pattern safety coverage | Novel/combined attack vectors |
| 2. Council & Deliberation | Decision mechanics | ~170 | E1-E3 | Mechanical correctness | Decision quality (E6) |
| 3. Memory, Subject, Handoff | Continuity mechanisms | ~150 | E1-E3 | Storage/retrieval correctness | Continuity effectiveness (E6) |
| 4. Governance, Runtime, Audit | System governance | ~350 | E1-E3 | Mechanism operation | Governance effectiveness (E6) |
| 5. Schema & Data | Data structure | ~60 | E1-E2 | Structural validity | Semantic correctness |
| 6. Integration & E2E | Multi-component | ~100 | E1-E3 | Pipeline completion | Output quality (E6) |
| 7. Narrative & Doctrine | Documentation | 0 | E4-E5 | Conceptual framework | Everything — no verification |

---

## Visual Topology

```
Verification Strength:
  Strong (E1)              Medium (E2-E3)           Weak/None (E4-E6)
  │                        │                        │
  ├── Vow system (25+)     ├── Risk calc (3)        ├── Lifecycle lanes
  ├── Adaptive gate (23)   ├── Subject snapshot (2)  ├── Import posture
  ├── Tension engine (47)  ├── Compaction (2)        ├── Receiver rules
  ├── Schemas (38)         ├── Checkpoint (2)        ├── Dossier shape
  ├── Council coherence    ├── Session lifecycle     ├── Mode selection
  ├── Council runtime      ├── Hippocampus (9)       ├── Soul Modes
  ├── Time islands (36)    ├── Router (2)            ├── Lex Lattice
  ├── Crystallizer (17)    ├── Content filter        ├── LAR metric
  ├── Stale rules (23)     ├── Agent integrity (2)   ├── Isnād protocol
  ├── Red team (8 files)   ├── Drift detection       ├── Haven federation
  ├── Handoff HMAC (4)     ├── Benevolence (8)       ├── Axiom enforcement
  ├── Escape valve (15)    ├── Evolution (5)         ├── Confidence posture
  ├── Safe parse (8)       ├── Delta feed            ├── Prompt topology
  │                        │                        │
  ~450 tests               ~350 tests               0 tests
```

---

## The Meta-Gap: Mechanism Tests vs System-Property Claims

The most important finding in this topology is:

**ToneSoul's tests verify mechanisms. ToneSoul's documents claim system properties.**

- "Coherence is computed correctly" (mechanism, E1) ≠ "The council makes good decisions" (system property, E6)
- "Handoff packets are signed" (mechanism, E1) ≠ "Context is preserved across sessions" (system property, E6)
- "Vow violations are detected" (mechanism, E1) ≠ "The system is safe" (system property, E6)

Mechanism verification is necessary but not sufficient for system-property claims. The gap between "mechanisms work" and "the system works" is where overclaiming lives.

Later agents should always specify whether they are making a mechanism claim (testable, often E1) or a system-property claim (usually E6). Mechanism claims with E1 evidence are trustworthy. System-property claims assembled from mechanism tests are not — they require outcome-level evidence that does not yet exist.

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md` | Defines the E1-E6 levels used in this map |
| `TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md` | Maps individual claims; this document maps validation surfaces |
| `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` | Council claims in Lane 2 are contextualized by independence assessment |
| `TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md` | Confidence claims in Lane 2 are contextualized by calibration assessment |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Lane 7 illustrates what "narrative coherence is not evidence" means in practice |

---

## Canonical Handoff Line

ToneSoul has ~1,900 tests across 7 validation lanes. The strongest lanes (safety mechanisms, council mechanics, schema validation) provide genuine E1 regression protection for defined mechanisms. The weakest lane (narrative and doctrine) has zero tests and describes intent rather than reality. The critical gap is not in any single lane — it is in the space between mechanism verification and system-property claims. Tests prove mechanisms work. Documents claim the system works. The distance between these two is where honest description begins and overclaiming ends.
