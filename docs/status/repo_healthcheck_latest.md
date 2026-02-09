# Repo Healthcheck Latest

- generated_at: 2026-02-09T07:07:34Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.11 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.68 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 30.09 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 5.92 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.52 | `npm --prefix apps/web run test` |
| audit_7d | PASS | 0 | 37.27 | `python scripts/verify_7d.py` |
