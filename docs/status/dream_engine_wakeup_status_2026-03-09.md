# Dream Engine / Wake-up Status (2026-03-09)

## Scope

Phase 138 completed the host-side wiring for Dream Engine persistence, wake-up scheduling, and dashboard observability on `feat/env-perception`.

## Delivery Summary

- Dream Engine collisions now persist through `MemoryWriteGateway.write_payload()` as `dream_collision` working-memory records under `MemorySource.CUSTOM`.
- Persisted dream-collision payloads now carry provenance with:
  - `dream_cycle_id`
  - `source_url`
  - `stimulus_record_id`
  - `generated_at`
- `DreamCycleResult` now exposes:
  - `dream_cycle_id`
  - `write_gateway` write summary (`written`, `skipped`, `rejected`, `record_ids`, `reject_reasons`)
- `AutonomousWakeupLoop` now adds:
  - periodic `sleep_consolidate()` execution
  - configurable `consolidate_every_cycles`
  - configurable consecutive-failure breaker (`failure_threshold`, `failure_pause_seconds`)
  - cycle summaries for collision success rate, gateway write counts, token totals, consolidation status, and breaker pauses
- `dream_observability.py` now surfaces:
  - collision success rate
  - write-gateway written/skipped/rejected counters
  - prompt/completion/total token usage
  - recent-cycle consolidation and pause flags

## Scheduler Defaults

- `interval_seconds`: `10800.0`
- `consolidate_every_cycles`: `3`
- `failure_threshold`: `3`
- `failure_pause_seconds`: `3600.0`

## Validation

- `python -m pytest tests/ -x --tb=short -q` -> `1457 passed`
- `ruff check tonesoul tests` -> passed

## Notes

- Routing-only tests that instantiate `UnifiedPipeline` now pin `TONESOUL_MEMORY_EMBEDDER=hash` in-test so Windows CI/local runs do not crash on heavyweight sentence-transformer native loads during compute/runtime assertions.
- No `.env`, `.db`, `.jsonl`, or private memory artifacts were added for this phase.
