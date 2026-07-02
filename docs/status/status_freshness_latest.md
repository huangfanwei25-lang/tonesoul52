# Status Artifact Freshness

- generated_at: 2026-07-02T08:01:00Z
- overall_ok: `true`
- policy: assertive<= 45d, episodic<= 120d
- artifacts: 72 (fresh 58, stale assertive 0, stale episodic 5, untimestamped 9)

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
