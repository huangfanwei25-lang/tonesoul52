# Status Handoff & Settlement Grammar — 狀態交接與結算語法

> 合併日期：2026-03-19
> 原始 addendum 數：14
> 時間跨度：2026-03-12 ~ 2026-03-15
> 合併者：痕 (Hén)

緊湊狀態行語法、refreshable handoff、settlement 可認可性、runtime 排程。

---

## 目錄

1. `runtime_source_change_status_surface_addendum_2026-03-12.md`
2. `schedule_runtime_failure_budget_addendum_2026-03-12.md`
3. `schedule_runtime_lineage_handoff_addendum_2026-03-12.md`
4. `refreshable_handoff_surface_parity_addendum_2026-03-14.md`
5. `status_compact_handoff_grammar_addendum_2026-03-14.md`
6. `refreshable_handoff_nested_fallback_addendum_2026-03-15.md`
7. `refreshable_subjectivity_focus_parity_addendum_2026-03-15.md`
8. `settlement_admissibility_label_parity_addendum_2026-03-15.md`
9. `settlement_subjectivity_focus_compact_parity_addendum_2026-03-15.md`
10. `settlement_subjectivity_topline_addendum_2026-03-15.md`
11. `status_handoff_metadata_contract_addendum_2026-03-15.md`
12. `status_preview_path_metadata_addendum_2026-03-15.md`
13. `subjectivity_admissibility_label_parity_addendum_2026-03-15.md`
14. `weekly_host_status_mirror_addendum_2026-03-15.md`

---

## 1. 原始檔案：`runtime_source_change_status_surface_addendum_2026-03-12.md`

# Runtime Source Change Status Surface Addendum (2026-03-12)

## Why

`runtime_source_change_groups` should not become the primary weekly runtime-posture
surface. That role now belongs to higher-level governance artifacts such as
`repo_healthcheck`.

But the change-group report still leaves one review gap:

- it tells later agents which runtime files changed
- it does not tell them which status artifacts best explain those changes

That forces another search step even when the correct operator-facing surface is
already known.

## Chosen Role

Keep `scripts/run_runtime_source_change_report.py` as a dirty review-scope
artifact, not a runtime-truth artifact.

Add only static, deterministic metadata:

- per-group `status_surfaces`
- markdown hints that point to the right top-level artifacts

## Boundaries

Allowed:

- attach known status-artifact paths to review groups
- mirror those paths into JSON and markdown output
- use this as a reviewer navigation aid

Not allowed:

- parsing live task-status payloads here
- reopening history artifacts to compute runtime posture
- inventing another host-status summary separate from `repo_healthcheck`

## Intended Effect

A later agent reading `runtime_source_change_groups_latest.*` should be able to
answer two different questions without confusion:

1. Which runtime files belong in the same review group?
2. Which governance artifact should I open next to understand the operator view?

---

## 2. 原始檔案：`schedule_runtime_failure_budget_addendum_2026-03-12.md`

# Schedule Runtime Failure Budget Addendum (2026-03-12)

## 問題

`AutonomousRegistrySchedule` 已經會對 friction、Lyapunov、council count、LLM latency 做 tension budget，但還沒有把跨 heartbeat 延續的 `consecutive_failure_count` 當成一種可治理的 runtime 壓力。

這代表：

- wake-up runtime 已經知道自己在連續失敗
- schedule policy 卻可能繼續用同樣節奏往前推

## 這一步要做什麼

這一步只增加一個最小 policy knob：

- `tension_max_consecutive_failure_count`

它的語意很簡單：

- 如果 nested wake-up runtime 的 failure streak 超過這個上限
- schedule 就把它視為一種 tension budget breach
- 既有 category cooldown 機制因此可以接手

## 邊界

這不是新的 subjectivity 邏輯，也不是新的 runtime state machine。

這一步不做：

- 不新增獨立 runtime backoff 狀態檔
- 不把 failure streak 直接等同於 LLM backoff
- 不引入新的 market / mirror 耦合

## 成功標準

後續 agent 應該能做到：

1. 在 schedule policy 中讀到跨 heartbeat 延續的 failure streak
2. 用既有 tension cooldown 機制對它做 deterministic 回應
3. 不需要新的一整套 runtime governance subsystem

---

## 3. 原始檔案：`schedule_runtime_lineage_handoff_addendum_2026-03-12.md`

# Schedule Runtime Lineage Handoff Addendum (2026-03-12)

## 問題

現在 `AutonomousDreamCycleRunner` 已經會回傳 `runtime_state`，但到了 `AutonomousRegistrySchedule` 與 dream observability 的 schedule 視角，這條脈絡幾乎沒有被好好顯示。

結果是：

