# Changed Surface Checks Latest

- generated_at: 2026-03-21T16:38:54Z
- plan_ok: true
- checks_ok: null
- execution_mode: plan
- changed_path_count: 112
- surface_count: 3
- planned_check_count: 5
- blocking_check_count: 5
- failed_check_count: 0

## Surfaces
- `python_runtime` (97): Python modules, scripts, or tests changed and need code-level verification.
  - `scripts/render_true_verification_task_scheduler.py`
  - `scripts/verify_docs_consistency.py`
  - `scripts/verify_web_api.py`
  - `tests/smoke_test_market.py`
  - `tests/test_adaptive_deliberation.py`
  - `tests/test_adaptive_pipeline.py`
  - `tests/test_ai_sleep.py`
  - `tests/test_alert_escalation.py`
- `core_runtime` (11): Governance, memory, council, or pipeline surfaces changed and need deeper regression coverage.
  - `tonesoul/council/vtp.py`
  - `tonesoul/deliberation/engine.py`
  - `tonesoul/deliberation/persona_track_record.py`
  - `tonesoul/deliberation/perspectives.py`
  - `tonesoul/llm/lmstudio_client.py`
  - `tonesoul/llm/ollama_client.py`
  - `tonesoul/memory/crystallizer.py`
  - `tonesoul/memory/soul_db.py`
