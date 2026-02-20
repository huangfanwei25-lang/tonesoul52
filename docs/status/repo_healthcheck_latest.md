# Repo Healthcheck Latest

- generated_at: 2026-02-20T17:50:16Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.10 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.75 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 75.16 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 6.09 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.99 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 1.90 | `python scripts/verify_git_hygiene.py` |
| persona_swarm | PASS | 0 | 0.29 | `python scripts/run_persona_swarm_framework.py --strict` |
| external_source_registry | PASS | 0 | 0.12 | `python scripts/verify_external_source_registry.py --strict` |
| audit_7d | PASS | 0 | 98.13 | `python scripts/verify_7d.py` |
