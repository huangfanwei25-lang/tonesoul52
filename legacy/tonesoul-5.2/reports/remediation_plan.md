# Remediation Plan (ToneSoul 5.2)

This plan proposes fixes without modifying legacy workspaces. Implement via patches or instructions when approved.

## 1) Dependency Alignment
- Update `requirements.txt` to include:
  - `streamlit`, `plotly`, `pandas`, `psutil`, `numpy`, `chromadb`, `sentence-transformers`, `requests`
- Update `pyproject.toml` `[project].dependencies` to match the runtime list.
- Keep dev-only tools in a separate dev group or `requirements-dev.txt`.

## 2) Encoding Normalization
- Target files: `yuhun_cli.py`, `ToneSoul-Repo/app.py`, `body/dashboard/app.py`.
- Re-save as UTF-8 (no BOM) and replace garbled strings.
- Move banners and UI strings into a dedicated module to enforce consistent encoding.

## 3) Dashboard Portability
- Replace absolute `file:///c:/Users/...` links with relative `docs/...` paths.
- Add a helper to resolve doc paths from repo root at runtime.

## 4) Entrypoint Stability
- Create a canonical CLI entrypoint (single file) and update test scripts to import it.
- Ensure `run_dashboard.py` exists and points to `body/dashboard/app.py`.

## 5) Import-Time Side Effects
- Avoid heavy logic or emoji output during module import (use functions instead).
- On Windows, force UTF-8 output where necessary:
  - `sys.stdout.reconfigure(encoding="utf-8")` (Py 3.7+)

## 6) Test Strategy
- Add smoke checks for imports and entrypoint existence.
- Skip Ollama-dependent tests unless `OLLAMA_HOST` is reachable.
