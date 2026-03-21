# True Verification Governance Surface — 真實驗證治理表面

> 合併日期：2026-03-19
> 原始 addendum 數：17
> 時間跨度：2026-03-12 ~ 2026-03-15
> 合併者：痕 (Hén)

週度任務狀態工件的 handoff 擴展：runtime lineage、Scribe 整合、settlement 鏡像、可認可性。

---

## 目錄

1. `true_verification_repo_healthcheck_handoff_addendum_2026-03-12.md`
2. `true_verification_runtime_lineage_handoff_addendum_2026-03-12.md`
3. `true_verification_task_runtime_lineage_card_addendum_2026-03-12.md`
4. `true_verification_task_status_line_handoff_addendum_2026-03-12.md`
5. `true_verification_task_status_refreshable_preview_addendum_2026-03-12.md`
6. `true_verification_task_status_settlement_handoff_addendum_2026-03-12.md`
7. `true_verification_dream_alignment_addendum_2026-03-14.md`
8. `true_verification_scribe_anchor_handoff_addendum_2026-03-14.md`
9. `true_verification_scribe_handoff_addendum_2026-03-14.md`
10. `true_verification_scribe_problem_route_addendum_2026-03-14.md`
11. `true_verification_scribe_problem_route_optionality_addendum_2026-03-14.md`
12. `true_verification_scribe_problem_route_secondary_addendum_2026-03-14.md`
13. `true_verification_scribe_repo_healthcheck_addendum_2026-03-14.md`
14. `true_verification_scribe_settlement_preview_addendum_2026-03-14.md`
15. `true_verification_scribe_settlement_topline_addendum_2026-03-14.md`
16. `true_verification_weekly_admissibility_handoff_addendum_2026-03-15.md`
17. `true_verification_weekly_artifact_policy_handoff_addendum_2026-03-15.md`

---

## 1. 原始檔案：`true_verification_repo_healthcheck_handoff_addendum_2026-03-12.md`

# True Verification Repo Healthcheck Handoff Addendum (2026-03-12)

## Why

The weekly task-status artifact already exposes a compact host-facing handoff:

- `handoff.queue_shape = weekly_host_status`
- `primary_status_line`
- `runtime_status_line`

Settlement surfaces now pass that preview through correctly, but the top repo
governance surface still makes later agents do one extra hop:

- read `repo_healthcheck_latest.json`
- then reopen the weekly task-status artifact to understand runtime posture

That is unnecessary, because `repo_healthcheck` already executes the weekly
task-status producer as a blocking check on Windows hosts.

## Chosen Seam

Use `scripts/run_repo_healthcheck.py`, not
`scripts/run_runtime_source_change_report.py`.

Why this seam is cleaner:

- `repo_healthcheck` already owns the direct execution of
  `scripts/report_true_verification_task_status.py --strict`
- the healthcheck artifact is already the top repo-governance status snapshot
- `runtime_source_change_groups` is about dirty review scope, not live weekly
  runtime truth

## Minimal Contract

Do not teach repo governance how to reopen task-status artifacts by path.
Do not add a task-status-specific adapter.

Instead, let `repo_healthcheck` capture generic JSON handoff surfaces from
checks that already emit compact status payloads, then mirror only the compact
handoff facts it finds:

