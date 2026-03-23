# Repo Healthcheck Evolution — 倉庫健檢擴展

> Purpose: consolidate repo-healthcheck addenda and explain how preview, fallback, and operator render behavior evolved.
> Last Updated: 2026-03-23

> 合併日期：2026-03-19
> 原始 addendum 數：7
> 時間跨度：2026-03-15 ~ 2026-03-15
> 合併者：痕 (Hén)

被動鏡像表面、嵌套 fallback、operator 渲染、主觀焦點預覽、週度狀態整合。

---

## 目錄

1. `repo_healthcheck_admissibility_preview_parity_addendum_2026-03-15.md`
2. `repo_healthcheck_handoff_nested_fallback_addendum_2026-03-15.md`
3. `repo_healthcheck_handoff_operator_render_addendum_2026-03-15.md`
4. `repo_healthcheck_preview_contract_addendum_2026-03-15.md`
5. `repo_healthcheck_subjectivity_focus_mirror_addendum_2026-03-15.md`
6. `repo_healthcheck_subjectivity_passive_fallback_addendum_2026-03-15.md`
7. `repo_healthcheck_weekly_mirror_addendum_2026-03-15.md`

---

## 1. 原始檔案：`repo_healthcheck_admissibility_preview_parity_addendum_2026-03-15.md`

# Repo Healthcheck Admissibility Preview Parity Addendum (2026-03-15)

## Why

The shared compact handoff grammar already treats
`admissibility_primary_status_line` as an optional first-class field. Refreshable
and settlement artifacts preserve it, but `repo_healthcheck` was still dropping
it from normalized handoff previews and markdown rendering.

## Decision

Teach repo healthcheck to preserve and render
`admissibility_primary_status_line` anywhere it already mirrors other compact
preview lines.

## Constraints

- Keep the field optional.
- No new fallback logic.
- No new schema beyond restoring existing grammar parity.

## Expected Effect

Repo healthcheck no longer strips admissibility hints from source-declared
previews, so upper debugging and governance surfaces can rely on one consistent
compact grammar.

---

## 2. 原始檔案：`repo_healthcheck_handoff_nested_fallback_addendum_2026-03-15.md`

# Repo Healthcheck Handoff Nested Fallback Addendum (2026-03-15)

## Why

`repo_healthcheck` already falls back from nested `handoff` for most compact
lines, but it still skipped `artifact_policy_status_line` and
`admissibility_primary_status_line`. That meant a handoff-only source could keep
those lines inside the nested object while repo healthcheck silently dropped
them.

## Decision

Extend the existing nested handoff fallback in `_extract_handoff_surface(...)`
to cover both optional fields.

## Constraints

- Reuse the existing handoff-only fallback pattern.
- Do not invent new fields.
- Keep the change local to repo healthcheck extraction.

## Expected Effect

Repo healthcheck no longer truncates handoff-only compact metadata for artifact
policy and admissibility when mirroring source artifacts.

---

## 3. 原始檔案：`repo_healthcheck_handoff_operator_render_addendum_2026-03-15.md`

# Repo Healthcheck Handoff Operator Render Addendum (2026-03-15)

## Why

`repo_healthcheck_latest.json` already preserves `requires_operator_action` inside
its normalized handoff previews, but the markdown renderer drops that field in
the `## Handoff Previews` section. That creates a small integrity gap between the
machine-readable preview and the human-readable mirror.

## Decision

Render `requires_operator_action` for each handoff preview item in repo
healthcheck markdown, matching the behavior already used by refreshable and
settlement reports.

## Constraints

- Markdown-only change.
- No payload change.
- No new fallback logic.

## Expected Effect

Later agents and operators reading repo healthcheck markdown can see whether a
preview expects operator action without reopening the JSON payload.

---

## 4. 原始檔案：`repo_healthcheck_preview_contract_addendum_2026-03-15.md`

# Repo Healthcheck Preview Contract Addendum

Date: 2026-03-15

## Why

`repo_healthcheck` has grown beyond a flat check runner. It now also mirrors several
bounded status surfaces so later agents can read one high-level artifact without
recomputing compact governance language.

The README still describes the checks it runs, but not the passive/structured preview
mirrors it now carries, including the new subjectivity focus fallback behavior.

## Decision

Document the repo-healthcheck preview mirrors in `docs/status/README.md`.

