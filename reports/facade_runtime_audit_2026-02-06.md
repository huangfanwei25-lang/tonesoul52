# Facade Runtime Audit (2026-02-06)

## Scope
- Council facade: `tonesoul/council/pre_output_council.py`
- Runtime orchestrator: `tonesoul/council/runtime.py`
- Legacy compatibility path: `role_council.run_role_council` (deprecated)

## Runtime Flow (Current)
1. `CouncilRuntime.deliberate()` builds summary and thresholds.
2. Runtime delegates to `PreOutputCouncil.validate()`.
3. Verdict is decorated with genesis fields:
   - `genesis`
   - `responsibility_tier`
   - `intent_id`
   - `is_mine`
4. Transcript and role summary are emitted for inspection.
5. Provenance ledger is updated through `ProvenanceManager`.

## Test Evidence
- `tests/test_pre_output_council.py`
- `tests/test_pre_output_council_integration.py`
- `tests/test_council_runtime.py`
- `tests/test_genesis_integration.py`
- `tests/test_self_journal.py`
- `tests/test_provenance_chain.py`

## Findings
- Runtime and facade are aligned on data flow, but there are still two entry styles:
  - modern runtime (`CouncilRuntime`)
  - legacy wrapper (`run_role_council`)
- Provenance write path exists and is covered, but external consumers may still rely on legacy verdict keys.
- Threshold adjustment in runtime is active; behavior is correct in tests but should remain observable in production logs.

## Risks
- If external integrations still parse legacy payload shape, stricter runtime outputs may appear as regressions.
- Multiple facade entry points increase maintenance burden and debugging cost.
- Character encoding inconsistencies in historical notes can reduce audit trace readability.

## Recommendations
1. Make `CouncilRuntime` the canonical public path and keep legacy wrapper as thin adapter only.
2. Add one contract test asserting verdict payload shape stability for external integrators.
3. Keep provenance and transcript fields in a stable schema with explicit version tag.
4. Continue UTF-8 cleanup for historical audit docs to preserve cross-agent readability.
