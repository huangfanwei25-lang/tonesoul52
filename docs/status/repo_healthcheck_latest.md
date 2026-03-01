# Repo Healthcheck Latest

- generated_at: 2026-03-01T15:22:21Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.09 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.77 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 171.67 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 7.99 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 3.13 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 2.61 | `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28` |
| dual_track_boundary | PASS | 0 | 0.13 | `python scripts/verify_dual_track_boundary.py --strict --staged` |
| persona_swarm | PASS | 0 | 0.46 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.14 | `python scripts/verify_external_source_registry.py --strict` |
| skill_registry | PASS | 0 | 0.15 | `python scripts/verify_skill_registry.py --strict` |
| multi_agent_divergence | PASS | 0 | 1.33 | `python scripts/run_multi_agent_divergence_report.py --strict` |
| memory_quality | PASS | 0 | 1.38 | `python scripts/run_memory_quality_report.py --strict` |
| memory_governance_contract | PASS | 0 | 0.09 | `python scripts/run_memory_governance_contract_check.py --strict` |
| friction_shadow_replay_export | PASS | 0 | 1.51 | `python scripts/run_friction_shadow_replay_export.py --strict` |
| friction_shadow_calibration | PASS | 0 | 0.17 | `python scripts/run_friction_shadow_calibration_report.py --strict` |
| philosophical_reflection | PASS | 0 | 2.41 | `python scripts/run_philosophical_reflection_report.py --strict` |
| memory_topology_fit | PASS | 0 | 0.09 | `python scripts/run_memory_topology_fit_report.py --strict` |
| audit_7d | PASS | 0 | 242.75 | `python scripts/verify_7d.py` |
