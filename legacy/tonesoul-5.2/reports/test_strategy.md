# Test & Entrypoint Stability Strategy (ToneSoul 5.2)

## Goals
- Validate entrypoints exist.
- Provide smoke checks without modifying legacy code.
- Skip tests that require Ollama unless configured.

## 5.2 Approach
1. Keep validation in `tonesoul52.run_validate`.
2. Add a thin wrapper test in 5.2 to:
   - import entrypoint modules (non-running),
   - confirm imports do not raise,
   - log missing dependencies.
3. Optional: add a `--run` flag to execute entrypoints when explicitly requested.

## Suggested Smoke Checks (No legacy edits)
- `python -m tonesoul52.run_validate`
- `python -m tonesoul52.run_import_check`

## Skipping Rules
- If `OLLAMA_HOST` is not reachable, skip Ollama-dependent tests.
- If `streamlit` missing, skip dashboard import check.
