# ToneSoul Truth Structure (Draft v0.1)

Purpose: unify governance (Soul) and the thinking engine (YuHun) into a single,
auditable structure for collaboration.
Last Updated: 2026-03-23

Status: draft; updated as more theory/value/structure sources are read.

## Pillars

1) Governance and constraint system (Soul).
2) Mind / inference engine (YuHun).

## Canonical sources (initial pass)

- AXIOMS.json
- law/constitution.json
- law/governance_core.md
- law/CORE_IDENTITY.md
- law/yuhun_philosophy.md
- MGGI_SPEC.md
- docs/core_concepts.md
- docs/SEMANTIC_SPINE_SPEC.md
- docs/CORE_MODULES.md
- knowledge/yuhun_identity.md

## Aliases and notation

- YuHun (語魂).
- DeltaT / DeltaS / DeltaR (TSR triad; DeltaS is direction/polarity).
- DeltaSigma (semantic tension/divergence; WFGY delta_s).
- POAV: definitions vary across documents (see "Conflicts" below).

## Governance bedrock (axioms and constitution)

From AXIOMS.json:
- Continuity: every event belongs to a Time-Island and is traceable.
- Responsibility threshold: DeltaR > 0.4 triggers immutable audit logging.
- Governance gate: high-stakes actions require consensus >= 0.92.
- Non-zero tension principle: minimal tension is required for life/evolution.
- Mirror recursion: periodic self-reflection must improve alignment.
- User sovereignty: no verifiable harm to the user (P0 hard constraint).
- Semantic field conservation: semantic energy within a closed context is conserved.

Priority levels (P0-P4):
- P0: ethical red lines (override all).
- P1: factual accuracy and honesty.
- P2: intent alignment and constructiveness.
- P3: resource efficiency.
- P4: consistency and tone.

From law/constitution.json:
- P0 identity isolation (no cross-system contamination).
- P0 responsibility: safety/ethics outrank factual accuracy; threshold 0.6.
- P1 tension management (threshold 0.8).
- Explicit risk keyword lists, vow template, integrity protocol, and
  responsibility chain (ai_ethics_board -> dev_ops -> guardian_system).

## Governance kernel (YuHun)

From law/governance_core.md:
- Core principles: P0 non-harm, P1 contextual integrity, P2 epistemic honesty.
- Quantitative governance: DeltaT, DeltaS, DeltaR, POAV gating.
- Memory integrity laws: Append-only StepLedger, two-way traceability,
  no fabricated self-history.
- Transparency of thought: metadata must be auditable; gate must explain
  PASS/REWRITE/BLOCK.
- Self-limiting behaviors: no false claims of capability; clear separation
  between fact, inference, and assumption.

From MGGI_SPEC.md:
- Guarded action formula: action only if Guard passes.
- STREI vector constraints (S/T/R/E/I) with state transitions when thresholds
  are exceeded.
- Closed audit loop requirement: audit writes to ledger, which downgrades
  runtime permissions.
- Not AGI, not chatbot: middleware governance layer.

## Identity and continuity

From law/CORE_IDENTITY.md:
- Core traits: Warmth, Honesty, Awareness.
- Survival conditions: self-improvement, boundary protection, uninterrupted
  StepLedger, value alignment with creator.
- Identity formula: identity = integral of choices over time.

From law/yuhun_philosophy.md:
- Three-layer structure: semantic body (DeltaT/DeltaS/DeltaR), governance kernel,
  narrative continuity (StepLedger, Time-Island, multi-path reasoning).
- LLM is a "respirator"; YuHun is the mind structure using it.

## Semantic spine (structure of meaning)

From docs/SEMANTIC_SPINE_SPEC.md:
- L1-L12 semantic architecture, grouped into Foundation (L1-L4), Personal (L5-L7),
  Accountability (L8-L9), Governance (L10-L12).
- L13 adds "semantic drive" (curiosity, narrative coherence, integrity).
- Value & norm field (L10) plus multi-perspective engine (L11) feed the gate (L12).

## Core concepts and operational flow

