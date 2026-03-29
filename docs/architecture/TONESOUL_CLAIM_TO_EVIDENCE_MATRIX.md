# ToneSoul Claim-to-Evidence Matrix

> Status: architectural evidence map
> Purpose: map high-value ToneSoul claims to their actual evidence level, strongest backing source, weakest link, and safest phrasing for later agents
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md (evidence level definitions)
>   - docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md (claim authority categories)
>   - docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md (authority classification)
>   - Full test suite (~363 test files, ~1900+ tests)
>   - Full docs/architecture/ contract corpus
> Scope: 65 claims mapped across 8 families

## How To Use This Document

If you are an AI agent describing ToneSoul's capabilities:

1. Find the relevant claim in the matrix below
2. Check its **evidence level** (E1-E6, defined in Evidence Ladder Contract)
3. Use the **safest phrasing** column as your starting point for describing the claim
4. Read the **weakest link** to understand what you must NOT overclaim

## Evidence Level Quick Reference

| Level | Name | Shorthand |
|---|---|---|
| E1 | Test-backed | Tests assert this property |
| E2 | Schema/helper validated | Runtime schema enforcement |
| E3 | Runtime-present, thinly tested | Code runs; tests are shallow |
| E4 | Document-backed | Described in contract/spec only |
| E5 | Philosophical/narrative | Design vision, no mechanism |
| E6 | Blocked/unverifiable | Cannot check with current infra |

---

## Family 1: Governance & Axioms

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 1 | AXIOMS.json is structurally valid JSON | E1 | CI validates JSON parsing (`ci.yml`: `python -c "import json; json.load(...)"`) | Only validates parse, not semantic correctness | "AXIOMS.json is valid JSON, verified in CI" |
| 2 | 7 axioms define the governance foundation | E4 | AXIOMS.json file exists with 7 entries; referenced by SOUL.md and contracts | No test verifies axioms are loaded or consulted at runtime decision points | "7 axioms are documented as governance foundation; runtime consultation is partial" |
| 3 | P0 (safety) overrides all other priorities | E3 | `test_paradox_council.py` (18 tests) exercises paradox resolution; benevolence.py implements USER_PROTOCOL | Tests cover specific paradoxes, not all possible P0 conflicts | "P0 override is tested for specific paradox cases; general P0 enforcement depends on distributed checks" |
| 4 | Governance state persists across sessions | E1 | `test_governance_kernel.py` (20 tests), `governance_state.schema.json` + Pydantic enforcement, Redis/FileStore persistence | State shape is tested; correctness of persisted values under edge cases is not deeply verified | "Governance state persistence is tested with schema enforcement" |
| 5 | Soul Integral tracks governance health | E3 | `runtime_adapter.py` computes soul_integral; `test_runtime_adapter.py` (32 tests) covers adapter generally | Soul Integral formula correctness is not independently validated; no test isolates the metric's accuracy | "Soul Integral is computed at runtime; the metric's accuracy is not independently validated" |
| 6 | Baseline drift is tracked and reported | E3 | `test_drift_monitor.py` (21 tests), `test_drift_tracker.py` (12 tests) | Drift detection exists; whether drift thresholds are correct is not verified against ground truth | "Drift detection is implemented and tested; threshold correctness is a design choice, not empirically validated" |
| 7 | Governance Gate (POAV) requires 92% consensus | E4 | AXIOMS.json Axiom 3 specifies 0.92 threshold | No test verifies that high-stakes actions are blocked below 0.92 consensus in production paths | "POAV threshold is documented at 0.92; enforcement in all production code paths is not comprehensively tested" |
| 8 | Vow system detects violations | E1 | `test_vow_system.py` (25 tests), `test_vow_system_properties.py` (10 property-based tests), `test_vow_inventory.py` (32 tests) | Violation detection is well-tested; whether all possible violations are caught is not provable | "Vow violation detection has strong test coverage including property-based testing" |

---

