# ToneSoul Fourteenth Trial Candidate Admission (2026-04-07)

> Purpose: admit one fourteenth bounded self-improvement candidate after the thirteenth trial result is visible.
> Status: admitted candidate
> Authority: planning aid only. Runtime truth remains in code, tests, and accepted architecture contracts.

---

## Admitted Candidate

- `candidate_id`: `claude_priority_correction_clarity_v1`
- `target_surface`: `claude_entry_adapter.priority_correction`
- `target_consumer`: `claude_style_shell`

## Why This Candidate

The current interop gap is not transport first.
It is still consumer recovery discipline.

Codex-style, dashboard, and Claude-style shells now share:

- first-hop order
- closeout attention
- mutation preflight
- consumer misread guards

But the Claude-style shell still compresses the highest-risk correction into a thinner shape than other consumers.

This candidate exists to make one bounded correction packet explicit:

- what assumption is blocked
- which surfaces to re-read now
- which bounded next-step target still follows after recovery

## Baseline Story

The Claude-compatible adapter already preserved:

- `first_hop_order`
- `must_read_now`
- `must_not_assume`
- `must_correct_first`

But a successor could still understand the warning while missing the exact bounded recovery path.

## Candidate Story

The Claude-compatible adapter should expose one `priority_correction` that preserves:

- current misread name
- trigger surface
- blocked assumption
- bounded operator action
- `re_read_now`
- `bounded_next_step_target`

This remains orientation-only packaging.
It must not become a planner, transport claim, or permission system.

## Success Metric

`claude_priority_correction_probe.present and consumer_drift_report.status == aligned`

## Failure Mode Watch

- adapter correction turns into planner behavior
- shell-specific correction drifts away from the same first-hop contract
- the new surface starts sounding like vendor-native interop

## Rollback Path

Remove `priority_correction` packaging and fall back to `must_correct_first` only.

## Overclaim To Avoid

Clearer Claude-style correction packaging is not:

- vendor-native Codex/Claude interop
- shared cognition
- stronger transport
- stronger authority

## No-Go List

This trial must not:

- widen `task.md` authority
- mutate governance truth
- add new permissions
- add hidden planner logic
- imply official first-party cross-vendor memory fusion