- `queue_shape`
- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`
- `requires_operator_action`

At the top level, prefer a queue-shape-based mirror for
`weekly_host_status`, not a file-path-based parser.

## Boundaries

Allowed:

- parse structured stdout from machine-readable child checks
- expose generic healthcheck `handoff_previews`
- expose one compact `weekly_host_status_preview` selected by
  `queue_shape == weekly_host_status`

Not allowed:

- reading raw wake-up history here
- reopening `true_verification_task_status_latest.json` by path
- inventing a new task-status-only schema
- moving market or subjectivity logic into repo governance

## Intended Effect

A later agent reading only `repo_healthcheck_latest.json` or
`repo_healthcheck_latest.md` should be able to answer, at a glance:

1. Are repo-level gates green?
2. What is the current weekly host-status line?
3. Is the weekly runtime posture resumed / failure-burdened / attention-needed?

---

## 2. 原始檔案：`true_verification_runtime_lineage_handoff_addendum_2026-03-12.md`

# True Verification Runtime Lineage Handoff Addendum (2026-03-12)

## Why

Wake-up runtime lineage is already visible in:

- `AutonomousWakeupLoop` runtime state
- dream observability wake-up views
- schedule-facing observability and tension budget

But the compact `true_verification` summaries are still too thin. A host-facing
artifact can currently tell whether a weekly tick passed, yet still miss whether
that tick resumed an existing wake-up session or arrived while a failure streak
was already in progress.

That creates a handoff gap:

- observability knows the runtime context
- host / verification summaries do not

## Minimal Contract

Do not teach every settlement artifact how to parse raw wake-up history.
Instead, widen the existing compact verification summary just enough to carry:

- `autonomous_payload.runtime_state`
- `tension_budget.observation.max_consecutive_failure_count`

This keeps the handoff compact while preserving the most important runtime
lineage facts:

- which wake-up session produced the latest verification cycle
- whether the session was resumed
- how much failure pressure had already accumulated

## Boundaries

This seam must remain a summary-layer change only.

Allowed:

- compact runtime lineage in `tonesoul/true_verification_summary.py`
- host-tick / experiment / task-status artifacts inheriting that summary

Not allowed:

- new subjectivity semantics
- new settlement policy
- direct parsing of raw wake-up files inside unrelated settlement reports
- treating runtime state as proof of subjecthood

## Intended Effect

Later agents should be able to read one compact verification artifact and answer:

1. Was this a fresh weekly tick or a resumed wake-up session?
2. Was the latest schedule result already under cross-heartbeat failure pressure?
3. Did the verification artifact preserve runtime context without importing the
   whole dashboard payload?

---

## 3. 原始檔案：`true_verification_task_runtime_lineage_card_addendum_2026-03-12.md`

# True Verification Task Runtime Lineage Card Addendum (2026-03-12)

## Why

`true_verification` compact summaries already preserve:

- `autonomous_payload.runtime_state`
- `tension_budget.observation.max_consecutive_failure_count`

But the host-facing task-status artifact still forces operators to dig through
nested summary payloads to answer a simple question:

- was the latest weekly result a resumed wake-up session?
- was failure pressure already accumulating?

That is unnecessary friction for the highest-level handoff surface.

## Minimal Surface

Do not widen the task-status artifact with raw history.
Add one compact `runtime_lineage` mirror that extracts only the latest useful
facts from:

- `artifacts.host_tick_summary.schedule`
- `artifacts.schedule_snapshot`

The card should stay small and deterministic:

- `session_id`
- `session_resumed`
- `next_cycle`
- `consecutive_failures`
- `max_consecutive_failure_count`
- `tension_status`
- `latest_available_source`

## Boundaries

Allowed:

- task-status level runtime lineage mirror
- deterministic extraction from already-summarized artifacts

Not allowed:

- parsing raw wake-up history files here
- new policy or governance decisions
- treating runtime lineage as subjectivity proof

## Intended Effect

An operator or later agent reading only the task-status artifact should be able
to see, at a glance, whether the current weekly chain is continuing an older
wake-up session and whether runtime instability was already building.

---

## 4. 原始檔案：`true_verification_task_status_line_handoff_addendum_2026-03-12.md`

# True Verification Task Status Line Handoff Addendum (2026-03-12)

## Why

`true_verification_task_status_latest.json` now carries compact
`runtime_lineage`, but top-level handoff surfaces still need to read nested JSON
to understand the weekly runtime posture.

That is one layer too deep for:

- operators scanning status artifacts
- refreshable handoff previews
- later agents doing quick coordination reads

## Minimal Surface

Expose deterministic top-level status lines directly on the task-status
artifact:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`

Also expose a minimal `handoff` mirror so existing preview tooling can pick up
the artifact without learning a new schema.

## Boundaries

Allowed:

- string summaries derived from already-compacted task-status fields
- a stable `handoff.queue_shape` for preview tooling

Not allowed:

- new runtime policy
- raw wake-up history parsing
- inflating task-status into a full dashboard

## Intended Effect

The weekly task-status artifact should become readable at a glance and
previewable by existing settlement / refreshable tooling without extra adapters.

---

## 5. 原始檔案：`true_verification_task_status_refreshable_preview_addendum_2026-03-12.md`

# True Verification Task Status Refreshable Preview Addendum (2026-03-12)

## Why

`true_verification_task_status_latest.json` now exposes preview-ready top-level
handoff strings:

- `primary_status_line`
- `runtime_status_line`
- `handoff.queue_shape = weekly_host_status`

