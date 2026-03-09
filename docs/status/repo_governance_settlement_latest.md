# Repo Governance Settlement Latest

- Generated at: `2026-03-08T15:40:43Z`
- Overall OK: `false`
- Settlement status: `runtime_green_metadata_blocked`
- Healthcheck generated at: `2026-03-08T14:20:47Z`
- Healthcheck pass/fail: `19` / `1`
- Failing checks: `commit_attribution`
- Metadata-only blocker: `true`
- Runtime green except attribution: `true`

## Attribution

- Planner recommendation: `defer_until_worktree_clean`
- Tree equal: `true`
- Missing trailers: current=`5`, backfill=`0`

## Repo Governance Group

- Dirty entries in repo governance group: `24`
- Sample: `.github/workflows/test.yml`
- Sample: `scripts/healthcheck.py`
- Sample: `scripts/run_repo_healthcheck.py`
- Sample: `scripts/verify_7d.py`
- Sample: `scripts/verify_command_registry.py`
- Sample: `scripts/verify_docs_consistency.py`
- Sample: `tests/test_agent_discussion_tool.py`
- Sample: `tests/test_run_repo_healthcheck.py`

## Next Actions

- Do not reinterpret the remaining failure as runtime drift; current repo governance gates are green except for historical commit trailers.
- Keep branch movement deferred until the dirty worktree is settled, then prefer the tree-equivalent backfill branch as the clean attribution base.
- Current attribution planner recommendation: `defer_until_worktree_clean`.