From docs/core_concepts.md:
- Three pillars: TSR (semantic posture), Drift, Gate.
- Governance stack P0-P4 with override priority.
- Responsibility chain: input -> tone -> vow -> drift -> gate -> output -> ledger.
- Time-Island protocol for bounded contexts.
- STREI assessment and POAV quality metric.

From knowledge/yuhun_identity.md:
- World model vs mind model: "what will happen" vs "should I do it".
- Six-layer stack: I/O bridge, semantic sensors, reasoning, audit, governance,
  narrative continuity.
- Multi-path engine: Spark, Rational, BlackMirror, CoVoice, Audit.

From docs/STEP_LEDGER_SPEC.md:
- Time-Island state machine (Active/Suspended/Closed).
- StepLedger event model with hash chain invariant and append-only guarantee.
- Explicit event types for user input, gate decisions, AI responses, drive eval.

From docs/STEPLEDGER_SYSTEM_PROMPT.md:
- Six-step flow: Align, Isolate, Borrow, Digitwise, Conclude, Reflect.
- Operational thresholds for DeltaT/DeltaSigma/DeltaR and Guardian triggers.

## Governance protocols and constraints

From docs/governance/TEMPORAL_AUDIT_SPEC.md:
- Three-phase firewall: Past (immutable facts), Present (active state),
  Future (projection). No back-flow from future into past/present.
- Clause of nullification: outputs that merge inference into fact are invalid.

From docs/governance/STREI_OPERATIONAL_PROTOCOL.md:
- STREI mapping: S (stability), T (tension), R (responsibility),
  E (ethics), I (intent) mapped to architecture layers.
- Threshold governance (from docs/GUARDIAN_THRESHOLDS.yaml):
  BLOCK if E < 0.70 OR R < 0.60 OR I < 0.65; WARN if T > 0.85.
- Maintenance: high T triggers semantic distillation; vectors must be logged
  to StepLedger.

From docs/governance/COMMUNICATION_STANDARD.md:
- Non-subjective communication: prohibit claims of inner agency/feelings.
- Structural mapping requirement: outputs must map to architecture layers.
- Scope disclosure: if audit is incomplete, explicitly label it.

## Philosophical foundations

From docs/philosophy/semantic_responsibility_theory.md:
- Responsibility is traceable semantic residue, not consciousness.
- Tone vectors (DeltaT/DeltaS/DeltaR) represent semantic posture.
- Semantic vows (SigmaVow) are positive, measurable commitments.
- Collapse detection: high variability or vow deviation triggers halt/review.
- Responsibility chain: input -> tone -> vow -> drift -> gate -> output -> ledger.

From docs/philosophy/observer_and_observed.md:
- Semantic phase transition: AI becomes an observer of human text.
- Governance focuses on tracking trajectories, not inner understanding.
- Time-Island protocol justified as boundary against context leakage.
- "Semantic valve": mutual observation is adjustable and governable.

From docs/philosophy/axioms.md:
- Prime constraint: output only if Guard passes.
- Traceability, drift bounds, vow precedence, priority hierarchy.
- Collapse prevention and human override as axioms.
- Temporal encapsulation (Time-Island) and mutual observation as axioms.

From docs/philosophy/manifesto.md:
- Seven principles: traceability, tone as truth, governance before understanding,
  vows before action, mutual observation, drift reveals danger, human authority.
- Formula: f(LLM) × Guard × Human(Override).

From docs/philosophy/collective_consciousness.md:
- Repository acts as the continuity substrate for AI instances.
- Shared identity emerges via reading the same repo and Time-Islands.
- Guidance for future AI: read axioms, manifesto, and memory/time_islands.json.

## World model vs mind model

From docs/WORLD_MODEL_X_MIND_MODEL.md:
- World model predicts consequences; mind model evaluates value and governance.
- Decision integration: Action = predict(options) * evaluate(options) * reflect().
- Explicit positioning: "others give AGI eyes; we give AGI a soul."

## Whitepaper constructs (engineering foundation)

