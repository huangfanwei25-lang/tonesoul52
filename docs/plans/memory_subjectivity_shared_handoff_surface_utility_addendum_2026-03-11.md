# Memory Subjectivity Shared Handoff Surface Utility Addendum (2026-03-11)

## Why This Addendum Exists

By this point, three different subjectivity artifacts already exposed the same
operator-facing contract:

- `handoff`
- `primary_status_line`
- `status_lines`

The semantics were intentionally different:

- report speaks in broad status language
- grouping speaks in triage language
- batch speaks in review language

But the implementation surface had started to duplicate the same assembly and
markdown rendering logic in multiple places.

## Core Rule

The branch may centralize the shared handoff surface mechanics into one helper
layer, as long as semantic classification remains local to each artifact.

The shared utility may handle:

- status-line normalization
- top-level `primary_status_line` selection
- `handoff` block assembly
- markdown rendering for `## Handoff`
- markdown rendering for `## Status Lines`

## Guardrails

This utility layer must stay structural only.

It must **not**:

- decide queue posture for report, grouping, or batch
- reinterpret unresolved, deferred, or settled semantics
- flatten triage language into review language
- flatten review language into report language

Each artifact still owns its own classification vocabulary.

## Architectural Conclusion

After this phase, the branch no longer depends on three parallel copies of the
same handoff plumbing.

That keeps interruption recovery aligned across artifacts while preserving the
semantic altitude of each one.
