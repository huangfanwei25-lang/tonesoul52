# ToneSoul Fifteenth Trial Candidate Admission (2026-04-07)

> Purpose: admit one fifteenth bounded self-improvement candidate after the fourteenth trial result is visible.
> Status: admitted candidate
> Authority: planning aid only. Runtime truth remains in code, tests, and accepted architecture contracts.

---

## Admitted Candidate

- `candidate_id`: `hot_memory_pull_boundary_clarity_v1`
- `target_surface`: `hot_memory_ladder.current_pull_boundary`
- `target_consumer`: `observer_dashboard_operator_shells`

## Why This Candidate

The next latency tax is not missing memory.
It is still over-pulling.

The hot-memory ladder already says:

- which layer is parent truth
- which layer is advisory
- which layer is stale or contested

But a successor still has to infer:

- where to stop
- when Tier-1 is already enough
- when bounded handoff must be reviewed before deeper replay

This candidate exists to make that stop rule explicit.

## Baseline Story

Current hot-memory readouts show layer status, but later agents can still over-pull deeper context because the stop boundary is only implicit.

## Candidate Story

`hot_memory_ladder` should expose one bounded `current_pull_boundary` with:

- `pull_posture`
- `preferred_stop_at`
- `why_now`
- `operator_action`

This remains a latency and interpretation aid only.
It must not become a planner, retrieval myth, or deeper-pull permission system.

## Success Metric

`hot_memory_pull_boundary_probe.present and consumer_drift_report.status == aligned`

## Failure Mode Watch

- pull-boundary packaging turns into planner behavior
- it starts implying deeper pulls are authorized by default
- it starts reading like retrieval or transport truth

## Rollback Path

Remove `current_pull_boundary` packaging and fall back to layer statuses only.

## Overclaim To Avoid

Clearer hot-memory pull boundaries are not:

- better memory
- better retrieval
- stronger transport
- shared cognition

## No-Go List

This trial must not:

- widen retrieval scope
- promote replay into authority
- authorize deeper default pulls
- mutate governance truth
- imply transport or vendor-native interop
