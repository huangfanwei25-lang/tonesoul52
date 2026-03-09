# Dirty Worktree Settlement Addendum

> Date: 2026-03-08
> Status: Applied

## Why This Exists

The commit-attribution planner already proves three things:

1. The current branch still carries trailer debt.
2. The backfill branch is attribution-clean.
3. Both branches are tree-equivalent.

That proof is necessary, but it still leaves one operational question unanswered:

> What should humans settle first before any branch-base movement becomes safe?

Counting dirty paths is not enough. A worktree with 200 entries can be mostly refreshable
artifacts, or it can be mostly high-signal source edits. Those are different recovery
problems and should not share the same operator ritual.

## Settlement Lanes

The repo now treats dirty paths as belonging to one of five settlement lanes:

1. `refreshable_artifacts`
2. `private_memory_review`
3. `public_contract_docs`
4. `runtime_source_changes`
5. `experimental_misc_review`

This keeps three separations explicit:

- Generated evidence vs authored source
- Private memory channels vs public branch content
- Core runtime changes vs exploratory drift

## Architectural Rule

The dirty worktree is not itself the next task. It is a queue that must be shaped.

That means the operational truth is no longer only:

- `worktree is dirty`

It is now:

- which lane is active
- how many files are in it
- what kind of cleanup it requires
- what the next checkpoint command is

## Result

`scripts/run_worktree_settlement_report.py` converts the planner's category view into a
human-operable settlement report and emits:

- `docs/status/worktree_settlement_latest.json`
- `docs/status/worktree_settlement_latest.md`

This report is intentionally non-destructive. It does not mutate refs, stage files, or
rewrite history. Its only job is to shorten the path from "branch movement is unsafe" to
"the worktree is finally settled enough to re-run the base-switch planner."