- 看 wake-up artifact 的 agent 知道 session 在續接
- 只看 schedule artifact 的 agent 卻可能以為每個 schedule tick 都是全新 runtime

這會讓 handoff 在 schedule 層失真。

## 這一步要做什麼

這一步只做一件事：

把 nested wake-up runtime lineage 明確帶到 schedule observability。

具體來說，要能在 schedule 視角看見：

- 對應的 wake-up `session_id`
- 這個 schedule tick 內的 wake-up 是否為 resumed session
- 當下 failure streak 多高
- runtime state file 指向哪裡

## 邊界

這一步是 handoff / observability widening，不是 policy widening。

不做的事：

- 不新增 schedule runtime gate
- 不新增 category cooling 規則
- 不把 runtime resume 誤解成 persistent selfhood
- 不改 market 或 subjectivity contract

## 成功標準

後續 agent 如果只打開 schedule snapshot 或 dashboard，也能判斷：

1. 這個 schedule tick 是接在同一個 wake-up session 上，還是 fresh start
2. 目前看到的失敗計數是不是跨 heartbeat 延續
3. runtime lineage 有沒有在 schedule handoff 中被吃掉

---

## 4. 原始檔案：`refreshable_handoff_surface_parity_addendum_2026-03-14.md`

# Refreshable Handoff Surface Parity Addendum (2026-03-14)

## Why

`run_repo_healthcheck.py` already treats several compact preview lines as
source-declared handoff metadata: if the top-level field is missing, it will
read the same line from the nested `handoff` object.

`run_refreshable_artifact_report.py` is still behind that contract. It now
preserves `dream_weekly_alignment_line` from nested `handoff`, but it still
drops other optional compact lines when they are exposed only there.

## Goal

Bring the refreshable generic handoff extractor up to parity for the compact
lines that later governance surfaces already expect:

- `scribe_status_line`
- `anchor_status_line`
- `problem_route_status_line`
- `problem_route_secondary_labels`

## Chosen Strategy

1. Keep the change local to `run_refreshable_artifact_report.py`.
2. Read the compact lines from the candidate document first.
3. Fall back to the nested `handoff` object only when the top-level field is
   absent.
4. Preserve the same optional rendering behavior: only print lines that exist.

## Boundaries

Allowed:

- extractor parity for the existing compact preview grammar
- one focused regression using a handoff-only source artifact
- matching markdown rendering for the newly preserved optional line

Not allowed:

- inventing a refreshable-specific preview schema
- changing producer commands, queue shapes, or planner logic
- widening this into a broad preview refactor

## Intended Effect

Refreshable previews should stop silently discarding source-declared Scribe and
route-first diagnostics just because they were surfaced under `handoff` instead
of duplicated at the top level.

---

## 5. 原始檔案：`status_compact_handoff_grammar_addendum_2026-03-14.md`

# Status Compact Handoff Grammar Addendum (2026-03-14)

## Why

The repository now has several generated status surfaces that intentionally
carry the same small set of compact lines across refreshable previews, repo
healthcheck, settlement mirrors, weekly host-facing status, and dream
observability.

That grammar is already real in code, but it is still under-documented in
`docs/status/README.md`. Without one explicit note, later agents can see the
field names and still misread their semantics or assume they are ad-hoc.

## Goal

Document the compact status grammar in one place:

- which lines are mandatory vs optional
- which ones are source-declared and should be mirrored instead of recomputed
- how route-first and alignment lines are meant to be read

## Chosen Strategy

1. Keep the change documentation-only.
2. Add one short section to `docs/status/README.md`.
3. Describe the fields as a bounded cross-artifact contract, not as
   implementation trivia.

## Boundaries

Allowed:

- one compact README section explaining the shared handoff grammar

Not allowed:

- changing any generator behavior
- renaming existing fields
- turning README into a full schema spec

## Intended Effect

Future agents should be able to read a generated status artifact and know which
compact lines are authoritative, which are optional, and which should flow
through upper mirrors unchanged.

---

## 6. 原始檔案：`refreshable_handoff_nested_fallback_addendum_2026-03-15.md`

# Refreshable Handoff Nested Fallback Addendum (2026-03-15)

## Why

`run_refreshable_artifact_report.py` already preserves many compact lines from a
nested `handoff`, but it still skipped `artifact_policy_status_line` and
`admissibility_primary_status_line`. That created the same handoff-only truncation
risk that repo healthcheck just fixed.

## Decision

Extend refreshable handoff fallback to cover both optional fields.

## Constraints

- Reuse the existing handoff-only fallback pattern.
- Keep all fields optional.
- Do not change the preview schema.

## Expected Effect

Refreshable preview extraction no longer strips artifact/admissibility compact
lines when the source artifact keeps them only inside `handoff`.

