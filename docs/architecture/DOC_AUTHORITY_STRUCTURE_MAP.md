# Documentation Authority Structure Map

> Purpose: define the retrieval-oriented structure of ToneSoul's documentation so later agents can tell entrypoints, canonical anchors, governance contracts, and generated status surfaces apart.
> Status: active documentation authority map for convergence cleanup.
> Last Updated: 2026-03-29

---

## Why This Exists

The repository already has a document inventory and multiple convergence contracts.
What it still lacked was a compact answer to this question:

`which document lane should I open first for this kind of work?`

This map is not another abstract taxonomy.
It is a retrieval structure for documentation authority.

## Core Lanes

### 1. Entrypoint lane

Open these when you are orienting to the repo:

- `README.md`
- `README.zh-TW.md`
- `AI_ONBOARDING.md`
- `docs/INDEX.md`
- `docs/README.md`

### 2. Canonical architecture lane

Open these before making architecture claims:

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
- `docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md`
- `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`

### 3. Governance and execution lane

Open these when you need runtime contracts, audit posture, or API behavior:

- `docs/7D_AUDIT_FRAMEWORK.md`
- `docs/7D_EXECUTION_SPEC.md`
- `docs/AUDIT_CONTRACT.md`
- `docs/API_SPEC.md`
- `docs/COUNCIL_RUNTIME.md`

### 4. Documentation governance lane

Open these when you are restructuring docs or checking naming/authority rules:

- `docs/DOCS_INFORMATION_ARCHITECTURE_v1.md`
- `docs/DOCS_CLASSIFICATION_LEDGER_v1.md`
- `docs/FILE_PURPOSE_MAP.md`
- `docs/status/doc_convergence_inventory_latest.json`
- `docs/plans/doc_convergence_cleanup_plan_2026-03-22.md`

### 5. Convergence contract lane

Open these when duplicate-like surfaces are in scope:

- `docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`
- `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`
- `docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md`
- `docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md`

### 6. Generated status lane

Open these when you need the current machine-readable posture instead of prose:

- `docs/status/basename_divergence_distillation_latest.json`
- `docs/status/private_memory_shadow_latest.json`
- `docs/status/paradox_fixture_ownership_latest.json`
- `docs/status/engineering_mirror_ownership_latest.json`
- `docs/status/doc_convergence_inventory_latest.json`

### 7. Observable-shell and axiom challenge lane

Open these when the question is:

- what is honestly observable,
- what remains opaque,
- what would actually weaken an axiom claim.

- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`
- `docs/plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md`

### 8. Council deliberation discipline lane

Open these when the question is:

- what a council verdict should preserve beyond the flat verdict word,
- how dissent survives into later-agent handoff,
- when deliberation should stay lightweight versus escalate.

- `docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`
- `docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md`
- `docs/plans/tonesoul_council_followup_candidates_2026-03-28.md`

### 9. Context continuity adoption lane

Open this when the question is:

- what structure should survive across sessions, tasks, agents, or models,
- which transfer instincts already fit ToneSoul surfaces,
- which transfer ideas still need boundary contracts before implementation.

- `docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md`

### 10. Prompt discipline skeleton lane

Open this when the question is:

- how an extraction or transfer prompt should be structured,
- how goal, priority, confidence, and compression should stay separated,
- how receiver instructions should be made explicit instead of implied.

- `docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`
- `docs/architecture/TONESOUL_PROMPT_VARIANTS.md`
- `docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md`

### 11. Continuity import and receiver lane

Open these when the question is:

- what a later agent may safely `ack`, `apply`, or `promote`,
- how continuity surfaces decay across minutes, days, or weeks,
- which continuity surfaces are most dangerous to over-import.

- `docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`
- `docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`
- `docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md`
- `docs/plans/tonesoul_continuity_followup_candidates_2026-03-29.md`

### 12. Council realism and calibration lane

Open these when the question is:

- how independent the current council really is,
- whether a confidence surface is descriptive or calibrated,
- which adversarial or deliberation-quality upgrades are safe now versus blocked.

- `docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`
- `docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`
- `docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md`
- `docs/plans/tonesoul_council_realism_followup_candidates_2026-03-29.md`

## Retrieval Order

1. Start in the entrypoint lane.
2. Move to the canonical architecture lane when making system claims.
3. Move to governance/execution when implementing or verifying behavior.
4. Move to the observable-shell and axiom challenge lane when overclaim risk or constitutional challengeability is the issue.
5. Move to the council deliberation discipline lane when replayable verdict structure or deliberation depth is the issue.
6. Move to the context continuity adoption lane when the question is no longer "how do I hand off now" but "what should continuity mean in ToneSoul."
7. Move to the continuity import and receiver lane when the question is no longer only "what should continue" but "what may the receiver safely import or let decay."
8. Move to the council realism and calibration lane when a verdict sounds stronger than its real independence or confidence backing.
9. Move to the prompt discipline skeleton lane when the question is no longer "what should transfer" but "how should the prompt be built."
10. Move to documentation governance and convergence contracts when restructuring docs.
11. Prefer generated status surfaces over stale prose when checking current posture.

## Current Rule

Do not flatten all docs into one undifferentiated search space.

The same repository contains:

- entrypoints
- constitutions
- runtime contracts
- cleanup governance
- generated status snapshots
- private-boundary notes

This map exists so those roles stay legible.
