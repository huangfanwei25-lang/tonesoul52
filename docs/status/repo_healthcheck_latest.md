# Repo Healthcheck Latest

- generated_at: 2026-02-10T10:01:15Z
- overall_ok: true

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| python_lint | PASS | 0 | 0.10 | `python -m ruff check tonesoul tests scripts` |
| python_format | PASS | 0 | 0.60 | `python -m black --check tonesoul tests scripts` |
| python_tests | PASS | 0 | 38.48 | `python -m pytest tests -q` |
| web_lint | PASS | 0 | 5.55 | `npm --prefix apps/web run lint` |
| web_test | PASS | 0 | 1.51 | `npm --prefix apps/web run test` |
| git_hygiene | PASS | 0 | 38.62 | `python scripts/verify_git_hygiene.py` |
| audit_7d | PASS | 0 | 51.33 | `python scripts/verify_7d.py --include-sdh --check-council-modes` |