---

## 7. 原始檔案：`refreshable_subjectivity_focus_parity_addendum_2026-03-15.md`

# Refreshable Subjectivity Focus Parity Addendum

Date: 2026-03-15

## Why

`run_refreshable_artifact_report.py` already preserves `runtime_status_line` and
`artifact_policy_status_line` inside the normalized subjectivity focus preview payload.
But the markdown `## Subjectivity Focus` block only rendered primary line,
route-related lines, and admissibility.

That meant a source artifact could declare bounded runtime/policy posture and still
lose it in the first human-readable mirror.

## Decision

Keep the payload unchanged and widen only the markdown renderer for the refreshable
subjectivity focus card:

- render `runtime_status_line` when present
- render `artifact_policy_status_line` when present

## Boundaries

- no new fields
- no schema change
- no recomputation
- renderer parity only

## Success Criteria

The refreshable `## Subjectivity Focus` section mirrors the same compact runtime/policy
lines already present in the normalized focus preview payload, instead of truncating them.

---

## 8. 原始檔案：`settlement_admissibility_label_parity_addendum_2026-03-15.md`

# Settlement Admissibility Label Parity Addendum

Date: 2026-03-15

## Why

`admissibility_primary_status_line` is already the shared compact-grammar field name in
payloads, refreshable previews, repo healthcheck previews, and settlement focus mirrors.
The remaining inconsistency was only in the generic settlement handoff preview list, which
rendered the same field under a shorter markdown label: `admissibility`.

That alias is small, but it reintroduces avoidable ambiguity for later agents reading
top-level governance artifacts.

## Decision

Keep the payload schema unchanged and tighten only the markdown renderer:

- worktree settlement handoff preview list should render
  `admissibility_primary_status_line`
- repo-governance settlement handoff preview list should render
  `admissibility_primary_status_line`

## Boundaries

- no payload rename
- no new field
- no behavior change outside settlement markdown parity

## Success Criteria

Settlement markdown no longer invents a shorter alias for admissibility handoff lines; the
shared compact grammar uses one label consistently across source, preview, and governance
surfaces.

---

## 9. 原始檔案：`settlement_subjectivity_focus_compact_parity_addendum_2026-03-15.md`

# Settlement Subjectivity Focus Compact Parity Addendum

Date: 2026-03-15

## Why

The normalized `subjectivity_focus_preview` already preserves the same compact optional
lines used elsewhere in the preview chain:

- `scribe_status_line`
- `anchor_status_line`
- `problem_route_status_line`
- `problem_route_secondary_labels`
- `dream_weekly_alignment_line`

But the markdown `## Subjectivity Focus Mirror` blocks in worktree and repo-governance
settlement still rendered only runtime, artifact policy, and admissibility.

That left the source preview semantically richer than the first governance mirror.

## Decision

Keep payloads unchanged and widen only the settlement markdown renderers so
`Subjectivity Focus Mirror` passively mirrors the same compact optional lines when present.

## Boundaries

- no schema changes
- no new route computation
- markdown parity only

## Success Criteria

Settlement `Subjectivity Focus Mirror` blocks no longer truncate existing compact Scribe,
anchor, route, or alignment lines that are already present in the normalized preview.

---

## 10. 原始檔案：`settlement_subjectivity_topline_addendum_2026-03-15.md`

# Settlement Subjectivity Topline Addendum

Date: 2026-03-15

## Why

Both settlement artifacts already expose a detailed `## Subjectivity Focus Mirror`, but
their top summary block still only lifts:

- weekly host status
- dream observability

That makes subjectivity governance posture harder to see at a glance, even though the
focus mirror already has bounded compact lines for runtime, Scribe posture, anchor,
route, artifact policy, and admissibility.

## Decision

Promote the existing subjectivity focus compact lines into settlement toplines for:

- `scripts/run_worktree_settlement_report.py`
- `scripts/run_repo_governance_settlement_report.py`

## Constraints

- No schema change.
- No new recomputation.
- Reuse only lines already present in `subjectivity_focus_preview`.
- Keep the detailed mirror section unchanged.

## Success Criteria

Settlement markdown shows subjectivity focus posture in its main summary block, so a
later agent can read governance posture at a glance before drilling into the detailed
focus mirror.

---

## 11. 原始檔案：`status_handoff_metadata_contract_addendum_2026-03-15.md`

# Status Handoff Metadata Contract Addendum

Date: 2026-03-15

## Why

`docs/status/README.md` already documents the shared compact status lines, but the two
metadata fields that every preview/mirror layer relies on are still only implied:

- `queue_shape`
- `requires_operator_action`

