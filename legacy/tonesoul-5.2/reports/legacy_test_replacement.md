# Legacy Test Replacement (ToneSoul 5.2)

## Goal
Replace missing `scripts/test_yuhun_loop.py` with a 5.2-native smoke test.

## Replacement
- Use `5.2/tonesoul52/run_yuhun_smoke.py`.
- This runs `yuhun_cli.py -h` and a short query invocation.

## Usage
```
python -m tonesoul52.run_yuhun_smoke
```

## Notes
- Non-interactive and safe for CI.
- Does not require modifying legacy scripts.