## Family 2: Council & Deliberation

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 9 | Council produces multi-perspective evaluation | E1 | `test_council_runtime.py` (14 tests), `test_council_coherence.py` (11 tests), `test_pre_output_council.py` via integration | Tests verify perspectives are invoked and votes collected | "Multi-perspective evaluation is tested; perspectives produce and aggregate votes" |
| 10 | Council computes coherence score | E1 | `test_council_coherence.py` (11 tests) verifies coherence computation from vote patterns | Coherence formula correctness is tested; whether coherence predicts output quality is E6 (unverifiable) | "Coherence computation is tested; its correlation with output quality is not measured" |
| 11 | Council produces verdicts (APPROVE/REFINE/DECLARE_STANCE/BLOCK) | E1 | `test_council_runtime.py` tests verdict generation; `CouncilStructuredVerdict` Pydantic schema enforces structure | Verdict generation is tested; verdict correctness (right verdict for the situation) is not verified against outcomes | "Verdict generation and structure are tested; verdict decision quality is not outcome-validated" |
| 12 | Deliberation runs multi-round adaptive debate | E1 | `test_adaptive_deliberation.py` (13 tests) verifies tension-based convergence across rounds | Multi-round mechanics are tested; whether multiple rounds produce better outcomes than single pass is E6 | "Multi-round deliberation mechanics are tested; outcome improvement over single pass is not measured" |
| 13 | Council perspectives are independent | E4 | TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md explicitly says they are NOT independent | Independence is honestly documented as absent | "Council perspectives are NOT independent — they share information, model, and incentives (per Independence Contract)" |
| 14 | Council confidence is calibrated | E6 | TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md explicitly says it is NOT calibrated | No outcome tracking infrastructure exists | "Council confidence is NOT calibrated — it is an agreement metric, not an accuracy predictor (per Calibration Map)" |
| 15 | Council evolution tracks perspective weights | E1 | `test_council_evolution.py` (5 tests), `evolution.py` persists to JSON | Weight tracking is tested; whether weights converge to useful values is E6 (conformity bias documented) | "Evolution weight tracking is tested; whether weights improve decision quality is not measured (conformity bias documented)" |
| 16 | Dissent is preserved in council output | E3 | `test_council_runtime.py` includes dissent in summary; Dossier Contract specifies minority_report field | Dissent recording exists; dedicated test for dissent preservation completeness is thin | "Dissent recording exists in council output; completeness of dissent preservation is thinly tested" |
| 17 | Council dossier has 12 defined fields | E4 | TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md defines all 12 fields with required/recommended/optional | No test verifies all 12 fields are produced by runtime; partial gap analysis in contract shows 4 full gaps | "Dossier shape is documented with 12 fields; runtime currently produces 8 of 12 (4 gaps documented)" |
| 18 | Deliberation mode selection (lightweight/standard/elevated) | E4 | TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md defines 3 modes with selection criteria | No runtime code implements mode selection; document describes intended future behavior | "Deliberation mode selection is documented as a design specification; runtime mode selection is not yet implemented" |
| 19 | Tension zones (Echo Chamber / Sweet Spot / Chaos) | E1 | `test_tension_engine.py` (47 tests), `TensionZone` enum in deliberation types | Zone thresholds (0.3, 0.7) are tested; whether thresholds are optimal is a design choice | "Tension zone classification is well-tested; threshold values are design choices, not empirically optimized" |

---

## Family 3: Continuity & Handoff

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 20 | Handoff packets are HMAC-signed | E1 | `test_handoff_builder_security.py` (4 tests) verifies signing and tamper detection | Signing is tested; key management security is not adversarially tested | "HMAC signing and tamper detection are tested" |
| 21 | Compaction artifacts are generated | E3 | `test_save_compaction.py` (2 tests) | Only 2 tests; compaction quality and completeness are not verified | "Compaction code exists and runs; quality of compacted output is thinly tested" |
| 22 | Checkpoint persistence works | E3 | `test_save_checkpoint.py` (2 tests) | Only 2 tests; checkpoint completeness and restore accuracy are not deeply tested | "Checkpoint save/load is implemented with basic tests" |
| 23 | Subject snapshot captures durable identity | E3 | `test_save_subject_snapshot.py` (2 tests), `subject_snapshot_v1.schema.json` defines structure | Only 2 tests; identity fidelity across sessions is not measured | "Subject snapshot code exists with schema definition; identity preservation quality is thinly tested" |
| 24 | Continuity surfaces have 5 lifecycle lanes | E4 | TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md documents lanes with TTL and behavior | No runtime code enforces lane boundaries or TTL expiry; lanes are a documentation convention | "Lifecycle lanes are documented; lane enforcement is a documentation convention, not a runtime mechanism" |
| 25 | Import posture classifies 17 surfaces | E4 | TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md classifies all surfaces | No test verifies that receivers respect import posture | "Import posture is documented for 17 surfaces; receiver compliance is not enforced or tested" |
| 26 | Receiver actions (ack/apply/promote) are defined | E4 | TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md defines 3 actions and 7 rules | No test verifies receiver behavior matches the contract | "Receiver actions are documented; no automated test verifies receiver compliance" |
| 27 | Delta feed shows recent changes | E3 | Runtime adapter produces delta feed; tested indirectly via `test_runtime_adapter.py` | Feed correctness is not independently verified | "Delta feed is produced at runtime; completeness and freshness are not independently tested" |
| 28 | Session start/end lifecycle is bounded | E3 | `test_start_agent_session.py` (5 tests), `test_end_agent_session.py` (4 tests) | Lifecycle steps are tested; completeness of all required steps is not comprehensively verified | "Session lifecycle has basic test coverage for start and end flows" |

