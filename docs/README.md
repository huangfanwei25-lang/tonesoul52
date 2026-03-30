# ToneSoul Documentation Index

> Purpose: documentation entrypoint and guided index for ToneSoul architecture, status artifacts, and convergence surfaces.
> Last Updated: 2026-03-30
---

## AI Reading Stack

| Lane | Files | Authority | Use When |
|------|-------|-----------|----------|
| **Operational Start** | `AI_QUICKSTART.md` | `operational` | first minute of a later agent session |
| **Working Reference** | `AI_REFERENCE.md` | `operational` | term lookup, routing, red-line checks during work |
| **Canonical Anchor** | see section below | `canonical` | before architecture or runtime claims |
| **Design Center** | `../DESIGN.md` | `design_center` | when you need to know why the layers are split this way and which invariants must not drift |
| **Whole-System Guide** | `architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md` | `deep_map` | when you need one grounded explanation of the whole stack and why the subsystems are separated |
| **Deep Anatomy** | `narrative/TONESOUL_ANATOMY.md` | `deep_map` | before repo-wide refactor or whole-system explanation |
| **Interpretive Lane** | `notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`, `narrative/TONESOUL_CODEX_READING.md` | `interpretive` | when the map is navigable but the deeper load-bearing meaning still feels unclear |

Do not collapse these into one layer. Operational guides help an agent work; canonical anchors decide authority; deep and interpretive docs help explanation.

---

## Canonical Architecture Anchor

