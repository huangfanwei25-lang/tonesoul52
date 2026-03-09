# Repo Healthcheck Latest

- generated_at: 2026-03-08T15:43:20Z
- overall_ok: false

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.18 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.89 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 187.09 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 8.29 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.43 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 2.85 | `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28` |
| commit_attribution | FAIL | 1 | 0.84 | `python scripts/verify_incremental_commit_attribution.py --strict --artifact-path docs/status/commit_attribution_local.json` |
| dual_track_boundary | PASS | 0 | 0.11 | `python scripts/verify_dual_track_boundary.py --strict --staged` |
| persona_swarm | PASS | 0 | 0.67 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.15 | `python scripts/verify_external_source_registry.py --strict` |
| skill_registry | PASS | 0 | 0.13 | `python scripts/verify_skill_registry.py --strict` |
| multi_agent_divergence | PASS | 0 | 0.58 | `python scripts/run_multi_agent_divergence_report.py --strict` |
| memory_quality | PASS | 0 | 0.56 | `python scripts/run_memory_quality_report.py --strict` |
| memory_governance_contract | PASS | 0 | 0.08 | `python scripts/run_memory_governance_contract_check.py --strict` |
| friction_shadow_replay_export | PASS | 0 | 0.56 | `python scripts/run_friction_shadow_replay_export.py --strict` |
| friction_shadow_calibration | PASS | 0 | 0.14 | `python scripts/run_friction_shadow_calibration_report.py --strict` |
| philosophical_reflection | PASS | 0 | 1.68 | `python scripts/run_philosophical_reflection_report.py --strict` |
| memory_topology_fit | PASS | 0 | 0.11 | `python scripts/run_memory_topology_fit_report.py --strict` |
| true_verification_weekly | PASS | 0 | 1.18 | `python scripts/report_true_verification_task_status.py --strict` |
| audit_7d | PASS | 0 | 280.44 | `python scripts/verify_7d.py` |

## Failures
- `commit_attribution`:  add GovernanceKernel, LLM Router, Perception Layer, Agent Protocol",
      "agent": null,
      "topic": null,
      "has_agent": false,
      "has_topic": false,
      "changed_files": [
        "AGENT_PROTOCOL.md",
        "memory/antigravity_architecture_plan_2026-03-07.md",
        "memory/antigravity_journal.md",
        "memory/architecture_reflection_2026-03-07.md",
        "tests/test_governance_kernel.py",
        "tests/test_perception.py",
        "tonesoul/governance/__init__.py",
        "tonesoul/governance/kernel.py",
        "tonesoul/llm/__init__.py",
        "tonesoul/llm/router.py",
        "tonesoul/perception/__init__.py",
        "tonesoul/perception/stimulus.py",
        "tonesoul/perception/web_ingest.py"
      ],
      "docs_only": false,
      "exempted": false,
      "exemption_reason": null,
      "rev": "c225332e2f4c6854dba231b1805d0d1d97d4ad42",
      "exit_code": 0
    }
  ],
  "advice": {
    "agent_trailer": "Agent: Codex",
    "trace_topic_trailer": "Trace-Topic: <topic-name>"
  }
}
::error::Missing Agent/Trace-Topic trailers in incremental commits.
::error::Add commit trailers, for example:
::error::Agent: Codex
::error::Trace-Topic: <topic-name>

## Recovery Advice
- `commit_attribution_recovery`: defer_until_worktree_clean
  - rationale: Backfill branch is clean and tree-equivalent, but the current worktree is dirty. Do not switch branch pointers in-place until local changes are settled or moved to a clean worktree.
  - suggested_commands:
    - `git worktree add <clean-path> feat/env-perception-attribution-backfill`
    - `python scripts/plan_commit_attribution_base_switch.py --current-ref HEAD --backfill-ref feat/env-perception-attribution-backfill --strict`
