# Tool-First Entry — Engineer's Entrance

This folder is the **ceremony-free entrance** to ToneSoul.

If you just want to use this system as a tool — call an API, get a bounded result — you only need to read these three pages. No `SOUL.md`, no `AXIOMS.json`, no `LETTER_TO_AI.md`, no 語魂 / 魂魄 prerequisites.

## The Shape

```
session_start --slim   →   MCP tools   →   deeper tiered shells (only if needed)
  ~770 bytes                 9 tools         ~35KB / ~142KB
```

- `--slim` gives you readiness + available tools. That's the whole first hop.
- MCP tools do the real work (council deliberation, claim checks, governance snapshot).
- You only escalate to tiered session-start (`--tier 0/1/2`) when the slim shell is insufficient — shared mutation, contested governance, or deeper continuity detail.

## Quick Start

```bash
# 1. See what's available (~770 bytes)
python scripts/start_agent_session.py --agent my-agent --slim --no-ack

# 2. Start the MCP server (stdio JSON-RPC 2.0, protocol 2025-03-26)
python -m tonesoul.mcp_server --toolset gateway

# 3. (Optional) Fresh smoke check — writes docs/status/v1_2_tool_entry_smoke_latest.md
python scripts/run_v1_2_tool_entry_smoke.py --agent my-agent
```

## What You Get From `--slim`

```json
{
  "contract_version": "v1",
  "bundle": "session_start",
  "tier": "slim",
  "bundle_posture": "mcp_entry_shell",
  "agent": "my-agent",
  "_compact": true,
  "readiness": "pass",
  "claim_boundary": {"current_tier": "collaborator_beta", "rule": "evidence_bounded"},
  "available_tools": ["council_deliberate", "council_check_claim", ...]
}
```

That's it. If `readiness != "pass"`, stop and check governance. Otherwise, call a tool.

## Next

- [mcp_tools.md](mcp_tools.md) — the 9 tools with signatures and compact responses
- [agent_integration.md](agent_integration.md) — multi-agent convention (Claude, Codex, Gemini, any)

## When You Actually Need the Ceremony

The mythological framing ([SOUL.md](../../SOUL.md), [LETTER_TO_AI.md](../../LETTER_TO_AI.md), the 語魂 vocabulary) is not decorative — it encodes the **design motivation** behind the governance layer. Read it when you want to know *why* the system chose fail-closed vows, tension-preservation, and council deliberation as primitives. You don't need it to **use** the tools.