1. [architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
2. [notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md](notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md)
3. [notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md](notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md)
4. [architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md](architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)
5. [architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md](architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md)
6. [notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md](notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md)

## Interpretive Readings

- `notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`
  - compact handoff for Codex's deeper cross-repo reading after runtime-adapter and documentation-convergence work
- `narrative/TONESOUL_CODEX_READING.md`
  - Codex's longer interpretive reading of ToneSoul's load-bearing question, constitutional center, runtime narrow waist, anti-smuggling logic, and hidden temporal structure

## Whole-System Guide

- `architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md`
  - one-pass explanation of what each load-bearing subsystem does, why it exists, what it prevents, and what it should not be confused with

Open this when you need to explain ToneSoul as a whole without flattening governance, council, continuity, evidence, and safety into one vague "AI memory system."

## Design Center

- `../DESIGN.md`
  - durable design rationale for why ToneSoul is layered this way, which invariants must not drift, and why later agents should not collapse authority, evidence, continuity, and style into one story

Open this when you do not just need subsystem descriptions, but the design logic that holds them together.

## Retrieval Boundary

- `architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
  - clarifies how to read `knowledge/`, `knowledge_base/`, and `PARADOXES/` without collapsing them into one authority surface

## Architecture Companion

- `architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - reconciles the older six-layer runtime model with the newer externalized-cognition and model-attachment roadmap
- `notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md`
  - preserves the current handoff context for the next build seam: self-dogfooding ToneSoul through a lightweight developer runtime adapter
- `RFC-015_Self_Dogfooding_Runtime_Adapter.md`
  - draft source note for the runtime-adapter direction; keep it subordinate to the newer memory anchor until it is rewritten cleanly
- `architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
  - detailed recommendation for Redis-backed "R-memory", dominance order inside live compute, and the external repository stack that best fits ToneSoul
- `notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`
  - preserves the runtime review logic for authoritative state flow, safety-before-mutation, and one-cause-one-effect during Redis/world/gateway work
- `architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - evidence-backed contract for how far ToneSoul may push multi-agent shared state, where semantic-field synthesis remains experimental, and why canonical commit must stay serialized
- `architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
  - operating contract for what shared R-memory actually exposes to later agents, when to claim/checkpoint/compact, and which order preserves continuity without pretending agents share hidden thought
- `research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md`
  - official-source evidence map covering Anthropic, OpenAI, Microsoft, Google Cloud, and Google Research before ToneSoul promotes semantic-field language into canonical architecture
- `architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md`
  - triages recent compaction-memory, world-gamification, legacy-trace-repair, and security ideas into mainline, experimental, delayed, and forbidden lanes

## Engineering Contracts

- `architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
  - defines which retrieval surface to open first and when to switch from prose to executable verification
- `architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
  - defines what may and may not be distilled into adapters, RL traces, or future model-attached layers
- `architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`
  - defines the A/B/C firewall for separating mechanism, observable behavior, and interpretation in documents and claims
- `architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - defines the boundary between parallel perspective lanes, experimental field synthesis, and serialized canonical governance commit
- `architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
  - defines the practical multi-agent operating cadence across diagnose, packet, claim, perspective, checkpoint, compaction, commit, and release
- `architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md`
  - defines what part of the newer runtime/world/security proposal belongs in canonical runtime, projection layers, or separate workstreams

## Claim Authority Distillation

- `architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`
  - 75-term matrix for checking whether a ToneSoul term is canonical, runtime, law/spec vocabulary, research/theory, or projection, and whether it is safe to rely on operationally
- `architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md`
  - higher-signal boundary contract for the most confusing law/runtime terms so later agents stop mistaking theory, worldview, or design vocabulary for live implementation
- `status/claim_authority_latest.json`
  - machine-readable merge of the matrix, quick lookup, and overclaiming-risk list when later agents need fast term-status retrieval instead of re-reading long prose tables

Treat these as boundary aids. They help later agents classify claims, but they do not outrank code, tests, `AXIOMS.json`, or canonical architecture contracts.

## Evidence And Verifiability

- `architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md`
  - maps high-value ToneSoul claims to their actual evidence level, strongest backing source, weakest link, and safest phrasing
- `architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md`
  - defines the six evidence levels and the honest language that belongs to each
- `architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md`
  - organizes the repo's validation lanes and names what each lane does and does not prove
- `plans/tonesoul_evidence_followup_candidates_2026-03-29.md`
  - bounded next-step list for moving continuity and other thinly tested claims from E3 toward E1

Treat these as evidence aids. They help later agents distinguish authority from proof strength, but they do not outrank runtime code, tests, or canonical governance truth.

## Subject Refresh Boundaries

- `architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md`
  - field-level boundary contract for which hot-state surfaces may refresh `subject_snapshot` families, at what evidence standard, and where over-promotion begins
- `architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md`
  - lane map for separating durable identity, refreshable working identity, temporary carry-forward, and never-auto-promote fields before adding heuristics

Treat these as subject-refresh boundary aids. They help later agents write or review `subject_snapshot` safely, but they do not outrank runtime code, tests, canonical posture, or governance contracts.

## Control Plane Discipline

- `architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`
  - defines readiness states, task tracks, exploration depth, and claim/review requirements so later agents stop treating every task like a full-system refactor
- `architecture/TONESOUL_PLAN_DELTA_CONTRACT.md`
  - defines when to keep a plan, append a bounded delta, fork a new phase, or stop and ask a human instead of silently rewriting `task.md`
- `architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md`
  - formalizes when ToneSoul should stop mirroring, refuse unsupported L3 filler, and return current reasoning to a validated anchor center instead of continuing on drifted premises
- `plans/tonesoul_control_plane_followup_candidates_2026-03-28.md`
  - bounded implementation candidates for surfacing readiness, track hints, plan-delta telemetry, track-aware claim TTL, and exploration checkpoints

Treat these as control-plane discipline aids. They help later agents classify work and manage plan changes, but they do not outrank runtime code, canonical governance truth, or the current session bundle output.

## Observable-Shell And Axiom Boundaries

- `architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
  - defines what ToneSoul may honestly call observable, partially observable, or opaque when describing traces, packets, council outputs, and hidden reasoning
- `architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`
  - defines what currently supports or weakens each axiom without mutating `AXIOMS.json` or pretending theory-only axioms are already runtime-hard
- `plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md`
  - records why these two ideas were adopted now while impact tracking, decision-path marking, and tension-delayed commit remain deferred

Treat these as observability and methodological boundary aids. They help later agents stay honest about opacity and challengeability, but they do not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.

## Council Deliberation Discipline

- `architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`
  - defines the minimum dossier shape that preserves dissent, confidence posture, replay safety, and bounded council output semantics
- `architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md`
  - defines when work should stay in lightweight review, move through standard council, or escalate to elevated council depth
- `plans/tonesoul_council_followup_candidates_2026-03-28.md`
  - bounded follow-up list for dossier extraction, mode selection, change-of-position tracking, and evolution suppression flags

Treat these as council-discipline aids. They help later agents decide what a verdict preserved and whether deliberation depth matched task stakes, but they do not outrank runtime code or current council behavior.

## Council Realism And Calibration

- `architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`
  - explains where ToneSoul's council is genuinely plural versus where it is still one-model perspective multiplication
- `architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`
  - maps confidence-bearing council surfaces and separates descriptive agreement metrics from true calibration
- `architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md`
  - bounded adoption map for devil's advocate, pre-mortem, self-consistency, calibration, and blocked future improvements
- `plans/tonesoul_council_realism_followup_candidates_2026-03-29.md`
  - small next-step list derived from the realism/calibration pass

Treat these as realism and calibration aids. They help later agents describe the current council honestly and choose bounded quality improvements, but they do not outrank runtime code or mutate current council behavior by themselves.

## Context Continuity Adoption

- `architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md`
  - translates broad context-transfer instincts into ToneSoul-native continuity lanes across packet, compaction, subject snapshot, council dossier, and plan-delta surfaces

Treat this as an adoption map. It helps later agents decide what should continue across sessions, tasks, agents, and models, but it does not authorize raw transcript carry, hidden-thought transfer, or automatic promotion into canonical truth.

## Continuity Import And Receiver Discipline

- `architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`
  - classifies which continuity surfaces are directly importable, advisory, ephemeral, or manual-confirmation only
- `architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`
  - defines the receiver-side difference between `ack`, `apply`, and `promote`, and names the most dangerous silent-override hazards
- `architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md`
  - groups continuity surfaces into immediate coordination, bounded handoff, working identity, replay/review, and canonical foundation lanes
- `architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md`
  - defines how later agents may inherit operating habits and prompt style without turning them into canonical identity or law
- `plans/tonesoul_continuity_followup_candidates_2026-03-29.md`
  - bounded follow-up list for freshness, import posture surfacing, promotion guards, and decay reporting

Treat these as receiver-side continuity discipline aids. They help later agents import packet / compaction / checkpoint / snapshot surfaces without over-trusting them, but they do not outrank live runtime posture or canonical governance truth.

## Prompt Discipline Skeleton

- `architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`
  - translates prompt-side logic about goal function, rule priority, confidence, recovery, compression, and receiver instructions into ToneSoul-native control-plane language
- `architecture/TONESOUL_PROMPT_VARIANTS.md`
  - practical ToneSoul-native prompt variants for project continuity, meeting distillation, operator snapshot, council replay, and session-end resumability
- `architecture/TONESOUL_PROMPT_STARTER_CARDS.md`
  - short ready-to-adapt cards so later agents can start with a bounded prompt shape instead of a blank page

Treat this as a prompt-design companion. It helps later agents build better extraction, transfer, and summarization prompts, but it does not outrank runtime code, schemas, or existing governance contracts.

## Machine-Readable Mirrors

- `status/l7_retrieval_contract_latest.json`
  - compact L7 reading order, question routes, and verifier checklist
- `status/l8_distillation_boundary_latest.json`
  - compact L8 export gates, forbidden surfaces, and evaluation dimensions

## Operational Packets

- `status/l7_operational_packet_latest.json`
  - short agent-facing retrieval packet with selected route, first surfaces, and planned checks
- `status/l8_adapter_dataset_gate_latest.json`
  - adapter-row gate report showing whether public-safe distillation inputs pass the first L8 review
- `status/abc_firewall_latest.json`
  - doctrine verifier status for disclaimer-first, entrypoint references, and observable-shell claim boundaries
- `../spec/governance/r_memory_packet_v1.schema.json`
  - schema for the compact hot-state packet emitted by `python scripts/run_r_memory_packet.py` or `GET /packet`
- `../scripts/run_task_claim.py`
  - local CLI for claim/release/list task locks before multiple terminals touch the same surface

## Current Collaborator-Beta Surfaces

- `plans/tonesoul_launch_operations_surface_2026-03-30.md`
  - current operator-facing launch posture for guided collaborator beta, freeze rules, and bounded public-claim language
- `status/collaborator_beta_preflight_latest.json`
  - latest one-command collaborator-beta preflight bundle showing entry-stack health, launch scope, claim trigger, and visible `aegis` caution
- `status/collaborator_beta_preflight_latest.md`
  - markdown rendering of the same preflight bundle for quick human review
- `status/collaborator_beta_entry_validation_latest.json`
  - bounded external-style validation record showing what a lower-context collaborator agent still found ambiguous after using only the normal entry surfaces
- `status/collaborator_beta_entry_validation_latest.md`
  - readable version of the same collaborator-beta validation result and remaining frictions

## Current Continuation Surfaces

- `plans/tonesoul_3day_execution_program_2026-03-30.md`
  - concrete 3-day continuation program for the next agent, with bucket rotation and stop conditions
- `status/codex_handoff_2026-03-30.md`
  - current branch-local handoff note capturing today's working truth, private residues to avoid, and the next shortest board
 
## Documentation Convergence
 
- `status/doc_convergence_inventory_latest.json`
  - inventories authored doc surfaces, same-basename collisions, content similarity, and missing metadata gaps
- `status/doc_convergence_inventory_latest.mmd`
  - mermaid overview of authored doc categories, collision families, and cleanup priority nodes
- `plans/doc_convergence_cleanup_plan_2026-03-22.md`
  - first cleanup wave for engineering mirrors, divergent same-name docs, paradox fixture policy, and entrypoint metadata backfill
- `plans/doc_convergence_master_plan_2026-03-23.md`
  - program-level roadmap for multi-wave documentation cleanup, metadata reduction, and boundary maintenance
- `architecture/DOC_AUTHORITY_STRUCTURE_MAP.md`
  - retrieval-oriented structure map for entrypoints, canonical anchors, governance contracts, and generated status lanes
- `architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`
  - distills same-basename but non-duplicate files into explicit governance categories
- `status/basename_divergence_distillation_latest.json`
  - machine-readable registry report for resolved boundary pairs, generated namespace duals, backend duals, and deferred private shadows
- `status/doc_authority_structure_latest.json`
  - machine-readable map of document authority groups, tracked retrieval surfaces, and metadata posture across the main doc lanes
- `architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`
  - declares `memory/.hierarchical_index/` as the active lane and `memory/memory/.hierarchical_index/` as the deferred shadow lane during public convergence
- `status/private_memory_shadow_latest.json`
  - machine-readable report for active-vs-shadow private-memory pairs, hashes, JSON-shape drift, and deferred cleanup posture
- `architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md`
  - declares `PARADOXES/` as the canonical paradox casebook and `tests/fixtures/paradoxes/` as the projection lane
- `status/paradox_fixture_ownership_latest.json`
  - reports which paradox fixtures are exact mirrors, which are reduced test projections, and whether any pair needs review
- `architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md`
  - declares `docs/engineering/` as canonical owner and `law/engineering/` as the mirror lane
- `status/engineering_mirror_ownership_latest.json`
  - reports which engineering mirror pairs are exact, which still need sync, and which files remain canonical-only
- `architecture/HISTORICAL_DOC_LANE_POLICY.md`
  - declares `docs/archive/` and `docs/chronicles/` as historical lanes with different metadata rules from active architecture docs
- `status/historical_doc_lane_latest.json`
  - machine-readable report for chronicle pairs, generated-at markers, archive presence, and historical-lane governance posture

## Reality Alignment And Render Boundaries

- `architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md`
  - measured baseline for current README / AI entry routing after correcting older cleanup drift
- `architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md`
  - reproducible counting rules for `docs/architecture/`, `TONESOUL_*`, and `*_CONTRACT.md` claims
- `architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md`
  - separates real file corruption from terminal rendering noise and structural readability hazards
- `architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md`
  - register of which older cleanup recommendations remain valid, drifted, or already invalidated

Treat these as reality-alignment aids. They help later agents avoid stale counts, loose entrypoint claims, and false mojibake reports, but they do not outrank runtime code or canonical architecture contracts.

## Entry Simplification And Lineage Routing

- `architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md`
  - bounded first-hop routing for developers, researchers, AI agents, and curious humans
- `architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md`
  - separates canonical, companion, lineage, and legacy surfaces without flattening them
- `architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md`
  - names which simplification moves are safe and which would hide authority or depth
- `architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md`
  - distinguishes file corruption from render-layer noise and structural readability hazards
- `plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md`
  - staged cleanup sequence for metadata hygiene, if-wall cleanup, index differentiation, and lineage labeling

Treat these as entry-cleanup aids. They help later agents choose the right first surface and keep lineage legible, but they do not outrank current canonical architecture or runtime surfaces.

## Prompt Surface Topology And Adoption

- `architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md`
  - current-state classification of live prompt families, helpers, and the next adoption short board
- `architecture/TONESOUL_PROMPT_SURFACE_BOUNDARY_CONTRACT.md`
  - boundary rules for when starter-card adoption is justified versus when a prompt should stay specialized
- `architecture/TONESOUL_PROMPT_SURFACE_TOPOLOGY_MAP.md`
  - family map for council governance, governance review, context injection, output refinement, ToneBridge pipeline, persona voice, and helper-only surfaces
- `plans/tonesoul_prompt_adoption_followup_candidates_2026-03-29.md`
  - bounded next-wave candidates after the already-completed council and refinement waves

Treat these as prompt-adoption aids. They help later agents avoid reopening finished waves and point them toward the current short board, but they do not outrank live prompt code or tests.

## ? 敹恍?憪?
1. [AI_ONBOARDING.md](../AI_ONBOARDING.md) ??蝯行 AI ??撠?2. [terminology.md](terminology.md) ??**?詨?銵?摰儔**
3. [core_concepts.md](core_concepts.md) ???詨?璁艙隤芣?

---


## ?? ??蝯?

| 憿 | 瑼? | 隤芣? |
|------|------|------|
| **?仿?** | `core_concepts.md` | ?詨?璁艙 |
| **銵?** | `terminology.md` | TSR, STREI, POAV 蝑?蝢?|
| **?賜??* | `WHITEPAPER.md` | 摰?銵?格 |
| **FAQ** | `faq.md` | 撣貉??? |

---


## ?? 摮??
### `/philosophy/` ???脣飛撅?
| 瑼? | 隤芣? |
|------|------|
| `axioms.md` | Axiom 蝟餌絞閰唾圾 |
| `truth_vector_architecture.md` | ?????嗆? |
| `collective_consciousness.md` | ????璁艙 |
| `manifesto.md` | ?摰?? |

### `/engineering/` ??撌亦?撅?
| 瑼? | 隤芣? |
|------|------|
| `OVERVIEW.md` | 撌亦?璁汗 |

### `/governance/` ??瘝餌?撅?
| 瑼? | 隤芣? |
|------|------|
| `STREI_OPERATIONAL_PROTOCOL.md` | STREI ???降 |

### `/research/` ???弦???典???
| 瑼? | 隤芣? |
|------|------|
| `RESEARCH_CONTEXT_2.0.md` | 2.0 ?弦?窗???脰???|
| `experimental_design.md` | ??撽??祕撽身閮?|
| `multi_agent_architecture_patterns.md` | OpenClaw ?蜓瘚??嗅??扼???CP 閰摯 |
| `tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md` | L7/L8 ??皞??嗚enchmark???舀蝝????|

---


## ?? ?賊??辣

- [/spec/council_spec.md](../spec/council_spec.md) ??憭犖?潭?霅啁頂蝯梯???- [/AXIOMS.json](../AXIOMS.json) ???詨?瘜? (JSON)
- [/README.md](../README.md) ????亙

---


*Last updated: 2026-03-22*
