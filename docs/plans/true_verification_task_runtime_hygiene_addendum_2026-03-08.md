# True Verification Task Runtime Hygiene Addendum

## Why This Addendum Exists

Weekly True Verification now has two distinct operating surfaces:

- a human-facing host tick CLI used for direct debugging
- a scheduler-facing host task used for quiet, non-interactive execution

Treating those as the same thing looked simpler, but it produced two different failures:

- tests polluted live weekly artifacts by writing into the same `*_latest.json` roots
- the Windows scheduled task initially executed the noisy human CLI and terminated with
  `0xC000013A`

The correction was to separate operating modes instead of adding heuristics.

## Operating Doctrine

`run_true_verification_host_tick.py` remains the manual entrypoint.

- it is allowed to stay legible and verbose
- it is the right place for operators to inspect one bounded cycle by hand

`run_true_verification_host_tick_task.py` is the scheduler-only wrapper.

- it suppresses import-time warnings and runtime stdout/stderr before loading the real host tick
- it exists because host schedulers need quiet, bounded launch contracts
- it should be the default target of rendered/installed Task Scheduler definitions

## Artifact Doctrine

In `host_trigger_mode = single_tick`, `true_verification_experiment_latest.json` is not the live
truth of execution.

- it describes the wrapper-style weekly envelope
- it may be absent, stale, or irrelevant during host-driven operation
- `true_verification_task_status_latest.json` therefore ignores it in single-tick mode

The live host truth comes from:

- Task Scheduler runtime readback
- `true_verification_host_tick_latest.json`
- the weekly dream/schedule artifacts produced by that tick

## Architectural Conclusion

Autonomy becomes operationally trustworthy only after three boundaries are explicit:

- human debugging versus scheduler execution
- wrapper summaries versus live host-tick artifacts
- mutation success versus post-mutation readback

Without those separations, the repo still runs, but operators no longer know which evidence is
real.
