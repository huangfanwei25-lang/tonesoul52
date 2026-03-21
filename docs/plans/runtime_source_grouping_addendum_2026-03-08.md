# Runtime Source Grouping Addendum

> Date: 2026-03-08
> Status: Applied

## Why This Exists

After `refreshable_artifacts` and `private_memory_review` were both reduced to zero unknowns,
the main remaining blocker was no longer classification but review shape.

`runtime_source_changes` was still one large lane containing:

- core runtime code
- repo governance scripts
- API delivery surfaces
- autonomous verification runners
- skill contracts
- support tooling

That is too much signal to treat as one reviewable unit.

## The Rule

The runtime lane should not be settled path-by-path.

It should be settled as a small set of reviewable change groups that preserve coupling:

1. governance / pipeline / LLM runtime
2. perception / ingest
3. autonomous verification runtime
4. repo governance and settlement
5. API contract surface
6. skill and registry contracts
7. supporting runtime and math
8. tooling/editor drift

## Why This Matters

Tests and scripts are not independent cleanup noise.

For example:

- `tests/test_unified_pipeline_v2_runtime.py` belongs with `tonesoul/unified_pipeline.py`
- `tests/test_run_true_verification_host_tick.py` belongs with weekly host-tick orchestration
- `tests/test_verify_skill_registry.py` belongs with the skill registry contract

If the settlement layer splits those paths only by directory, humans are forced to rebuild the
real changesets manually after every interruption.

## Result

`scripts/run_runtime_source_change_report.py` now emits:

- `docs/status/runtime_source_change_groups_latest.json`
- `docs/status/runtime_source_change_groups_latest.md`

The report is intentionally non-destructive. It does not stage, discard, or move files. It only
answers the next governance question:

> Which runtime changes belong together when the worktree is eventually settled into reviewable batches?
