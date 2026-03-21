# True Verification Task Scheduler Install Addendum

## Why An Installer Exists

After Phase 156, the repo could render a correct Task Scheduler XML definition, but operators
still had to manually convert that artifact into an installation command.

That leaves one more avoidable gap:

- the repo knows how the task should be defined
- but the final installation step is still reconstructed by hand

## What The Installer Owns

`scripts/install_true_verification_task_scheduler.py` owns only the installation boundary:

- optional template refresh
- explicit dry-run summary
- explicit `schtasks` invocation when `--apply` is provided

It does not own:

- XML structure policy
- host tick semantics
- weekly experiment cadence logic beyond what is already delegated to the renderer

## Default Safety Posture

The installer defaults to:

- render or refresh the XML template
- write an install summary artifact
- stop before touching Task Scheduler

Only `--apply` turns the summary into a real system mutation.

That means the repo can verify:

- what XML would be used
- what exact `schtasks` command would run
- where the resulting install evidence is stored

before any host scheduler state changes occur.

## Result

The weekly True Verification stack now has three explicit layers:

- render the scheduler template
- dry-run or apply the installer
- execute host-driven ticks at runtime

This keeps installation legible and reversible instead of hiding it inside ad hoc shell history.
