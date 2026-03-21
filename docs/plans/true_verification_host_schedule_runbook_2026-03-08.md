# True Verification Host Schedule Runbook

## Why This Is Host-Driven

The weekly True Verification experiment depends on:

- local `soul.db`
- local `self_journal.jsonl`
- local LLM readiness
- long-lived artifact continuity

So this is not a good fit for GitHub Actions. GitHub can verify code and contracts, but it
should not impersonate a local runtime substrate that it does not actually own.

The resilient operating model is:

- host scheduler wakes ToneSoul every 3 hours
- one invocation runs one bounded preflight + one real schedule cycle
- continuity lives in explicit experiment artifacts under `true_verification_weekly`

## Canonical Host Tick Command

Run from repo root:

```bash
python scripts/run_true_verification_host_tick.py --strict
```

This command:

- runs exactly one host-driven tick
- executes runtime preflight first
- runs one real registry schedule cycle
- reuses the weekly experiment artifact roots

Use this once manually before handing control to Task Scheduler so you can confirm the local
runtime is healthy enough to begin the experiment.

## Start A Fresh Weekly Experiment

If you want to discard the previous weekly experiment state before the next tick:

```bash
python scripts/run_true_verification_host_tick.py --fresh-experiment-state --strict
```

This clears the weekly long-run state/history/latest-dashboard artifacts before the tick.

## Windows Task Scheduler Recommendation

Render the canonical task definition first:

```bash
python scripts/render_true_verification_task_scheduler.py --strict
```

This writes:

- `docs/status/true_verification_weekly/true_verification_task_scheduler.xml`
- `docs/status/true_verification_weekly/true_verification_task_scheduler_latest.json`

Then register it with Task Scheduler using the generated XML:

```powershell
schtasks /Create /TN "ToneSoul True Verification Weekly" /XML "C:\Users\user\Desktop\倉庫\docs\status\true_verification_weekly\true_verification_task_scheduler.xml" /F
```

Or use the safe installer wrapper first:

```bash
python scripts/install_true_verification_task_scheduler.py --strict
```

That command performs a dry-run by default and writes the exact pending install command to:

- `docs/status/true_verification_weekly/true_verification_task_scheduler_install_latest.json`

Only use this when you want to mutate Task Scheduler:

```bash
python scripts/install_true_verification_task_scheduler.py --apply --strict
```

After installation, read back the live host task status into a repo artifact:

```bash
python scripts/report_true_verification_task_status.py --strict
```

This writes:

- `docs/status/true_verification_weekly/true_verification_task_status_latest.json`

The task runs:

```powershell
python C:\Users\user\Desktop\倉庫\scripts\run_true_verification_host_tick.py --strict
```

Recommended task settings:

Generated templates and live Task Scheduler registrations now use the quiet wrapper
`run_true_verification_host_tick_task.py --strict` instead of the human-facing host tick CLI.

- Manual operators still use `run_true_verification_host_tick.py` for direct debugging.
- Task Scheduler now uses the quiet wrapper so import-time warnings and large runtime payloads
  do not become part of the host execution contract.

- Trigger: daily, repeat every `3 hours`
- Duration: `Indefinitely`
- Run whether user is logged in or not: optional, depending on local LLM host setup
- Stop the task if it runs longer than: `2 hours`
- Do not start a new instance if one is already running

The important part is not the GUI path; it is the contract:

- one host tick per trigger
- no internal sleep loop
- continuity stored in artifacts, not in the task scheduler itself

## What To Watch

The main weekly artifact roots are:

- `docs/status/true_verification_weekly/true_verification_host_tick_latest.json`
- `docs/status/true_verification_weekly/true_verification_task_status_latest.json`
- `docs/status/true_verification_weekly/dream_observability_latest.json`
- `docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json`
- `memory/autonomous/true_verification_weekly/dream_wakeup_history.jsonl`
- `memory/autonomous/true_verification_weekly/registry_schedule_history.jsonl`

Preflight-specific artifacts remain isolated under:

- `docs/status/true_verification_weekly/preflight/`
- `memory/autonomous/true_verification_weekly/preflight/`

## Compact Summary Contract

The host-facing `latest.json` artifacts are now intentionally compact.

- `true_verification_host_tick_latest.json` is a summary, not a full nested replay:
  - keeps `gate`
  - keeps compact `preflight` / `schedule`
  - keeps `result_count`, `latest_result`, and state counters
  - does not recursively inline full lower-layer `results/state` bodies
- `true_verification_task_status_latest.json` is also a summary:
  - joins live Task Scheduler truth with compact artifact readback
  - points operators toward detailed evidence instead of duplicating it

Detailed evidence still lives in:

- `docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json`
- `docs/status/true_verification_weekly/dream_observability_latest.json`
- `docs/status/true_verification_weekly/preflight/autonomous_registry_schedule_latest.json`
- `docs/status/true_verification_weekly/preflight/dream_observability_latest.json`

## Operator Ritual

Use this reading order during the weekly experiment:

1. Refresh live host truth:

```bash
python scripts/report_true_verification_task_status.py --strict
```

2. Read `true_verification_task_status_latest.json` first:
   - confirm `task_registered = true`
   - confirm scheduler `State`, `LastTaskResult`, `NextRunTime`
   - confirm `artifact_policy.host_trigger_mode = single_tick`

3. Read `true_verification_host_tick_latest.json` second:
   - inspect `gate.status`
   - inspect compact `preflight.result_count` and `preflight.latest_result`
   - inspect compact `schedule.result_count` and `schedule.latest_result`

4. Read `dream_observability_latest.json` third:
   - look for category cooldown vs global LLM backoff as separate curves
   - look for friction / Lyapunov / token or preflight-latency movement

5. Only if something looks wrong, open the detailed schedule/preflight artifacts listed above.

## Operational Reading

- `true_verification_task_status_latest.json` ignores `true_verification_experiment_latest.json`
  when `host_trigger_mode = single_tick`, because wrapper summaries are not the live truth of
  host-driven execution.

- If preflight blocks, the host tick should fail before the real schedule advances.
- If LLM runtime degrades, scheduler state may continue rotating sources while reflective
  execution backs off.
- If governance tension rises, category cooldown may activate independently of runtime state.

That separation is intentional. Runtime incapacity and governance tension are different failure
surfaces and should remain legible as different curves in the weekly artifacts.

## Triage

- If `task_registered = false` or Task Scheduler readback fails:
  - rerun `python scripts/install_true_verification_task_scheduler.py --strict`
  - if the dry-run looks correct, rerun with `--apply`
  - then rerun `python scripts/report_true_verification_task_status.py --strict`

- If `gate.status = blocked`:
  - open `docs/status/true_verification_weekly/preflight/autonomous_registry_schedule_latest.json`
  - inspect compact `preflight.latest_result.tension_budget`
  - confirm whether the block came from LLM readiness or another runtime preflight cause

- If `schedule.latest_result.tension_budget.governance_breached = true`:
  - inspect `dream_observability_latest.json`
  - treat this as governance pressure, not runtime outage

- If `schedule.latest_result.tension_budget.llm_breached = true` or `llm_policy.active = true`:
  - inspect preflight dashboard and schedule summary together
  - treat this as runtime degradation/backoff, not a source-registry trust failure
