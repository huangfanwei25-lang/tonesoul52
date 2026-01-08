# Reliability Check Report (ToneSoul 5.2)

Command: `python -m tonesoul52.run_reliability_check`

## Results
- entrypoint:dashboard -> OK
- entrypoint:dashboard_alt -> OK
- entrypoint:yuhun_cli -> OK
- entrypoint:yuhun_loop_test -> FAIL (missing `scripts/test_yuhun_loop.py`)
- entrypoint:yuhun_loop_test_52 -> OK (5.2 wrapper)
- ollama:tcp -> OK (port 11434 reachable)
