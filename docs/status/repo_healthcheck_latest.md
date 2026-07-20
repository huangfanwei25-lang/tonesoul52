# Repo Healthcheck Latest

- generated_at: 2026-07-20T05:32:50Z
- overall_ok: false
- handoff_preview_count: 1
- repo_intelligence: `repo_intelligence_ready | available_surfaces=4/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- repo_intelligence_entrypoints: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- subjectivity_focus: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- subjectivity_admissibility: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`
- dream_observability: `dream_observability_ready | wakeup_cycles=1 schedule_cycles=0 warnings=1 overall_ok=yes`
- dream_runtime_posture: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
- dream_problem_route: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
- dream_artifact_policy: `dashboard_inputs | wakeup=yes schedule=no invalid_json=0`

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.18 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 21.92 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 127.20 | `python -m pytest tests -q` |
| web_lint | FAIL | 127 | 0.31 | `npm --prefix apps/web run lint` |
| web_test | FAIL | 127 | 0.12 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 0.45 | `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28` |
| commit_attribution | FAIL | 1 | 0.12 | `python scripts/verify_incremental_commit_attribution.py --strict --artifact-path docs/status/commit_attribution_local.json` |
| dual_track_boundary | PASS | 0 | 0.06 | `python scripts/verify_dual_track_boundary.py --strict --staged` |
| persona_swarm | PASS | 0 | 0.45 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.09 | `python scripts/verify_external_source_registry.py --strict` |
| status_freshness | PASS | 0 | 0.12 | `python scripts/verify_status_freshness.py --strict` |
| doc_links | PASS | 0 | 0.29 | `python scripts/verify_doc_links.py --strict` |
| skill_registry | PASS | 0 | 0.08 | `python scripts/verify_skill_registry.py --strict` |
| multi_agent_divergence | PASS | 0 | 0.05 | `python scripts/run_multi_agent_divergence_report.py --strict` |
| memory_quality | PASS | 0 | 0.05 | `python scripts/run_memory_quality_report.py --strict` |
| memory_governance_contract | PASS | 0 | 0.05 | `python scripts/run_memory_governance_contract_check.py --strict` |
| friction_shadow_replay_export | FAIL | 1 | 0.05 | `python scripts/run_friction_shadow_replay_export.py --strict` |
| friction_shadow_calibration | FAIL | 1 | 0.07 | `python scripts/run_friction_shadow_calibration_report.py --strict` |
| philosophical_reflection | PASS | 0 | 0.05 | `python scripts/run_philosophical_reflection_report.py --strict` |
| memory_topology_fit | PASS | 0 | 0.05 | `python scripts/run_memory_topology_fit_report.py --strict` |
| repo_intelligence | PASS | 0 | 0.22 | `python scripts/run_repo_intelligence_report.py` |
| true_verification_weekly | SKIP | - | 0.00 | `python scripts/report_true_verification_task_status.py --strict` |
| audit_7d | SKIP | - | 0.00 | `python scripts/verify_7d.py` |

## Handoff Previews
- `repo_intelligence` (`repo_intelligence_ready`): `repo_intelligence_ready | available_surfaces=4/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
  - runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
  - artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`
  - requires_operator_action: `false`

## Repo Intelligence Mirror
- name: `repo_intelligence`
- queue_shape: `repo_intelligence_ready`
- requires_operator_action: `false`
- primary_status_line: `repo_intelligence_ready | available_surfaces=4/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`

## Repo Semantic Atlas Mirror
- None

## Weekly Host Status Mirror
- None

