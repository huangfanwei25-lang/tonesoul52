# ToneSoul Eight-Layer Convergence Map

> Status: canonical architecture companion as of 2026-03-22
> Audience: future AI agents, maintainers, and architecture reviews
> Purpose: reconcile ToneSoul's six operational governance layers with the newer retrieval and model-attachment layers without implying a hidden ninth layer.
> Last Updated: 2026-04-18 (added orthogonality disclaimer pointing at the 13-layer body map)

> **⚠️ This is a request-flow axis, not an import-dependency axis.**
> The eight layers below describe **stages a single request passes through** (ingress → sensing → deliberation → governance → audit → memory → retrieval → attachment). They are not the same thing as — and do not compete with — the **13-layer body map** at [../status/codebase_graph_latest.md](../status/codebase_graph_latest.md), which describes **allowed import directions between Python subpackages** (surface / orchestration / pipeline / governance / semantic / perception / evolution / memory / domain / observability / infrastructure / shared / legacy), enforced by [../ARCHITECTURE_BOUNDARIES.md](../ARCHITECTURE_BOUNDARIES.md).
>
> The two views are **orthogonal**: one request can cross several body-map layers in sequence, and one body-map layer can serve several request-flow stages. Use this document when you need to reason about **where in a request's lifecycle** a concern lives; use the body map when you need to reason about **what a file may import**.

## Why This Document Exists

ToneSoul currently has two useful but incomplete architecture views:

- the older `v1.1` six-layer model explains the operational runtime core
- the newer externalized-cognition roadmap explains the evolution path toward retrieval and adapters

This document fuses them into one eight-layer map.

Use it when you need:

- one layer-by-layer view of the current repo
- a bridge between old runtime language and new externalized-cognition language
- a clear answer to where retrieval artifacts and model attachment belong

## Design Rule

The first six layers are the explicit governance runtime.

The last two layers are not "more hidden intelligence."
They are the engineering surfaces that make ToneSoul:

- retrievable before prompting
- verifiable before completion
- attachable to models without collapsing public and private memory boundaries

## The Eight Layers

| Layer | Name | Primary Role | Main Surfaces |
| --- | --- | --- | --- |
| L1 | Interface and Context Ingress | receive requests, normalize payloads, preserve boundary metadata | `apps/web/src/app/api/chat/route.ts`, `apps/api/server.py`, request adapters, **`tonesoul/yuhun/dpr.py`** (dynamic priority routing — decides FAST_PATH vs COUNCIL_PATH at the ingress boundary) |
| L2 | Semantic Sensing and Tension Field | compute drift, tension, semantic pressure, and resonance signals | `tonesoul/tension_engine.py`, `tonesoul/semantic_control.py`, `tonesoul/drift_monitor.py`, `tonesoul/resonance.py`, **`tonesoul/yuhun/world_sense.py`** (integrates DriftMonitor + JumpMonitor as the sensory layer for MCC) |
| L3 | Deliberation and Scenario Framing | generate multi-perspective reasoning candidates before final action | `tonesoul/council/*`, `tonesoul/tonebridge/scenario_envelope.py`, `tonesoul/deliberation/*`, **`.agent/agents/yuhun_*.md`** (Logician / Creator / Safety Guard / Empath — four-direction parallel deliberation), **`tonesoul/yuhun/vod.py`** (Visibility of Divergence — dual-track matrix output) |
| L4 | Governance Kernel and Action Control | decide pass, rewrite, block, escalate, or constrain action sets | `tonesoul/governance/kernel.py`, `tonesoul/yss_gates.py`, `tonesoul/poav.py`, `tonesoul/dcs.py`, `tonesoul/vow_system.py`, `tonesoul/alert_escalation.py`, **`tonesoul/yuhun/shadow_doc.py`** (JSON Shadow Document — black-box recorder for every council deliberation) |
| L5 | Audit, Provenance, and Explainability | expose why a decision happened and leave replayable evidence | `tonesoul/council/transcript.py`, `tonesoul/council/summary_generator.py`, `memory/provenance_chain.py`, `tonesoul/contract_observer.py`, `tonesoul/exception_trace.py`, **`memory/yuhun_shadows/*.json`** (cold-storage archive from ShadowDocument.save(), retrievable for audit) |
| L6 | Memory, Continuity, and Dream Loop | retain, decay, crystallize, review, and replay long-horizon continuity | `tonesoul/memory/*`, `tonesoul/dream_engine.py`, `tonesoul/stale_rule_verifier.py`, `tonesoul/vow_inventory.py`, **`WorldSense.dream_candidates()`** (sleep-period extraction of high-drift + high-tension moments for Offline RL), **`WorldSense.inbreeding_risk()`** (detects synthetic data echo-chamber risk), **`WorldSense.stable_anchors()`** (wake-verification baseline) |
| L7 | Compiled Retrieval and Verifier Surfaces | compile prose into graph, status, and enforcement artifacts that agents can open first | `docs/status/*`, `scripts/run_tonesoul_knowledge_graph.py`, `scripts/run_changed_surface_checks.py`, `scripts/verify_protected_paths.py`, `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`, **`graphify-out/graph.json`** (46-node knowledge graph, rebuildable via `graphify-out/build_graph.py`) |
| L8 | Model Attachment and Distillation Boundary | expose only stable public-safe behavior for adapters, RL loops, or future retrieval-native interfaces | `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`, `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`, `docs/philosophy/cultural_vector_distillation.md`, distillation and adapter-facing plans, **`docs/yuhun_core_protocol_v1.md`** (YUHUN behavioral specification for L8 adapters) |

