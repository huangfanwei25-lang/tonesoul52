# True Verification Experiment Entrypoint Addendum

## Why A Weekly Entrypoint Exists

After `runtime_probe_watch` and `run_autonomous_registry_long_run.py`, ToneSoul already had:

- a repeatable runtime gate
- a reusable long-run primitive

But Phase 7 still lacked one thing:

- a first-class weekly experiment entrance that encoded the intended ritual as policy instead of operator memory

Without that entrance, "run the one-week True Verification experiment" remained a social instruction, not an executable contract.

## What This Wrapper Owns

`scripts/run_true_verification_experiment.py` owns only four things:

- experiment identity
- default cadence
- artifact namespace
- fresh-start behavior

It does not own:

- runtime preflight logic
- registry schedule logic
- governance thresholds

Those remain delegated to the existing lower-level wrappers and profiles.

## Default Operating Envelope

The wrapper promotes the Phase 7 proposal into executable defaults:

- duration: 7 days
- wake interval: 3 hours
- default profile: `security_watch`

When the operator does not explicitly set `--max-cycles`, the wrapper derives:

- `planned_cycles = ceil(days * 24 / wake_interval_hours)`

So the weekly experiment becomes a governed cadence, not a remembered CLI recipe.

## Why Fresh State Matters Here Too

A weekly experiment entrance should describe one experiment, not a blended sediment of previous attempts.

So the wrapper clears its own long-run history/state/latest-dashboard artifacts by default and makes reuse explicit via:

- `--reuse-experiment-state`

This preserves the same rule already established for runtime preflight:

- verification and experiment rituals should default to isolation
- historical accumulation should be a deliberate operator choice

## Result

Phase 7 now has a proper top-level entrance:

- preflight is mandatory by default
- weekly cadence is encoded
- artifact roots are stable
- experiment identity survives beyond stdout

That means the system can now say "start the weekly True Verification run" in one governed command, instead of relying on humans to restitch the orchestration from memory.
