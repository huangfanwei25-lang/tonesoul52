# Encoder/Dependency Scan Results (ToneSoul 5.2)

## Encoding Scan
- Failed on: `archive/舊檔案/ToneSoul-Memory-Vault-main - 複製/README.md`
- Cause: non-UTF8 bytes.
- Suggested: identify encoding (likely UTF-16/UTF-8 BOM or legacy) and re-save.

## Dependency Scan
- Use: `python -m tonesoul52.run_dependency_scan`
- Expected misses: streamlit/plotly/pandas/psutil in requirements/pyproject.
