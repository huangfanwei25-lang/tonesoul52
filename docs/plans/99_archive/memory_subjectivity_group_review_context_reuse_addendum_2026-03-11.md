# Memory Subjectivity Group Review Context Reuse Addendum (2026-03-11)

> Purpose: allow group-review workflows to reuse prior reviewed context as an explicit operator action.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already has a safe operator lane for batch `deferred` / `rejected`
settlement.

What it still lacks is ergonomic continuity.

Once a semantic group re-opens with a fresh `candidate` slice, the operator has
to copy the same reviewed status, basis, and notes back into the CLI by hand.

That is not a semantic gap. It is an operator debt.

## Core Rule

The group-review lane may reuse the latest matched reviewed decision for the
same semantic group, but only as an explicit operator action.

This means:

- no automatic settlement
- no silent carry-forward write
- no new review semantics

It only means the CLI can resolve:

- latest reviewed status
- latest review basis
- latest review notes

from the matched group instead of forcing manual copy/paste.

## Guardrails

This lane must remain:

- explicit
- auditable
- group-scoped

It must **not**:

- infer a decision when no prior reviewed context exists
- silently mix reused context with partially overridden explicit text
- promote `vow` at batch scope

If no latest matched reviewed decision exists, reuse must fail loudly.

## Architectural Conclusion

Carry-forward should stay human-governed.

But human-governed does not require repeated manual transcription of the same
decision text every time the same deferred or rejected pattern reappears.
