# ToneSoul Documentation Index

> Purpose: top-level documentation index for ToneSoul authority surfaces, operational packets, and convergence maps.
> Last Updated: 2026-04-18
> Status: full registry, not the default first-hop gateway.
> Use When: `docs/README.md` was not enough, or you need broader inventory coverage instead of guided routing.
---

## AI Reading Stack

| Lane | Files | Authority | Use When |
|------|-------|-----------|----------|
| **Operational Start** | [AI_QUICKSTART.md](AI_QUICKSTART.md) | `operational` | first minute of a later agent session |
| **Working Reference** | [AI_REFERENCE.md](AI_REFERENCE.md) | `operational` | term lookup, routing, red-line checks during work |
| **Canonical Anchor** | see section below | `canonical` | before architecture or runtime claims |
| **Design Center** | [../DESIGN.md](../DESIGN.md) | `design_center` | when you need the durable design rationale and invariants before opening narrow contracts |
| **Whole-System Guide** | [architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | `deep_map` | when you need one grounded explanation of the whole stack and why the subsystems are separated |
| **Deep Anatomy** | [narrative/TONESOUL_ANATOMY.md](narrative/TONESOUL_ANATOMY.md) | `deep_map` | before repo-wide refactor or whole-system explanation |
| **Interpretive Lane** | [notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md](notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md), [narrative/TONESOUL_CODEX_READING.md](narrative/TONESOUL_CODEX_READING.md) | `interpretive` | when the map is clear but the load-bearing meaning still feels diffuse |
| **Code-Level Lookup** | [status/codebase_graph_latest.md](status/codebase_graph_latest.md) | `generated_truth` | when you need to know what a specific `tonesoul/...` module does, its layer, coupling, and upstream/downstream deps |

Use these in order if you intentionally need the fuller registry. Do not let a deep or interpretive document silently outrank code, tests, or architecture contracts.

### Routing rule for "what does this file do?"

- **Query**: "what does `tonesoul/<x>.py` do / which layer is it / who depends on it?"
  - **Go to**: [status/codebase_graph_latest.md](status/codebase_graph_latest.md) — auto-generated from the live code by `scripts/analyze_codebase_graph.py`, covers all 254 modules with declared layer + purpose + coupling.
  - **Do NOT go to**: [CORE_MODULES.md](CORE_MODULES.md) — narrative explanation of ~20 conceptual modules (TSC-01, PN-02, MCP-03…), last hand-updated 2026-03-23. It is interpretive design history, not a file-level index. Treat it as a lens, not a lookup table.
- **Query**: "what are the legitimate import directions between layers?"
  - **Go to**: [ARCHITECTURE_BOUNDARIES.md](ARCHITECTURE_BOUNDARIES.md) — reconciled against the body-map's 13-layer taxonomy.
- **Query**: "what is this repo *about* at the design level?" → `DESIGN.md`, `architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`.

---

## Canonical Architecture Anchor

- [architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
- [notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md](notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md)
- [notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md](notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md)
- [architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md](architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)
- [architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md](architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md)
- [notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md](notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md)
- [architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md](architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Interpretive Reading Layer

- [notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md](notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md)
  - open this when the repository map is clear but the deeper load-bearing meaning still feels diffuse
- [narrative/TONESOUL_CODEX_READING.md](narrative/TONESOUL_CODEX_READING.md)
  - Codex's longer structural reading of ToneSoul as a constitutional continuity system rather than only a memory stack

Use these after the canonical architecture anchor, not before it.

## Whole-System Guide

- [architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md)
  - one-pass explanation of what each load-bearing subsystem does, why it exists, what it prevents, and what it should not be confused with

Use this when you need to explain ToneSoul as a whole without flattening governance, council, continuity, evidence, and safety into one vague "AI memory system."

## Design Center

- [../DESIGN.md](../DESIGN.md)
  - durable design rationale for why ToneSoul is layered this way, what invariants must not drift, and why continuity/evidence/style are kept separate

Use this when you need the architectural "why" before drilling into subsystem-specific contracts.

## Engineering Contracts

- [architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md](architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md)
- [architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md](architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md)
- [architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md](architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
- [architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md](architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Claim Authority Distillation

- [architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md](architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md)
  - full cross-lane matrix for whether a term is canonical, runtime, vocabulary, theory, or projection
- [architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md](architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md)
  - compact boundary contract for the highest-confusion `law/` and deep-prose terms
- [status/claim_authority_latest.json](status/claim_authority_latest.json)
  - machine-readable merge of the 75-term matrix, the 18-term quick lookup, and the overclaiming-risk list for fast agent-side term checks

## Evidence And Verifiability

- [architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md](architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md)
  - maps high-value ToneSoul claims to their current evidence level, strongest backing source, weakest link, and safest phrasing
- [architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
  - defines the six evidence levels and the honest language each level allows
- [architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md](architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md)
  - groups test and validation lanes by what confidence they actually buy and what false inference they do not justify
- [plans/tonesoul_evidence_followup_candidates_2026-03-29.md](plans/tonesoul_evidence_followup_candidates_2026-03-29.md)
  - bounded follow-up list for lifting thinly tested continuity claims toward regression-backed status

## Subject Refresh Boundaries

- [architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md](architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md)
  - boundary contract for deciding which hot-state surfaces may refresh `subject_snapshot` field families and at what minimum evidence level
- [architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md](architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md)
  - quick lane map for durable identity, refreshable working identity, temporary carry-forward, and never-auto-promote fields

Use these when `subject_snapshot` is in play. They are boundary aids for heuristics and review, not replacements for runtime code or canonical governance truth.

## Control Plane Discipline

- [architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
  - readiness states, task tracks, exploration depth, and claim/review requirements for classifying work before it starts
- [architecture/TONESOUL_PLAN_DELTA_CONTRACT.md](architecture/TONESOUL_PLAN_DELTA_CONTRACT.md)
  - bounded rules for keep / append delta / fork new phase / stop and ask human when scope shifts
- [architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md](architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md)
  - control-plane contract for when ToneSoul should stop mirroring, declare fail-stop, and pull drifted reasoning back toward a validated anchor center
- [plans/tonesoul_control_plane_followup_candidates_2026-03-28.md](plans/tonesoul_control_plane_followup_candidates_2026-03-28.md)
  - small implementation candidate list derived from the control-plane contracts

Use these when readiness, track classification, or `task.md` mutation discipline is the question. They are control-plane aids, not live runtime enforcement.

## Observable-Shell And Axiom Boundaries

- [architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md](architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md)
  - observable-shell honesty contract for distinguishing what ToneSoul can really audit from what remains opaque
- [architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md](architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md)
  - support/weakening map for the 7 axioms so later agents can challenge claims without rewriting the constitution
- [plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md](plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md)
  - adoption review for the extracted external theory proposals, including what was translated into ToneSoul-native naming and what remains deferred

Use these when the question is not "what is the runtime path" but "how honest can I be about opacity" or "what would actually weaken an axiom claim." They are boundary aids, not runtime gates.

## Council Deliberation Discipline

- [architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md](architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md)
  - minimum dossier shape for verdict replay, dissent preservation, and confidence posture
- [architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md](architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md)
  - mode contract for lightweight review, standard council, and elevated council depth
- [plans/tonesoul_council_followup_candidates_2026-03-28.md](plans/tonesoul_council_followup_candidates_2026-03-28.md)
  - bounded implementation candidates derived from the council discipline contracts

Use these when the question is not only what verdict was produced, but whether dissent survived and whether the deliberation depth matched the task.

## Council Realism And Calibration

- [architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md](architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md)
  - honesty contract for where ToneSoul council is truly plural versus only perspective-voiced
- [architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md](architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md)
  - map of confidence surfaces, descriptive-vs-calibrated boundaries, and the infrastructure gap to true calibration
- [architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md](architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md)
  - adoption map for devil's advocate, pre-mortem, self-consistency, confidence decomposition, and blocked future upgrades
- [plans/tonesoul_council_realism_followup_candidates_2026-03-29.md](plans/tonesoul_council_realism_followup_candidates_2026-03-29.md)
  - small next-step list derived from the realism/calibration pass

Use these when the question is not merely "what did council output" but "how real is this plurality, what do the confidence numbers actually mean, and which next upgrade is honest to implement now."

## Context Continuity Adoption

- [architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md](architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md)
  - ToneSoul-native adoption map for what should continue across sessions, tasks, agents, and models, and what must stay bounded or not transfer at all

Use this when the question is not merely how to hand off current state, but what continuity discipline ToneSoul should adopt next. It is an adoption map, not live runtime permission.

## Continuity Import And Receiver Discipline

- [architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md](architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md)
  - import-posture contract for deciding what may be trusted directly, treated as advisory, or discounted by decay
- [architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md](architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md)
  - receiver-side boundary contract for `ack`, `apply`, `promote`, and silent-override hazards
- [architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md](architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md)
  - temporal lane map for continuity surfaces from immediate coordination to canonical foundation
- [architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md](architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md)
  - bounded contract for sharing operating style, prompt habits, and render caveats without over-promoting them
- [plans/tonesoul_continuity_followup_candidates_2026-03-29.md](plans/tonesoul_continuity_followup_candidates_2026-03-29.md)
  - bounded implementation candidates for freshness, import posture surfacing, promotion guards, and decay reporting

Use these when the question is no longer only what should continue, but what the receiver may safely import, how long it stays fresh, and what must never be silently promoted.

## Prompt Discipline Skeleton

- [architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md](architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md)
  - prompt-side discipline skeleton for goal function, priority, evidence, recovery, stability bands, compression levels, and receiver instructions
- [architecture/TONESOUL_PROMPT_VARIANTS.md](architecture/TONESOUL_PROMPT_VARIANTS.md)
  - practical prompt variants derived from the skeleton for common ToneSoul transfer and distillation tasks
- [architecture/TONESOUL_PROMPT_STARTER_CARDS.md](architecture/TONESOUL_PROMPT_STARTER_CARDS.md)
  - short starter cards for immediate use when there is no time to design a prompt from zero

Use this when the question is not only what should be transferred, but how the extraction or transfer prompt should be structured in the first place.

## Developer Runtime Adapter Direction

- [notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md](notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md)
- [RFC-015_Self_Dogfooding_Runtime_Adapter.md](RFC-015_Self_Dogfooding_Runtime_Adapter.md)
- [architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md](architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md)
- [notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md](notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md)
- [research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md](research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Machine-Readable Contract Mirrors

- [status/l7_retrieval_contract_latest.json](status/l7_retrieval_contract_latest.json)
- [status/l8_distillation_boundary_latest.json](status/l8_distillation_boundary_latest.json)

## Operational Packets

- [status/l7_operational_packet_latest.json](status/l7_operational_packet_latest.json)
- [status/l8_adapter_dataset_gate_latest.json](status/l8_adapter_dataset_gate_latest.json)
- [status/abc_firewall_latest.json](status/abc_firewall_latest.json)
- [../spec/governance/r_memory_packet_v1.schema.json](../spec/governance/r_memory_packet_v1.schema.json)
- [../scripts/run_task_claim.py](../scripts/run_task_claim.py)

## Current Collaborator-Beta Surfaces

- [status/phase724_launch_operations_surface_2026-04-15.md](status/phase724_launch_operations_surface_2026-04-15.md)
- [status/collaborator_beta_preflight_latest.json](status/collaborator_beta_preflight_latest.json)
- [status/collaborator_beta_preflight_latest.md](status/collaborator_beta_preflight_latest.md)
- [status/collaborator_beta_entry_validation_latest.json](status/collaborator_beta_entry_validation_latest.json)
- [status/collaborator_beta_entry_validation_latest.md](status/collaborator_beta_entry_validation_latest.md)

## Current Continuation Surfaces

- [plans/tonesoul_3day_execution_program_2026-03-30.md](plans/tonesoul_3day_execution_program_2026-03-30.md)
- [status/codex_handoff_2026-04-02.md](status/codex_handoff_2026-04-02.md)
- [plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md](plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md)
- [plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md](plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md)

## Successor Continuity And Hot Memory

- [architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md](architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md)
- [architecture/TONESOUL_LOW_DRIFT_ANCHOR_SOURCE_PRECEDENCE_CONTRACT.md](architecture/TONESOUL_LOW_DRIFT_ANCHOR_SOURCE_PRECEDENCE_CONTRACT.md)
- [architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md](architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md)
- [plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md](plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md)
- [plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md](plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md)
- [plans/tonesoul_successor_sidecar_residue_triage_2026-04-02.md](plans/tonesoul_successor_sidecar_residue_triage_2026-04-02.md)

## Research-Driven Memory Interop And Knowledge Layer

- [architecture/TONESOUL_CROSS_AGENT_MEMORY_CONSUMER_CONTRACT.md](architecture/TONESOUL_CROSS_AGENT_MEMORY_CONSUMER_CONTRACT.md)
  - shared first-hop reading contract for Codex, Claude-style shells, and dashboard/operator surfaces
- [architecture/TONESOUL_CLAUDE_COMPATIBLE_ENTRY_ADAPTER_CONTRACT.md](architecture/TONESOUL_CLAUDE_COMPATIBLE_ENTRY_ADAPTER_CONTRACT.md)
  - repo-native adapter boundary for Claude-style entry without pretending first-party vendor interop
- [architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md](architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md)
  - boundary between hot coordination state, compiled knowledge, exploratory residue, and future retrieval
- [architecture/TONESOUL_LAUNCH_HEALTH_TREND_READOUT_CONTRACT.md](architecture/TONESOUL_LAUNCH_HEALTH_TREND_READOUT_CONTRACT.md)
  - bounded contract for separating descriptive launch posture from trendable signals and deferred forecasting
- [architecture/TONESOUL_INTERNAL_STATE_OBSERVABILITY_REALITY_CHECK_CONTRACT.md](architecture/TONESOUL_INTERNAL_STATE_OBSERVABILITY_REALITY_CHECK_CONTRACT.md)
  - bounded contract for exposing strain, drift, stop-pressure, and deliberation-conflict signals without inflating observability into selfhood
- [architecture/TONESOUL_SURFACE_VERSIONING_AND_CONSUMER_LINEAGE_CONTRACT.md](architecture/TONESOUL_SURFACE_VERSIONING_AND_CONSUMER_LINEAGE_CONTRACT.md)
  - bounded versioning and fallback contract for session-start, observer-window, dashboard shells, and Claude-style adapters
- [architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md](architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md)
  - taxonomy and parking rule for raw sources, compiled knowledge, exploratory residue, operator retrieval, and public teaching
- [architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md](architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md)
  - future landing-zone spec for compiled artifacts, collection metadata, health checks, and queryable indexes
- [architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md](architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md)
  - bounded contract for future operator-facing compiled-knowledge queries with provenance-first results and explicit non-promotion posture
- [plans/tonesoul_research_lines_and_memory_interop_program_2026-04-06.md](plans/tonesoul_research_lines_and_memory_interop_program_2026-04-06.md)
  - active research-driven follow-through for cross-agent parity, knowledge layering, and predictive-boundary honesty

## Bounded Self-Improvement Loop

- [architecture/TONESOUL_SELF_IMPROVEMENT_LOOP_V0_SPEC.md](architecture/TONESOUL_SELF_IMPROVEMENT_LOOP_V0_SPEC.md)
  - bounded architecture spec for how ToneSoul may improve operator/runtime surfaces without mutating identity, vows, governance truth, or hot-memory transport
- [architecture/TONESOUL_SELF_IMPROVEMENT_EVALUATOR_HARNESS_CONTRACT.md](architecture/TONESOUL_SELF_IMPROVEMENT_EVALUATOR_HARNESS_CONTRACT.md)
  - evaluator contract for baseline, candidate, success metric, failure watch, rollback path, and honest promote / park / retire outcomes
- [architecture/TONESOUL_EXPERIMENT_REGISTRY_AND_LINEAGE_BOUNDARY_CONTRACT.md](architecture/TONESOUL_EXPERIMENT_REGISTRY_AND_LINEAGE_BOUNDARY_CONTRACT.md)
  - boundary contract for raw runs, distilled lessons, promotion-ready results, and the separation between experiment lineage, hot coordination, compiled knowledge, and identity
- [architecture/TONESOUL_BOUNDED_MUTATION_SPACE_CONTRACT.md](architecture/TONESOUL_BOUNDED_MUTATION_SPACE_CONTRACT.md)
  - mutation-space contract that splits self-improvement targets into allowed-now, human-gated, and forbidden-in-v0 classes
- [architecture/TONESOUL_ANALYZER_AND_PROMOTION_GATE_CONTRACT.md](architecture/TONESOUL_ANALYZER_AND_PROMOTION_GATE_CONTRACT.md)
  - analyzer closeout and promotion-gate contract that preserves unresolved items, rollback posture, and honest promote / park / retire / blocked outcomes
- [architecture/TONESOUL_PROMOTION_READY_RESULT_SURFACE_CONTRACT.md](architecture/TONESOUL_PROMOTION_READY_RESULT_SURFACE_CONTRACT.md)
  - result-surface contract for how trial outcomes stay visible, supersedable, and secondary to runtime truth without bloating first-hop shells
- [status/self_improvement_trial_wave_latest.md](status/self_improvement_trial_wave_latest.md)
  - latest bounded self-improvement trial-wave summary with result-surface posture, replay rule, and promotion limits
- [plans/tonesoul_self_improvement_loop_v0_program_2026-04-06.md](plans/tonesoul_self_improvement_loop_v0_program_2026-04-06.md)
  - active follow-through program for evaluator harness, experiment lineage, mutation-space boundaries, promotion gate, and bounded result surfacing

## Governance Depth And Consistency-First Validation

- [architecture/TONESOUL_GOVERNANCE_DEPTH_ROUTING_V0_SPEC.md](architecture/TONESOUL_GOVERNANCE_DEPTH_ROUTING_V0_SPEC.md)
  - bounded spec for reducing default governance cost through `light / standard / full` routing without deleting reflex, vow posture, or output-edge honesty
- [plans/tonesoul_consistency_first_governance_depth_program_2026-04-07.md](plans/tonesoul_consistency_first_governance_depth_program_2026-04-07.md)
  - queued follow-through program for first-hop consistency, governance-depth routing, high-risk grounding, fail-stop budget discipline, and deferred domain-trial gating
- [research/tonesoul_neurosymbolic_governance_depth_distillation_2026-04-07.md](research/tonesoul_neurosymbolic_governance_depth_distillation_2026-04-07.md)
  - ToneSoul-native distillation of recent neuro-symbolic efficiency ideas into what should be absorbed, what should be rejected, and why this should stay a bounded routing/grounding line instead of a new mythology

## Documentation Convergence

- [status/doc_convergence_inventory_latest.json](status/doc_convergence_inventory_latest.json)
- [status/doc_convergence_inventory_latest.mmd](status/doc_convergence_inventory_latest.mmd)
- [plans/doc_convergence_cleanup_plan_2026-03-22.md](plans/doc_convergence_cleanup_plan_2026-03-22.md)
- [plans/doc_convergence_master_plan_2026-03-23.md](plans/doc_convergence_master_plan_2026-03-23.md)
- [architecture/DOC_AUTHORITY_STRUCTURE_MAP.md](architecture/DOC_AUTHORITY_STRUCTURE_MAP.md)
- [status/doc_authority_structure_latest.json](status/doc_authority_structure_latest.json)
- [architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md](architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md)
- [status/basename_divergence_distillation_latest.json](status/basename_divergence_distillation_latest.json)
- [architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md](architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md)
- [status/private_memory_shadow_latest.json](status/private_memory_shadow_latest.json)
- [architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md](architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md)
- [status/paradox_fixture_ownership_latest.json](status/paradox_fixture_ownership_latest.json)
- [architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md](architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md)
- [status/engineering_mirror_ownership_latest.json](status/engineering_mirror_ownership_latest.json)
- [architecture/HISTORICAL_DOC_LANE_POLICY.md](architecture/HISTORICAL_DOC_LANE_POLICY.md)
- [status/historical_doc_lane_latest.json](status/historical_doc_lane_latest.json)

## Reality Alignment And Render Boundaries

- [architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md](architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md)
  - measured baseline for current README / AI entry routing and active entry surfaces
- [architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md](architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md)
  - reproducible count patterns for architecture files, `TONESOUL_*`, and actual contracts
- [architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md](architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md)
  - separates file corruption from terminal-display noise and structural readability hazards
- [architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md](architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md)
  - drift register for earlier cleanup advice versus current repo reality

Use these when a document claim sounds too clean, too rounded, or too shell-dependent to trust without measurement.

## Entry Simplification And Lineage Routing

- [architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md](architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md)
  - audience-specific first-hop routing for developers, researchers, AI agents, and curious humans
- [architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md](architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md)
  - category map for canonical, companion, historical-lineage, and legacy surfaces
- [architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md](architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md)
  - safe-versus-unsafe simplification rules for entry surfaces and deep lanes
- [architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md](architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md)
  - hazard register for structural readability, stale metadata, and render-layer noise
- [plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md](plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md)
  - bounded cleanup wave plan for metadata hygiene, if-wall restructuring, index differentiation, and lineage labeling

## Prompt Surface Topology And Adoption

- [architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md](architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md)
  - current-state classification of live prompt families, helper-only surfaces, and the next adoption short board
- [architecture/TONESOUL_PROMPT_SURFACE_BOUNDARY_CONTRACT.md](architecture/TONESOUL_PROMPT_SURFACE_BOUNDARY_CONTRACT.md)
  - rules for when starter-card adoption is justified versus when a prompt should remain specialized
- [architecture/TONESOUL_PROMPT_SURFACE_TOPOLOGY_MAP.md](architecture/TONESOUL_PROMPT_SURFACE_TOPOLOGY_MAP.md)
  - family map for governance prompts, context injection, refinement, domain pipelines, and persona voice
- [plans/tonesoul_prompt_adoption_followup_candidates_2026-03-29.md](plans/tonesoul_prompt_adoption_followup_candidates_2026-03-29.md)
  - bounded next-wave candidates after the already-completed council and refinement waves

## ?妣 Documentation Governance v1

| ?辣 | 隤芣? |
|------|------|
| [DOCS_INFORMATION_ARCHITECTURE_v1.md](DOCS_INFORMATION_ARCHITECTURE_v1.md) | ?辣?????蝞～???蝞∠??箇? |
| [DOCS_CLASSIFICATION_LEDGER_v1.md](DOCS_CLASSIFICATION_LEDGER_v1.md) | 蝚砌???憿撣喉???憿??祉宏嚗?|
| [FILE_PURPOSE_MAP.md](FILE_PURPOSE_MAP.md) | 頝函???蝝?|
| [plans/iu_oi_backplane_convergence_2026-03-18.md](plans/iu_oi_backplane_convergence_2026-03-18.md) | IU/OI/Backplane ?嗆??? |

---


## ?? Quick Start

| ?辣 | 隤? | 隤芣? |
|------|------|------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | EN | Setup & first run |
| [GETTING_STARTED_zh.md](GETTING_STARTED_zh.md) | 銝?| 摰???甈∪銵?|
| [?啣?閮剖?.md](?啣?閮剖?.md) | 銝?| ?啣??蔭 |
| [DEMO_SHOWCASE.md](DEMO_SHOWCASE.md) | EN | Demo walkthrough |
| [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) | EN | Vercel deployment |
| [faq.md](faq.md) | EN | FAQ |

---


## ?? Architecture

| ?辣 | 隤芣? |
|------|------|
| [CORE_MODULES.md](CORE_MODULES.md) | ?詨?璅∠?璁汗 |
| [MODULE_DEPENDENCIES.md](MODULE_DEPENDENCIES.md) | 璅∠?靘陷????|
| [ARCHITECTURE_BOUNDARIES.md](ARCHITECTURE_BOUNDARIES.md) | ?嗆???摰儔 |
| [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) | ?嗆?撖拇 |
| [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) | ?澈蝯?隤芣? |
| [STRUCTURE.md](STRUCTURE.md) | 蝟餌絞蝯? |
| [SPEC_LAW_CROSSWALK.md](SPEC_LAW_CROSSWALK.md) | `spec/` ??`law/` 銝??撠 |
| [FILE_PURPOSE_MAP.md](FILE_PURPOSE_MAP.md) | 瑼??券???|
| [architecture-notes.md](architecture-notes.md) | ?嗆?蝑? |
| [system_structure_overview.txt](system_structure_overview.txt) | 蝟餌絞蝮質汗 (text) |
| [system_walkthrough.md](system_walkthrough.md) | 蝟餌絞韏啗? |
| [NARRATIVE_MODULE_MAP.md](NARRATIVE_MODULE_MAP.md) | ???芋蝯??扯” |

---


## ?? Philosophy & Theory

| ?辣 | 隤芣? |
|------|------|
| [PHILOSOPHY.md](PHILOSOPHY.md) | ?詨??脣飛嚗葉?? |
| [PHILOSOPHY_EN.md](PHILOSOPHY_EN.md) | Core philosophy (EN) |
| [PHILOSOPHY_WHITEPAPER_v1.md](PHILOSOPHY_WHITEPAPER_v1.md) | ?脣飛?賜??v1 |
| [WHITEPAPER.md](WHITEPAPER.md) | 銝餌?格 (45KB) |
| [WORLD_MODEL_X_MIND_MODEL.md](WORLD_MODEL_X_MIND_MODEL.md) | 銝?璅∪? ? 敹璅∪? |
| [philosophy/ai_life_journal_protocol.md](philosophy/ai_life_journal_protocol.md) | AI ??亥????霅?|
| [AI_CONCEPT_ASSESSMENT.md](AI_CONCEPT_ASSESSMENT.md) | AI 璁艙閰摯 |
| [TRUTH_STRUCTURE.md](TRUTH_STRUCTURE.md) | ??蝯? (19KB) |
| [core_concepts.md](core_concepts.md) | ?詨?璁艙摰儔 |
| [terminology.md](terminology.md) | 銵?銵?|
| [glossary_engineering_mapping.md](glossary_engineering_mapping.md) | 銵??極蝔???|
| [philosophy/](philosophy/) | ?脣飛摮??(27 files) |

---


## ?? Governance & Safety

| ?辣 | 隤芣? |
|------|------|
| [7D_AUDIT_FRAMEWORK.md](7D_AUDIT_FRAMEWORK.md) | 7D 撖抵?獢 |
| [7D_EXECUTION_SPEC.md](7D_EXECUTION_SPEC.md) | 7D ?瑁?閬 |
| [AUDIT_CONTRACT.md](AUDIT_CONTRACT.md) | 撖抵??? |
| [HONESTY_MECHANISM.md](HONESTY_MECHANISM.md) | 隤祕璈 |
| [SECURITY_AUDIT_2025.md](SECURITY_AUDIT_2025.md) | 2025 摰撖抵? |
| [EXTERNAL_SOURCE_TRUST_POLICY.md](EXTERNAL_SOURCE_TRUST_POLICY.md) | 憭靘?靽∩遙??allowlist 蝑 |
| [VTP_SPEC.md](VTP_SPEC.md) | ?潸?蝘餃?霅啗???|
| [COUNCIL_RUNTIME.md](COUNCIL_RUNTIME.md) | Council ????|
| [SEMANTIC_BIFURCATION_AUDIT.md](SEMANTIC_BIFURCATION_AUDIT.md) | 隤儔??撖抵? |
| [when_to_ground.md](when_to_ground.md) | 雿??亙嚗??嗅摰? |
| [governance/](governance/) | 瘝餌?摮??(4 files) |

---


## ?? Specifications (`spec/`)

| ?辣 | 隤芣? |
|------|------|
| [council_spec.md](../spec/council_spec.md) | Council 閬 |
| [pre_output_council_spec.md](../spec/pre_output_council_spec.md) | ?撓??Council |
| [wfgy_semantic_control_spec.md](../spec/wfgy_semantic_control_spec.md) | WFGY 隤儔?批 |
| [intent_verification_spec.md](../spec/intent_verification_spec.md) | ??撽? |
| [memory_structure_spec.md](../spec/memory_structure_spec.md) | 閮蝯? |
| [skill_learning_spec.md](../spec/skill_learning_spec.md) | ??賢飛蝧?|
| [tech_trace_integration.md](../spec/tech_trace_integration.md) | Tech Trace ?游? |
| [test_cases_spec.md](../spec/test_cases_spec.md) | 皜祈岫獢?閬 |
| [frontend_architecture_spec.md](../spec/frontend_architecture_spec.md) | ?垢?嗆? |
| [frontend_human_centric_spec.md](../spec/frontend_human_centric_spec.md) | 鈭箸?垢 |
| [gemini_integration_spec.md](../spec/gemini_integration_spec.md) | Gemini ?游? |
| [chat_ui_improvement_spec.md](../spec/chat_ui_improvement_spec.md) | Chat UI ?孵? |
| [architecture_b_persona_dimension_spec.md](../spec/architecture_b_persona_dimension_spec.md) | 鈭箸蝬剖漲 |
| [tonesoul_improvement_derivation.md](../spec/tonesoul_improvement_derivation.md) | ?寥脫撠?|

---


## ?? Semantic & Metrics

| ?辣 | 隤芣? |
|------|------|
| [SEMANTIC_SPINE_SPEC.md](SEMANTIC_SPINE_SPEC.md) | 隤儔?閬 (20KB) |
| [METRICS_MAPPING.md](METRICS_MAPPING.md) | ???? |
| [DIMENSIONS.md](DIMENSIONS.md) | 蝬剖漲摰儔 |
| [STEP_LEDGER_SPEC.md](STEP_LEDGER_SPEC.md) | 甇仿?撣單閬 |
| [STEPLEDGER_SYSTEM_PROMPT.md](STEPLEDGER_SYSTEM_PROMPT.md) | 撣單蝟餌絞?內閰?|
| [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md) | ?亥??? |
| [NARRATIVE.md](NARRATIVE.md) | ??撅?|
| [NARRATIVE_LAYER.md](NARRATIVE_LAYER.md) | ??撅文?蝢?|
| [NARRATIVE_MAP.md](NARRATIVE_MAP.md) | ???啣? |

---


## ? API & Integration

| ?辣 | 隤芣? |
|------|------|
| [API_SPEC.md](API_SPEC.md) | API 閬 (8KB) |
| [TOOLS_API_CLIENT.md](TOOLS_API_CLIENT.md) | Tools API 摰Ｘ蝡?|
| [TOOLS_API_SCHEMA.md](TOOLS_API_SCHEMA.md) | Tools API Schema |
| [ORCHESTRATOR_MVP.md](ORCHESTRATOR_MVP.md) | ???MVP |
| [SOUL_DB.md](SOUL_DB.md) | ??鞈?摨?|
| [TRAINING_DATA_SPEC.md](TRAINING_DATA_SPEC.md) | 閮毀鞈?閬 |

---


## Research & Publications

| File | Purpose |
|------|------|
| [RESEARCH_EVIDENCE.md](RESEARCH_EVIDENCE.md) | research evidence and citation surface |
| [academic_comparison.md](academic_comparison.md) | academic comparison notes |
| [bayesian_accountability_literature.md](bayesian_accountability_literature.md) | literature review for Bayesian accountability direction |
| [bayesian_accountability_plan.md](bayesian_accountability_plan.md) | planning companion for the same accountability lane |
| [reproducibility_guide.md](reproducibility_guide.md) | reproducibility guidance |
| [rmf_crosswalk.md](rmf_crosswalk.md) | RMF crosswalk notes |
| [research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md](research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md) | earlier L7/L8 evidence map |
| [research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md](research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md) | official-source evidence map for semantic-field claims |
| [research/tonesoul_llm_classic_paper_map_2026-03-30.md](research/tonesoul_llm_classic_paper_map_2026-03-30.md) | selective map of classic LLM papers that still matter for ToneSoul design decisions |
| [plans/tonesoul_agent_os_pattern_distillation_2026-04-01.md](plans/tonesoul_agent_os_pattern_distillation_2026-04-01.md) | distilled Agent-OS patterns ToneSoul should learn without importing a foreign naming universe |
| [plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md](plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md) | successor/hot-memory planning that translates useful external frameworks into ToneSoul-native workstreams |
| [zenodo_publishing_guide.md](zenodo_publishing_guide.md) | Zenodo publishing guide |
| [research/](research/) | research working directory (12 files) |

---


## ? Marketing & Community

| ?辣 | 隤芣? |
|------|------|
| [BLOG_POST.md](BLOG_POST.md) | ?刻?潭?蝡?|
| [VOCUS_POST.md](VOCUS_POST.md) | Vocus 鞎潭? |
| [MOLTBOOK_POST_DRAFT.md](MOLTBOOK_POST_DRAFT.md) | Moltbook ?阮 |
| [GITHUB_INTRO_DRAFT.md](GITHUB_INTRO_DRAFT.md) | GitHub 隞晶?阮 |
| [CASE_STUDIES.md](CASE_STUDIES.md) | 獢??弦 |
| [use_cases.md](use_cases.md) | 雿輻獢? |
| [EXTERNAL_PR_GUIDE.md](EXTERNAL_PR_GUIDE.md) | 憭 PR ?? |
| [TECH_ARTICLE_DRAFT_v0.1.0.md](TECH_ARTICLE_DRAFT_v0.1.0.md) | ?銵?蝡?蝔?|

---


## ?? Engineering & Operations

| ?辣 | 隤芣? |
|------|------|
| [RELEASE_v0.1.0_PLAN.md](RELEASE_v0.1.0_PLAN.md) | ?澆?閮 v0.1.0 |
| [RELEASE_NOTES_v0.1.0.md](RELEASE_NOTES_v0.1.0.md) | ?澆?隤芣??阮 v0.1.0 |
| [plans/ANTIGRAVITY_VM_RUNBOOK.md](plans/ANTIGRAVITY_VM_RUNBOOK.md) | Antigravity ?璈??典銵???|
| [plans/git_local_repo_stabilization_plan_2026-02-20.md](plans/git_local_repo_stabilization_plan_2026-02-20.md) | Git/?砍?澈蝛拙?????|
| [plans/side_branch_isolation_playbook_2026-02-21.md](plans/side_branch_isolation_playbook_2026-02-21.md) | ?舐?????? |
| [../reports/project_audit_report_2026-02-21.md](../reports/project_audit_report_2026-02-21.md) | ??啣?獢祟閮??|
| [../reports/multi_persona_audit_discussion_2026-02-20.md](../reports/multi_persona_audit_discussion_2026-02-20.md) | 憭犖?澆祟閮?隢??|
| [GOLDEN_LOG.md](GOLDEN_LOG.md) | 暺??亥? |
| [ADR-001-dual-track-resolution.md](ADR-001-dual-track-resolution.md) | ADR: ??閫?? |
| [failure_analysis.md](failure_analysis.md) | 憭望??? |
| [privacy_policy.md](privacy_policy.md) | ?梁??輻? |
| [engineering/](engineering/) | 撌亦?摮??(9 files) |
| [status/](status/) | ????桅? (95 files) |

---


## ?? Subdirectory Index

| ?桅? | Files | ?批捆 |
|------|-------|------|
| `philosophy/` | 27 | ?怎?獢????鋡怨??恐閮 |
| `engineering/` | 9 | 撌亦?閬?祕雿敦蝭 |
| `research/` | 10 | 摮貉??弦??瘥???|
| `governance/` | 4 | 瘝餌?閬???閬?|
| `status/` | 99 | 撠???蕭頩?|
| `notes/` | 2 | ?酉 |
| `architecture/` | 8 | ?嗆???撌亦????? |
| `images/` | 2 | ??鞈? |
