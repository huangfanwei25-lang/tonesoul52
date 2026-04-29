# Memory Subjectivity Worktree Settlement Handoff Preview Addendum (2026-03-11)

## Why This Addendum Exists

The refreshable artifact report can now mirror compact subjectivity handoff
surfaces.

But the broader worktree settlement report still treated the entire
`refreshable_artifacts` lane as one abstract cleanup category.

That meant the operator could see that the lane was dirty, yet still had to open
another artifact to understand which kind of subjectivity queue was actually
waiting underneath.

## Core Rule

`scripts/run_worktree_settlement_report.py` may reuse the refreshable lane's
existing handoff previews and attach them to the `refreshable_artifacts`
settlement lane.

The settlement report may expose:

- `refreshable_artifacts.handoff_previews`
- `refreshable_artifacts.handoff_preview_count`
- `summary.refreshable_handoff_preview_count`

## Guardrails

This remains a settlement-layer mirror only.

It must **not**:

- rebuild subjectivity state independently
- replace refreshable artifact regeneration logic
- invent a new settlement-specific queue vocabulary

The settlement lane is allowed only to surface the preview contract that the
refreshable lane already knows.

## Architectural Conclusion

After this phase, the operator can read the top-level settlement report and
still know:

- the refreshable lane is dirty
- the subjectivity report says `deferred_monitoring`
- the grouping artifact says `monitoring_queue`
- the review batch says `stable_history_only`

So the settlement layer now carries a truthful view of queue posture without
pretending to own that judgment.
