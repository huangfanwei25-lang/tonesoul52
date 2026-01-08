# Code Review Report (ToneSoul 5.2)

Scope: read-only review of existing workspaces. No changes applied outside `5.2`.

## Findings
1. Dependency mismatch:
   - `pyproject.toml` only lists `requests`, but runtime code uses `streamlit`, `plotly`, `pandas`, `numpy`, `chromadb`, and `sentence-transformers`.
   - `requirements.txt` includes some but not all runtime deps (streamlit/plotly/pandas/psutil are missing).
   - Impact: fresh installs will fail at runtime or tests.
   - Evidence: `body/dashboard/app.py`, `body/memory/vector_store.py`, `body/rag_engine.py`, `setup_env.ps1`.

2. Encoding corruption / mojibake in source files:
   - `ToneSoul-Repo/app.py` and `yuhun_cli.py` show garbled characters in strings and comments.
   - Impact: unreadable UX, potential syntax issues (e.g., broken quotes) and maintenance risk.

3. Absolute local file links in dashboard:
   - `body/dashboard/app.py` embeds `file:///c:/Users/user/Desktop/...` links.
   - Impact: links break on other machines and can leak local paths.

4. Test runner assumes root `app.py` exists:
   - `scripts/test_yuhun_loop.py` imports `app` from repo root.
   - Impact: failures in layouts where `app.py` is absent or moved.

## Recommendations (no direct edits yet)
- Align `requirements.txt` and `pyproject.toml` with runtime usage; keep dev-only deps separate.
- Normalize file encodings to UTF-8 and re-save corrupted files.
- Replace absolute file links with relative docs paths.
- Add a stable CLI entrypoint for the YuHun loop and have tests import that.
