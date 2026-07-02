# Status Artifact Freshness

- generated_at: 2026-07-02T05:13:29Z
- overall_ok: `false`
- policy: assertive<= 45d, episodic<= 120d
- artifacts: 72 (fresh 42, stale assertive 16, stale episodic 5, untimestamped 9)

## Failures (stale, undated, or future-dated assertive artifacts)

| artifact | age (days) | issue |
|---|---|---|
| docs/status/autonomous_registry_schedule_latest.json | 116 | stale |
| docs/status/changed_surface_checks_latest.json | 102 | stale |
| docs/status/collaborator_beta_preflight_latest.json | 77 | stale |
| docs/status/dream_observability_latest.json | 116 | stale |
| docs/status/external_source_registry_latest.json | 131 | stale |
| docs/status/l8_adapter_dataset_gate_latest.json | 101 | stale |
| docs/status/observer_window_validation_latest.json | 91 | stale |
| docs/status/private_memory_review_latest.json | 115 | stale |
| docs/status/refreshable_artifact_report_latest.json | 112 | stale |
| docs/status/repo_governance_settlement_latest.json | 112 | stale |
| docs/status/runtime_source_change_groups_latest.json | 115 | stale |
| docs/status/subjectivity_report_latest.json | 112 | stale |
| docs/status/subjectivity_review_batch_latest.json | 112 | stale |
| docs/status/subjectivity_shadow_pressure_latest.json | 113 | stale |
| docs/status/subjectivity_tension_groups_latest.json | 112 | stale |
| docs/status/worktree_settlement_latest.json | 112 | stale |

## Warnings (episodic)

| artifact | age (days) | issue |
|---|---|---|
| docs/status/persona_swarm_long_task_latest.json | 122 | stale |
| docs/status/self_play_resonance_latest.json | 121 | stale |
| docs/status/swarm_long_task_plan_latest.json | 122 | stale |
| docs/status/swarm_resonance_roleplay_latest.json | 121 | stale |
| docs/status/philosophical_reflection_rfc013_latest.md | 122 | stale |
| docs/status/dilemma_pressure_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/drift_consistency_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/honesty_scoreboard_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/independent_check_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/launch_continuity_validation_wave_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/multi_persona_eval_latest.json | — | untimestamped (timestamp field present but null) |
| docs/status/self_improvement_trial_wave_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/sycophancy_pressure_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |
| docs/status/unsourced_confidence_characterization_latest.json | — | untimestamped (no recognizable timestamp field) |

A stale assertive artifact is treated as a failure because an expired `ok=true` can mask a live regression (incident of 2026-07-02, abc_firewall). Regenerate via the owning script, or rename one-off records from `*_latest.*` to dated filenames so they leave the freshness contract.
