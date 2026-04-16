# ToneSoul Dashboard

ToneSoul Dashboard is the repo's operator-facing Streamlit shell.

It is not the public/demo site, and it is not a second control plane.
It sits on top of the same CLI/runtime truth used elsewhere in the repo.

## Role Boundary

Use `apps/dashboard` for:

- Tiered operator orientation
- `Tier 0 / Tier 1 / Tier 2` workspace flow
- bounded status, memory-selection, and retrieval-preview cues
- dashboard-assisted chat that still stays subordinate to runtime truth

Do not use `apps/dashboard` as:

- public product truth
- a replacement for `start_agent_session.py`, `run_observer_window.py`, or other canonical CLI entry surfaces
- a place to invent new authority labels or hidden workflow semantics

Current authority order:

1. canonical/runtime truth
2. dashboard operator shell
3. public/demo surfaces

## Start

From repo root:

```bash
python apps/dashboard/run_dashboard.py
```

Equivalent direct command:

```bash
python -m streamlit run apps/dashboard/frontend/app.py
```

Legacy launcher remains available:

```bash
python scripts/launch_dashboard.py
```

## What The Dashboard Contains

- `Workspace`
  - the tiered operator shell
  - `Tier 0` instant gate, `Tier 1` orientation shell, `Tier 2` deep-governance pull
- `Status`
  - tier-aligned operator status panel
  - subordinate to the workspace shell, not a second summary authority
- `Memory`
  - reference-selection panel
  - auxiliary to operator truth
- Retrieval preview
  - shows local/web context that fed or is about to feed a search-assisted turn
  - never outranks `Tier 0 / Tier 1 / Tier 2`

## Requirements

- Python 3.10+
- `streamlit`
- whatever optional local model/search setup your current dashboard workflow expects

Minimal install:

```bash
pip install streamlit requests pyyaml
```

## Current Operator Rule

Use the smallest tier that keeps the next move honest.

- Start in `Tier 0`
- pull `Tier 1` when the short board or orientation is unclear
- open `Tier 2` only when mutation, closeout, or contested continuity explicitly requires it

If the dashboard and canonical CLI/runtime surfaces disagree, trust the canonical CLI/runtime surfaces and treat the dashboard as stale until refreshed.
