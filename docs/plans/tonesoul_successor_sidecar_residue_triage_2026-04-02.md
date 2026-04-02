# ToneSoul Successor Sidecar Residue Triage (2026-04-02)

> Purpose: record which successor/hot-memory sidecar files were integrated, which were retired, and why.
> Authority: cleanup and supersession note. Does not outrank runtime code, tests, or integrated contracts.

---

## Decision Summary

### Integrated

- `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md`

Why:

- current runtime already exposes `hot_memory_ladder` and `hot_memory_decay_map`
- the file could be rewritten to match live layer names and use-posture semantics
- it explains current behavior instead of proposing a second theory

### Retired

- `docs/architecture/TONESOUL_OBSERVER_WINDOW_MISREAD_AND_CORRECTION_MAP.md`
- `docs/architecture/TONESOUL_SUCCESSOR_MUTATION_BOUNDARY_AND_CLOSEOUT_CONTRACT.md`
- `docs/plans/tonesoul_successor_hot_memory_followup_candidates_2026-04-02.md`

Why:

- they overlapped too heavily with already-integrated contracts and live runtime readouts
- parts of them were already superseded by completed work:
  - compaction closeout surfacing
  - shared-edit preflight
  - low-drift anchor source precedence
- keeping them as parallel sidecar files would create multiple competing successor stories

---

## Useful Fragments Preserved

The residue files were not discarded blindly.

The following useful ideas were kept through integration or short-board rotation:

- `observer stable != execution permission`
- compaction closeout must outrank smooth summary
- shared mutation needs a bounded preflight
- low-drift anchor requires one explicit source-order rule
- hot-memory should be layered by authority and decay posture

These now live in active surfaces and contracts rather than sidecar drafts.

---

## What Remains Out Of Scope

- `.claude/`

This remains local residue and is not part of the active successor/hot-memory story.
