# RFC-002 Convergence Audit (Phase 1)

Purpose: audit the first non-breaking convergence pass from legacy UnifiedCore surfaces toward UnifiedPipeline.
Last Updated: 2026-03-23
Date: 2026-02-23  
Owner: codex  
Trace Topic: `rfc-002-unifiedcore-phase1`

## Scope

Phase 1 focuses on **non-breaking convergence**:

- keep current behavior stable
- mark legacy entry points explicitly
- document replacement path to `UnifiedPipeline`

## Inventory: UnifiedCore vs New Runtime

| Symbol | Current Role | Runtime Status | Replacement |
|---|---|---|---|
| `tonesoul.unified_core.UnifiedCore` | compatibility/test core | legacy non-runtime | `tonesoul.unified_pipeline.UnifiedPipeline` |
| `UnifiedCore.process_with_domain` | domain-prefixed compatibility wrapper | deprecated | pipeline + council capability routing |
| `UnifiedCore.process_with_correction` | loop-based self-correction wrapper | deprecated | pipeline internal deliberation flow |
| `tonesoul.unified_core.create_core` | legacy factory wrapper | deprecated | `tonesoul.unified_pipeline.create_unified_pipeline` |

## What Changed in Phase 1

1. Added explicit deprecation markers in `tonesoul/unified_core.py`.
2. Preserved behavior for compatibility and existing tests.
3. Kept `UnifiedCore.process`, `get_status`, and `reset` intact to avoid breaking:
   - `tests/test_unified_core.py`
   - `tests/test_unified_core_properties.py`
   - legacy helper usage (`tonesoul/tonesoul_llm.py`, `tonesoul/self_test.py`)

## What Changed in Phase 2

1. Created `tonesoul/_legacy/` and moved compatibility wrapper logic into:
   - `tonesoul/_legacy/unified_core_compat.py`
2. `tonesoul/unified_core.py` now keeps public API shape but delegates:
   - `process_with_domain()` -> `process_with_domain_compat()`
   - `process_with_correction()` -> `process_with_correction_compat()`
   - `create_core()` -> `create_core_compat()`
3. Marked `tonesoul/tonesoul_llm.py` as legacy with runtime deprecation warning.

## High-Risk Areas Not Moved Yet

- `UnifiedCore.process` path is still used by compatibility tests.
- `tonesoul/tonesoul_llm.py` remains legacy and import-path fragile; moving/removing now would risk collateral breakage.
- Demo/CLI code in `unified_core.py` bottom section is low-value runtime logic but harmless; defer to Phase 2 cleanup.

## Recommended Phase 2

1. Move compatibility-only wrappers into `tonesoul/_legacy/` with stable re-export shims.
2. Migrate `tonesoul_llm.py` to consume `UnifiedPipeline` or mark whole module legacy.
3. Reduce duplicated council/tension framing between older wrappers and pipeline metadata.
4. After migration, trim `UnifiedCore` surface to minimal compatibility API.