But `run_refreshable_artifact_report.py` still treats the whole
`docs/status/true_verification_weekly/` namespace as one broad regeneration
bucket. That is too coarse for the task-status artifact, which is now one of the
most operator-facing summaries in the weekly chain.

## Minimal Change

Promote `true_verification_task_status_latest.json` to an exact refreshable
producer entry so the refreshable report can:

- name the direct regenerator
- keep using the existing handoff-preview extraction
- expose the weekly host-status preview without introducing a new adapter

## Boundaries

Allowed:

- exact producer mapping for the task-status artifact
- focused preview regression

Not allowed:

- new preview schema
- new settlement policy
- special-case parsing beyond the existing handoff surface

## Intended Effect

If the task-status artifact is dirty, refreshable preview tooling should now
treat it as a first-class refreshable status artifact and surface its weekly
host-status line directly.

---

## 6. 原始檔案：`true_verification_task_status_settlement_handoff_addendum_2026-03-12.md`

# True Verification Task Status Settlement Handoff Addendum (2026-03-12)

## Why

The weekly task-status artifact is now a preview-ready refreshable artifact with:

- a direct producer
- `handoff.queue_shape = weekly_host_status`
- deterministic top-level status lines

That means settlement surfaces must stop speaking as if refreshable previews are
always subjectivity artifacts.

## Minimal Change

Keep the data model intact, but update settlement language and coverage so:

- refreshable preview counts are described as generic handoff previews
- worktree settlement is explicitly proven to pass through weekly host-status previews
- repo-governance settlement is explicitly proven to mirror them without
  relabeling them as subjectivity

## Boundaries

Allowed:

- wording correction
- focused pass-through regressions

Not allowed:

- new settlement policy
- changing `subjectivity_focus_preview` semantics
- adding task-status-specific settlement adapters

## Intended Effect

Downstream agents can read settlement artifacts and understand that:

- subjectivity focus remains a special preview
- refreshable handoff previews are broader than subjectivity alone
- weekly host-status artifacts now travel through the same handoff chain cleanly

---

## 7. 原始檔案：`true_verification_dream_alignment_addendum_2026-03-14.md`

# True Verification Dream Alignment Addendum (2026-03-14)

## Why

Repo healthcheck and settlement summaries can now state whether weekly host
status and dream observability agree on the dominant repair family.

But the weekly host-facing artifact itself still cannot say that directly, which
means the source layer remains less self-descriptive than the mirrors above it.

## Goal

Let `true_verification_task_status_latest.json` passively state its current
alignment with the latest dream observability artifact.

## Chosen Strategy

1. Read `dream_observability_latest.json` as an optional passive status source.
2. Reuse `build_dream_weekly_alignment_line(...)`.
3. Surface the result on weekly task status:
   - top-level `dream_weekly_alignment_line`
   - `handoff.dream_weekly_alignment_line`

## Boundaries

Allowed:

- passive reads of the latest dream observability status artifact
- route-family comparison only
- focused tests for aligned carry-through

Not allowed:

- letting dream observability read weekly status in return
- turning alignment into a new gate or policy
- re-running dream observability from weekly status generation

## Intended Effect

The weekly host-facing artifact should be able to say, on its own, whether it
is currently aligned with the latest dream posture, rather than relying on
higher mirrors to infer that relationship.

---

## 8. 原始檔案：`true_verification_scribe_anchor_handoff_addendum_2026-03-14.md`

# True Verification Scribe Anchor Handoff Addendum (2026-03-14)

## Why

Upper governance mirrors already know how to read an optional weekly
`anchor_status_line`, and they already reserve summary space for a weekly anchor
posture.

But the weekly source artifact still does not declare that line itself. The
result is a silent gap: upper layers are prepared to mirror the line, while the
weekly source keeps dropping it.

## Goal

Carry the Scribe lead anchor through the compact weekly lane:

- wakeup summary
- compact true-verification summary
- weekly task-status top level
- weekly `handoff`

## Chosen Strategy

1. Preserve the Scribe anchor under a wakeup-local key:
   `scribe_anchor_status_line`.
2. Keep the weekly top-level field generic: `anchor_status_line`.
3. Reuse the same source-prefixed format as the other weekly Scribe compact
   lines, for example `host_tick | anchor | ...`.

## Boundaries

Allowed:

- one new compact line in wakeup/weekly summaries
- focused regressions for wakeup summary and weekly task-status carry-through

Not allowed:

- introducing anchor-specific routing logic
- changing Scribe artifact payload schema
- widening this into a broader weekly grammar refactor