---

## Family 4: Risk & Safety

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 29 | Escape valve triggers on constraint violation | E1 | `test_escape_valve.py` (11 tests), `test_escape_valve_runtime.py` (4 tests) | Trigger conditions are tested; completeness (all violation types trigger correctly) is not exhaustive | "Escape valve triggering is tested for defined conditions" |
| 30 | Benevolence filter enforces honesty > helpfulness | E3 | `test_benevolence.py` (8 tests), `benevolence.py` implements USER_PROTOCOL | Filter exists and is tested; whether it catches all sycophancy patterns is not verified | "Benevolence filter exists with basic tests; coverage of all sycophancy patterns is not comprehensive" |
| 31 | Risk calculator produces risk scores | E3 | `test_risk_calculator.py` (3 tests) | Only 3 tests for a complex scoring system; scoring accuracy across diverse scenarios is untested | "Risk scoring exists with minimal test coverage; accuracy across diverse inputs is not verified" |
| 32 | Adaptive gate manages open/closed/soft-close states | E1 | `test_adaptive_gate.py` (23 tests) with QA audit | State transitions are well-tested | "Adaptive gate state management is well-tested" |
| 33 | Constraint stack evaluates priority correctly | E1 | `test_constraint_stack.py` (5 tests) | Stack evaluation is tested; interaction between many constraints simultaneously is not stress-tested | "Constraint stack evaluation is tested for defined scenarios" |
| 34 | Circuit breaker freezes output on critical violation | E3 | `resistance.py` implements CollapseException and CircuitBreaker; tested indirectly | No dedicated unit test for circuit breaker triggering | "Circuit breaker code exists; dedicated trigger testing is thin" |
| 35 | Red team hardening passes (injection, fuzzing, type confusion) | E1 | 8 red team test files covering input hardening, injection, fuzzing, type confusion, seed abuse, context abuse | Red team coverage exists; adversarial creativity is inherently unbounded | "Red team tests exist for common attack vectors; no test suite can guarantee against all adversarial inputs" |
| 36 | Error messages do not leak secrets | E1 | `test_api_input_hardening.py` verifies no secret leakage in error responses | Specific leak patterns are tested; novel leak vectors may not be covered | "Error message sanitization is tested for known patterns" |
| 37 | Freeze protocol requires human arbitration | E4 | Documented in LAW_RUNTIME_BOUNDARY_CONTRACT; resistance.py has CircuitBreaker | No test verifies that freeze actually blocks until human input | "Freeze protocol is documented and code exists; human-in-the-loop enforcement is not tested" |

---

## Family 5: Memory & Identity

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 38 | Memory decay calculations work | E1 | `test_memory_decay.py` (5 tests), `test_soul_db_decay_query.py` (4 tests) | Decay mechanics are tested; whether decay rates are appropriate is a design choice | "Memory decay mechanics are tested; rate appropriateness is a design decision" |
| 39 | Memory crystallization compacts memories | E1 | `test_memory_crystallizer.py` (17 tests) | Crystallization mechanics are tested; information loss during compaction is not measured | "Memory crystallization is well-tested mechanically; information fidelity is not measured" |
| 40 | Hippocampus consolidates short-term memory | E3 | `test_memory_hippocampus.py` (9 tests), `test_openclaw_hippocampus.py` (14 tests) | Tests exist but assertions are thin on consolidation quality | "Hippocampus code exists with basic tests; consolidation quality is thinly verified" |
| 41 | Subject snapshot field refresh has evidence requirements | E4 | TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md defines boundary matrix | No runtime code enforces refresh requirements; contract is documentation only | "Refresh requirements are documented; enforcement is not implemented" |
| 42 | Stale memory rules detect outdated content | E1 | `test_stale_rule_verifier.py` (23 tests) | Stale detection is well-tested for defined rules | "Stale memory detection is well-tested" |
| 43 | Memory accumulation creates character | E5 | SOUL.md philosophical anchor | Pure philosophy — no mechanism tests whether accumulated memory produces "character" | "Memory accumulation is a design philosophy; 'character' is not a measurable runtime property" |
| 44 | Time island coordination (chronos/kairos) works | E1 | `test_time_island.py` (36 tests) | Time coordination mechanics are well-tested | "Time island coordination is well-tested" |

