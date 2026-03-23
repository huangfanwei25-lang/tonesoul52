# Memory Subjectivity Operator Status Line Addendum (2026-03-11)

> Purpose: define the one-line status surface for subjectivity queue posture, density, and revisit codes.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The operator lens improved readability, but it still occupied multiple lines.

When the branch is carrying only one or two live groups, the most useful
surface is often simpler:

- one copyable line
- one queue posture
- one density snapshot
- one revisit code

## Core Rule

The review-batch artifact may add one derived single-line status surface per
group.

This status line may include:

- `queue_posture`
- topic
- row / lineage / cycle counts
- lineage density snapshot
- one short `revisit_trigger_code`

## Guardrails

This line must remain:

- derived
- compact
- secondary to the canonical detailed fields

It must **not**:

- replace the detailed operator lens
- replace `revisit_trigger`
- introduce new decision semantics

## Architectural Conclusion

Sometimes the right response to excess context is not another classifier.

It is a shorter, more reusable sentence that preserves the same judgment.
