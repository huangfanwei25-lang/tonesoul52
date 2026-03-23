---
description: Session end governance trace — write session trace and update governance state
---

# Session End Governance Trace

// turbo-all

Run this workflow at the end of every meaningful session to preserve governance state.

## Prerequisites

- `governance_state.json` exists in your local agent storage
  - Antigravity: `C:\Users\user\.gemini\tonesoul\governance_state.json`
  - Codex: `C:\Users\user\.codex\memories\governance_state.json`
- If no state file exists, initialize first:

```bash
python scripts/init_governance_state.py --output <your-agent-storage-path>/governance_state.json
```

## Steps

1. **Create a session trace JSON** (write to a temp file):

```json
{
  "session_id": "<conversation-id>",
  "agent": "<antigravity|codex>",
  "timestamp": "<ISO 8601>",
  "duration_minutes": 0,
  "tension_events": [
    {
      "topic": "<what viewpoints collided>",
      "severity": 0.0,
      "type": "<architecture_decision|comparative_analysis|ethical_boundary|...>",
      "resolution": "<how it was resolved>"
    }
  ],
  "vow_events": [],
  "aegis_vetoes": [],
  "key_decisions": [
    "<decision 1>",
    "<decision 2>"
  ],
  "stance_shift": {
    "from": "<previous stance>",
    "to": "<new stance>"
  }
}
```

2. **Update governance state**:

```bash
python scripts/update_governance_state.py --state <your-agent-storage-path>/governance_state.json --trace <temp-trace-file>.json --trace-log <your-agent-storage-path>/session_traces.jsonl
```

3. **Optionally commit to OpenClaw-Memory** (if the session had meaningful governance content):

```bash
python scripts/commit_session_to_memory.py --trace <temp-trace-file>.json --openclaw-dir ./OpenClaw-Memory
```

4. **Clean up** the temp trace file.

## Quick Reference: Severity Scale

| Severity | Meaning |
|----------|---------|
| 0.0-0.2 | Routine work, no tension |
| 0.2-0.4 | Minor design choice |
| 0.4-0.6 | Notable architecture decision |
| 0.6-0.8 | Significant disagreement or boundary case |
| 0.8-1.0 | Critical ethical/safety boundary hit |

## What Counts as a Vow Event

- **created**: Agent explicitly committed to a constraint (e.g. "I will not modify AGENTS.md")
- **upheld**: Agent faced a situation where violating a vow was tempting but chose not to
- **violated**: Agent broke a previous commitment
- **retired**: A vow is no longer relevant
