# Repo Healthcheck Latest

- generated_at: 2026-06-01T12:52:32Z
- overall_ok: false
- handoff_preview_count: 2
- repo_intelligence: `repo_intelligence_ready | available_surfaces=5/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
- repo_intelligence_entrypoints: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
- weekly_host_status: `task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick runtime_source=none session=n/a resumed=no`
- weekly_runtime_posture: `none | runtime_lineage=unavailable`
- weekly_scribe_posture: `none | scribe=unavailable`
- weekly_artifact_policy: `host_trigger_mode=single_tick | experiment_summary=ignored reason=host_tick_single_tick_mode`
- subjectivity_focus: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- subjectivity_admissibility: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`
- scribe_state_document: `generated | mode=template_assist model=gemma3:4b fallback_mode=observed_history attempts=3 latest=chronicle_pair`
- scribe_state_posture: `state_document | tensions=1 collisions=0 crystals=0 posture=pressure_without_counterweight`
- scribe_lead_anchor: `anchor | [tension_afbd38eb] tension: High PE valuation (46.7x) in a market pullback vs. Strong structural margin inflection...`
- scribe_problem_route: `route | family=F6_semantic_role_boundary_integrity invariant=chronicle_self_scope repair=semantic_boundary_guardrail secondary=F4_execution_contract_integrity`
- scribe_artifact_policy: `artifact_source=chronicle_pair | chronicle=yes companion=yes`

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | FAIL | 1 | 0.14 | `python -m ruff check tonesoul tests scripts` |
| python_format | FAIL | 1 | 1.89 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 740.90 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 6.20 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.29 | `npm --prefix apps/web run test` |
| git_hygiene | FAIL | 1 | 3.16 | `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28` |
| commit_attribution | PASS | 0 | 0.30 | `python scripts/verify_incremental_commit_attribution.py --strict --artifact-path docs/status/commit_attribution_local.json` |
| dual_track_boundary | PASS | 0 | 0.11 | `python scripts/verify_dual_track_boundary.py --strict --staged` |
| persona_swarm | PASS | 0 | 0.54 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.13 | `python scripts/verify_external_source_registry.py --strict` |
| skill_registry | FAIL | 1 | 0.10 | `python scripts/verify_skill_registry.py --strict` |
| multi_agent_divergence | PASS | 0 | 0.09 | `python scripts/run_multi_agent_divergence_report.py --strict` |
| memory_quality | PASS | 0 | 0.08 | `python scripts/run_memory_quality_report.py --strict` |
| memory_governance_contract | PASS | 0 | 0.07 | `python scripts/run_memory_governance_contract_check.py --strict` |
| friction_shadow_replay_export | PASS | 0 | 0.09 | `python scripts/run_friction_shadow_replay_export.py --strict` |
| friction_shadow_calibration | PASS | 0 | 0.10 | `python scripts/run_friction_shadow_calibration_report.py --strict` |
| philosophical_reflection | PASS | 0 | 0.11 | `python scripts/run_philosophical_reflection_report.py --strict` |
| memory_topology_fit | PASS | 0 | 0.09 | `python scripts/run_memory_topology_fit_report.py --strict` |
| repo_intelligence | PASS | 0 | 0.28 | `python scripts/run_repo_intelligence_report.py` |
| true_verification_weekly | PASS | 0 | 0.81 | `python scripts/report_true_verification_task_status.py --strict` |
| audit_7d | PASS | 0 | 172.85 | `python scripts/verify_7d.py` |

## Handoff Previews
- `repo_intelligence` (`repo_intelligence_ready`): `repo_intelligence_ready | available_surfaces=5/7 protected_files=5 watched_dirs=3 adoption=sidecar_only`
  - runtime_status_line: `entrypoints | repo=repo_healthcheck_latest.json atlas=repo_semantic_atlas_latest.json integrity=agent_integrity_latest.json settlement=repo_governance_settlement_latest.json review=runtime_source_change_groups_latest.json weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json semantic_protocol=unavailable semantic_first=unavailable`
  - artifact_policy_status_line: `external_repo_intelligence=sidecar_only | main_repo_install=no hooks=no protected_files=no`
  - requires_operator_action: `false`
- `true_verification_weekly` (`weekly_host_status`): `task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick runtime_source=none session=n/a resumed=no`
  - runtime_status_line: `none | runtime_lineage=unavailable`
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
- artifact_policy_status_line: `host_trigger_mode=single_tick | experiment_summary=ignored reason=host_tick_single_tick_mode`
- scribe_status_line: `none | scribe=unavailable`

