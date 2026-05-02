# Memory Subjectivity Runtime Summary Addendum (2026-03-10)

## Why This Addendum Exists

Phase C already introduced reporting helpers, but those helpers still lived one step outside the normal runtime flow.

That meant the branch could inspect subjectivity distribution manually, yet `sleep_consolidate()` and the autonomous wake-up loop still reported only operational counts such as promoted, cleared, and gated.

This addendum closes that gap.

## Core Rule

If subjectivity structure is important enough to validate and report, it should also appear in the normal consolidation summary.

That does **not** mean subjectivity should steer runtime policy automatically.

It means the runtime should at least expose what kind of memory it has just carried forward.

## Narrow Runtime Wiring

This phase keeps the change small:

- `SleepResult` now includes `subjectivity_summary`
- `sleep_consolidate()` computes that summary from the current source after consolidation
- `AutonomousWakeupLoop` lifts two high-signal counts into cycle summary:
  - `consolidation_unresolved_tension_count`
  - `consolidation_vow_count`

The full `subjectivity_summary` remains in the consolidation payload for deeper inspection.

## Guardrail

This is runtime reporting, not runtime self-authorization.

The phase still does **not**:

- auto-promote `tension` into `vow`
- rank recall by `subjectivity_layer`
- widen public HTTP/API contracts
- sync private memory corpus into this repository

## Architectural Conclusion

The system is now using its memory structure in one more honest way:

after consolidation, it can say not only how much memory moved, but what kind of subjectivity those memories currently represent.
