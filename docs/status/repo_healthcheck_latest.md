# Repo Healthcheck Latest

- generated_at: 2026-02-20T18:17:23Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.09 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.62 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 73.45 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 6.36 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.23 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 1.85 | `python scripts/verify_git_hygiene.py` |
| persona_swarm | PASS | 0 | 0.29 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.12 | `python scripts/verify_external_source_registry.py --strict` |
| audit_7d | PASS | 0 | 96.72 | `python scripts/verify_7d.py` |
