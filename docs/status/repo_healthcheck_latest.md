# Repo Healthcheck Latest

- generated_at: 2026-02-10T10:12:21Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.13 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 1.64 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 39.24 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 5.69 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.41 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 37.95 | `python scripts/verify_git_hygiene.py` |
| audit_7d | PASS | 0 | 50.29 | `python scripts/verify_7d.py` |
