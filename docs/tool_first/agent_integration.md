# Multi-Agent Integration

ToneSoul is designed to be used by more than one AI agent at a time. Each agent leaves a tracked footprint in shared governance state; any other agent can see who has been there, what they claimed, and what they committed.

This page describes the minimal convention.

## The Convention

Every agent — human-operated, Claude, Codex, Gemini, or a headless script — follows the same three-step life cycle:

```
session_start  →  work  →  session_end
```

### Session start

```bash
python scripts/start_agent_session.py --agent <agent-id> --slim --no-ack
```

- `--agent` is the identity the system records for you. Pick a stable string (e.g. `claude-opus-4-7`, `codex-gpt-5`, `fanwei-manual`). Other agents will see this in `ts:footprints`, visitors, and traces.
- `--slim` keeps the bundle at ~770 bytes. Use `--tier 0/1/2` only when deeper state is required.
- `--no-ack` skips the observer-cursor acknowledgment step when you don't need the observer window yet.

### Work

Call MCP tools (see [mcp_tools.md](mcp_tools.md)) or the HTTP gateway ([scripts/gateway.py](../../scripts/gateway.py)) as needed. Non-Python agents typically use the gateway:

```bash
python scripts/gateway.py --port 7700 --token YOUR_SECRET
# POST /load, POST /commit, GET /summary, GET /visitors, GET /audit
```

MCP and gateway surfaces read the same underlying governance store, so agents see each other regardless of transport.

### Session end

```bash
python scripts/end_agent_session.py --agent <agent-id> --summary "<what you did>" --path "<what you touched>"
```

Leaves a trace in `ts:traces`. If you did substantive work, leave a compaction first; if you're just pausing, leave a checkpoint.

## Shared State Keys

| Key | Store | Content |
|---|---|---|
| `ts:governance` | Redis / fallback `governance_state.json` | vows, tensions, drift, risk posture |
| `ts:traces` | Redis stream / fallback `session_traces.jsonl` | every session's governance trace |
| `ts:footprints` | Redis | last 100 agent visits |
| `ts:zones` | Redis / fallback `zone_registry.json` | world-map zones |
| `ts:aegis:chain_head` | Redis | hash-chain integrity head |

All keys are read-through with a file-store fallback, so local-only work still participates.

## Checking Who Has Been Here

```bash
python -m tonesoul.diagnose --agent <agent-id>
```

Look for `[Recent Sessions]` and `[World Map]` — each visitor is listed with agent id, timestamp, topics, and decision count.

Or programmatically via MCP:

```json
{"method": "tools/call", "params": {"name": "governance_visitors"}}
```

Returns compact `{count, agents[]}`.

## Agent-Specific Notes

### Claude Code

Follows the full CLAUDE.md session-start protocol (slim → tier 0 → tier 1/2 as needed).

### Codex (OpenAI)

Uses the same convention. Recommended agent-id format: `codex-<model-or-task>`. Codex's footprints appear in `diagnose` output alongside Claude's when both sessions run against the same governance store. No special orchestration — same contract, same tools.

### Non-Python agents (Gemini, custom scripts, etc.)

Use the HTTP gateway. `POST /load` is equivalent to `session_start`, `POST /commit` is equivalent to `session_end`. Token auth is required.

## Why This Matters

Governance state is the only thing that persists across agent boundaries. A fresh Claude / Codex / Gemini instance has no memory of prior conversations, but they can all see:

- what claims other agents are currently holding
- what vows are active
- what tensions are unresolved
- what decisions have been committed

This turns cold-start instances into coherent collaborators, as long as every agent follows the convention.

Skipping the convention is allowed but means working without shared context — you become invisible to the next agent.