They are already part of the de facto contract across refreshable preview extraction,
repo healthcheck, settlement mirrors, and weekly/task status handoff selection.

## Decision

Document them explicitly as shared handoff metadata in `docs/status/README.md`.

## Boundaries

- no schema change
- no renderer change
- documentation-only contract clarification

## Success Criteria

The compact handoff contract in `docs/status/README.md` explicitly names both routing and
operator-action metadata, so later agents do not treat them as undocumented implementation
details.

---

## 12. 原始檔案：`status_preview_path_metadata_addendum_2026-03-15.md`

# Status Preview Path Metadata Addendum

Date: 2026-03-15

## Why

The shared compact handoff contract already documents:

- `queue_shape`
- `requires_operator_action`

But multiple passive/focus preview layers also rely on `path` as stable metadata:

- refreshable focus cards
- repo healthcheck passive mirrors
- settlement focus mirrors

Without documenting `path`, later agents can mistake it for an incidental
renderer-specific field rather than shared preview metadata.

## Decision

Document `path` in `docs/status/README.md` as shared preview metadata for passive
or artifact-backed mirrors.

## Boundaries

- Documentation-only.
- No schema change.
- Keep `path` framed as optional preview metadata, not a required handoff field.

## Success Criteria

The status README explicitly names `path` as optional shared preview metadata for
artifact-backed mirrors, alongside the existing routing/operator metadata.

---

## 13. 原始檔案：`subjectivity_admissibility_label_parity_addendum_2026-03-15.md`

# Subjectivity Admissibility Label Parity Addendum

Date: 2026-03-15

## Why

The compact grammar already standardized on `admissibility_primary_status_line` across
subjectivity payloads, refreshable previews, repo healthcheck, and settlement mirrors.
`run_subjectivity_review_batch.py` still rendered the grouped markdown bullet under the
short alias `admissibility`, even though it was describing the same first-class compact
line.

## Decision

Keep the grouped markdown human-readable, but render the field using the shared compact
label:

- `admissibility_primary_status_line`

## Boundaries

- no payload change
- no checklist schema change
- markdown-label parity only

## Success Criteria

The subjectivity batch markdown no longer invents a shorter admissibility alias, so the
same compact grammar label appears consistently from source artifact to mirror layers.

---

## 14. 原始檔案：`weekly_host_status_mirror_addendum_2026-03-15.md`

# Weekly Host Status Mirror Addendum (2026-03-15)

## Why

`worktree_settlement` and `repo_governance_settlement` already render dedicated
detail mirrors for `Dream Observability` and `Scribe`, but the weekly host-facing
artifact still only appears as topline summary plus a generic handoff list item.
That makes weekly status the odd one out even though it now carries anchor,
problem-route, secondary-route, Scribe posture, and dream/weekly alignment.

## Decision

Add a markdown-only `Weekly Host Status Mirror` section to both settlement
reports, using the existing `weekly_host_status_preview` object directly.

## Constraints

- No schema change.
- No new fallback logic.
- No recomputation of compact lines.
- Only render fields already declared by the weekly source artifact.

## Expected Effect

Later agents can read the settlement markdown and see weekly runtime posture,
anchor, route, secondary hints, Scribe posture, and alignment in one bounded
detail mirror, instead of reconstructing that context from toplines plus generic
handoff previews.

---

## 15. 原始檔案：runtime_status_handoff_fallback_parity_addendum_2026-03-15.md

# Runtime Status Handoff Fallback Parity Addendum

Date: 2026-03-15

## Why

The shared compact handoff grammar already says upper preview surfaces should preserve
source-declared compact lines from nested `handoff` blocks when the top-level field is
missing.

Two generic extractors already follow that rule for:

- `primary_status_line`
- `scribe_status_line`
- `anchor_status_line`
- `problem_route_status_line`
- `problem_route_secondary_labels`
- `dream_weekly_alignment_line`
- `artifact_policy_status_line`
- `admissibility_primary_status_line`

But they still skip `runtime_status_line`.

That means a source artifact can declare runtime posture under `handoff` and still lose
it in refreshable preview or repo-healthcheck mirror, even though the public grammar now
implies that line should be preserved.

## Decision

Extend the generic handoff extractors in:

- `scripts/run_refreshable_artifact_report.py`
- `scripts/run_repo_healthcheck.py`

so `runtime_status_line` falls back from nested `handoff` exactly like the other compact
lines.

## Constraints

- No schema change.
- No new preview field.
- Only widen existing handoff fallback behavior.
- Add focused handoff-only regressions rather than broad fixture churn.

## Success Criteria

If a source artifact declares `runtime_status_line` only inside nested `handoff`, both
refreshable preview and repo-healthcheck preserve it instead of silently dropping the
runtime posture.

---
