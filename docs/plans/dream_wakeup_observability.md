# Dream & Wakeup Observability — 夢境與喚醒可觀測性

> Purpose: collect observability addenda for Dream Engine, Wakeup lineage, and Scribe-facing telemetry surfaces.
> Last Updated: 2026-03-23

> 合併日期：2026-03-19
> 原始 addendum 數：13
> 時間跨度：2026-03-12 ~ 2026-03-15
> 合併者：痕 (Hén)

Dream Engine 可觀測性儀表板、Wakeup 運行時 lineage、Scribe 整合、週度對齊線的完整鏈路。

---

## 目錄

1. `wakeup_runtime_lineage_observability_addendum_2026-03-12.md`
2. `wakeup_scribe_integration_addendum_2026-03-13.md`
3. `wakeup_scribe_observability_addendum_2026-03-13.md`
4. `dream_observability_anchor_topline_addendum_2026-03-14.md`
5. `dream_observability_governance_mirror_addendum_2026-03-14.md`
6. `dream_observability_handoff_addendum_2026-03-14.md`
7. `dream_observability_scribe_anchor_addendum_2026-03-14.md`
8. `dream_observability_settlement_topline_addendum_2026-03-14.md`
9. `dream_weekly_alignment_line_addendum_2026-03-14.md`
10. `dream_weekly_alignment_preview_passthrough_addendum_2026-03-14.md`
11. `dream_weekly_alignment_refreshable_handoff_fallback_addendum_2026-03-14.md`
12. `wakeup_scribe_secondary_observability_addendum_2026-03-14.md`
13. `dream_focus_anchor_render_addendum_2026-03-15.md`

---

## 1. 原始檔案：`wakeup_runtime_lineage_observability_addendum_2026-03-12.md`

# Wakeup Runtime Lineage Observability Addendum (2026-03-12)

## 為什麼還要再做一步

前一個 phase 已經讓 wake-up runtime 有 persisted session state，但如果這些資訊只留在 state JSON 或 snapshot 裡，後續 agent 仍然很容易把每次短 heartbeat 誤看成一次全新的 autonomous run。

所以這一步的目的不是新增 runtime 能力，而是把 runtime lineage 變成可讀 artifact。

## 要被看見的是什麼

對語魂系統來說，最重要的不是「看起來連續」，而是能誠實地說明：

- 這是不是同一個 wake-up session
- 這次 cycle 是 fresh start 還是 resumed
- failure streak 是本輪新生成，還是從前一個 heartbeat 延續
- 目前 observability 看到的是短執行窗中的第幾個 heartbeat

## 邊界

這一步只做 observability widening：

- 可以擴充 dashboard payload / HTML / recent tables
- 可以擴充 summary / metrics / recent cycle rows

這一步不做：

- 不改 subjectivity review
- 不改 market world-model
- 不把 runtime state 寫成 identity claim
- 不把 resumed session 誤講成 persistent selfhood

## 成功標準

Dream observability artifact 應該讓後續 agent 一眼看出：

1. wake-up cycle 是否延續同一個 runtime session
2. resume 發生了幾次
3. consecutive failure streak 是否在跨 heartbeat 累積
4. 目前 dashboard 看到的是哪個 session、哪個短執行窗位置

一句話總結：

不是讓 ToneSoul 看起來更像主體，而是讓它的 runtime 連續性更誠實可見。

---

## 2. 原始檔案：`wakeup_scribe_integration_addendum_2026-03-13.md`

# Wakeup Scribe Integration Addendum (2026-03-13)

## Why

Scribe is now structurally honest enough to act as an internal chronicle layer:

- it distinguishes observed history from bootstrap reflection
- it preserves failure metadata through companion/status artifacts
- it exposes compact handoff surfaces instead of hiding inside markdown only

But it still lives outside the autonomous wake-up rhythm.

That leaves a gap in the system:

- Dream / wake-up / consolidation already happen in time
- Scribe still depends on a manual operator call

This breaks the intended continuity of the architecture.

## Goal

Let `AutonomousWakeupLoop` decide, after a successful wake-up cycle and memory
consolidation, whether the current internal slice is worth writing down as a
Scribe chronicle.

## Chosen Strategy

1. Keep Scribe as a post-cycle layer inside `wakeup_loop`, not inside
   `DreamEngine`.
