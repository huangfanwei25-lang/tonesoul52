# Inferred Work Items (ToneSoul 5.2)

This list is inferred from repository state and prior review. No changes applied outside `5.2`.

## High Priority
1. Dependency alignment
   - Update `requirements.txt` and `pyproject.toml` to reflect runtime deps.
   - Add streamlit, plotly, pandas, psutil, numpy, chromadb, sentence-transformers.

2. Encoding normalization
   - Re-save corrupted source files as UTF-8 (e.g., `ToneSoul-Repo/app.py`, `yuhun_cli.py`).
   - Verify strings render correctly and no syntax breaks.

3. Dashboard link portability
   - Replace absolute file URLs with relative docs links.

4. Stable CLI entrypoint
   - Create a single supported CLI script and keep tests pointing to it.

## Medium Priority
5. Test coverage
   - Add smoke tests for dashboard and YuHun CLI (non-interactive).
   - Flag tests that require Ollama and skip when absent.

6. Inventory automation
   - Expand 5.2 inventory to include dependency scanning and encoding checks.

## Low Priority
7. Archive clean-up policy
   - Document what to keep and what can be pruned later.

8. Documentation hygiene
   - Consolidate multiple README variants and improve onboarding.