## Subjectivity Focus Mirror
- path: `docs/status/subjectivity_review_batch_latest.json`
- name: `subjectivity_review_batch`
- queue_shape: `monitoring_queue`
- requires_operator_action: `false`
- primary_status_line: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- admissibility_primary_status_line: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`

## Agent Integrity Mirror
- None

## Failures
- `web_lint`: sh: 1: eslint: not found
- `web_test`: sh: 1: vitest: not found
- `commit_attribution`: ",
        "tools/probe/memory_claim_fuzzy_redteam_eval.py",
        "tools/probe/memory_consent_eval.py",
        "tools/probe/memory_output_surface_eval.py",
        "tools/probe/memory_response_composer_eval.py",
        "tools/probe/output_redaction_eval.py",
        "tools/probe/reflection_revision_probe.py",
        "tools/probe/responsibility_runtime_eval.py",
        "tools/probe/semantic_overclaim_eval.py",
        "tools/probe/stance_survival_probe.py",
        "tools/schema.py",
        "tools/summary_ball_converter.py",
        "tools/theater_page/precompute_council.py",
        "tools/trace_dataset/__init__.py",
        "tools/trace_dataset/extract.py",
        "tools/trace_dataset/validate.py",
        "vercel.json"
      ],
      "docs_only": false,
      "exempted": false,
      "exemption_reason": null,
      "rev": "6569a1dcca92517fff33ef841daf3ff83bb6313d",
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
- `friction_shadow_replay_export`:   "min_scenarios": 24,
    "max_invalid_lines": 200,
    "max_avg_tension_drift": 0.35,
    "max_avg_friction_drift": 0.35,
    "max_high_friction_rate_drift": 0.4,
    "min_scenario_count_ratio": 0.2
  },
  "metrics": {
    "scenario_count": 2,
    "source_journal_count": 2,
    "source_discussion_count": 0,
    "source_synthetic_count": 0,
    "free_tier_count": 0,
    "premium_tier_count": 2,
    "journal_invalid_json_line_count": 0,
    "discussion_invalid_json_line_count": 0,
    "invalid_json_line_count": 0,
    "average_initial_tension": 0.573,
    "average_friction_score": 0.6,
    "high_friction_scenario_count": 0,
    "high_friction_scenario_rate": 0.0,
    "drift": {
      "has_previous_snapshot": true,
      "guard_applied": true,
      "guard_skip_reason": null,
      "scenario_count_ratio": 0.0048,
      "average_initial_tension_delta": 0.1753,
      "average_friction_score_delta": 0.2211,
      "high_friction_scenario_rate_delta": -0.0095
    }
  },
  "issues": [
    "scenario_count below threshold (2 < 24)",
    "scenario_count ratio below threshold (0.0048 < 0.2)"
  ],
  "warnings": [
    "discussion path does not exist: memory/agent_discussion_curated.jsonl"
  ]
}
- `friction_shadow_calibration`: ncil_rate": 1.0,
    "council_rate_delta": 0.0,
    "high_friction_candidate_count": 0,
    "high_friction_escape_count": 0,
    "high_friction_escape_rate": 0.0
  },
  "route_distribution": {
    "active": {
      "route_local_llm": 0,
      "route_single_cloud": 0,
      "route_full_council": 2,
      "block_rate_limit": 0
    },
    "shadow": {
      "route_local_llm": 0,
      "route_single_cloud": 0,
      "route_full_council": 2,
      "block_rate_limit": 0
    }
  },
  "friction_band_metrics": [
    {
      "band": "low",
      "count": 0,
      "active_council_rate": 0.0,
      "shadow_council_rate": 0.0
    },
    {
      "band": "mid",
      "count": 2,
      "active_council_rate": 1.0,
      "shadow_council_rate": 1.0
    },
    {
      "band": "high",
      "count": 0,
      "active_council_rate": 0.0,
      "shadow_council_rate": 0.0
    },
    {
      "band": "unknown",
      "count": 0,
      "active_council_rate": 0.0,
      "shadow_council_rate": 0.0
    }
  ],
  "route_changes": [],
  "issues": [
    "insufficient calibration scenarios: 2 (< 8)"
  ],
  "warnings": [
    "shadow thresholds are identical to active thresholds (this run is a baseline snapshot)."
  ]
}

## Skipped
- `true_verification_weekly`: requires Windows Task Scheduler host
- `audit_7d`: missing discussion file: /home/runner/work/tonesoul52/tonesoul52/memory/agent_discussion_curated.jsonl

## Recovery Advice
- `commit_attribution_recovery`: backfill_branch_not_viable
  - rationale: Backfill branch does not currently satisfy attribution requirements, so base switching would not remove the governance debt.
