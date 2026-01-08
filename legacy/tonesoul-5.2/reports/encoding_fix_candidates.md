# Encoding Fix Candidates (ToneSoul 5.2)

## Known Problem Files
- `ToneSoul-Repo/app.py`
- `yuhun_cli.py`
- `body/dashboard/app.py`
- `archive/舊檔案/ToneSoul-Memory-Vault-main - 複製/README.md`

## Suggested Workflow
1. Detect encoding:
   - Use a detector (e.g., `chardet` or `charset-normalizer`).
2. Re-save as UTF-8 (no BOM).
3. Replace garbled glyphs with ASCII or intended text.

## Notes
- Keep banner text in separate module to reduce encoding drift.
- Avoid emoji in import-time prints to prevent cp950 errors.
