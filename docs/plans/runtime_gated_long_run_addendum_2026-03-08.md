# Runtime-Gated Long Run Addendum

## The Missing Step

After `runtime_probe_watch` existed as a repeatable preflight ritual, ToneSoul still lacked one thing:

- a first-class long-run entrance that refused to begin without that ritual

Without this, preflight remained advisory. Operators could remember to run it, but the system itself still had no opinion about whether long-running autonomy should require it.

## Why A Dedicated Wrapper

`scripts/run_autonomous_registry_long_run.py` exists to encode one orchestration rule:

- verify runtime first
- then begin the real autonomous schedule

This rule belongs in orchestration, not inside generic schedule primitives.

## Budget Continuity

The first live version of the wrapper exposed a subtle but important flaw:

- preflight used a 2-second runtime budget
- the downstream schedule silently reverted to the generic 10-second probe budget

That is a governance lie.

It means the system says:

- "I verified readiness under budget A"

and then immediately acts under:

- budget B

So the wrapper now inherits the preflight timeout into the real schedule unless the operator explicitly overrides it.

## Result

The long-run gate is now meaningful in two senses:

- it can block execution before a real run starts
- it preserves budget continuity between the verifying ritual and the verified run

That turns preflight from a recommendation into an actual operating contract.
