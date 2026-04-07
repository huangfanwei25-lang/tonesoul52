# ToneSoul Seventeenth Trial Candidate Admission (2026-04-07)

> Purpose: admit one seventeenth bounded self-improvement candidate after the sixteenth trial result is visible.
> Status: admitted candidate
> Authority: planning aid only. Runtime truth remains in code, tests, and accepted architecture contracts.

---

## Admitted Candidate

- `candidate_id`: `status_panel_operator_copy_clarity_v1`
- `target_surface`: `dashboard.status_panel.operator_posture`
- `target_consumer`: `dashboard_operator_shell`

## Why This Candidate

The status panel already follows the tier model structurally.

The remaining risk is more mundane and more dangerous than it looks:

- operator-facing copy still carries display noise
- telemetry labels are less readable than the surrounding shell
- the panel's `primary vs secondary` boundary is not stated sharply enough

That weakens first-hop trust even when the structure is correct.

## Baseline Story

Current status-panel hierarchy is good, but human-readable operator copy and telemetry labels still lag behind the rest of the dashboard shell.

## Candidate Story

`dashboard.status_panel` should expose:

- a clean operator note
- one explicit `primary_rule`
- one explicit `secondary_rule`
- readable telemetry labels

This remains dashboard packaging only.
It must not become:

- a second control plane
- a stronger authority lane
- a new planner story

## Success Metric

`status_panel_probe.present and consumer_drift_report.status == aligned`

## Failure Mode Watch

- cleaner copy hides primary-vs-secondary boundaries instead of clarifying them
- the status panel starts reading like the parent action surface instead of a tier-aligned readout
- telemetry polish is mistaken for stronger runtime truth

## Rollback Path

Restore the prior status-panel copy and drop the extra operator-boundary cues.

## Overclaim To Avoid

Cleaner status-panel copy is not:

- better reasoning
- better runtime truth
- better memory transport
- stronger authority

## No-Go List

This trial must not:

- change tier structure
- widen self-improvement authority
- flatten secondary telemetry into operator truth
- turn the dashboard into a browser-only control plane
