# True Verification Task Scheduler Template Addendum

## Why A Template Is Needed

After the host-driven tick runner existed, weekly True Verification already had the right
runtime semantics:

- one invocation
- one runtime gate
- one real cycle

But Windows task registration was still living as prose inside a runbook.

That is not enough. Once an operational ritual becomes recurring, the registration surface
must also become versioned and reproducible.

## What The Template Owns

`scripts/render_true_verification_task_scheduler.py` owns only the host registration layer:

- task name
- start boundary
- repeat interval
- repeat duration
- execution time limit
- command wiring to `run_true_verification_host_tick.py --strict`

It does not own:

- runtime gate logic
- weekly experiment policy
- registry schedule policy

Those remain in the lower orchestration seams.

## Why XML Instead Of Direct Registration

The generator deliberately renders a Task Scheduler XML definition instead of silently
registering a task during development.

That keeps the contract auditable:

- the repo can test and diff the template
- the operator can inspect the exact command and cadence before installation
- registration remains an explicit human-controlled step

## Result

Weekly True Verification now has:

- a runbook
- a host tick runner
- a versioned Task Scheduler template

So the host-driven operating ritual is no longer trapped in terminal history or GUI muscle
memory. It is expressed as code, documentation, and generated artifacts together.
