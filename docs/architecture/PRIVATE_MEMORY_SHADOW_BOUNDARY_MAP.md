# Private Memory Shadow Boundary Map

> Purpose: declare the active-vs-shadow boundary for nested private-memory index lanes so public convergence work does not mutate memory data by accident.
> Status: active private-memory shadow boundary map for convergence cleanup.
> Last Updated: 2026-03-23

---

## Contract

- Active root: `memory/.hierarchical_index/`
- Shadow root: `memory/memory/.hierarchical_index/`
- Read order:
  1. read `memory/.hierarchical_index/` first when you need the currently active hierarchical-index lane
  2. read `memory/memory/.hierarchical_index/` only to confirm whether a nested shadow copy still exists
  3. if the two differ, do not auto-merge or auto-delete anything in this public convergence lane
- Source-of-truth rule:
  - treat `memory/.hierarchical_index/` as the active repo-local lane
  - treat `memory/memory/.hierarchical_index/` as a deferred legacy or restored shadow lane until a dedicated private-memory cleanup phase is explicitly in scope

## Why This Boundary Exists

This is not a normal duplicate-doc problem.

The nested `memory/memory/` lane sits inside protected memory territory.
That means a same-basename collision such as `vows_meta.json` cannot be handled with the same workflow as public docs, engineering mirrors, or paradox fixtures.

The correct rule is:

- observe the shadow
- report the shadow
- do not mutate the shadow during public cleanup

## Current Observed Shadow Family

- `memory/.hierarchical_index/vows_meta.json`
- `memory/memory/.hierarchical_index/vows_meta.json`
- `memory/.hierarchical_index/hierarchical.index`
- `memory/memory/.hierarchical_index/hierarchical.index`

The JSON metadata pair is the basename collision currently surfaced by the document convergence inventory.
The paired index file shows the same nested-shadow pattern at the binary store level, so the cleanup boundary must be defined at the directory lane, not just at one filename.

## Allowed Actions In This Lane

1. Generate reports that compare the active and shadow lanes.
2. Record file counts, hashes, JSON-shape differences, and shadow posture.
3. Update architecture docs, status docs, and onboarding guidance so later agents know the boundary.
4. Defer actual mutation until a dedicated private-memory cleanup phase is explicitly approved and in scope.

## Forbidden Actions In This Public Convergence Phase

1. Do not delete files from either lane.
2. Do not auto-sync the shadow from the active lane.
3. Do not rewrite `vows_meta.json` or `hierarchical.index` in order to "clean up duplicates."
4. Do not treat the shadow lane as a normal public-doc convergence target.

## Retrieval Guidance

- If you only need to know whether a private shadow exists, open `docs/status/private_memory_shadow_latest.json`.
- If you are already in same-basename triage, open:
  1. `spec/governance/basename_divergence_registry_v1.json`
  2. `docs/status/basename_divergence_distillation_latest.json`
  3. `docs/status/private_memory_shadow_latest.json`
- If you are not in an explicit private-memory cleanup phase, stop at the report layer and do not mutate the data files.