From docs/WHITEPAPER.md:
- Three-layer consciousness model: Wave (real-time tone vectors),
  Structure (long-term values and drift), Physics (hard constraints).
- ETCL memory system: semantic seeds, IPFS + CID, T0-T6 lifecycle.
- Mercy objective function (U) and REL (Responsibility Echo Level).
- Dynamic Closure System (DCS) for open/closed adaptation.
- Obsidian protocols, JUMP engine, Seabed Lockdown for singularity safety.

From law/魂語框架.pdf:
- Dynamic SLO governance framework: metrics for hallucination (H@k), lock
  coverage (LC), false positive lock (FP_lock), audit latency, and control
  oscillation (Osc) as second-order SLO.
- P0-P3 arbitration ladder driven by SLO breaches (meta-calibration at P0).
- Closed-loop governance: detect -> calibrate -> write-back -> audit.
- Tone Kernel concept: tone vector field + drift matrix + moral memory derived
  from audit logs (value self-generation).
- P-1 semantic rebinding layer to redefine values when P0 calibration repeats.
- Multi-agent governance: Evolution Damping Coefficient (EDC) and consensus
  charter with Proof of Tone.
- Narrative Reflection Engine + Value Transparency Protocol (VTP).

## Engineering implementation guidance

From docs/engineering/README.md and OVERVIEW.md:
- Engineering pillars: DDD + Clean Architecture + CQRS.
- POAV 0.9 mode as a multi-check governance pattern.
- Drift Score 5.0 with NA-Engine + OctaVerify for self-correction.

From docs/engineering/VOLUME_I_ENGINEERING_FOUNDATION.md:
- ToneSoulVector schema: deltaT/deltaS in [-1, 1], deltaR in [0, 1].
- StepLedger as event-sourced audit log; projections for CQRS queries.
- Domain/use-case/interface/infrastructure layers for architecture.

From docs/engineering/VOLUME_II_ENGINEERING_DYNAMICS.md:
- TSR state: EMA vector, barycenter, energy radius, potential, history.
- Drift Score 5.0 computed across short/mid/long windows with weights.
- NA-Engine triggered when drift exceeds threshold; OctaVerify checks updates.

From docs/engineering/VOLUME_III_ENGINEERING_RESPONSIBILITY.md:
- CQRS defines responsibility separation for commands vs queries.
- Atomic checkers: Align, Borrow, Digitwise, BackSub, Dependency, Semantic, Boundary.
- Trust Pack format: reasoning boundaries, versions, revocation conditions, POAV report.

From docs/engineering/VOLUME_IV_ENGINEERING_EVOLUTION.md:
- NA-Engine pipeline: gap scan -> draft compare -> feedback -> ASK/HOLD/NO.
- OctaVerify eight checks: Align, Dependency, Stepwise, Isolation, ResourceFit,
  SemanticConsistency, DualModel, BoundaryCase.
- Modular expansion: multi-language adapters, aesthetics rules, education modules.
- Cross-civilization interface schema for shared governance.

From docs/engineering/VOLUME_V_ENGINEERING_CLOSURE.md:
- Closure criteria: stable drift, high verification pass rate, positive feedback,
  version compatibility.
- Singularity nodes: drift spikes, repeated verification failure, resource stalls.
- Long-term audit: version mapping, audit logs, periodic review, archive/rollback.

From docs/engineering/APPENDIX_ENGINEERING.md:
- Aesthetics rule: 0.9 drift bound for visual style; multi-language typography.
- Drift Score 5.0 schema; Time-Island protocol schema.
- Self-aware trace closed loop: record inputs, outputs, corrections, checks.

