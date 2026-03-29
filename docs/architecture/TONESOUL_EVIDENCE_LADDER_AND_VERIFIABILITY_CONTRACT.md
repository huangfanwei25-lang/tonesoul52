# ToneSoul Evidence Ladder And Verifiability Contract

> Status: architectural honesty contract
> Purpose: define a small number of evidence levels that classify how strongly each ToneSoul claim is backed, what language is honest at each level, and what upgrade would move a claim higher
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md (applies these levels)
>   - docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md (organizes validation surfaces)
>   - docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md (council evidence posture)
>   - docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md (confidence evidence posture)
>   - docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md (claim authority categories)
> Scope: 6 evidence levels, 6 overclaiming patterns, upgrade paths for each level

## How To Use This Document

If you are an AI agent describing what ToneSoul can do, or deciding how much to trust a claim about ToneSoul:

1. Find the claim's **evidence level** in the Claim-to-Evidence Matrix
2. Use this document to understand what that level means
3. Use the **honest language** column to phrase your description
4. Check the **overclaiming patterns** to avoid common inflation

## Why This Document Exists

ToneSoul has a large codebase, extensive documentation, a live test suite, and many architectural contracts. These are different kinds of evidence, but they are easy to conflate. A claim that has a well-written document, a schema definition, AND a passing test suite is much stronger than a claim that only has a well-written document. But all three look equally authoritative when quoted in prose.

This contract defines a ladder of evidence strength so that later agents can distinguish between "this is tested" and "this is described" without collapsing everything into one generic "supported" category.

## Compressed Thesis

Authority and evidence are different axes. A claim can have high authority (it is in AXIOMS.json, it governs the system) but low evidence (no test verifies it actually works). A claim can have low authority (it is a helper function) but high evidence (it has 20 passing tests). Later agents must report both axes honestly. A well-written contract is not a test. A passing test is not production validation. A philosophy is not a mechanism. Name the level. Use the right words.

---

## The Six Evidence Levels

### Level E1: Test-Backed

**Definition**: the claim is directly verified by one or more automated tests that assert the claimed property. The test runs in CI, fails if the property breaks, and has been passing.

**What this means**: if the claimed behavior broke, a test would fail. The claim is protected by automated regression.

**Examples in ToneSoul**:
- Pydantic schema validation (30+ models with field validators, tested in `test_schemas.py`)
- Handoff packet HMAC signing and tamper detection (`test_handoff_builder_security.py`)
- Escape valve triggering conditions (`test_escape_valve.py`, 11 tests)
- Vow system violation detection (`test_vow_system.py`, 25 tests)
- Adaptive gate state transitions (`test_adaptive_gate.py`, 23 tests)
- Council coherence computation (`test_council_coherence.py`, 11 tests)
- Safe JSON parsing from LLM output (`test_safe_parse.py`, 8 tests)
- Red team input hardening (`test_api_input_hardening.py`)
- Memory decay calculations (`test_memory_decay.py`)
- Constraint stack evaluation (`test_constraint_stack.py`)

**Honest language at this level**:
- "X is tested and protected by automated regression"
- "X has N passing tests that verify [specific property]"
- "If X broke, CI would catch it"

**What this level does NOT prove**:
- That the tests cover all edge cases
- That the tests match real-world conditions
- That the tested behavior is correct (tests verify implementation, not specification correctness)
- That the feature works in production at scale

### Level E2: Schema / Helper Validated

**Definition**: the claim is enforced by schema validation (Pydantic models, JSON Schema) or helper-level validation code that runs at runtime but may not have deep dedicated test coverage for all edge cases.

**What this means**: invalid data would be rejected at runtime. The structural shape of the claim is enforced. But the semantic correctness of the data within the valid shape may not be verified.

**Examples in ToneSoul**:
- Governance state schema (`governance_state.schema.json` + Pydantic)
- Session trace schema (`session_trace.schema.json` + Pydantic)
- Council verdict structure (`CouncilStructuredVerdict` Pydantic model)
- Tool response envelope (`tool_response.schema.json`)
- Subject snapshot structure (`subject_snapshot_v1.schema.json`)
- Seed schema validation (`seed_schema_check.py`, 14 required fields)
- Tech-trace payload validation (`validate.py`, claim-attribution cross-reference)
- YSS gates validation (context linting, time island validation)
- Skill registry verification (pattern, semver, SHA256 checks)

**Honest language at this level**:
- "X has schema enforcement that rejects invalid structure"
- "X is structurally validated at runtime"
- "The data shape is enforced; semantic correctness depends on the producer"

