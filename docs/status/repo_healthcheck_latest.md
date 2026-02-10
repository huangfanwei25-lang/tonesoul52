# Repo Healthcheck Latest

- generated_at: 2026-02-10T06:03:31Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.10 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.59 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 30.41 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 5.13 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.32 | `npm --prefix apps/web run test` |
| audit_7d | PASS | 0 | 45.54 | `python scripts/verify_7d.py` |