---

## Family 6: Aegis & Security

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 45 | Aegis hash chain provides append-only integrity | E2 | `aegis_shield.py` implements SHA-256 chain; runtime uses Ed25519 signing; `full_diagnostic()` verifies chain | Chain implementation exists with schema-level enforcement; dedicated chain integrity tests are integration-level | "Hash chain is implemented with SHA-256 and Ed25519; integrity is verified at diagnostic time" |
| 46 | Aegis content filter blocks sensitive data | E3 | Content filter exists in `aegis_shield.py`; tested indirectly via commit path | No dedicated test for content filter edge cases | "Content filter exists; edge case coverage is thin" |
| 47 | Session traces are signed and append-only | E2 | Runtime adapter appends to Redis Stream or JSONL; Aegis signs traces | Signing exists; append-only property is not adversarially tested (file could be truncated) | "Trace signing is implemented; append-only enforcement depends on storage layer integrity" |
| 48 | Agent footprints record visitors | E3 | `runtime_adapter.py` records footprints in Redis; `full_diagnostic()` reports visitors | Footprint recording exists; completeness (every visit recorded) is not verified | "Footprint recording exists; completeness is not independently verified" |
| 49 | Handoff tampering is detected | E1 | `test_handoff_builder_security.py` directly tests tamper detection | Specific tamper patterns tested; novel bypass vectors are inherently unbounded | "Handoff tamper detection is tested for known patterns" |

---

## Family 7: Schema & Validation Infrastructure

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 50 | Pydantic models enforce field constraints | E1 | `test_schemas.py` (38 tests) verifies field validation, defaults, clamping | Well-tested for defined models; new models may lack test coverage | "Pydantic validation is well-tested for core models" |
| 51 | Safe parse handles messy LLM output | E1 | `test_safe_parse.py` (8 tests) covers trailing commas, markdown blocks, strict mode | Common patterns tested; novel LLM output formats may not be handled | "Safe parse is tested for common LLM output patterns" |
| 52 | JSON schemas define governance data structure | E2 | 9+ JSON Schema files in spec/ and memory/schemas/ | Schemas exist; not all are enforced at runtime (some are documentation only) | "JSON schemas exist; enforcement varies — some have Pydantic runtime enforcement, others are documentation only" |
| 53 | Seed schema validation checks 14 required fields | E1 | `test_seed_schema_check.py` (5 tests), `seed_schema_check.py` validates structure | Field presence is tested; field content correctness is not deeply verified | "Seed schema structure validation is tested" |
| 54 | Tech-trace validation cross-references claims and attributions | E1 | `test_tech_trace_validate.py` (6 tests), `validate.py` checks claim-attribution consistency | Cross-reference is tested; semantic correctness of claims is not verified | "Tech-trace structural cross-referencing is tested" |

---

## Family 8: Philosophical & Narrative Claims