**What this level does NOT prove**:
- That semantically correct data is produced (schema validates shape, not meaning)
- That all code paths produce valid data (validation runs on consumption, not always on production)
- That the schema itself is correct (the schema is a human design artifact)

**Common overclaiming**: "X is validated" (sounds like full verification, but schema validation only checks structure)

### Level E3: Runtime-Present But Thinly Tested

**Definition**: the code path exists and is reachable at runtime. It may have a few tests, but the tests are shallow (e.g., "does it not crash?" rather than "does it produce the correct output for known inputs?"). Or the feature is tested indirectly through integration tests without dedicated unit coverage.

**What this means**: the feature exists and runs. If you call it, something happens. But the "something" may not be deeply verified.

**Examples in ToneSoul**:
- Council evolution weight tracking (`test_council_evolution.py` — 5 tests, mostly happy path)
- Risk calculator scoring (`test_risk_calculator.py` — 3 tests for a complex scoring system)
- Subject snapshot save/load (`test_save_subject_snapshot.py` — 2 tests)
- Checkpoint persistence (`test_save_checkpoint.py` — 2 tests)
- Compaction artifact generation (`test_save_compaction.py` — 2 tests)
- Deliberation engine sync/async (`test_deliberation_engine.py` — 3 tests)
- Router mechanism (`test_router.py` — 2 tests)
- Agent integrity check (`test_check_agent_integrity.py` — 2 tests)
- Session start/end lifecycle (`test_start_agent_session.py` — 5 tests, `test_end_agent_session.py` — 4 tests)
- Memory hippocampus consolidation (`test_memory_hippocampus.py` — 9 tests but thin assertions)

**Honest language at this level**:
- "X exists in the codebase and runs without error"
- "X has basic test coverage; edge cases are not deeply verified"
- "The code path is exercised but correctness is not comprehensively tested"

**What this level does NOT prove**:
- That the feature handles edge cases correctly
- That the feature produces semantically correct results under adversarial or unusual inputs
- That the feature's behavior matches its documentation

**Common overclaiming**: "X is implemented and tested" (sounds like thorough verification, but 2-3 tests for a complex system is thin)

### Level E4: Document-Backed

**Definition**: the claim is described in an architectural contract, spec document, or design document. The document may reference specific code paths. But no automated test directly verifies the claimed property.

**What this means**: someone (human or AI) wrote a careful description of what the system should do or how it should behave. The description may be accurate. It may also be aspirational, outdated, or disconnected from what the code actually does.

**Examples in ToneSoul**:
- Continuity lifecycle lanes (5 lanes with TTL, refresh, decay — documented in Lifecycle Map, no test verifies lane boundaries)
- Import posture classifications (directly_importable / advisory / ephemeral — documented in Import Contract, no test verifies receiver behavior)
- Receiver interpretation rules (ack / apply / promote — documented in Receiver Contract, no test enforces)
- Council dossier 12-field shape (documented in Dossier Contract, no test verifies all 12 fields are produced)
- Deliberation mode selection criteria (documented in Adaptive Deliberation Contract, no test verifies mode selection logic)
- Prompt discipline skeleton (10-section structure — documented, no test verifies prompt conformance)
- Prompt surface adoption waves (documented in Adoption Matrix, describes future work)
- Confidence posture derivation rules (documented in Calibration Map, no test verifies threshold logic)
- Silent-override hazards (documented in Receiver Contract, no test detects silent promotion)
- Evolution suppression / conformity bias (documented in Independence Contract, no test detects bias)

**Honest language at this level**:
- "X is documented as a design intention"
- "The architecture describes X; implementation may vary"
- "X is specified in [document]; no automated test verifies this property"

**What this level does NOT prove**:
- That the code implements what the document describes
- That the document is up-to-date with the current codebase
- That the described behavior actually occurs at runtime

**Common overclaiming**: "X is enforced" or "X is guaranteed" (documents describe intent, not enforcement)

### Level E5: Philosophical / Narrative Only

**Definition**: the claim is part of ToneSoul's philosophical framework, identity narrative, or design vision. It may be deeply meaningful as a guiding principle but has no direct mechanism, code path, or test that implements or verifies it.

**What this means**: the claim describes what ToneSoul aspires to be or how it frames its purpose. It is a design compass, not a runtime property.