## Intended Effect

When a later agent reads the weekly host-facing artifact, `weekly_anchor_posture`
should finally reflect a real source-declared line instead of an always-empty
placeholder slot.

---

## 9. 原始檔案：`true_verification_scribe_handoff_addendum_2026-03-14.md`

# True Verification Scribe Handoff Addendum (2026-03-14)

## Why

The wake-up loop can now write Scribe chronicles, and dream observability can
already mirror the resulting compact posture.

But the host-facing weekly `true_verification` surfaces still stop one layer too
early:

- they preserve runtime lineage
- they preserve schedule tension posture
- they do **not** yet preserve whether wake-up actually wrote a chronicle, or
  what internal posture that chronicle represented

That means an operator can read the weekly status chain and still miss the most
recent inner-writing posture unless they reopen the dream dashboard.

## Goal

Carry one compact Scribe handoff from autonomous wake-up into the weekly
`true_verification` host-facing chain.

The host-facing layer should be able to show:

- whether Scribe was triggered
- the latest compact Scribe status
- the generation mode
- the latest state-document posture
- whether the latest available source is a chronicle pair or companion only

## Chosen Strategy

1. Extend `tonesoul.true_verification_summary` so compact schedule summaries keep
   one bounded `wakeup_summary`.
2. Extract the Scribe handoff only from that compact wake-up summary.
3. Mirror it into `true_verification_task_status_latest.json` as a new
   `scribe_status_line` plus a machine-readable `scribe_handoff` block.
4. Prefer the same source ordering already used by runtime lineage:
   `schedule_snapshot` first, then `host_tick`.

## Boundaries

Allowed:

- copying `scribe_*` fields already present in wake-up summary
- adding one host-facing `scribe_status_line`
- preserving compact machine-readable Scribe handoff metadata

Not allowed:

- reparsing chronicle markdown or companion JSON at report time
- rerunning Scribe from `true_verification` scripts
- turning weekly host status into a full replay of wake-up history

## Intended Effect

After this phase, a host/operator should be able to read the weekly
`true_verification` status artifact and immediately see not just runtime
continuity, but also the latest internal chronicle posture carried by wake-up.

---

## 10. 原始檔案：`true_verification_scribe_problem_route_addendum_2026-03-14.md`

# True Verification Scribe Problem Route Addendum (2026-03-14)

## Why

The upper preview chain can now mirror optional `problem_route_status_line`, but
the weekly host-facing artifact still only emits:

- `primary_status_line`
- `runtime_status_line`
- `scribe_status_line`
- `artifact_policy_status_line`

That means weekly status can describe Scribe posture without carrying the first
repair surface that posture implies.

## Goal

Let the weekly true-verification artifact expose the latest Scribe problem route
as a compact top-line and handoff field.

## Chosen Strategy

1. Preserve one namespaced route line inside wakeup summaries:
   `scribe_problem_route_status_line`.
2. Keep that line when compacting host-tick / schedule summaries.
3. Translate it once inside `report_true_verification_task_status.py` into the
   generic preview field `problem_route_status_line`.

## Boundaries

Allowed:

- copying one compact scalar line through wakeup and weekly summaries
- one weekly renderer/helper that prefixes the route with its source
- focused tests for summary compaction and task-status handoff

Not allowed:

- recomputing route-family logic outside Scribe status generation
- reopening chronicle/status artifacts during weekly report generation
- introducing a second weekly-only route schema

## Intended Effect

After this phase, the weekly host-facing artifact should be able to say not
only how Scribe ended up, but also where the first repair surface sits, so
later agents can stay on the right layer without reopening lower-level status
files.

---

## 11. 原始檔案：`true_verification_scribe_problem_route_optionality_addendum_2026-03-14.md`

# True Verification Scribe Problem Route Optionality Addendum (2026-03-14)

## Why

The weekly task-status artifact now mirrors Scribe problem routes, but the first
implementation still emits placeholder text such as `route=none` or
`route=unavailable` when no real route exists.

That breaks the preview-chain convention we already established for compact
metadata:

- carry the line when the source truly has signal
- stay silent when the signal is absent

## Goal

Make weekly `problem_route_status_line` behave like other optional handoff lines:
present when real, absent in practice when empty.

## Chosen Strategy

1. Return an empty string when weekly Scribe handoff has no concrete route.
2. Keep the existing non-empty format unchanged when a route exists.
3. Add one focused regression that proves the helper stays silent when the
   route is missing.

