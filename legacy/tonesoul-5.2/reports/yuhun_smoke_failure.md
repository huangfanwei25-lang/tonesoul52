# YuHun CLI Smoke Failure Analysis (ToneSoul 5.2)

Command: `python -m tonesoul52.run_yuhun_smoke`

## Failure Summary
- Relative imports fail when `yuhun_cli.py` is executed from repo root.
- `body/yuhun_metrics.py` -> `body/neuro_sensor_v2.py` relative import fails.
- UnicodeEncodeError on cp950 when printing warning emoji.

## Likely Root Causes
1. `body` is treated as a top-level package but relative imports assume package context.
2. Emoji printing on Windows cp950 terminal encoding.

## Suggested Fixes (No edits applied)
- Normalize import paths in `body/*` to use absolute imports.
- Add `sys.path` adjustment in `yuhun_cli.py` to include repo root and `body`.
- Remove emoji from log lines or force UTF-8 output.