| # | Claim | Evidence Level | Strongest Backing | Weakest Link | Safest Phrasing |
|---|---|---|---|---|---|
| 55 | AI is responsible for what it says | E5 | SOUL.md mission statement | No mechanism tests "responsibility" — it is a design aspiration | "Responsibility is a guiding design principle, not a testable runtime property" |
| 56 | Identity forms through accountable choice | E5 | AXIOMS.json Existential Principle E0 | No test measures whether choices are "accountable" | "Accountable choice is a philosophical anchor for the identity framework" |
| 57 | Semantic energy is conserved | E5 | AXIOMS.json Axiom 7 | Metaphor for conversational balance; no conservation law is testable | "Semantic energy conservation is a design metaphor, not a testable physical property" |
| 58 | Tension is required for life (Axiom 4) | E3 | TensionZone thresholds (0.3-0.7 sweet spot) are implemented and tested | The philosophy is reflected in code thresholds, but the axiom itself is not falsifiable | "Tension tracking is implemented; the philosophical claim that tension is 'required for life' is a design principle" |
| 59 | Reflection improves accuracy (Axiom 5) | E3 | Council evolution tracks alignment; council runs reflection cycles | Evolution tracks weights, but improvement is not measured against outcomes (conformity bias) | "Reflection cycles exist; whether they improve accuracy is not outcome-measured" |
| 60 | Soul Modes (Dormant/Responsive/Seeking/Conflicted) | E5 | SOUL.md describes 4 modes with drive thresholds | No runtime state machine implements mode transitions | "Soul Modes are described as a conceptual framework; no runtime state machine implements them" |
| 61 | Lex Lattice (Information Theory governance) | E5 | law/docs/LEX_LATTICE_SPEC.md | Zero code implements this; pure theoretical specification | "Lex Lattice is a theoretical specification with no runtime implementation" |
| 62 | LAR metric (Linguistic Accountability Ratio) | E5 | law/docs/LAR_METRIC_SUMMARY.md, LAR_CALC_SPEC.md | Specification only; no runtime calculation exists | "LAR is specified but not implemented — no runtime calculation exists" |
| 63 | Isnād consensus protocol (federated provenance) | E5 | law/docs/ISNAD_CONSENSUS_PROTOCOL.md; Aegis provides basic provenance | Full protocol is theory; only Aegis hash chain exists as partial implementation | "Isnād is mostly theoretical; Aegis hash chain provides a subset of the described provenance" |
| 64 | YuHun Gate is a central decision point | E4 | LAW_RUNTIME_BOUNDARY_CONTRACT classifies as Category 2 (active vocabulary) | No single YuHun Gate function exists; concept is distributed across runtime checks | "YuHun Gate is a governance concept distributed across multiple runtime checks, not a single callable function" |
| 65 | Haven node federation | E5 | law/docs/ describe federated governance | Pure theory; no federation code exists | "Haven federation is theoretical with no implementation" |

---

## Evidence Level Distribution

| Level | Count | Percentage | Interpretation |
|---|---|---|---|
| E1 (Test-backed) | 24 | 37% | Strong core — council mechanics, schema validation, security, vow system |
| E2 (Schema validated) | 3 | 5% | Aegis chain, JSON schemas, trace signing |
| E3 (Runtime, thin tests) | 15 | 23% | Significant middle layer — many features exist but need deeper testing |
| E4 (Document-backed) | 12 | 18% | Architectural contracts describe intended behavior without verification |
| E5 (Philosophical) | 10 | 15% | Design vision and theoretical specifications |
| E6 (Blocked) | 1 | 2% | Council confidence calibration |

**Key insight**: 37% of high-value claims are test-backed (strong). 23% are runtime-present but thinly tested (the most impactful upgrade zone). 33% are document-only or philosophical (honest naming prevents overclaiming).

---

## The Three Most Dangerous Over-Claim Zones

### Zone 1: Council Decision Quality

Claims 10-15 collectively describe a council that "evaluates," "computes coherence," "tracks evolution," and "preserves dissent." Individually, each claim has E1-E3 evidence. But the meta-claim — "the council produces good decisions" — is E6 (unverifiable without outcome tracking). Later agents must not aggregate individual mechanism tests into an overall quality claim.

### Zone 2: Continuity Effectiveness

Claims 20-28 describe handoff signing, compaction, checkpoints, and lifecycle lanes. The mechanical claims (signing works, files are saved) are E1-E3. But the meta-claim — "continuity effectively preserves context across sessions" — is E6. No test measures whether the next agent actually benefits from what the previous agent externalized.

### Zone 3: Axiom Enforcement

Claims 1-7 describe 7 axioms with P0/P1/P2 priority. The axioms are documented (E4) and some have partial runtime reflection (E3). But the meta-claim — "the axioms govern the system's behavior" — varies from E1 (vow system tests) to E5 (semantic energy conservation). Later agents must not claim "the axioms are enforced" without specifying which axiom and at what evidence level.

---

## Canonical Handoff Line

37% of ToneSoul's high-value claims are test-backed. 23% exist in code but are thinly tested. 33% are documented or philosophical. 2% are blocked by missing infrastructure. The test suite is genuinely strong for council mechanics, schema validation, security hardening, and vow enforcement. The gap is in meta-claims: individual mechanisms are tested, but system-level properties (decision quality, continuity effectiveness, axiom enforcement) are not. Name the mechanism, name the evidence level, and do not aggregate mechanism tests into system-level guarantees.