## Boundaries

Allowed:

- tightening route-line formatting semantics
- focused unit-style test coverage

Not allowed:

- changing the meaning of existing non-empty route lines
- adding new route families or recomputation logic

## Intended Effect

After this phase, upper preview layers will only mirror weekly problem-route
metadata when the weekly artifact actually carries a real first-repair route.

---

## 12. 原始檔案：`true_verification_scribe_problem_route_secondary_addendum_2026-03-14.md`

# True Verification Scribe Problem Route Secondary Addendum (2026-03-14)

## Why

Weekly host-facing status now carries the dominant Scribe repair route, but
mixed-signal Scribe runs can also preserve compact `secondary_route_labels`.

Those secondary hints already travel through Scribe status previews, repo
healthcheck, and settlement mirrors. The weekly artifact is now the remaining
mainline surface that still drops them.

## Goal

Let the weekly true-verification artifact carry one compact scalar field for
Scribe secondary route labels, so later agents can keep the mixed-signal route
shape without reopening lower-level Scribe status files.

## Chosen Strategy

1. Preserve one namespaced scalar in wakeup summaries:
   `scribe_problem_route_secondary_labels`.
2. Keep that scalar when compacting schedule / host-tick summaries.
3. Translate it once in `report_true_verification_task_status.py` into the
   generic weekly field `problem_route_secondary_labels`.
4. Mirror it through the weekly handoff only when non-empty.

## Boundaries

Allowed:

- one optional comma-joined scalar field for secondary route labels
- focused carry-through changes in wakeup summary, true-verification summary,
  and weekly task-status output
- focused tests for wakeup, summary compaction, and weekly handoff

Not allowed:

- recomputing route precedence outside Scribe status generation
- replacing the dominant weekly route line with a multi-route schema
- adding a second prose route line to weekly markdown/status output

## Intended Effect

After this phase, the weekly host-facing artifact should preserve not only the
dominant Scribe repair surface, but also a compact machine-readable hint about
secondary route families, keeping the mixed-signal route shape intact across
the mainline governance chain.

---

## 13. 原始檔案：`true_verification_scribe_repo_healthcheck_addendum_2026-03-14.md`

# True Verification Scribe Repo-Healthcheck Addendum (2026-03-14)

## Why

Weekly `true_verification` task status now carries a compact `scribe_status_line`,
but the higher repo-governance preview layer still mirrors only:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`

That means repo healthcheck can see the weekly scheduler/runtime posture, yet it
still hides the latest wake-up Scribe posture one layer below.

## Goal

Extend the existing passive `weekly_host_status_preview` mirror in
`repo_healthcheck` so it also preserves and renders `scribe_status_line`.

## Chosen Strategy

1. Treat `scribe_status_line` as an optional fourth compact line on generic
   handoff surfaces.
2. Keep the queue-shape selection unchanged: repo healthcheck should still pick
   the weekly preview by `queue_shape == weekly_host_status`.
3. Mirror the extra line only when it already exists in the source artifact.

## Boundaries

Allowed:

- extending generic handoff preview extraction with one optional field
- rendering the weekly Scribe line in repo healthcheck markdown
- preserving the same line in the machine-readable preview payload

Not allowed:

- special-casing repo healthcheck to reopen chronicle files
- rerunning weekly task status or Scribe during repo healthcheck rendering
- changing how the weekly preview is selected

## Intended Effect

After this phase, repo healthcheck should be able to show the latest weekly
runtime posture and the latest weekly Scribe posture together, without reopening
lower-level artifacts.

---

## 14. 原始檔案：`true_verification_scribe_settlement_preview_addendum_2026-03-14.md`

# True Verification Scribe Settlement Preview Addendum (2026-03-14)

## Why

Weekly `true_verification` task status and `repo_healthcheck` now both preserve a
compact `scribe_status_line`, but the settlement mirrors still render only:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`
- `admissibility_primary_status_line`

That means the higher settlement artifacts can show weekly runtime posture, yet
they still hide the weekly wake-up Scribe posture one layer below.

## Goal

Extend the existing settlement handoff mirrors so `scribe_status_line` can pass
through and render when it is already present on a weekly host-status preview.

## Chosen Strategy

1. Treat `scribe_status_line` as an optional fifth compact line on settlement
   handoff preview payloads.
