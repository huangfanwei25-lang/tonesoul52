# Repo Governance Settlement Addendum (2026-03-08)

## Why This Addendum Exists

`repo_healthcheck_latest.json` had already become mostly green, but the operator story was still blurry:

- the overall healthcheck stayed red
- the remaining red gate was `commit_attribution`
- the attribution planner had already proven the backfill branch was tree-equivalent

Without a dedicated settlement view, those three facts were easy to collapse into one vague feeling that "repo governance is still not converged."

## Core Distinction

Repo governance needs one extra state beyond simple green/red:

- `green`: all blocking gates pass
- `runtime_blocked`: at least one non-attribution blocking gate still fails
- `runtime_green_metadata_blocked`: runtime and repo-level operational checks are green, but history metadata debt still blocks formal convergence

That third state matters because it changes the next action:

- if runtime is blocked, fix the failing gate
- if only metadata is blocked, do not touch runtime code again; settle the worktree and then move to the attribution-clean base

## Contract Sources

The settlement report intentionally reads existing status artifacts instead of recomputing everything:

- `repo_healthcheck_latest.json` is the source of truth for blocking checks
- `commit_attribution_base_switch_latest.json` is the source of truth for metadata-debt recovery
- `runtime_source_change_groups_latest.json` is the source of truth for how the current dirty runtime lane is grouped

That keeps the report lightweight and makes it explain the current operational truth instead of creating a second healthcheck.

## Error Noted During Implementation

The first version of this phase added a new settlement report correctly, but forgot one adjacent hygiene rule:

- newly created status artifacts must immediately register their own producer command in `run_refreshable_artifact_report.py`

Because that mapping was incomplete, `refreshable_artifact_report_latest.json` temporarily regressed from `inspect_count = 0` back to `inspect_count = 4`.

The four missed artifacts were:

- `docs/status/private_memory_review_latest.json`
- `docs/status/private_memory_review_latest.md`
- `docs/status/runtime_source_change_groups_latest.json`
- `docs/status/runtime_source_change_groups_latest.md`

This was fixed in the same phase. The correct rule is simple:

- when a new `docs/status/*latest*` artifact is introduced, its refresh producer must be added in the same changeset

## Architectural Conclusion

Governance convergence should not confuse content truth with history hygiene.

- runtime truth answers: "is the system operating correctly?"
- metadata truth answers: "is the branch lineage acceptable?"

They are related, but not interchangeable. A good settlement layer must expose both, and must teach operators which one is actually asking for action.