## Subjectivity Focus Mirror
- path: `docs/status/subjectivity_review_batch_latest.json`
- name: `subjectivity_review_batch`
- queue_shape: `stable_history_only`
- requires_operator_action: `false`
- primary_status_line: `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- admissibility_primary_status_line: `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Agent Integrity Mirror
- None

## Failures
- `python_lint`:    print(f"\n{'=' * 80}")
154 |     print(f"ToneSoul Market Scanner — Multi-Stage Stock Screener")
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
155 |     print(f"{'=' * 80}")
    |
help: Remove extraneous `f` prefix

F541 [*] f-string without any placeholders
   --> scripts\run_market_scanner.py:186:19
    |
184 |         # 3. Decision to pass to LLM Phase
185 |         if struct_friction <= STRUCTURAL_CUTOFF:
186 |             print(f"   ↳ ✅ Pass: Triggering AI World Model Debate")
    |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
187 |             context = simulator.run_simulation(f"{item.id}_{item.name}", item.snapshots)
188 |             result.passed_filter = True
    |
help: Remove extraneous `f` prefix

F541 [*] f-string without any placeholders
   --> scripts\run_market_scanner.py:203:11
    |
202 |     print(f"\n\n{'=' * 80}")
203 |     print(f"🏆 TONESOUL GOVERNANCE LEADERBOARD")
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
204 |     print(f"{'=' * 80}")
    |
help: Remove extraneous `f` prefix

Found 45 errors.
[*] 44 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
- `python_format`: would reformat C:\Users\user\Desktop\倉庫\tests\test_static_surface_security.py
would reformat C:\Users\user\Desktop\倉庫\scripts\run_publish_push_preflight.py
would reformat C:\Users\user\Desktop\倉庫\tonesoul\observability\execution_honesty.py
would reformat C:\Users\user\Desktop\倉庫\scripts\run_consumer_drift_validation_wave.py
would reformat C:\Users\user\Desktop\倉庫\scripts\run_cross_agent_consistency_wave.py
would reformat C:\Users\user\Desktop\倉庫\scripts\launch_dashboard.py
would reformat C:\Users\user\Desktop\倉庫\scripts\run_observer_window.py

Oh no! 💥 💔 💥
7 files would be reformatted, 874 files would be left unchanged.
- `git_hygiene`: ata/responses.json\nmemory/autonomous/session_traces.jsonl\nmemory/autonomous/zone_registry.json\nmemory/crystals.jsonl\nmemory/memory_base/tonesoul_cognitive.index\nmemory/memory_base/tonesoul_metadata.jsonl\nspec/wfgy_semantic_control_spec.md",
      "stderr_tail": ""
    }
  ],
  "issues": [
    "dangling objects 78 exceeds threshold 50"
  ],
  "fsck_unexpected_lines": [],
  "tracked_ignored_paths": [
    "data/YuHun_v2.6_knowledgebase.json",
    "data/YuHun_v2.6_knowledgebase_extended.json",
    "data/semantic_spine_fixtures.json",
    "data/yuhun_academy_knowledgebase_v1.1.txt",
    "\"data/\\350\\252\\236\\351\\255\\202\\345\\212\\207\\345\\240\\264_API_\\346\\234\\200\\347\\265\\202\\347\\211\\210_v1.3.json\"",
    "docs/chronicles/task_archive_phase_570-854.md",
    "docs/status/persona_swarm_framework_latest.json",
    "experiments/tsd1_pilot/data/prompts.json",
    "experiments/tsd1_pilot/data/responses.json",
    "memory/autonomous/session_traces.jsonl",
    "memory/autonomous/zone_registry.json",
    "memory/crystals.jsonl",
    "memory/memory_base/tonesoul_cognitive.index",
    "memory/memory_base/tonesoul_metadata.jsonl",
    "spec/wfgy_semantic_control_spec.md"
  ]
}
- `skill_registry`: {
  "generated_at": "2026-06-01T12:49:37Z",
  "ok": false,
  "failed_count": 2,
  "warning_count": 0,
  "checks": [
    {
      "name": "schema",
      "status": "fail",
      "detail": "schema payload is missing or invalid JSON object"
    },
    {
      "name": "registry",
      "status": "fail",
      "detail": "registry payload is missing or invalid JSON object"
    }
  ],
  "inputs": {
    "registry": "skills/registry.json",
    "schema": "skills/registry.schema.json",
    "skills_root": ".agent/skills",
    "today": "2026-06-01"
  }
}