2. Keep the existing settlement shapes intact:
   - `worktree_settlement` should continue mirroring refreshable handoff previews
   - `repo_governance_settlement` should continue mirroring worktree settlement
3. Render the extra line only when the source preview already carries it.

## Boundaries

Allowed:

- widening normalized preview payloads with one optional field
- rendering the weekly Scribe line in worktree and repo-governance settlement markdown
- preserving the same line in machine-readable settlement payloads

Not allowed:

- creating a new weekly-only settlement adapter
- re-reading chronicle files from settlement scripts
- rerunning weekly task status or Scribe during settlement rendering

## Intended Effect

After this phase, settlement artifacts should be able to show the weekly runtime
posture and the weekly Scribe posture together, without reopening lower-level
artifacts or changing the existing preview routing.

---

## 15. 原始檔案：`true_verification_scribe_settlement_topline_addendum_2026-03-14.md`

# True Verification Scribe Settlement Topline Addendum (2026-03-14)

## Why

Settlement artifacts now preserve weekly `scribe_status_line` inside handoff
preview rows, but operator-facing settlement summaries still require opening the
preview list to see it.

That keeps the data honest, yet it still leaves the weekly Scribe posture one
layer too low for a quick governance read.

## Goal

Promote the existing weekly host-status preview to a small top-line settlement
mirror so higher-level settlement artifacts can show:

- weekly host status
- weekly runtime posture
- weekly Scribe posture

without changing any preview routing.

## Chosen Strategy

1. Reuse the existing `queue_shape == weekly_host_status` preview selection.
2. Add one top-level `weekly_host_status_preview` mirror to worktree settlement.
3. Let repo-governance settlement pass that same compact preview through and
   render its three compact lines when present.

## Boundaries

Allowed:

- selecting one existing weekly preview from normalized handoff previews
- mirroring it as a top-level settlement payload field
- rendering compact summary lines from that preview

Not allowed:

- inventing a new weekly settlement adapter
- reopening true-verification artifacts from settlement scripts
- rerunning weekly task status or Scribe during settlement rendering

## Intended Effect

After this phase, settlement artifacts should not only carry weekly Scribe
posture in preview rows, but also expose it as an immediate top-line signal for
operator review.

---

## 16. 原始檔案：`true_verification_weekly_admissibility_handoff_addendum_2026-03-15.md`

# True Verification Weekly Admissibility Handoff Addendum (2026-03-15)

## Why

`true_verification_task_status_latest.json` 已經是 weekly host-facing 的來源面，
但它目前沒有被動攜帶 `subjectivity_review_batch_latest.json` 已宣告的
`admissibility_primary_status_line`。結果是上層 `repo_healthcheck` / settlement
雖然都懂這條 compact line，weekly 這條 source 本身卻說不出來。

這是來源與鏡像之間的 compact-grammar 缺口，不是新 schema。

## Decision

- weekly task-status 被動讀取 `subjectivity_review_batch_latest.json`
  的 `admissibility_primary_status_line`
- 只在來源真的有值時才帶進 weekly top-level 與 `handoff`
- `repo_healthcheck` / worktree settlement / repo-governance settlement
  的 weekly topline 與 detail mirror 一起補齊這條 line

## Constraints

- 不從 runtime / dream / task XML 推導 admissibility
- 不改動 subjectivity artifact 自己的語義
- 不新增 blocking policy，只鏡像已存在的 compact line

## Expected Effect

weekly host-facing artifact 可以誠實說出自己目前對應的 admissibility posture，
而上層治理報表也不再只在 subjectivity focus mirror 裡看得到這條線。

---

## 17. 原始檔案：`true_verification_weekly_artifact_policy_handoff_addendum_2026-03-15.md`

# True Verification Weekly Artifact Policy Handoff Addendum (2026-03-15)

## Why

`true_verification_task_status_latest.json` already source-declares
`artifact_policy_status_line`, but the weekly `handoff` omits it, and upper
weekly summary/detail mirrors therefore also omit it. This is a compact-grammar
parity gap, not a new schema request.

## Decision

Carry `artifact_policy_status_line` into weekly `handoff`, then mirror it through
weekly-specific summary and detail surfaces in repo healthcheck and settlement
reports.

## Constraints

- Reuse the existing compact line.
- No new fallback logic.
- Keep the field optional.

## Expected Effect

Weekly host-facing status can finally say not only what its runtime posture was,
but also what artifact policy governed that report, and upper governance mirrors
will stop dropping that source-declared line.

---