**Examples in ToneSoul**:
- "AI is responsible for what it says" (SOUL.md mission — guiding philosophy, not a testable mechanism)
- "Identity forms through accountable choice under conflict" (AXIOMS.json E0 — existential principle, not a runtime assertion)
- "Memory accumulation creates character" (SOUL.md — philosophical anchor)
- "Internal drive enables agency" (SOUL.md — I_drive vector is described but not mechanically enforced)
- "Semantic energy is conserved" (Axiom 7 — metaphor for conversational balance, not a physical conservation law)
- "Tension is required for life" (Axiom 4 — design principle, partially reflected in TensionZone thresholds)
- "Reflection improves accuracy" (Axiom 5 — aspiration, partially reflected in council evolution)
- Soul Modes (Dormant/Responsive/Seeking/Conflicted — described in SOUL.md, no runtime mode state machine)
- Lex Lattice (Information Theory basis, Resonance Mesh — pure theory, zero code)
- LAR metric (Linguistic Accountability Ratio — specification only, no runtime calculation)
- Isnād consensus protocol (federated provenance — theory, only Aegis hash chain exists)
- Haven node federation (distributed governance — pure theory, no code)

**Honest language at this level**:
- "X is a design principle that guides ToneSoul's architecture"
- "X is described as a philosophical foundation; it is not a runtime mechanism"
- "X frames the system's intent but is not directly verifiable"

**What this level does NOT prove**:
- Anything about runtime behavior
- That the philosophy is internally consistent
- That the philosophy produces better outcomes than alternative framings

**Common overclaiming**: "ToneSoul ensures X" or "ToneSoul implements X" when X is a philosophical aspiration

### Level E6: Blocked / Currently Unverifiable

**Definition**: the claim describes a property that cannot be verified with current infrastructure, even in principle. Verification would require capabilities (outcome tracking, production deployment data, calibration curves, multi-model comparison) that do not exist yet.

**What this means**: the claim may be true, but there is no way to check. It is not that evidence is missing — it is that the infrastructure to produce evidence does not exist.

**Examples in ToneSoul**:
- "Council confidence is calibrated" (requires outcome tracking — no outcome pipeline exists)
- "Council deliberation improves output quality" (requires A/B comparison — no comparison infrastructure)
- "Evolution weights converge to correct perspective importance" (requires outcome-based reward — no outcome tracking)
- "Multi-perspective evaluation catches more issues than single-pass" (requires controlled comparison — not measured)
- "Continuity handoff preserves context effectively" (requires multi-session outcome measurement — not tracked)
- "Governance posture prevents real harm" (requires production incident tracking — no deployment)

**Honest language at this level**:
- "X cannot be verified with current infrastructure"
- "Verifying X would require [specific capability] that does not exist"
- "X is plausible but currently untestable"

**What this level does NOT prove**: nothing — that is the point.

**Common overclaiming**: "X works" or "X has been validated" when no validation infrastructure exists

---

## Evidence Level Summary Table

| Level | Name | Meaning | Strength |
|---|---|---|---|
| E1 | Test-backed | Automated test asserts this property; CI would catch breakage | Strong |
| E2 | Schema/helper validated | Runtime schema enforcement catches structural violations | Medium-Strong |
| E3 | Runtime-present, thinly tested | Code exists and runs; test coverage is shallow | Medium |
| E4 | Document-backed | Described in architectural contract or spec; no automated verification | Weak |
| E5 | Philosophical/narrative | Part of design vision or identity framework; no mechanism or test | Very Weak |
| E6 | Blocked/unverifiable | Cannot be checked with current infrastructure | None |

---

## Upgrade Paths

For each level, what would move a claim one level higher:

| From | To | What Is Needed |
|---|---|---|
| E6 → E5 | Blocked → Philosophical | Articulate the claim as a design principle (trivial but unhelpful) |
| E6 → E4 | Blocked → Document-backed | Write a contract specifying what the claim means and how it would be tested |
| E5 → E4 | Philosophical → Document-backed | Connect the philosophy to specific runtime surfaces and expected behaviors |
| E4 → E3 | Document → Runtime-present | Implement the code path (even minimally) and add 1-2 smoke tests |
| E3 → E2 | Thin test → Schema validated | Add Pydantic models or JSON Schema enforcement at the relevant data boundary |
| E3 → E1 | Thin test → Test-backed | Add dedicated tests that assert specific properties with meaningful inputs and edge cases |
| E2 → E1 | Schema → Test-backed | Add tests that verify semantic correctness beyond structural validity |

**The most impactful upgrades are E4→E3 and E3→E1**: getting a first test for an untested claim, and deepening thin tests into real verification.

---

