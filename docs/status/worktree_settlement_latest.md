# Worktree Settlement Latest

- Generated at: `2026-03-08T14:36:40Z`
- Overall OK: `false`
- Worktree dirty: `true`
- Planner recommendation: `defer_until_worktree_clean` (`tree_equal=true`)
- Attribution debt: current=`5`, backfill=`0`

## Settlement Order

1. **Refreshable Artifacts** (`entries=51`, `active=true`)
   - Goal: Separate reproducible outputs from authored source edits before any branch movement.
   - Exit criteria: No remaining dirty paths in generated outputs or reports, or an explicit decision to preserve them.
   - Action: Do not let generated status snapshots and derived reports drive branch-base decisions.
   - Action: Refresh, discard, or restage reproducible artifacts only after the authored source set is stable.
   - `generated_status`: count=`47`, staged=`0`, unstaged=`22`, untracked=`25`
     samples: `docs/status/dual_track_boundary_latest.json`, `docs/status/dual_track_boundary_latest.md`, `docs/status/friction_shadow_calibration_latest.json`, `docs/status/friction_shadow_calibration_latest.md`, `docs/status/friction_shadow_replay_latest.json`
   - `reports`: count=`4`, staged=`0`, unstaged=`0`, untracked=`4`
     samples: `reports/analysis_gpt53.md`, `reports/analysis_gpt54.md`, `reports/model_comparison_latest.json`, `reports/model_comparison_latest.md`

2. **Private Memory Review** (`entries=5`, `active=true`)
   - Goal: Review private memory artifacts outside the public-branch settlement path.
   - Exit criteria: Private memory changes are either archived to the private path or consciously excluded from branch movement.
   - Action: Treat raw memory artifacts as private-evolution evidence, not ordinary public repo edits.
   - Action: Mirror only public-safe learnings into task/reflection/status artifacts when needed.
   - `memory`: count=`5`, staged=`0`, unstaged=`4`, untracked=`1`
     samples: `memory/antigravity_architecture_plan_2026-03-07.md`, `memory/antigravity_journal.md`, `memory/architecture_reflection_2026-03-07.md`, `memory/crystals.jsonl`, `memory/autonomous/`

3. **Public Contract Docs** (`entries=23`, `active=true`)
   - Goal: Group public documentation and spec edits by owning implementation phase.
   - Exit criteria: Docs/spec edits are paired with their implementation or intentionally deferred.
   - Action: Settle docs and specs after generated artifacts are separated, but before final branch movement.
   - Action: Keep public docs aligned with the actual runtime and governance artifacts they describe.
   - `docs`: count=`22`, staged=`0`, unstaged=`3`, untracked=`19`
     samples: `docs/7D_EXECUTION_SPEC.md`, `docs/governance/COMMUNICATION_STANDARD.md`, `docs/status/README.md`, `docs/plans/commit_attribution_base_switch_addendum_2026-03-08.md`, `docs/plans/registry_schedule_category_policy_addendum_2026-03-07.md`
   - `spec`: count=`1`, staged=`0`, unstaged=`0`, untracked=`1`
     samples: `spec/registry_schedule_profiles.yaml`

4. **Runtime Source Changes** (`entries=122`, `active=true`)
   - Goal: Review high-signal code and contract changes as cohesive change groups.
   - Exit criteria: Core source edits are grouped into reviewable changesets with matching tests and docs.
   - Action: Keep tests paired with the code paths they validate instead of settling them independently.
   - Action: Treat scripts, runtime apps, and core `tonesoul` changes as the public source-of-truth lane.
   - `scripts`: count=`35`, staged=`0`, unstaged=`17`, untracked=`18`
     samples: `scripts/deduplicate_crystals.py`, `scripts/generate_stress_data.py`, `scripts/healthcheck.py`, `scripts/memory_compact.py`, `scripts/run_repo_healthcheck.py`
   - `tests`: count=`49`, staged=`0`, unstaged=`16`, untracked=`33`
     samples: `tests/test_agent_discussion_tool.py`, `tests/test_api_phase_a_security.py`, `tests/test_governance_kernel.py`, `tests/test_local_llm.py`, `tests/test_perception.py`
   - `tonesoul`: count=`30`, staged=`0`, unstaged=`17`, untracked=`13`
     samples: `tonesoul/council/model_registry.py`, `tonesoul/council/perspective_factory.py`, `tonesoul/deliberation/engine.py`, `tonesoul/gates/compute.py`, `tonesoul/governance/__init__.py`
   - `runtime_apps`: count=`3`, staged=`0`, unstaged=`3`, untracked=`0`
     samples: `api/_shared/core.py`, `api/chat.py`, `apps/api/server.py`
   - `skills`: count=`3`, staged=`0`, unstaged=`3`, untracked=`0`
     samples: `.agent/skills/tonesoul_governance/SKILL.md`, `.agent/skills/tonesoul_philosophy/SKILL.md`, `skills/registry.json`
   - `tooling`: count=`2`, staged=`0`, unstaged=`1`, untracked=`1`
     samples: `.github/workflows/test.yml`, `.vscode/`

5. **Experimental and Misc Review** (`entries=10`, `active=true`)
   - Goal: Resolve root-level drift and experimental assets deliberately instead of letting them hitchhike.
   - Exit criteria: Experimental and miscellaneous paths have an explicit keep/defer/drop decision.
   - Action: Decide whether experimental files belong to the public repo, a follow-up branch, or should be dropped.
   - Action: Review uncategorized root-level files manually before any git history movement.
   - `experiments`: count=`2`, staged=`0`, unstaged=`0`, untracked=`2`
     samples: `experiments/compare_model_reports.py`, `experiments/test_lmstudio_governance.py`
   - `repo_misc`: count=`8`, staged=`0`, unstaged=`4`, untracked=`4`
     samples: `.env.example`, `.gitignore`, `run_qa_audit.py`, `task.md`, `.agent/workflows/architecture-audit.md`

## Notes

- Private memory paths remain governed by the dual-track boundary; settle them as private evidence, not as ordinary public branch content.
- Generated status artifacts and derived reports should be refreshed only after the authored source set is stable.
- Re-check branch movement readiness with `python scripts/plan_commit_attribution_base_switch.py --current-ref HEAD --backfill-ref feat/env-perception-attribution-backfill --strict` after settlement.
