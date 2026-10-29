# Validation receipt — 2026-10-29

Base: public master 2f4530ccb5ce913b1b636edda209f424f132e12d.

- Focused pytest (sidecar + existing CLI): 14 passed.
- Required `pytest tests/ -x`: 8158 passed, 5 skipped, 1 warning, 45.38 seconds.
- `ruff check tonesoul tests`: passed.
- `npm run lint`: passed (Python and web).
- `npm run build`: passed with NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1;
  default run failed fetching Google Fonts due to TLS. Certificate verification stayed enabled.
- Python compileall, git diff --check, agent integrity check: passed. Existing protected-file
  metadata and skills warnings were reported; protected files were not changed.
- Initial full test failures: missing Flask dependency (environment restored), then missing
  architecture annotations on three added modules (fixed). No tests disabled.

These are engineering checks, not financial prediction validation. The source replay is
curated retrospectively. Two insufficient-evidence flags are not two proven false predictions.
The CLI is opt-in; no council outcome, account, ledger, trading behavior or scoring is modified.

Code migrated from the earlier local Evidence Audit v0.2 / Argument Integration pilot into
`tonesoul/reviewer/`. Earlier archives remain historical snapshots; this feature branch is
now the integration working location. No additional legal skill code or personal financial
records were copied into the public repository.
