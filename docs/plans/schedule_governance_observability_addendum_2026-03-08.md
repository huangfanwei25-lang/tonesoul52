# Schedule Governance Observability Addendum

Date: 2026-03-08
Scope: Phase 149 schedule-side observability for cooldown and LLM backoff

## 1. Problem

Phase 148 already split scheduler consequences into two control surfaces:

- governance/category cooldown
- global LLM backoff

But the dashboard still saw only journal traces and wake-up summaries. That meant a human
operator could observe runtime tension without directly seeing how the scheduler chose to
react.

## 2. Boundary

The dashboard must not reverse-engineer scheduler intent from wake-up latency alone.

- wake-up artifacts describe what the dream cycle experienced
- schedule artifacts describe how the scheduler reacted

These are related, but they are not interchangeable.

So the correct observability boundary is:

- `journal + wakeup` for experiential traces
- `schedule_history + schedule_state` for cadence/governance consequences

## 3. Contract

The enriched dashboard now accepts two optional schedule inputs:

- `schedule_history_path`
- `schedule_state_path`

They are optional so dream-only callers remain backward compatible.

When present, the dashboard surfaces four schedule curves:

- governance cooldown applied
- governance cooldown deferred
- LLM backoff requested
- LLM backoff active

This lets operators distinguish:

- "the scheduler cooled a category because governance tension spiked"
- "the scheduler degraded reflection globally because the runtime substrate was unstable"

## 4. Artifact Law

Schedule history and schedule state answer different questions:

- history explains what happened on each schedule tick
- state explains what remains active after the tick

Therefore the dashboard should show both:

- time-series curves from schedule history
- present-tense status from schedule state

If one is missing, the other must not be fabricated.

## 5. Historical Compatibility

Older schedule artifacts may predate the LLM backoff split. In those cases:

- governance cooldown curves may appear
- LLM backoff curves may remain zero or absent in effect

That is historical schema reality, not a dashboard defect.

## 6. Design Law

A governance dashboard is trustworthy only when each layer is allowed to speak in its own
artifact language.

- dream artifacts should not impersonate scheduler policy
- scheduler artifacts should not impersonate dream semantics

Observability becomes clearer when explanation follows the same layer boundaries as control.