- `docs_governance` (14): Docs, workflow, or authority files changed and need consistency verification.
  - `.github/workflows/critical_path.yml`
  - `AI_ONBOARDING.md`
  - `docs/INDEX.md`
  - `docs/README.md`
  - `task.md`
  - `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - `docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md`
  - `docs/plans/tonesoul_agent_enforcement_plan_2026-03-21.md`

## Checks
- `protected_paths` [planned]: `python scripts/verify_protected_paths.py --repo-root . --strict --changed-file .github/workflows/critical_path.yml --changed-file AI_ONBOARDING.md --changed-file docs/INDEX.md --changed-file docs/README.md --changed-file scripts/render_true_verification_task_scheduler.py --changed-file scripts/verify_docs_consistency.py --changed-file scripts/verify_web_api.py --changed-file task.md --changed-file tests/smoke_test_market.py --changed-file tests/test_adaptive_deliberation.py --changed-file tests/test_adaptive_pipeline.py --changed-file tests/test_ai_sleep.py --changed-file tests/test_alert_escalation.py --changed-file tests/test_audit_interface.py --changed-file tests/test_concept_store.py --changed-file tests/test_constraint_stack.py --changed-file tests/test_context_compiler.py --changed-file tests/test_contract_observer.py --changed-file tests/test_corpus_consent.py --changed-file tests/test_council_capability.py --changed-file tests/test_council_summary_generator.py --changed-file tests/test_data_ingest.py --changed-file tests/test_deliberation_gravity.py --changed-file tests/test_dream_engine_stale_verification.py --changed-file tests/test_error_event.py --changed-file tests/test_etcl_lifecycle.py --changed-file tests/test_generation_orch.py --changed-file tests/test_handoff_builder_security.py --changed-file tests/test_integration_deliberation_council.py --changed-file tests/test_integration_memory_lifecycle.py --changed-file tests/test_integration_tonebridge_pipeline.py --changed-file tests/test_intent_reconstructor.py --changed-file tests/test_inter_soul_negotiation.py --changed-file tests/test_jump_engine.py --changed-file tests/test_lmstudio_client.py --changed-file tests/test_loop_events.py --changed-file tests/test_memory_crystallizer.py --changed-file tests/test_memory_hippocampus.py --changed-file tests/test_memory_stats.py --changed-file tests/test_mirror.py --changed-file tests/test_observability_logger.py --changed-file tests/test_ollama_client.py --changed-file tests/test_perception_stimulus.py --changed-file tests/test_persona_dimension.py --changed-file tests/test_property_soul_db.py --changed-file tests/test_reflection.py --changed-file tests/test_reflection_integration.py --changed-file tests/test_render_true_verification_task_scheduler.py --changed-file tests/test_run_change_intent_report.py --changed-file tests/test_run_subjectivity_shadow_pressure_report.py --changed-file tests/test_safe_parse.py --changed-file tests/test_security_memory_boundary.py --changed-file tests/test_semantic_embedder.py --changed-file tests/test_soul_db_migration.py --changed-file tests/test_stale_rule_verifier.py --changed-file tests/test_status_alignment.py --changed-file tests/test_subjectivity_admissibility.py --changed-file tests/test_tech_trace_normalize.py --changed-file tests/test_tonebridge_analyzer.py --changed-file tests/test_tonebridge_entropy_engine.py --changed-file tests/test_tonebridge_personas.py --changed-file tests/test_tonebridge_rupture_detector.py --changed-file tests/test_tonebridge_trajectory.py --changed-file tests/test_unified_pipeline_governance_delegate.py --changed-file tests/test_verify_web_api.py --changed-file tests/test_vow_inventory.py --changed-file tests/test_vow_system_properties.py --changed-file tests/test_web_ingest.py --changed-file tests/test_yss_gates.py --changed-file tests/test_yss_pipeline.py --changed-file tests/test_ystm_demo.py --changed-file tests/test_ystm_representation.py --changed-file tonesoul/alert_escalation.py --changed-file tonesoul/council/vtp.py --changed-file tonesoul/deliberation/engine.py --changed-file tonesoul/deliberation/persona_track_record.py --changed-file tonesoul/deliberation/perspectives.py --changed-file tonesoul/drift_monitor.py --changed-file tonesoul/drift_tracker.py --changed-file tonesoul/inter_soul/negotiation.py --changed-file tonesoul/inter_soul/sovereignty.py --changed-file tonesoul/inter_soul/types.py --changed-file tonesoul/jump_monitor.py --changed-file tonesoul/llm/lmstudio_client.py --changed-file tonesoul/llm/ollama_client.py --changed-file tonesoul/market/analyzer.py --changed-file tonesoul/market/data_ingest.py --changed-file tonesoul/memory/crystallizer.py --changed-file tonesoul/memory/soul_db.py --changed-file tonesoul/memory/stats.py --changed-file tonesoul/memory/subjectivity_shadow.py --changed-file tonesoul/mirror.py --changed-file tonesoul/stale_rule_verifier.py --changed-file tonesoul/unified_pipeline.py --changed-file tonesoul/vow_inventory.py --changed-file tonesoul/vow_system.py --changed-file .agent/workflows/repo-sync.md --changed-file docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md --changed-file docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md --changed-file docs/plans/tonesoul_agent_enforcement_plan_2026-03-21.md --changed-file docs/plans/tonesoul_knowledge_graph_plan_2026-03-21.md --changed-file docs/status/changed_surface_checks_latest.json --changed-file docs/status/changed_surface_checks_latest.md --changed-file docs/status/tonesoul_knowledge_graph_latest.json --changed-file docs/status/tonesoul_knowledge_graph_latest.md --changed-file docs/status/tonesoul_knowledge_graph_latest.mmd --changed-file scripts/run_changed_surface_checks.py --changed-file scripts/run_tonesoul_knowledge_graph.py --changed-file scripts/verify_protected_paths.py --changed-file tests/test_run_changed_surface_checks.py --changed-file tests/test_run_tonesoul_knowledge_graph.py --changed-file tests/test_verify_protected_paths.py`
  - reason: Fail closed when protected files or private memory paths are touched.
  - blocking: true
  - surfaces: `core_runtime`, `docs_governance`, `python_runtime`
- `python_lint_changed` [planned]: `python -m ruff check scripts/render_true_verification_task_scheduler.py scripts/verify_docs_consistency.py scripts/verify_web_api.py tests/smoke_test_market.py tests/test_adaptive_deliberation.py tests/test_adaptive_pipeline.py tests/test_ai_sleep.py tests/test_alert_escalation.py tests/test_audit_interface.py tests/test_concept_store.py tests/test_constraint_stack.py tests/test_context_compiler.py tests/test_contract_observer.py tests/test_corpus_consent.py tests/test_council_capability.py tests/test_council_summary_generator.py tests/test_data_ingest.py tests/test_deliberation_gravity.py tests/test_dream_engine_stale_verification.py tests/test_error_event.py tests/test_etcl_lifecycle.py tests/test_generation_orch.py tests/test_handoff_builder_security.py tests/test_integration_deliberation_council.py tests/test_integration_memory_lifecycle.py tests/test_integration_tonebridge_pipeline.py tests/test_intent_reconstructor.py tests/test_inter_soul_negotiation.py tests/test_jump_engine.py tests/test_lmstudio_client.py tests/test_loop_events.py tests/test_memory_crystallizer.py tests/test_memory_hippocampus.py tests/test_memory_stats.py tests/test_mirror.py tests/test_observability_logger.py tests/test_ollama_client.py tests/test_perception_stimulus.py tests/test_persona_dimension.py tests/test_property_soul_db.py tests/test_reflection.py tests/test_reflection_integration.py tests/test_render_true_verification_task_scheduler.py tests/test_run_change_intent_report.py tests/test_run_subjectivity_shadow_pressure_report.py tests/test_safe_parse.py tests/test_security_memory_boundary.py tests/test_semantic_embedder.py tests/test_soul_db_migration.py tests/test_stale_rule_verifier.py tests/test_status_alignment.py tests/test_subjectivity_admissibility.py tests/test_tech_trace_normalize.py tests/test_tonebridge_analyzer.py tests/test_tonebridge_entropy_engine.py tests/test_tonebridge_personas.py tests/test_tonebridge_rupture_detector.py tests/test_tonebridge_trajectory.py tests/test_unified_pipeline_governance_delegate.py tests/test_verify_web_api.py tests/test_vow_inventory.py tests/test_vow_system_properties.py tests/test_web_ingest.py tests/test_yss_gates.py tests/test_yss_pipeline.py tests/test_ystm_demo.py tests/test_ystm_representation.py tonesoul/alert_escalation.py tonesoul/council/vtp.py tonesoul/deliberation/engine.py tonesoul/deliberation/persona_track_record.py tonesoul/deliberation/perspectives.py tonesoul/drift_monitor.py tonesoul/drift_tracker.py tonesoul/inter_soul/negotiation.py tonesoul/inter_soul/sovereignty.py tonesoul/inter_soul/types.py tonesoul/jump_monitor.py tonesoul/llm/lmstudio_client.py tonesoul/llm/ollama_client.py tonesoul/market/analyzer.py tonesoul/market/data_ingest.py tonesoul/memory/crystallizer.py tonesoul/memory/soul_db.py tonesoul/memory/stats.py tonesoul/memory/subjectivity_shadow.py tonesoul/mirror.py tonesoul/stale_rule_verifier.py tonesoul/unified_pipeline.py tonesoul/vow_inventory.py tonesoul/vow_system.py scripts/run_changed_surface_checks.py scripts/run_tonesoul_knowledge_graph.py scripts/verify_protected_paths.py tests/test_run_changed_surface_checks.py tests/test_run_tonesoul_knowledge_graph.py tests/test_verify_protected_paths.py`
  - reason: Lint only the changed Python surface before wider validation.
  - blocking: true
  - surfaces: `python_runtime`
- `layer_boundaries` [planned]: `python scripts/verify_layer_boundaries.py --project-root .`
  - reason: Core runtime edits must preserve explicit architecture boundaries.
  - blocking: true
  - surfaces: `core_runtime`
- `docs_consistency` [planned]: `python scripts/verify_docs_consistency.py --repo-root .`
  - reason: Authority and workflow docs must remain consistent with runtime enforcement.
  - blocking: true
  - surfaces: `docs_governance`
- `python_full_regression` [planned]: `python -m pytest tests -x --tb=short -q`
  - reason: The change surface is broad or critical enough to require full Python regression.
  - blocking: true
  - surfaces: `core_runtime`

## Warnings
- targeted pytest candidate count exceeded limit; using full regression instead
