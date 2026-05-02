# Memory Subjectivity Refreshable Handoff Preview Addendum (2026-03-11)

> Purpose: define the refreshable handoff preview that summarizes subjectivity artifacts and regeneration state.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already taught three subjectivity artifacts to speak in compact
handoff form:

- report
- grouping
- batch

But the higher-level refreshable artifact lane still only said whether those
files were dirty and how to regenerate them.

That meant the operator could see that subjectivity artifacts existed, but not
what shape of queue they currently described.

## Core Rule

`scripts/run_refreshable_artifact_report.py` may read existing latest artifact
JSON files and surface compact handoff previews when those artifacts already
publish a handoff contract.

The refreshable report may expose:

- `handoff_previews`
- `summary.handoff_preview_count`
- markdown `## Handoff Previews`

## Guardrails

This phase remains:

- read-only
- artifact-derived
- preview-only

It must **not**:

- recompute subjectivity judgments
- invent queue shapes on behalf of another artifact
- replace artifact-specific status reports

The refreshable lane is only allowed to mirror the handoff surface that already
exists elsewhere.

## Architectural Conclusion

After this phase, the operator can open one broader refreshable report and still
see the three subjectivity queue readings immediately:

- report-level status
- grouping-level status
- batch-level status

So the branch now preserves semantic altitude while reducing reopening cost.
