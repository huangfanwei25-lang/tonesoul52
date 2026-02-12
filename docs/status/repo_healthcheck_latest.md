# Repo Healthcheck Latest

- generated_at: 2026-02-11T18:50:16Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.10 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.63 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 45.17 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 6.53 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.09 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 39.99 | `python scripts/verify_git_hygiene.py` |
| audit_7d | PASS | 0 | 58.29 | `python scripts/verify_7d.py` |
