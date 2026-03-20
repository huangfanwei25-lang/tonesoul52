# Codex Handoff

**Phase**: 584-587 Reflection Loop + ThinkingTier Routing
**Date**: 2026-03-20
**Status**: completed and regression-verified

## What Changed
- Phase 584 introduced `ReflectionVerdict`, `MAX_REVISIONS`, and `REFLECTION_TENSION_THRESHOLD` in `tonesoul/reflection.py`, plus `UnifiedPipeline._self_check()` for VowEnforcer, council, and tension-delta review.
- Phase 585 connected a bounded reflection loop into `UnifiedPipeline.process()`, added `build_revision_prompt()`, and wrote reflection history into `dispatch_trace["reflection_count"]`, `dispatch_trace["reflection_verdicts"]`, and `dispatch_trace["reflection_verdict"]`.
- Phase 586 added `ThinkingTier`, `resolve_thinking_tier()`, and `LLMRouter.chat_with_tier()` in `tonesoul/llm/router.py`. Initial generation now routes through local/cloud tiers and records `dispatch_trace["thinking_tier"]`.
- Phase 587 added `ReflectionStats`, severity-aware revision routing, a cloud floor for already-escalated alert sessions, `dispatch_trace["reflection_tiers"]`, and sectioned `dispatch_trace["reflection_stats"]`.

## Behavioral Notes
- Initial generation uses `ThinkingTier.LOCAL` for `AlertLevel.CLEAR` / `L1`, and `ThinkingTier.CLOUD` for `L2` / `L3`.
- Revision turns escalate to cloud when `verdict.severity >= 0.5`.
- If the initial alert-selected tier is already cloud, revision turns stay on cloud even when a later verdict is low severity.
- `LLMRouter` now respects manually injected clients when backend metadata is absent, preventing tests or explicit DI paths from touching live LM Studio / Gemini accidentally.

## Files Added
- `tests/test_reflection.py`
- `tests/test_reflection_loop.py`
- `tests/test_thinking_tier.py`
- `tests/test_reflection_integration.py`

## Files Updated
- `tonesoul/reflection.py`
- `tonesoul/llm/router.py`
- `tonesoul/unified_pipeline.py`
- `tests/test_unified_pipeline_governance_delegate.py`
- `tests/test_unified_pipeline_llm_router.py`
- `tests/test_reflection_loop.py`
- `tests/test_unified_pipeline_v2_runtime.py` was not edited, but it caught the injected-client routing regression during validation.
- `task.md`

## Validation History
- After Phase 584:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2537 passed, 6 warnings
- After Phase 585:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2548 passed, 6 warnings
- After Phase 586 targeted verification:
  `ruff check tonesoul tests` -> passed
  `pytest tests/test_thinking_tier.py tests/test_unified_pipeline_llm_router.py tests/test_reflection_loop.py tests/test_unified_pipeline_v2_runtime.py -q` -> 23 passed, 2 warnings
- Final after Phase 587:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2564 passed, 6 warnings

## Test Count Notes
- Live baseline before this work was `2526 passed`.
- Reflection / router work increased the suite to `2564 passed` (`+38` tests total).
- The task's forecast counts (`2540`, `2555`, `2570`, `2580`) did not match the live worktree baseline exactly; recorded counts above are the actual verified numbers.

## Remaining Warnings
- Hypothesis warns that `.hypothesis` is skipped because `pytest.ini` replaces default `norecursedirs`.
- `requests` reports the existing dependency-version warning.
- `tonesoul/market/data_ingest.py` still emits the existing `datetime.utcnow()` deprecation warning.

## Guardrail Notes
- `AGENTS.md`, `CODEX_PROTOCOL.md`, `AXIOMS.json`, and `tonesoul/inter_soul/` were not modified.
- Existing unrelated worktree changes, including `tonesoul/drift_tracker.py`, were left untouched.