## Layer Details

### L1. Interface and Context Ingress

This is where requests enter the system.

Responsibilities:

- validate and normalize payloads
- preserve session, user, consent, and route metadata
- convert frontend or API calls into a bounded runtime request

Without L1, every later layer receives ambiguous input.

### L2. Semantic Sensing and Tension Field

This layer translates raw input into measurable semantic signals.

Responsibilities:

- estimate drift and mismatch
- compute tension and resistance
- surface resonance or divergence posture
- make semantic pressure visible before the council speaks

This is where ToneSoul stops being plain request routing and becomes a tension-aware system.

### L3. Deliberation and Scenario Framing

This layer constructs candidate interpretations and competing responses.

Responsibilities:

- run multi-perspective council deliberation
- compare alternative frames
- preserve disagreement instead of hiding it
- make scenario assumptions explicit before final adjudication

L3 is where "do not erase disagreement" becomes runtime behavior.

### L4. Governance Kernel and Action Control

This layer decides what the system is allowed to do.

Responsibilities:

- run hard gates and policy checks
- constrain actions under risk or lockdown
- escalate under crisis or drift
- convert deliberation into operational permission

If L3 generates options, L4 determines admissibility.

### L5. Audit, Provenance, and Explainability

This layer turns decisions into evidence.

Responsibilities:

- record rationale, uncertainty, and transcript structure
- expose provenance chains and replayable decision fields
- surface suppressed exceptions instead of silently hiding them
- keep final claims tied to observable traces

This layer protects ToneSoul from becoming a "trust me" system.

### L6. Memory, Continuity, and Dream Loop

This layer maintains long-horizon identity and correction.

Responsibilities:

- decay weak traces
- crystallize durable rules
- revisit stale rules through verification
- consolidate recurring patterns into continuity

L6 is where the system becomes more than a single response.

### L7. Compiled Retrieval and Verifier Surfaces

This is the new layer that the old six-layer model did not name explicitly.

Responsibilities:

- compile long markdown into machine-usable artifacts
- expose knowledge graphs, latest status, and boundary maps
- connect changed files to concrete checks
- enforce protected paths and completion claims

This layer exists because later agents repeatedly failed when forced to reconstruct the repo from long prose and implicit joins.

Operational contract:

- `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
- `docs/status/l7_retrieval_contract_latest.json`

### L8. Model Attachment and Distillation Boundary

This is the other new layer that the old six-layer model did not name explicitly.

Responsibilities:

- define what behavior is stable enough to attach to models
- define what can be distilled into adapters or RL traces
- preserve the public/private boundary before any training-like export
- provide a path toward retrieval-native or memory-native model integration

Important rule:

- ToneSoul may distill stable public behavior
- ToneSoul must not distill raw private memory, vault contents, or irreversible user history

Operational contract:

- `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
- `docs/status/l8_distillation_boundary_latest.json`

## Why There Is No Ninth "Model-Internalized Runtime Layer"

The earlier four-stage roadmap includes model internalization.

That is real, but it is not treated here as an always-on repository layer.
Once behavior crosses into weights, it stops being directly inspectable in the repo.

So this map treats internalization as an output boundary of L8, not as a new in-repo operational layer.

That keeps the architecture honest:

- L1-L7 remain auditable here
- L8 is the controlled export seam
- full internalization is downstream and selective, never the new source of truth

## Mapping From Six Layers To Eight Layers

| Older v1.1 layer | New eight-layer interpretation |
| --- | --- |
| L1 Input and Context | L1 Interface and Context Ingress |
| L2 Semantic Sensing | L2 Semantic Sensing and Tension Field |
| L3 Reasoning and Deliberation | L3 Deliberation and Scenario Framing |
| L4 Audit and Explainability | L5 Audit, Provenance, and Explainability |
| L5 Governance Kernel | L4 Governance Kernel and Action Control |
| L6 Narrative Continuity | L6 Memory, Continuity, and Dream Loop |
| not explicit in v1.1 | L7 Compiled Retrieval and Verifier Surfaces |
| not explicit in v1.1 | L8 Model Attachment and Distillation Boundary |

## Mapping From Four Stages To Eight Layers

| Externalized roadmap stage | Main eight-layer span |
| --- | --- |
| External Soul | L1-L6 |
| Model-Readable Soul | L7 |
| Model-Attachable Soul | L8 |
| Model-Internalized Soul | selective downstream output from L8, never a replacement for L1-L7 |

## Public and Private Boundary

Cross-cutting rule across all layers:

- public repo stores engine behavior, contracts, status artifacts, and safe abstractions
- private vault stores personal memory, sensitive traces, and deletion-sensitive detail
- verifier and governance control points stay outside irreversible model weights

This rule matters most at L6-L8.

## Recommended Reading Order

When architecture direction is ambiguous:

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
3. `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
4. `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
5. `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
6. `docs/status/tonesoul_knowledge_graph_latest.md`
7. `AI_ONBOARDING.md`

## Canonical Instruction For Future Agents

If you need one sentence to remember this file:

> ToneSoul's first six layers are the explicit governance runtime, the seventh layer compiles retrieval and verification surfaces, and the eighth layer is the controlled attachment seam for adapters and distillation, not a license to collapse private memory into model weights.
