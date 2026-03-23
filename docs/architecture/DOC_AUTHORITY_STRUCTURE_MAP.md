# Documentation Authority Structure Map

> Purpose: define the retrieval-oriented structure of ToneSoul's documentation so later agents can tell entrypoints, canonical anchors, governance contracts, and generated status surfaces apart.
> Status: active documentation authority map for convergence cleanup.
> Last Updated: 2026-03-23

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

## Retrieval Order

1. Start in the entrypoint lane.
2. Move to the canonical architecture lane when making system claims.
3. Move to governance/execution when implementing or verifying behavior.
4. Move to documentation governance and convergence contracts when restructuring docs.
5. Prefer generated status surfaces over stale prose when checking current posture.

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
