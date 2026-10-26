# Status Artifact Freshness

- generated_at: 2026-10-26T07:14:48Z
- overall_ok: `false`
- policy: assertive<= 45d, episodic<= 120d
- artifacts: 80 (fresh 11, stale assertive 28, stale episodic 29, untimestamped 12)

## Failures (stale, undated, or future-dated assertive artifacts)

| artifact | age (days) | issue |
|---|---|---|
| docs/status/abc_firewall_latest.json | 116 | stale |
| docs/status/autonomous_registry_schedule_latest.json | 115 | stale |
| docs/status/changed_surface_checks_latest.json | 115 | stale |
| docs/status/collaborator_beta_preflight_latest.json | 115 | stale |
| docs/status/command_registry_latest.json | 116 | stale |
| docs/status/doc_links_latest.json | 114 | stale |
| docs/status/dream_observability_latest.json | 115 | stale |
| docs/status/external_source_registry_latest.json | 115 | stale |
| docs/status/friction_shadow_calibration_latest.json | 114 | stale |
| docs/status/friction_shadow_replay_latest.json | 114 | stale |
| docs/status/l8_adapter_dataset_gate_latest.json | 115 | stale |
| docs/status/memory_governance_contract_latest.json | 114 | stale |
| docs/status/memory_quality_latest.json | 114 | stale |
| docs/status/memory_topology_fit_latest.json | 114 | stale |
| docs/status/multi_agent_divergence_latest.json | 114 | stale |
| docs/status/philosophical_reflection_latest.json | 114 | stale |
| docs/status/private_memory_review_latest.json | 115 | stale |
| docs/status/refreshable_artifact_report_latest.json | 115 | stale |
| docs/status/repo_governance_settlement_latest.json | 115 | stale |
| docs/status/repo_healthcheck_latest.json | 114 | stale |
| docs/status/runtime_source_change_groups_latest.json | 115 | stale |
| docs/status/stale_command_refs_latest.json | 116 | stale |
| docs/status/subjectivity_report_latest.json | 115 | stale |
| docs/status/subjectivity_review_batch_latest.json | 115 | stale |
| docs/status/subjectivity_shadow_pressure_latest.json | 115 | stale |
| docs/status/subjectivity_tension_groups_latest.json | 115 | stale |
| docs/status/submodule_integrity_latest.json | 116 | stale |
| docs/status/worktree_settlement_latest.json | 115 | stale |

## Warnings (episodic)

| artifact | age (days) | issue |
|---|---|---|
| docs/status/basename_divergence_distillation_latest.json | 217 | stale |
| docs/status/change_intent_latest.json | 221 | stale |
| docs/status/claim_authority_latest.json | 212 | stale |
| docs/status/collaborator_beta_entry_validation_latest.json | 210 | stale |
| docs/status/commit_attribution_base_switch_latest.json | 231 | stale |
| docs/status/corrective_recall_characterization_latest.json | 130 | stale |
| docs/status/council_calibration_latest.json | 193 | stale |
| docs/status/cross_agent_consistency_latest.json | 146 | stale |
| docs/status/doc_authority_structure_latest.json | 201 | stale |
| docs/status/egress_gate_characterization_latest.json | 130 | stale |
| docs/status/engineering_mirror_ownership_latest.json | 217 | stale |
| docs/status/historical_doc_lane_latest.json | 217 | stale |
| docs/status/l7_operational_packet_latest.json | 217 | stale |
| docs/status/l7_retrieval_contract_latest.json | 217 | stale |
| docs/status/l8_distillation_boundary_latest.json | 217 | stale |
| docs/status/observer_window_latest.json | 193 | stale |
| docs/status/paradox_fixture_ownership_latest.json | 217 | stale |
| docs/status/persona_swarm_long_task_latest.json | 238 | stale |
| docs/status/private_memory_shadow_latest.json | 217 | stale |
| docs/status/self_play_resonance_latest.json | 237 | stale |
| docs/status/swarm_long_task_plan_latest.json | 238 | stale |
| docs/status/swarm_resonance_roleplay_latest.json | 237 | stale |
| docs/status/tonesoul_convergence_audit_latest.json | 194 | stale |
| docs/status/tonesoul_knowledge_graph_latest.json | 217 | stale |
| docs/status/v1_2_tool_entry_smoke_latest.json | 191 | stale |
| reports/model_comparison_latest.json | 233 | stale |
| docs/status/philosophical_reflection_rfc013_latest.md | 238 | stale |
| docs/status/repo_hygiene_value_triage_latest.md | 223 | stale |
| reports/test_coverage_latest.md | 254 | stale |
| docs/status/dilemma_pressure_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/drift_consistency_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/honesty_scoreboard_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/independent_check_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/launch_continuity_validation_wave_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/multi_persona_eval_latest.json | — | untimestamped (timestamp field present but null) |
| docs/status/self_improvement_trial_wave_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/sycophancy_pressure_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/unsourced_confidence_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| reports/decay_query_benchmark_latest.json | — | untimestamped (no recognizable timestamp field) |
| reports/security_pip_audit_latest.json | — | untimestamped (no recognizable timestamp field) |
| reports/security_vulnerability_assessment_latest.md | — | untimestamped (no generated_at line) |

A stale assertive artifact is treated as a failure because an expired `ok=true` can mask a live regression (incident of 2026-07-02, abc_firewall). Regenerate via the owning script, or rename one-off records from `*_latest.*` to dated filenames so they leave the freshness contract.
