# Repo Healthcheck Latest

- generated_at: 2026-02-13T17:20:33Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.11 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 1.08 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 76.89 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 7.70 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.25 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 2.04 | `python scripts/verify_git_hygiene.py` |
| audit_7d | PASS | 0 | 102.04 | `python scripts/verify_7d.py` |
