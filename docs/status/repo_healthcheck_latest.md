# Repo Healthcheck Latest

- generated_at: 2026-02-13T15:23:28Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.15 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.84 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 82.47 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 7.33 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 2.26 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 1.90 | `python scripts/verify_git_hygiene.py` |
| audit_7d | PASS | 0 | 98.36 | `python scripts/verify_7d.py` |
