# Codex Handoff

**Phase**: 578-581 Deprecated Removal Cleanup
**Date**: 2026-03-20
**Status**: completed and regression-verified

## What Changed
- Phase 578 removed the two thinnest deprecated wrappers: `tonesoul/council_adapter.py` and `tonesoul/tonesoul_llm.py`, plus their deprecated-only tests.
- Phase 579 moved `build_council_summary` into `tonesoul/council/runtime.py`, updated `tonesoul/frame_router.py`, deleted `tonesoul/role_council.py`, and kept the transcript key `role_council` unchanged.
- Phase 580 removed the `UnifiedCore` compatibility chain: `tonesoul/unified_core.py`, `tonesoul/_legacy/unified_core_compat.py`, `_legacy/__init__.py`, the related tests, and repo-root helper `fix_nonlocal.py`. `examples/demo_loop_integration.py` now demonstrates `UnifiedPipeline`.
- Phase 581 removed deprecated market modules `tonesoul/market/forecaster.py` and `tonesoul/market/gold_detector.py`, deleted their tests, and converted legacy scripts into explicit exit notices.

## Script Behavior Changes
- `scripts/run_gold_scan.py` now exits with: `run_gold_scan.py: GoldDetector has been removed. See task.md Phase 581.`
- `scripts/run_market_sweep.py` now exits with: `run_market_sweep.py: GoldDetector has been removed. See task.md Phase 581.`
- `scripts/test_dream_engine_5289.py` now exits with: `test_dream_engine_5289.py: MarketDreamEngine has been removed. See task.md Phase 581.`
- Script coverage was updated to assert these exit notices in `tests/test_run_market_sweep.py` and `tests/test_run_market_removed_scripts.py`.

## Validation History
- After Phase 578:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2568 passed, 9 warnings
- After Phase 579:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2567 passed, 9 warnings
- After Phase 580:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2545 passed, 8 warnings
- Final after Phase 581:
  `ruff check tonesoul tests` -> passed
  `ruff check scripts/run_gold_scan.py scripts/run_market_sweep.py scripts/test_dream_engine_5289.py tests/test_run_market_sweep.py tests/test_run_market_removed_scripts.py` -> passed
  `pytest tests/ -x --tb=short -q` -> 2526 passed, 6 warnings

## Notes
- Final warning set no longer includes deprecated `forecaster`, `gold_detector`, or `UnifiedCore` imports. Remaining warnings are the existing Hypothesis directory notice, the `requests` dependency warning, and `tonesoul/market/data_ingest.py` using `datetime.utcnow()`.
- `tonesoul/inter_soul/` was not modified in this cleanup pass.
- There was an existing worktree modification in `tonesoul/drift_tracker.py`; it was left untouched.
