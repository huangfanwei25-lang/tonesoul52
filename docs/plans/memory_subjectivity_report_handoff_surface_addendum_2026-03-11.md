# Memory Subjectivity Report Handoff Surface Addendum (2026-03-11)

> Purpose: define the fast-resume handoff surface for the main subjectivity report artifact.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already aligned handoff surfaces across:

- review batch
- tension grouping

The plain subjectivity report still started from raw metrics.

That meant the broadest operator artifact was still the slowest to resume.

## Core Rule

The top-level subjectivity report may expose a compact handoff block and one
single-line status surface.

This layer may classify the report as:

- `empty_report`
- `observational_only`
- `settled_or_reviewed`
- `deferred_monitoring`
- `action_required`

These are report-level shapes, not new promotion states.

## Guardrails

This phase must remain:

- artifact-level
- read-only
- metric-derived

It must **not**:

- redefine unresolved counts
- reinterpret reviewed settlement
- replace the existing metrics tables

## Architectural Conclusion

After this phase, all three main subjectivity artifacts answer the same first
question before showing details:

- what shape is the queue/report in
- does it require operator action now
- what is the shortest truthful line that summarizes it
