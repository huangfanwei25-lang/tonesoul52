# ToneSoul 5.2 Architecture Map (Read-Only Synthesis)

## Layer Model
- Law Layer: `law/` (axioms, constitutional rules)
- Core Layer: `core/` (governance, reasoning, dreaming)
- Modules Layer: `modules/` (protocol, integrity, ethics)
- Body Layer: `body/` (spine/controller, sensors, dashboard, memory)
- Data Layer: `data/`, `memory/`, `ledger.jsonl`

## Main Control Flow (Conceptual)
1. User Input
2. Telemetry Sensor (STREI metrics)
3. Guardian (axiom enforcement)
4. LLM Bridge / Brain
5. Ledger append
6. Response output

## Key Entrypoints
- Dashboard: `run_dashboard.py` -> `body/dashboard/app.py`
- CLI: `yuhun_cli.py`
- Dream Cycle: `body/run_dream_cycle.py`

## Observed Constraints
- Law is immutable.
- Core reads Law; no reverse dependency.
- Modules should avoid circular dependencies.

## Risks Observed (No edits yet)
- Dependency mismatch across files.
- Encoding/garbled strings in some code artifacts.
- Absolute file links in the dashboard.
