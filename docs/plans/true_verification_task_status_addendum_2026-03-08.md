# True Verification Task Status Addendum

## Why Status Reporting Exists

After Phase 158, the weekly task was real. But being real is not the same as being legible.

Operators still needed a way to answer:

- is the task currently enabled?
- when will it run next?
- how did the last run end?
- what weekly experiment artifacts does that live task connect to?

If those answers live only inside the Task Scheduler GUI, then the experiment is running but
not yet operationally observable from the repo.

## What The Reporter Owns

`scripts/report_true_verification_task_status.py` is read-only. It joins:

- live Task Scheduler readback
- the latest task-install artifact
- the latest task-template artifact
- the latest host tick / experiment / schedule artifacts

It does not:

- mutate Task Scheduler
- rerun the experiment
- infer host state from stale files alone

## Result

The weekly experiment now has three host-facing layers:

- install the scheduled task safely
- read back the live registered definition
- publish a joined status snapshot for ongoing operations

That means the host scheduler is no longer a hidden sidecar. It is part of the same observable
artifact surface as the rest of the weekly True Verification stack.