## Six Overclaiming Patterns To Avoid

### Pattern 1: Document-As-Test

**What it looks like**: "The Continuity Import Contract defines import posture for all 17 surfaces" → treated as if import posture is tested.

**Why it is wrong**: a document describes intended behavior. A test verifies actual behavior. The document may be correct, outdated, or aspirational.

**Honest version**: "Import posture is documented for 17 surfaces. No automated test verifies that receivers follow the documented posture."

### Pattern 2: Schema-As-Semantic-Validation

**What it looks like**: "Council verdicts are validated by Pydantic" → treated as if verdict correctness is verified.

**Why it is wrong**: Pydantic validates that the verdict has the right fields with the right types. It does not validate that the verdict is the right decision for the given input.

**Honest version**: "Council verdict structure is enforced by Pydantic. Verdict correctness (whether the right decision was made) is not tested."

### Pattern 3: Code-Existence-As-Verification

**What it looks like**: "The risk calculator computes risk scores" → treated as if risk scores are accurate.

**Why it is wrong**: the code exists and runs. But 3 tests for a complex scoring system is thin coverage. The risk score may be wrong for many inputs.

**Honest version**: "Risk scoring code exists and has basic test coverage. Scoring accuracy across diverse inputs is not comprehensively verified."

### Pattern 4: Philosophy-As-Mechanism

**What it looks like**: "ToneSoul ensures AI takes responsibility for what it says" → treated as if there is a mechanism that enforces responsibility.

**Why it is wrong**: this is a design aspiration from SOUL.md. Responsibility is a philosophical framing, not a runtime check.

**Honest version**: "Responsibility is a core design principle. The runtime provides accountability surfaces (traces, dossiers, governance state) but does not mechanically enforce 'taking responsibility.'"

### Pattern 5: Test-Count-As-Coverage

**What it looks like**: "The council has 83 test files and 550+ tests" → treated as if the council is thoroughly verified.

**Why it is wrong**: test count does not equal coverage quality. Many tests may verify the same happy path. Critical edge cases may be untested. The 550 tests may cover 40% of code paths.

**Honest version**: "The council has extensive test infrastructure. Specific coverage gaps include [named gaps]."

### Pattern 6: Narrative-Elegance-As-Evidence

**What it looks like**: the architecture documents are beautifully written and internally consistent → treated as if the described properties hold.

**Why it is wrong**: per the Observable Shell Opacity Contract, narrative coherence is not evidence. A well-written contract describing 5 lifecycle lanes does not mean the lanes are enforced at runtime.

**Honest version**: "The lifecycle model is well-documented. Lane enforcement is a documentation convention, not a runtime mechanism."

---

## Authority vs Evidence: Two Separate Axes

The Claim Authority Matrix classifies claims by authority (who may assert them, how they govern the system). This contract classifies claims by evidence (what verification exists). These are independent:

| | Low Evidence | High Evidence |
|---|---|---|
| **High Authority** | AXIOMS.json axioms (constitutionally protected, but some are philosophical with no test) | Pydantic schema enforcement (runtime-enforced AND well-tested) |
| **Low Authority** | Helper utility claims (minor and also untested) | Safe parse functions (low-stakes AND thoroughly tested) |

**High authority + low evidence** is the most dangerous quadrant: the claim governs the system but nothing verifies it works. This is where later agents are most likely to overclaim.

**Low authority + high evidence** is the safest quadrant: the claim is minor but well-verified. No one will overclaim a safe-parse helper.

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md` | Applies these levels to 60+ specific claims |
| `TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md` | Organizes validation surfaces into lanes using these levels |
| `TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md` | Claim authority categories are the authority axis; evidence levels are the evidence axis |
| `TONESOUL_CLAIM_AUTHORITY_MATRIX.md` | Authority classification — independent from but complementary to evidence classification |
| `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` | Council realism claims are classified at E4 (document-backed) for independence assessment |
| `TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md` | Calibration claims are E6 (blocked/unverifiable) until outcome tracking exists |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | "Narrative coherence is not evidence" aligns with Pattern 6 |

---

## Canonical Handoff Line

Evidence has levels. A passing test is not the same as a schema check is not the same as a well-written document is not the same as a beautiful philosophy. Each level is valuable in its own right — a design philosophy guides decisions, a document records intent, a schema catches structural errors, a test catches regressions. But they are not interchangeable. When describing ToneSoul, name the evidence level. "This is tested" means something different from "this is documented." Use the right word for the right level. Precision in evidence language prevents both mythologizing and dismissal.
