# Codex Handoff

**Phase**: 588-590 Tension-Adaptive Debate Rounds
**Date**: 2026-03-21
**Status**: completed and regression-verified

## What Changed
- Phase 588 added `tonesoul/deliberation/adaptive_rounds.py`, `RoundResult`, and multi-round metadata on `SynthesizedResponse`.
- Phase 589 converted deliberation from single-pass synthesis into adaptive 1/2/3-round debate, where round 2+ receives `prior_viewpoints` and `debate_round` context without changing any perspective `think()` signature.
- Phase 590 wired adaptive debate telemetry into `UnifiedPipeline`, including `dispatch_trace["deliberation_rounds"]`, `dispatch_trace["tensions_per_round"]`, and `dispatch_trace["debate_converged_early"]`, while keeping downstream persona outcome recording on the final dominant voice.

## Behavioral Notes
- Debate rounds are selected from first-round aggregate tension: `< 0.3 -> 1`, `0.3..0.6999 -> 2`, `>= 0.7 -> 3`.
- Guardian veto still short-circuits immediately, but any completed rounds remain attached to `round_results` for traceability.
- Round 2+ perspectives can see prior viewpoints and adjust their reasoning rather than re-running as isolated copies of round 1.
- Early convergence stops additional rounds once a later round falls below the low-tension threshold.
- API responses expose `adaptive_debate` only when more than one round was actually used.

## Files Added
- `tonesoul/deliberation/adaptive_rounds.py`
- `tests/test_adaptive_rounds.py`
- `tests/test_adaptive_deliberation.py`
- `tests/test_adaptive_pipeline.py`

## Files Updated
- `tonesoul/deliberation/types.py`
- `tonesoul/deliberation/__init__.py`
- `tonesoul/deliberation/perspectives.py`
- `tonesoul/deliberation/engine.py`
- `tonesoul/unified_pipeline.py`
- `tests/test_deliberation_types.py`
- `tests/test_deliberation_engine.py`
- `task.md`

## Validation History
- After Phase 588:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2576 passed, 6 warnings
- After Phase 589:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2589 passed, 6 warnings
- Final after Phase 590:
  `ruff check tonesoul tests` -> passed
  `pytest tests/ -x --tb=short -q` -> 2597 passed, 6 warnings

## Test Count Notes
- Live baseline before this work was `2564 passed`.
- Adaptive deliberation increased the suite to `2597 passed` (`+33` tests total).
- The task's forecast counts (`2580`, `2600`, `2615`) did not line up exactly with the live worktree baseline, so the numbers above are the actual verified counts.

## Remaining Warnings
- Hypothesis warns that `.hypothesis` is skipped because `pytest.ini` overrides default `norecursedirs`.
- `requests` still emits the existing dependency-version warning.
- `tonesoul/market/data_ingest.py` still emits the existing `datetime.utcnow()` deprecation warning.

## Guardrail Notes
- `AGENTS.md`, `CODEX_PROTOCOL.md`, `AXIOMS.json`, and everything under `tonesoul/inter_soul/` were left untouched.
- No perspective `think()` signature was changed.
