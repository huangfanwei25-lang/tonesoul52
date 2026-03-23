# Document Convergence Master Plan (2026-03-23)

> Purpose: define the full multi-wave repository documentation convergence program so ToneSoul can be cleaned up incrementally without losing authority boundaries.
> Status: active master plan for documentation convergence beyond the first-wave cleanup.
> Last Updated: 2026-03-23

---

## Why A Master Plan Exists

The repository is no longer in the "one cleanup pass" stage.

We now have:

- generated inventory and collision reports
- explicit contracts for engineering mirrors, paradox fixtures, basename divergence, and private-memory shadows
- a growing backlog of metadata gaps across authored docs
- enough structure that future cleanup should follow a stable wave sequence instead of ad hoc file picking

This document is the program-level plan above the individual cleanup phases.

## Current Baseline

Current machine-readable baseline comes from:

- `docs/status/doc_convergence_inventory_latest.json`
- `docs/status/doc_authority_structure_latest.json`
- `docs/status/engineering_mirror_ownership_latest.json`
- `docs/status/paradox_fixture_ownership_latest.json`
- `docs/status/private_memory_shadow_latest.json`

Current posture at the time of this plan:

- authored doc surfaces: `2206`
- basename collisions: `27`
- total missing `Purpose`: `281`
- total missing `Last Updated` / date hints: `196`
- core authority map tracked surfaces with complete metadata: `28 / 28`

## Program Invariants

1. Do not merge by filename alone.
2. Do not hand-edit generated `docs/status/*_latest.*` artifacts.
3. Do not touch protected human-managed files in this convergence lane:
   - `AGENTS.md`
   - `HANDOFF.md`
   - `MEMORY.md`
4. Do not mutate private memory data during public cleanup.
5. Prefer explicit ownership and boundary contracts over mass renames.

## Workstreams

### A. Metadata Backfill Program

Goal:
- reduce missing metadata on public and high-authority docs in controlled waves

Current status:
- entrypoints and the core authority map are already normalized
- public backlog remains large, so cleanup must continue in batches

Wave order:
1. high-authority architecture / governance docs
2. public ADR / continuity / architecture-history docs
3. public narrative / showcase / explanation docs
4. external-facing guides and trust-policy docs
5. philosophy / narrative map / module map docs
6. lower-priority drafts and historical notes

### B. Ownership and Boundary Contracts

Goal:
- keep duplicate-like surfaces governed instead of repeatedly rediscovered

Current contracts:
- `docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md`
- `docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md`
- `docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`
- `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`
- `docs/architecture/HISTORICAL_DOC_LANE_POLICY.md`

Ongoing rule:
- maintain these contracts before proposing structural moves

### C. Retrieval Structure and Authority Maps

Goal:
- make it obvious which doc lane to open first

Current maps:
- `docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md`
- `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`

Remaining task:
- keep these maps synchronized with later cleanup waves and major repo shifts

### D. Historical and Draft Labeling

Goal:
- stop historical reviews, public drafts, and superseded plans from reading like current policy

Action pattern:
- add short metadata
- explicitly label historical / draft / superseded posture
- avoid rewriting the whole body unless correctness demands it
- when generated historical lanes appear in backlog, prefer lane-level policy and reports over per-file manual backfill

### E. Final Convergence Gates

Goal:
- turn the cleanup program into a maintained steady state

Done condition:
- doc inventory is no longer dominated by missing metadata on high-authority/public docs
- collision families remain contract-governed
- future agents can start from structure maps and generated status artifacts instead of raw search

## Execution Sequence

### Stage 1. Stabilize authority surfaces

Already largely complete:
- entrypoints
- core architecture anchors
- key governance contracts
- ownership maps for mirror and shadow families

### Stage 2. Drain the public metadata queue

Run repeated metadata waves against the inventory sample head.

Per wave:
1. pick the next 5-10 public docs from the sample head
2. add `Purpose` and `Last Updated`
3. regenerate the inventory
4. confirm those docs disappeared from the sample head

### Stage 3. Reclassify historical and draft docs

After the metadata queue meaningfully shrinks:
- add clearer `historical`, `draft`, or `superseded` notes
- reduce retrieval confusion without destroying project memory

### Stage 4. Review remaining backlog by lane

When public backlog is lower:
- group remaining gaps by lane
- decide whether each lane needs metadata, archive treatment, or a new boundary rule

## Immediate Next Queue

At the time of writing, the next public docs near the sample head are:

- `docs/EXTERNAL_PR_GUIDE.md`
- `docs/EXTERNAL_SOURCE_TRUST_POLICY.md`
- `docs/GITHUB_INTRO_DRAFT.md`
- `docs/GLOBAL_TRACKING_BOARD.md`
- `docs/GOLDEN_LOG.md`
- `docs/HONESTY_MECHANISM.md`
- `docs/INTEGRATION_AUDIT_DRAFT.md`
- `docs/IRON_LAWS_PERSONA.md`

These should be the next metadata wave unless a new higher-priority contract issue appears.

## How To Work This Plan

If you are a later agent:

1. Open `docs/status/doc_convergence_inventory_latest.json`
2. Open `docs/status/doc_authority_structure_latest.json`
3. Open this master plan
4. Execute the next smallest safe wave
5. Regenerate artifacts and move the queue forward

This plan is successful if cleanup becomes boring, traceable, and repeatable.
