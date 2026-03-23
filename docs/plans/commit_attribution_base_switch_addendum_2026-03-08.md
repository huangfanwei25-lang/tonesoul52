# Commit Attribution Base-Switch Addendum

> Purpose: document the safe base-switch rule for commit-attribution cleanup when trees are equivalent but commit metadata differs.
> Last Updated: 2026-03-23

## Why This Exists

`commit_attribution` can fail for two very different reasons:

1. the current branch contains real content drift that has not been attributed yet
2. the current branch and a trailer-backfilled branch contain the same tree, and only commit metadata differs

These cases must not be treated with the same git operation.

## Operational Rule

If the current branch and the backfill branch are tree-equivalent:

- do not merge them just to "bring the trailers over"
- do not rewrite history in a dirty worktree
- treat the problem as branch-base selection, not content integration

## Safe Sequence

1. Prove current vs backfill tree equivalence.
2. Prove the backfill branch is attribution-clean.
3. Inspect current worktree dirtiness.
4. Only if the worktree is clean, continue from the clean backfill base.

If the worktree is dirty, defer the switch and keep working without moving branch pointers in place.

## Planner Contract

Use:

```bash
python scripts/plan_commit_attribution_base_switch.py
```

The planner is intentionally non-destructive. It only emits:

- current/backfill missing-trailer counts
- tree equivalence
- dirty-worktree snapshot
- recommended next step
- suggested commands

It does not:

- switch branches
- rewrite history
- stash changes
- mutate refs

## Architectural Conclusion

Metadata-only history debt should be closed with proof first and git movement second.  
If equivalence is not proven, it is not a base-switch problem.  
If the worktree is dirty, it is not yet a safe time to perform the switch.
