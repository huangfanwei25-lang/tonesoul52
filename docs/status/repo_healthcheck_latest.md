# Repo Healthcheck Latest

- generated_at: 2026-02-13T20:14:16Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.11 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.72 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 73.77 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 7.31 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.62 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 1.98 | `python scripts/verify_git_hygiene.py` |
| persona_swarm | PASS | 0 | 0.31 | `python scripts/run_persona_swarm_framework.py --strict` |
| audit_7d | PASS | 0 | 100.47 | `python scripts/verify_7d.py` |
