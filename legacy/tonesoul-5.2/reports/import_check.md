# Import Smoke Check Results (ToneSoul 5.2)

Command: `python -m tonesoul52.run_import_check`

## Results
- `body.dashboard.app`: FAIL (missing `streamlit`)
- `body.spine.controller`: FAIL (cp950 encoding error when printing emoji)
- `yuhun_cli`: OK
- `body.llm_bridge`: OK
- `body.rag_engine`: OK

## Notes
- The `body.spine.controller` failure suggests console encoding issues when modules print emojis on import.
- Recommend forcing UTF-8 output or delaying prints until runtime.
