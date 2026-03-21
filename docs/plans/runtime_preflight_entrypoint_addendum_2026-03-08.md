# Runtime Preflight Entrypoint Addendum

## The Problem

Once `runtime_probe_watch` existed as a named schedule profile, one problem still remained:

- the operator still had to remember a generic multi-flag command
- repeated runs silently accumulated prior state/history

That meant the system had a policy, but not yet a ritual.

## Why A Dedicated Entrypoint

`scripts/run_runtime_probe_watch.py` exists to do one thing:

- run the governed runtime probe the same way every time

It should not invent new scheduling logic. It should only compress the operational ceremony around an already approved policy surface.

## Fresh By Default

Preflight is a verdict about the current operating moment.

If a dedicated preflight runner quietly reuses yesterday's schedule state and history, then:

- `cycles_run` stops meaning "this verification sample"
- dashboard totals stop meaning "this probe"
- the operator can no longer tell whether the result came from today's failure or yesterday's residue

So this runner defaults to clearing its own artifacts unless `--reuse-state` is explicitly requested.

## Design Rule

Named profiles encode policy.

Dedicated preflight entrypoints encode ritual.

Both are required if a governance system wants runtime verification that is repeatable, legible, and not dependent on operator folklore.