2. Trigger Scribe from wake-up summary and consolidation signals instead of only
   from `write_gateway_written`.
3. Make the Scribe call best-effort:
   - Scribe failures must not fail the wake-up cycle itself
   - Scribe output should still be mirrored into wake-up summary when present
4. Persist a small dedupe state so repeated unresolved slices do not produce the
   same diary on every cycle.

## Trigger Shape

The first integration gate should consider the cycle materially writable when at
least one of these is true:

- `collision_count > 0`
- `consolidation_promoted_count > 0`
- `consolidation_gated_count > 0`
- `consolidation_unresolved_tension_count > 0`
- `consolidation_vow_count > 0`

This intentionally does **not** depend only on `write_gateway_written`.

The probe run already showed why:

- a wake-up cycle can contain real collisions and unresolved tension pressure
- yet all writes can still be skipped by existing dedupe / active-signature logic

## Boundaries

Allowed:

- one best-effort post-cycle Scribe pass
- a separate Scribe dedupe state file under `memory/autonomous/`
- writing the existing Scribe status artifact when a chronicle is attempted
- mirroring compact Scribe outcome fields into wake-up summaries

Not allowed:

- making Scribe part of the blocking DreamEngine path
- rerunning Scribe on every identical unresolved slice
- reparsing chronicle markdown to decide whether a new chronicle is needed
- treating Scribe success/failure as the same thing as wake-up success/failure

## Intended Effect

After this phase, the wake-up system should be able to:

- wake
- dream
- consolidate
- decide whether the current internal slice has enough weight to record
- write one bounded internal chronicle when warranted
- keep sleeping even if Scribe itself fails

---

## 3. 原始檔案：`wakeup_scribe_observability_addendum_2026-03-13.md`

# Wakeup Scribe Observability Addendum (2026-03-13)

## Why

`AutonomousWakeupLoop` can now trigger Scribe after a material cycle, and the
cycle summary already carries compact Scribe outcome fields.

But the dashboard layer still treats wake-up as if it stops at friction,
collision, write-gateway, and LLM preflight metrics.

That leaves a handoff gap:

- the wake-up loop knows whether a cycle produced a chronicle
- the Scribe status artifact knows the latest posture
- the dream observability dashboard does not surface that continuity yet

## Goal

Mirror the compact Scribe outcome already present in wake-up summaries into
`dream_observability` so an operator can see, from the dashboard alone:

- whether wake-up evaluated or triggered Scribe
- the latest Scribe status / generation mode
- the latest state-document posture
- whether the latest available source is a chronicle pair or companion only

## Chosen Strategy

1. Keep this as a passive observability mirror of wake-up summary fields.
2. Do not parse chronicle markdown or companion JSON from the dashboard.
3. Surface the latest compact Scribe state in:
   - wake-up summary payload
   - recent wake-up cycle rows
   - HTML cards / recent-cycle table
4. Use deterministic defaults when older wake-up history rows do not yet carry
   Scribe fields.

## Boundaries

Allowed:

- reading `scribe_*` fields already written into wake-up summaries
- aggregating `scribe_triggered` counts for trend visibility
- rendering posture/status as dashboard metadata

Not allowed:

- re-running Scribe from dream observability
- reparsing markdown chronicle content
- introducing a second source of truth separate from wake-up summary / status

## Intended Effect

After this phase, dream observability should show wake-up not only as a cycle of
friction and memory pressure, but also as a cycle that may or may not have
written an internal chronicle.

---

## 4. 原始檔案：`dream_observability_anchor_topline_addendum_2026-03-14.md`

# Dream Observability Anchor Topline Addendum (2026-03-14)

## Why

`dream_observability_latest.json` now source-declares the latest Scribe anchor.

But the higher-level governance summaries still stop at dream posture and route.
That means the anchor is technically available, yet still hidden one layer too
deep for quick reading.

## Goal

Mirror the dream anchor into the human-readable top-line summaries of:

- repo healthcheck
- worktree settlement
- repo-governance settlement

## Chosen Strategy

1. Reuse the existing optional `anchor_status_line` from the dream preview.
2. Add one compact line only when the source preview actually carries it.
3. Keep the focus-preview sections unchanged; this is a topline addition only.

## Boundaries

Allowed:

- one optional `dream_anchor_posture` / `Dream anchor posture` line per summary
- focused regression updates for the existing dream-preview tests

