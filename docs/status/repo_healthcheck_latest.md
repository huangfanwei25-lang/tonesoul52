# Repo Healthcheck Latest

- generated_at: 2026-07-03T21:40:15Z
- overall_ok: true
- handoff_preview_count: 2
- repo_intelligence: `repo_intelligence_ready | available_surfaces=5/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- repo_intelligence_entrypoints: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- weekly_host_status: `task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick runtime_source=none session=n/a resumed=no`
- weekly_runtime_posture: `none | runtime_lineage=unavailable`
- weekly_scribe_posture: `none | scribe=unavailable`
- weekly_artifact_policy: `host_trigger_mode=single_tick | experiment_summary=ignored reason=host_tick_single_tick_mode`
- subjectivity_focus: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- subjectivity_admissibility: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`
- dream_observability: `dream_observability_ready | wakeup_cycles=1 schedule_cycles=0 warnings=1 overall_ok=yes`
- dream_runtime_posture: `wakeup_scribe | status=llm_unavailable posture=anchor_only source=companion_only`
- dream_problem_route: `route | family=F4_execution_contract_integrity invariant=local_model_availability repair=model_allowlist_and_runtime_readiness`
- dream_artifact_policy: `dashboard_inputs | wakeup=yes schedule=no invalid_json=0`
- dream_weekly_alignment: `dream_weekly_alignment | alignment=partial dream=F4_execution_contract_integrity`
- scribe_state_document: `generated | mode=llm_chronicle model=qwen2.5:1.5b fallback_mode=observed_history attempts=1 latest=chronicle_pair`
- scribe_state_posture: `state_document | tensions=1 collisions=0 crystals=0 posture=pressure_without_counterweight`
- scribe_lead_anchor: `anchor | [tension_afbd38eb] tension: High PE valuation (46.7x) in a market pullback vs. Strong structural margin inflection...`
- scribe_artifact_policy: `artifact_source=chronicle_pair | chronicle=yes companion=yes`

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.11 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 1.63 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 952.68 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 6.78 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.00 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 3.29 | `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28` |
| commit_attribution | PASS | 0 | 0.27 | `python scripts/verify_incremental_commit_attribution.py --strict --artifact-path docs/status/commit_attribution_local.json` |
| dual_track_boundary | PASS | 0 | 0.11 | `python scripts/verify_dual_track_boundary.py --strict --staged` |
| persona_swarm | PASS | 0 | 0.76 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.14 | `python scripts/verify_external_source_registry.py --strict` |
| status_freshness | PASS | 0 | 0.23 | `python scripts/verify_status_freshness.py --strict` |
| doc_links | PASS | 0 | 0.66 | `python scripts/verify_doc_links.py --strict` |
| skill_registry | PASS | 0 | 0.13 | `python scripts/verify_skill_registry.py --strict` |
| multi_agent_divergence | PASS | 0 | 0.11 | `python scripts/run_multi_agent_divergence_report.py --strict` |
| memory_quality | PASS | 0 | 0.11 | `python scripts/run_memory_quality_report.py --strict` |
| memory_governance_contract | PASS | 0 | 0.08 | `python scripts/run_memory_governance_contract_check.py --strict` |
| friction_shadow_replay_export | PASS | 0 | 0.11 | `python scripts/run_friction_shadow_replay_export.py --strict` |
| friction_shadow_calibration | PASS | 0 | 0.11 | `python scripts/run_friction_shadow_calibration_report.py --strict` |
| philosophical_reflection | PASS | 0 | 0.15 | `python scripts/run_philosophical_reflection_report.py --strict` |
| memory_topology_fit | PASS | 0 | 0.11 | `python scripts/run_memory_topology_fit_report.py --strict` |
| repo_intelligence | PASS | 0 | 0.35 | `python scripts/run_repo_intelligence_report.py` |
| true_verification_weekly | PASS | 0 | 1.03 | `python scripts/report_true_verification_task_status.py --strict` |
| audit_7d | PASS | 0 | 213.91 | `python scripts/verify_7d.py` |

## Handoff Previews
- `repo_intelligence` (`repo_intelligence_ready`): `repo_intelligence_ready | available_surfaces=5/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
  - runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
  - artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`
  - requires_operator_action: `false`
- `true_verification_weekly` (`weekly_host_status`): `task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick runtime_source=none session=n/a resumed=no`
  - runtime_status_line: `none | runtime_lineage=unavailable`
  - dream_weekly_alignment_line: `dream_weekly_alignment | alignment=partial dream=F4_execution_contract_integrity`
  - artifact_policy_status_line: `host_trigger_mode=single_tick | experiment_summary=ignored reason=host_tick_single_tick_mode`
  - scribe_status_line: `none | scribe=unavailable`
  - requires_operator_action: `false`

## Repo Intelligence Mirror
- name: `repo_intelligence`
- queue_shape: `repo_intelligence_ready`
- requires_operator_action: `false`
- primary_status_line: `repo_intelligence_ready | available_surfaces=5/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`

## Repo Semantic Atlas Mirror
- None

## Weekly Host Status Mirror
- name: `true_verification_weekly`
- queue_shape: `weekly_host_status`
- requires_operator_action: `false`
- primary_status_line: `task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick runtime_source=none session=n/a resumed=no`
- runtime_status_line: `none | runtime_lineage=unavailable`
- dream_weekly_alignment_line: `dream_weekly_alignment | alignment=partial dream=F4_execution_contract_integrity`
- artifact_policy_status_line: `host_trigger_mode=single_tick | experiment_summary=ignored reason=host_tick_single_tick_mode`
- scribe_status_line: `none | scribe=unavailable`

## Subjectivity Focus Mirror
- path: `docs/status/subjectivity_review_batch_latest.json`
- name: `subjectivity_review_batch`
- queue_shape: `monitoring_queue`
- requires_operator_action: `false`
- primary_status_line: `active_reject_queue | A distributed vulnerability database for Open Source | rows=1 lineages=1 cycles=1 | density=1r x1 | trigger=reject_review`
- admissibility_primary_status_line: `insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure`

## Agent Integrity Mirror
- None
