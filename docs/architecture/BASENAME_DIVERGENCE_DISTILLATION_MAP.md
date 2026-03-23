# Basename Divergence Distillation Map

> Purpose: distill same-basename but semantically different files into explicit governance categories so later agents stop guessing whether they are duplicates.
> Status: active divergence map for convergence cleanup.
> Last Updated: 2026-03-22

---

## What "Distillation" Means Here

This is not model distillation.
This is document-surface distillation:

- collect same-basename collisions
- separate true mirrors from semantic divergence
- compress the result into a small set of explicit rules
- let later agents read the rules instead of improvising from raw file search

## Distilled Categories

### 1. Constitutional vs philosophical

- Example: `constitution/manifesto.md` vs `docs/philosophy/manifesto.md`
- Rule:
  - keep both
  - do not merge by basename
  - constitutional text governs system priority order
  - philosophy text frames public ethical meaning

### 2. Public grounding vs private thread

- Example: `docs/philosophy/academic_grounding.md` vs `memory/narrative/threads/academic_grounding.md`
- Rule:
  - keep both
  - do not sync by content
  - public philosophy docs support citations and public retrieval
  - private memory threads capture evolving narrative or reflective context

### 3. Generated namespace duals

- Example:
  - `docs/status/autonomous_registry_schedule_latest.json`
  - `docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json`
- Rule:
  - keep both
  - treat directory namespace as the differentiator
  - do not hand-edit generated artifacts just to remove basename collisions

### 4. Private backend duals

- Example:
  - `memory/.semantic_index/metadata.json`
  - `memory/vectors/metadata.json`
- Rule:
  - keep both
  - treat them as different backend metadata lanes
  - do not normalize them into one file during public convergence work

### 5. Private shadow / legacy duplicates

- Example:
  - `memory/.hierarchical_index/vows_meta.json`
  - `memory/memory/.hierarchical_index/vows_meta.json`
- Rule:
  - do not edit during this public cleanup lane
  - mark as deferred private-memory shadow cleanup
  - require a dedicated memory-lane review later
  - open `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`
  - confirm live posture in `docs/status/private_memory_shadow_latest.json`

## Retrieval Order

1. Open `docs/status/doc_convergence_inventory_latest.json`
2. Open `spec/governance/basename_divergence_registry_v1.json`
3. Open `docs/status/basename_divergence_distillation_latest.json`
4. If the pair sits inside nested private-memory lanes, open `docs/status/private_memory_shadow_latest.json`
5. Only then decide whether a same-basename pair should be renamed, preserved, or deferred

## Current Principle

Same basename is a search symptom, not a truth claim.
The right question is:

`are these files actually duplicates, or are they different authority surfaces that happen to share a name?`

This map exists so the answer becomes explicit.