Not allowed:

- recomputing anchors from raw wakeup history
- inventing dream-specific fallback logic
- changing queue shapes or preview normalization rules

## Intended Effect

An operator or later agent should be able to see the dream anchor posture from
the summary itself, without opening the focus-preview section to discover what
the latest Scribe state document was actually anchored to.

---

## 5. 原始檔案：`dream_observability_governance_mirror_addendum_2026-03-14.md`

# Dream Observability Governance Mirror Addendum (2026-03-14)

## Why

`dream_observability_latest.json` now exposes a compact handoff surface, but
upper governance artifacts still only mirror it as a generic handoff preview.

That means later agents can technically find it, yet repo-level summaries still
do not elevate it the way they already elevate weekly host status or Scribe.

## Goal

Promote dream observability into a first-class passive governance mirror:

- `repo_healthcheck` should expose `dream_observability_preview`
- settlement artifacts should expose `dream_observability_focus_preview`

## Chosen Strategy

1. Register the dashboard artifact as a passive status preview in
   `run_repo_healthcheck.py`.
2. Select it by name for a top-level repo-healthcheck mirror.
3. Select it from refreshable handoff previews inside worktree settlement.
4. Mirror that focus preview into repo-governance settlement.

## Boundaries

Allowed:

- passive preview selection by status-artifact path / queue shape
- compact markdown summary lines and focus sections
- focused tests for healthcheck and settlement carry-through

Not allowed:

- treating dream observability as a second weekly host status
- adding dashboard-specific preview parsers beyond the generic handoff extractor
- re-running the dashboard from settlement rendering

## Intended Effect

After this phase, higher-level governance artifacts should surface the latest
dream observability posture directly, so route-first wakeup diagnostics remain
visible without scanning generic handoff lists.

---

## 6. 原始檔案：`dream_observability_handoff_addendum_2026-03-14.md`

# Dream Observability Handoff Addendum (2026-03-14)

## Why

Dream observability now carries the latest Scribe route and mixed-signal
secondary hints inside its dashboard payload and HTML, but
`dream_observability_latest.json` still lacks a compact handoff surface.

That means upper preview tooling has to treat the dashboard artifact as a large
report instead of a readable status surface.

## Goal

Give `dream_observability_latest.json` the same bounded handoff shape used by
other status artifacts, so refreshable and governance tooling can mirror the
latest wakeup/Scribe posture without reopening the full dashboard report.

## Chosen Strategy

1. Add compact top-level lines to the dashboard payload:
   - `primary_status_line`
   - `runtime_status_line`
   - `problem_route_status_line`
   - `problem_route_secondary_labels`
   - `artifact_policy_status_line`
2. Build one passive `handoff` surface with queue shape
   `dream_observability_ready`.
3. Keep the dominant route and secondary hints sourced from wakeup summary
   carry-through, not recomputed locally.

## Boundaries

Allowed:

- one compact handoff surface for the dashboard JSON artifact
- focused tests in dashboard generation and refreshable preview plumbing
- reuse of existing generic preview extractors

Not allowed:

- turning observability into a new governance router
- introducing another dream-specific preview schema
- reopening Scribe status artifacts from dashboard generation

## Intended Effect

After this phase, `dream_observability_latest.json` should behave like other
status artifacts: readable on its own, and mirrorable by higher-level preview
tooling without parsing the full dashboard structure.

---

## 7. 原始檔案：`dream_observability_scribe_anchor_addendum_2026-03-14.md`

# Dream Observability Scribe Anchor Addendum (2026-03-14)

## Why

`dream_observability` already mirrors the latest Scribe posture, dominant route,
and secondary route hints.

But it still drops the lead anchor itself. That leaves a small but important
source-level gap: downstream mirrors can preserve an `anchor_status_line`, yet
the dream dashboard source artifact does not currently declare one.

## Goal

Make `dream_observability` source-declare the latest Scribe anchor alongside
the existing posture and route-first diagnostics.

## Chosen Strategy

1. Preserve `scribe_anchor_status_line` while extracting wakeup rows.
2. Surface the latest anchor in:
   - summary
   - `wakeup_scribe_state`
   - recent wakeup rows
   - top-level `anchor_status_line`
   - nested `handoff`
3. Keep the line optional; absent anchors should remain quiet.

## Boundaries

Allowed:

- one new compact anchor line in the dream dashboard source artifact
- focused tests for summary, wakeup state, and top-level payload carry-through

Not allowed:

- new dream-specific routing logic
- changing preview or settlement renderers in the same phase
- widening this into a broader dashboard redesign

## Intended Effect

Later agents reading `dream_observability_latest.json` should be able to see
not only what posture and repair family dominated, but also which anchor the
latest Scribe state document was actually carrying.

---

## 8. 原始檔案：`dream_observability_settlement_topline_addendum_2026-03-14.md`

# Dream Observability Settlement Topline Addendum (2026-03-14)

## Why

`dream_observability_focus_preview` is now available in worktree and
repo-governance settlement artifacts, but later agents still need to scan a
dedicated focus section to notice it.

Weekly host status already has compact top-line mirrors. Dream observability now
deserves the same treatment so route-first wakeup diagnostics remain visible at
first glance.

## Goal

Promote dream observability from a focus section into settlement top-lines:

- `run_worktree_settlement_report.py` should emit compact dream posture lines in
  the main summary block when a dream focus preview exists
- `run_repo_governance_settlement_report.py` should mirror the same compact
  lines from worktree settlement

## Chosen Strategy

1. Reuse the existing `dream_observability_focus_preview` object.
2. Surface only compact lines already present on the preview:
   - `primary_status_line`
   - `runtime_status_line`
   - `problem_route_status_line`
   - `problem_route_secondary_labels`
   - `artifact_policy_status_line`
3. Keep the dedicated focus section intact for detail.

## Boundaries

Allowed:

- passive markdown summary lines driven by existing preview fields
- focused regressions proving the top-line wording appears

Not allowed:

- new dream-specific payload parsers
- treating dream observability as weekly host status
- refreshing live artifacts just to prove the mirror works

## Intended Effect

Settlement markdown should become one-glance readable: later agents can see the
latest dream posture and route-first diagnostics without opening the Dream
Observability Focus Mirror section first.

---

## 9. 原始檔案：`dream_weekly_alignment_line_addendum_2026-03-14.md`

# Dream Weekly Alignment Line Addendum (2026-03-14)

## Why

Weekly host status and dream observability now both surface route-first posture,
but upper artifacts still show them as separate lines.

That is readable, yet it still leaves later agents to perform their own mental
comparison: are weekly and dream telling the same story, or are they diverging?

## Goal

Add one compact cross-artifact line that summarizes whether weekly host status
and dream observability are aligned at the route-family level.

## Chosen Strategy

1. Derive a compact `dream_weekly_alignment_line` from existing preview fields.
2. Compare only bounded route-first data:
   - dominant `family=...`
   - shared secondary route hints when present
3. Surface that line in:
   - `repo_healthcheck`
   - `worktree_settlement`
   - `repo_governance_settlement`

## Boundaries

Allowed:

- passive comparison of already-exposed preview fields
- a shared helper for deterministic line construction
- focused tests covering aligned / diverged / partial cases

Not allowed:

- parsing or re-running weekly/dream artifacts in a new way
- inventing dream-specific governance decisions from the alignment line
- replacing the original weekly or dream lines

## Intended Effect

Later agents should be able to see, at one glance, whether weekly host status
and dream observability agree on the first repair family or whether they are
currently diverging.

---

## 10. 原始檔案：`dream_weekly_alignment_preview_passthrough_addendum_2026-03-14.md`

# Dream Weekly Alignment Preview Passthrough Addendum (2026-03-14)

## Why

`dream_weekly_alignment_line` now exists on the weekly host-facing artifact, but
generic preview extractors still drop it. That means upper governance mirrors
can only see the line by recomputing it locally.

This is not broken, but it is an integrity gap: source-declared alignment should
be able to travel through the preview chain unchanged.

## Goal

Let `dream_weekly_alignment_line` pass through the generic preview chain:

- refreshable handoff previews
- repo healthcheck preview extraction
- worktree settlement handoff mirrors
- repo-governance settlement compact mirrors

## Chosen Strategy

1. Treat `dream_weekly_alignment_line` as another optional compact preview field.
2. Preserve it anywhere the existing preview grammar already carries route or
   anchor lines.
3. Prefer source-declared alignment when present; only recompute as fallback.

## Boundaries

Allowed:

- optional field carry-through in preview extractors and compact mirrors
- markdown bullets for the new field where preview details are already rendered
- focused regressions for preview passthrough

Not allowed:

- replacing the fallback recomputation path
- inventing new queue shapes or preview schemas
- turning alignment mismatch into a new blocking gate

## Intended Effect

Later agents should be able to see one stable alignment line that originates
from the weekly source artifact and survives the whole preview chain without
being recomputed at every layer.

---

## 11. 原始檔案：`dream_weekly_alignment_refreshable_handoff_fallback_addendum_2026-03-14.md`

# Dream Weekly Alignment Refreshable Handoff Fallback Addendum (2026-03-14)

## Why

`dream_weekly_alignment_line` now survives the preview chain when it is present
as a top-level field on the source artifact.

But `run_refreshable_artifact_report.py` still differs from
`run_repo_healthcheck.py`: its generic handoff extractor does not fall back to
`handoff.dream_weekly_alignment_line` when the top-level field is absent.

## Goal

Make the refreshable handoff extractor treat `dream_weekly_alignment_line` the
same way the healthcheck extractor already does.

## Chosen Strategy

1. Read `dream_weekly_alignment_line` from the candidate document first.
2. If missing, fall back to the nested `handoff` object.
3. Keep the rest of the preview grammar unchanged.

## Boundaries

Allowed:

- one optional-field fallback in the generic refreshable extractor
- one focused regression proving handoff-only alignment survives

Not allowed:

- widening this into a larger handoff grammar refactor
- changing queue shapes or producer logic

## Intended Effect

Refreshable previews should preserve the same source-declared alignment line
even when an artifact exposes it only through its `handoff` object.

---

## 12. 原始檔案：`wakeup_scribe_secondary_observability_addendum_2026-03-14.md`

# Wakeup Scribe Secondary Observability Addendum (2026-03-14)

## Why

The wakeup/weekly/governance chain now preserves `problem_route_secondary_labels`
for mixed-signal Scribe runs, but dream observability still only shows:

- `scribe_status`
- `scribe_generation_mode`
- `scribe_state_document_posture`
- `scribe_latest_available_source`

That means dashboard readers can see that Scribe ran, but not which secondary
repair families stayed attached to the latest route.

## Goal

Let dream observability mirror the latest Scribe route hints from wakeup
summaries without adding a new chart family.

## Chosen Strategy

1. Extend wakeup extraction with:
   - `scribe_problem_route_status_line`
   - `scribe_problem_route_secondary_labels`
2. Preserve them in `wakeup_scribe_state`, summary payload, and recent wake-up
   rows.
3. Render them in compact HTML surfaces:
   - runtime meta string
   - recent wake-up table columns

## Boundaries

Allowed:

- passive carry-through from wakeup summary into dashboard payload
- compact HTML additions for route and secondary labels
- focused dashboard regressions

Not allowed:

- new route charts or family-specific trend series
- recomputing problem routes inside observability
- reopening Scribe artifacts from observability generation

## Intended Effect

After this phase, the dream dashboard should show not only the latest Scribe
status/posture, but also the dominant repair surface and mixed-signal secondary
families, so route-first diagnostics remain visible in the observability layer.

---

## 13. 原始檔案：`dream_focus_anchor_render_addendum_2026-03-15.md`

# Dream Focus Anchor Render Addendum (2026-03-15)

## Why

The dream summary toplines now expose `Dream anchor posture`, and the dream
preview payload itself already carries `anchor_status_line`.

But the dedicated `Dream Observability Focus Mirror` sections in settlement
markdown still omit that same line. This leaves the detailed mirror section less
informative than the topline summary above it.

## Goal

Render `anchor_status_line` inside the dream focus mirror sections of:

- worktree settlement
- repo-governance settlement

## Chosen Strategy

1. Reuse the existing optional `anchor_status_line` from the dream focus preview.
2. Render it only when present, matching the existing optional field style.
3. Keep all payload schemas unchanged; this is a markdown-surface fix only.

## Boundaries

Allowed:

- one optional line in each dream focus mirror renderer
- focused markdown regressions

Not allowed:

- changing preview extraction or normalization
- inventing new dream-specific compact fields
- touching unrelated settlement sections

## Intended Effect

The dream focus mirror section should show the same anchor posture already
present in the source preview, so later readers do not lose detail when moving
from topline summary to the focused mirror block.

---
