# Memory Subjectivity Repo Governance Handoff Preview Addendum (2026-03-11)

> Purpose: define the governance-facing handoff preview that surfaces subjectivity settlement state alongside repo governance signals.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The worktree settlement report can now mirror refreshable subjectivity handoff
previews.

But the repo-governance settlement report still summarized governance truth only
through:

- healthcheck gates
- attribution state
- runtime governance grouping

That left the highest governance summary disconnected from the actual queue
posture already visible one layer below.

## Core Rule

`scripts/run_repo_governance_settlement_report.py` may mirror the existing
subjectivity previews already exposed by `worktree_settlement_latest.json`.

The governance report may expose:

- `worktree_settlement.refreshable_handoff_preview_count`
- `worktree_settlement.handoff_previews`
- markdown `## Worktree Settlement Mirror`

## Guardrails

This phase remains mirror-only.

It must **not**:

- recompute subjectivity state
- reinterpret queue posture as a governance gate
- replace the worktree settlement artifact

The governance layer is allowed only to show the preview contract that the
settlement layer already knows.

## Architectural Conclusion

After this phase, the branch now supports interruption recovery across the full
operator ladder:

- report
- grouping
- batch
- settlement
- repo governance settlement

Each level still keeps its own semantic boundary, but none of them is blind to
the queue truth immediately below it.
