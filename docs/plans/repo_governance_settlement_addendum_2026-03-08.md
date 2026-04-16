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

## 2026-04-16 Red-Light Note

Two CI reds looked related but were not the same class of problem:

1. `Commit Attribution Check`
   - Root cause: one non-docs commit (`e3cedb4`) lacked `Agent` / `Trace-Topic` trailers.
   - Correct response: fix the commit message contract and re-run local parity.
   - Incorrect response: loosen the attribution gate or pretend co-author trailers are the same thing.
   - Governance note: day-to-day `push` / `pull_request` checks should stay incremental; historical trailer debt belongs to the backfill / planner lane.

2. `Dual-Track Boundary Gate`
   - Root cause: the workflow failed while resolving PR changed files, before `verify_dual_track_boundary.py` even ran.
   - Specific failure: `git diff origin/master...HEAD` on the synthetic PR merge ref produced `no merge base`.
   - Correct response: resolve PR changes from `github.event.pull_request.base.sha` and `head.sha`, not from `origin/<base>...HEAD`.

### Red-Light Triage Order

When repo governance turns red again:

1. read the failing job log and identify whether the red is:
   - content / policy failure,
   - metadata / trailer failure,
   - or workflow plumbing failure before the policy script ran
2. re-read the narrow memory lane before editing:
   - attribution -> `docs/governance/COMMUNICATION_STANDARD.md`
   - attribution lineage / tree-equivalence -> `docs/plans/commit_attribution_base_switch_addendum_2026-03-08.md`
   - public-private boundary -> `docs/ADR-001-dual-track-resolution.md`
   - status artifact semantics -> `docs/status/README.md`
3. only then change code, workflow, or history

This order matters because "a red CI badge" is not one category of bug.
