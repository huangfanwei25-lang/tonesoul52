# Repo Intelligence Latest

- generated_at: 2026-07-20T05:32:49Z
- status: ready
- primary_status_line: `repo_intelligence_ready | available_surfaces=4/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`

## External Tool Policy
- adoption_mode: `sidecar_only`
- main_repo_install_allowed: `false`
- mirror_clone_required: `true`
- hook_registration_allowed: `false`
- protected_file_mutation_allowed: `false`

## Recommended Surfaces
- `repo_healthcheck`
  - path: `docs/status/repo_healthcheck_latest.json`
  - role: `repo_governance`
  - available: `yes`
  - description: Top repo-level blocking posture and compact runtime previews.
- `repo_semantic_atlas`
  - path: `docs/status/repo_semantic_atlas_latest.json`
  - role: `semantic_memory`
  - available: `no`
  - description: Human-rememberable aliases, semantic neighborhoods, and domain-level nerve map.
- `agent_integrity`
  - path: `docs/status/agent_integrity_latest.json`
  - role: `integrity_governance`
  - available: `no`
  - description: Protected-file hash contract, embedded metadata drift, and watched-directory posture.
- `repo_governance_settlement`
  - path: `docs/status/repo_governance_settlement_latest.json`
  - role: `branch_settlement`
  - available: `yes`
  - description: Branch-movement and worktree settlement readback.
- `runtime_source_change_groups`
  - path: `docs/status/runtime_source_change_groups_latest.json`
  - role: `review_scope`
  - available: `yes`
  - description: Dirty review lanes and recommended runtime grouping.
- `true_verification_weekly`
  - path: `docs/status/true_verification_weekly/true_verification_task_status_latest.json`
  - role: `weekly_runtime`
  - available: `yes`
  - description: Host-facing weekly runtime posture and session lineage.
- `scribe_status`
  - path: `docs/status/scribe_status_latest.json`
  - role: `chronicle_runtime`
  - available: `no`
  - description: Latest Scribe chronicle/companion posture.

## Semantic Retrieval Protocol
- None

## Protected Files
- `AGENTS.md` (exists: `true`)
- `HANDOFF.md` (exists: `false`)
- `.env` (exists: `false`)
- `.gitignore` (exists: `true`)
- `MEMORY.md` (exists: `true`)

## Watched Directories
- `skills/` (exists: `true`)
- `.agent/` (exists: `true`)
- `.agents/` (exists: `false`)

## Handoff
- queue_shape: `repo_intelligence_ready`
- requires_operator_action: `false`
- preferred_first_surface: `docs/status/repo_healthcheck_latest.json`
- semantic_retrieval_protocol: ``
- semantic_preferred_neighborhood: ``
- primary_status_line: `repo_intelligence_ready | available_surfaces=4/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
