# Round 2 Handoff Framework

## Purpose

This file exists to prevent future agents from mixing three different things:

1. historical Round 2 completion,
2. current dirty-workspace observations,
3. unrelated architecture/runtime work that happened in the same commit series.

## Verified Facts

- Round 2 orphan cleanup was executed and committed in `ac1abef`.
- The cleanup was not isolated. The same commit also included V2 runtime wiring and web/API changes.
- All 15 Round 2 target modules are no longer in their original `tonesoul/` locations.
- Seven modules were archived into `docs/archive/deprecated_modules/`.
- Eight modules were fully deleted.
- `docs/status/orphan_modules_report.md` top summary reflects the earlier Round 1 baseline unless the reader also checks the Round 2 reconciliation section.

## Source Of Truth Order

1. `git show --stat ac1abef`
2. actual filesystem state (`Test-Path` / `Get-ChildItem`)
3. `docs/status/round2_progress.md`
4. `docs/archive/deprecated_modules/README.md`
5. `docs/status/orphan_modules_report.md`

If two sources disagree, trust the higher entry in this list.

## Known Traps

- PowerShell can display UTF-8 markdown as mojibake unless `Get-Content -Encoding UTF8` is used.
- The Round 2 commit mixed cleanup work with runtime feature work. Do not assume every file in `ac1abef` belongs to the orphan-module task.
- Current local pytest behavior may differ from the historical Round 2 result because the workspace is no longer clean.
- Generated topology/output files can create false-positive text references; runtime import evidence is stronger than token hits.

## Safe Handoff Procedure

1. Read `CODEX_TASK.md` with UTF-8.
2. Read `docs/status/round2_progress.md` with UTF-8.
3. Inspect `git show --stat ac1abef`.
4. Confirm the 15 target paths are either deleted or archived.
5. Separate historical validation from current validation in every report.
6. If re-running tests, use a clean worktree or separate worktree checkout.
7. Only then decide whether the next task is:
   - report reconciliation,
   - fresh verification,
   - or new code work.

## Suggested Commands

```powershell
Get-Content -Raw -Encoding UTF8 CODEX_TASK.md
Get-Content -Raw -Encoding UTF8 docs/status/round2_progress.md
git show --stat ac1abef
Get-ChildItem docs/archive/deprecated_modules
git status -sb
```

## Current Recommendation

For any next operator, treat Round 2 cleanup as already completed and treat the current job as documentation reconciliation unless there is a deliberate decision to reopen the cleanup.