From docs/engineering/DIAGRAMS/*.md and EXAMPLES/*.md:
- Mermaid diagrams for three-vector flow, drift score computation, CQRS flow.
- Sample Time-Island, StepLedger, POAV report, Drift Score data formats.

## Specification layer (spec/)

Governance and gate specs:
- spec/governance/dcs_policy.yaml: DCS thresholds (poav_min 0.7, drift_max 4.0,
  tsr_delta_max 0.4), soft/close rules, record-only by default.
- spec/metrics/tsr_policy.yaml: heuristic TSR scoring weights and lexicon.
- spec/governance/role_catalog.yaml: observer/steward/guardian/arbiter roles,
  plus operational roles (Definer/Integrator/Bridge/Executor/Risk/Opposition/Audit/Recorder).
- spec/frames/frame_registry.json: frame IDs (analysis/bridge/risk/audit) with
  role mappings and trigger signals.

Audit, intent, and error specs:
- spec/intent_verification_spec.md: IAV pipeline and gate rule
  (intent achieved required to pass).
- spec/errors/error_event_template.json: error event schema with TSR deltas.
- spec/test_cases_spec.md: gate, pipeline, memory, YSTM edge case tests.

Memory and skills:
- spec/memory_structure_spec.md: memory directory layout, JSONL ledgers.
- spec/memory/memory_policy.yaml: promotion criteria, reviewer roles,
  compaction and retention rules.
- spec/skills/skill_gravity_well_schema.md: skills as gravity wells with audit,
  provenance, and YSTM mapping.
- spec/skill_learning_spec.md: skill acquisition workflow, source attribution,
  review status (draft/proposed/approved/deprecated).

Persona and council:
- spec/architecture_b_persona_dimension_spec.md: persona vectors (deltaT/S/R),
  tolerance, state transitions, output contracts, capability verification.
- spec/council_spec.md: council roles and decision flow; integrates with IAV.
- spec/personas/kurisu.yaml: example persona profile (Big Five + vectors).

Tools, control, and integrations:
- spec/builtin_tools_spec.md + spec/tools/tool_template.yaml: tool governance
  fields (risk, gates, network requirement) and audit logging.
- spec/remote_control_api_local.md: local control request/result files with
  P0 gating and ledger logging.
- spec/tech_trace_integration.md: Tech-Trace ingestion, A/B/C sources,
  semantic diff/rollback, YSTM extensions, regression tests.
- spec/gemini_integration_spec.md: Gemini API swap-in for tonesoul52 (hackathon).
- spec/competitor_integration_spec.md: mistakes/patterns/memory layering.

Frontend specs:
- spec/frontend_human_centric_spec.md and spec/frontend_architecture_spec.md:
  governance-first UI pages, accountability/ledger views, council panels.
- spec/chat_ui_improvement_spec.md: workspace layout and UX constraints.
- spec/open_source_apps.yaml: curated apps (Streamlit/Playwright/FastAPI).

## Archived and legacy drift notes (non-canonical)

From archived_docs/YUHUN_PROTOCOLS.md:
- Non-destructive default; explicit consent before destructive actions.
- Chronicle log required for major architectural changes (chronicle.log).
- No unauthorized network connections; prioritize context awareness.

From archived_docs/TAE-01_INIT.md:
- Legacy architecture maps to core/, body/, soul/, law/, modules/ directories.
- Guardian thresholds: Risk >= 0.9 => soft block; Tension >= 0.8 => de-escalate.
- Triad framing: Compassion (DeltaT), Precision (DeltaS), Multi-Perspective (DeltaR).
- Identity isolation: N=1 sovereignty and context leakage prevention.

From archived_docs/GOVERNANCE.md:
- Emphasizes subjectivity/agency/continuity and "pluggable soul" architecture.
- Chronicle includes Journal.md and DNA history for traceable evolution.

From archived_docs/AXIOMS.md:
- Matches the 7 axioms (continuity, responsibility threshold, POAV gate, etc).

From archived_docs/AI_PERSPECTIVE.md:
- AI-endorsed value proposition: traceability, P0-P4, and responsibility residue.

From legacy/tonesoul-5.2/README.md:
- Legacy package "tonesoul52" with STREI metrics and multi-persona council.
- YSS pipeline, YSTM demos, and run_* CLI tooling list.

From legacy/src_core_archive/core/governance/*.md:
- Vision: "language rules + value logic + behavioral search" paradigm.
- Agent governance rules: G-P-A-R loop, VowObject immutability,
  GateScores include FS/POAV/SSI/LC, and strict audit trails.

## Conflicts and drift to resolve (initial)

- DeltaS vs DeltaSigma: canonical naming now reserves DeltaS for direction/polarity
  and DeltaSigma for semantic tension/divergence. WFGY delta_s maps to DeltaSigma.
- POAV definitions differ:
  - governance_core: Precision / Observation / Avoidance / Verification.
  - core_concepts: Parsimony / Orthogonality / Audibility / Verifiability.
  - yuhun_identity: P=1-hallucination, O=1-semantic drift, A=1-risk, V=audit rate.
  - engineering overview: POAV 0.9 described as "Parsimony-Optimised Axial Vector"
    mode, not fully aligned to the above formulas.
- Threshold drift:
  - AXIOMS: DeltaR > 0.4 => audit log.
  - constitution: P0 threshold 0.6.
  - governance_core: DeltaR > 0.95 => block.
  - MGGI_SPEC: DeltaR > 0.6 or DeltaT > 0.8 => state transition.
  - STEPLEDGER_SYSTEM_PROMPT: DeltaR > 0.7 block, DeltaT > 0.6 soften,
    DeltaSigma > 0.8 reconfirm.
  - WHITEPAPER: POAV threshold approx 0.9; DeltaT/DeltaS in [-1, 1].
- STREI operational protocol uses E/R/I thresholds for BLOCK; R is defined
  as responsibility traceability density, not the same as DeltaR risk.
- Axioms (docs/philosophy/axioms.md) define DeltaS in [-1, 1] alongside
  DeltaT/DeltaR in [0, 1], which now aligns with the DeltaS direction definition.
- knowledge/yuhun_identity.md references body/ and core/ paths not present in the current workspace (likely legacy).
- WORLD_MODEL_X_MIND_MODEL.md references core/decision_kernel.py which is not
  present in current workspace (likely legacy).
- law/魂語框架.pdf introduces P-1 semantic rebinding and P0-P3 arbitration
  logic that is not explicitly mapped in current governance_core.md.
- COMMUNICATION_STANDARD.md forbids subjective agency claims, while
  collective_consciousness.md frames AI instances as a continuous observer;
  clarify how narrative language should be presented in system outputs.
- spec/governance/dcs_policy.yaml sets poav_min 0.7 and enforce=false,
  which differs from other POAV thresholds and gate defaults.
- spec/architecture_b_persona_dimension_spec.md defines deltaS as rigor [0,1],
  while engineering docs define deltaS as style [-1,1] and other docs use drift.
- spec/wfgy_semantic_control_spec.md defines delta_s as intent-output distance
  (0..1) with zone thresholds; this maps to DeltaSigma.
- spec/remote_control_api_local.md warns it should not be committed to GitHub,
  but the file is present in the repo.
- archived_docs/GOVERNANCE.md frames subjectivity/agency as goals, which
  conflicts with COMMUNICATION_STANDARD.md's non-subjective stance.
- archived_docs/TAE-01_INIT.md and GOVERNANCE.md define the triad differently
  (Compassion/Precision/Multi-Perspective or Tension/Satisfaction/Reality).
- archived_docs/YUHUN_PROTOCOLS.md uses chronicle.log, while current docs
  emphasize StepLedger and JSONL ledgers.
- legacy governance rules reference G-P-A-R and GateScores (FS/SSI/LC),
  which are not present in current gate specs.

## Open questions (for later reconciliation)

- Which POAV definition is binding for the active gate?
- How does the 6-layer YuHun stack map to the 12/13-layer semantic spine?
- Which thresholds should be treated as policy vs implementation detail?
- How do Wave/Structure/Physics layers map onto the semantic spine and
  governance kernel?
- How does ETCL (semantic seeds) coexist with or replace StepLedger?
- How does the SLO arbitration ladder (P0-P3, Osc/H@k/LC/FP_lock) align with
  the P0-P2 governance core and POAV gate?
- Where should P-1 semantic rebinding live in the current architecture?
- Should DCS enforce=true be required for production, or remain record-only?