## Boundaries

- Documentation-only.
- No schema change.
- No renderer change.
- Describe current behavior, including that subjectivity focus prefers structured
  admissibility-carrying handoff previews and falls back to passive
  `subjectivity_review_batch_latest.json`.

## Success Criteria

The README explains that `repo_healthcheck_latest.json` is both a check aggregate and a
bounded preview mirror for repo intelligence, weekly host status, subjectivity focus,
dream observability, and Scribe status.

---

## 5. 原始檔案：`repo_healthcheck_subjectivity_focus_mirror_addendum_2026-03-15.md`

# Repo Healthcheck Subjectivity Focus Mirror Addendum

Date: 2026-03-15

## Why

`repo_healthcheck` already mirrors several bounded status surfaces:

- `repo_intelligence_preview`
- `weekly_host_status_preview`
- `dream_observability_preview`
- `scribe_status_preview`

It also preserves `admissibility_primary_status_line` inside generic handoff previews,
but it still lacks a dedicated `subjectivity_focus_preview` mirror. That means the
governance-oriented surface that declares admissibility pressure remains harder to read
in `repo_healthcheck` than it is in settlement artifacts.

## Decision

Add a passive `subjectivity_focus_preview` selector to `run_repo_healthcheck.py` that
chooses the first handoff preview carrying `admissibility_primary_status_line`, then
mirror that preview in both payload and markdown.

## Constraints

- No new schema family.
- No recomputation of compact lines.
- Reuse existing source-declared fields only.
- Do not override `weekly_host_status_preview`; keep weekly and subjectivity as separate
  mirrors even when the same source artifact satisfies both roles.

## Success Criteria

`repo_healthcheck` exposes a dedicated `subjectivity_focus_preview` plus a markdown
section/top-lines that render the same compact governance lines already declared by the
source preview, so later agents do not need to infer subjectivity focus from generic
handoff lists alone.

---

## 6. 原始檔案：`repo_healthcheck_subjectivity_passive_fallback_addendum_2026-03-15.md`

# Repo Healthcheck Subjectivity Passive Fallback Addendum

Date: 2026-03-15

## Why

`repo_healthcheck` now exposes a dedicated `subjectivity_focus_preview`, but the first
implementation only selects it from structured handoff previews that carry
`admissibility_primary_status_line`.

That means the mirror disappears whenever the weekly structured check is skipped, even
though the repo already has a passive subjectivity status artifact:

- `docs/status/subjectivity_review_batch_latest.json`

## Decision

Add `subjectivity_review_batch_latest.json` to passive status preview loading and let
`subjectivity_focus_preview` fall back to that passive artifact when no structured
handoff preview supplies admissibility.

## Constraints

- Keep the same `subjectivity_focus_preview` payload shape.
- Prefer source-declared handoff previews when they exist.
- Use passive subjectivity status only as a fallback, not as a competing mirror.
- No new markdown grammar.

## Success Criteria

`repo_healthcheck` still prefers structured admissibility-carrying handoff previews, but
it no longer loses the subjectivity focus mirror on runs where weekly status is skipped
and the passive subjectivity status artifact is already available.

---

## 7. 原始檔案：`repo_healthcheck_weekly_mirror_addendum_2026-03-15.md`

# Repo Healthcheck Weekly Mirror Addendum (2026-03-15)

## Why

`repo_healthcheck_latest.json` 已經有 top-level `weekly_host_status_preview`，summary
也會露出 weekly compact lines，但 markdown 仍然缺少一個 dedicated detail mirror。
結果是讀者只能從 generic `## Handoff Previews` 或 topline 拼湊 weekly host-facing
狀態，和 settlement 鏈的表面不一致。

## Decision

在 `repo_healthcheck` markdown 補一個被動的 `## Weekly Host Status Mirror` 區塊，
直接渲染已存在的 `weekly_host_status_preview`。

## Constraints

- 不新增任何 fallback 或重新選源邏輯
- 只渲染已存在於 `weekly_host_status_preview` 的 compact lines
- 保持欄位 optional；來源沒有值時不要造假

## Expected Effect

`repo_healthcheck` 不再只在 topline 與 generic handoff list 隱約提到 weekly；
它會像 settlement 一樣，提供一個 bounded 的 weekly detail mirror。

---
