# MCP Tools Reference

ToneSoul exposes a stdio JSON-RPC 2.0 MCP server at `python -m tonesoul.mcp_server`. Protocol: `2025-03-26`. Server info: `{"name": "tonesoul-mcp", "version": "1.2.0-alpha"}`.

Two toolsets:

- `--toolset core` — 4 council tools only
- `--toolset gateway` — 9 tools (core + 5 governance gateway)

All responses are **compact by construction** — bounded field sets, no verbose transcripts leaking into the tool output. Every response has `_compact: true` and a `kind` field.

## Core (Council) Tools

### `council_deliberate`

Run council deliberation on a draft output.

| Input | Type | Required |
|---|---|---|
| `draft_output` | string | yes |
| `user_intent` | string | no |
| `mode` | `"rules" \| "hybrid" \| "full_llm"` | no (default `rules`) |

Compact response keys: `verdict`, `coherence`, `minority`, `risk_level`, `matched_skill_ids`, optional `responsibility_tier`, `collapse_warning`, `uncertainty_band`.

### `council_check_claim`

Check whether a public claim stays inside the current collaborator-beta claim boundary.

| Input | Type | Required |
|---|---|---|
| `claim_text` | string | yes |

Compact response: `ceiling`, `evidence_level`, `blocked_reasons[]` (up to 3).

### `council_get_calibration`

Return the compact v0a council calibration realism baseline.

No arguments. Returns `status`, `ceiling_effect`, and four metric buckets (`agreement_stability`, `internal_self_consistency`, `suppression_recovery_rate`, `persistence_coverage`).

### `council_get_status`

Governance status for agent entry.

| Input | Type | Required |
|---|---|---|
| `agent_id` | string | no |

Compact response: `readiness`, `claim_tier`, `claim_rule`, `available_tools[]`.

## Gateway Tools

### `governance_load`

Load current governance posture. Same shape as `council_get_status` but with the full gateway tool list.

### `governance_commit`

Commit a bounded session trace.

| Input | Type |
|---|---|
| `agent` | string |
| `topics` | string[] |
| `tension_events` | object[] |
| `vow_events` | object[] |
| `key_decisions` | string[] |
| `duration_minutes` | number |

Compact response: `status`, `session_id`, `soul_integral`, `risk_level`.

### `governance_summary`

Clipped human-readable governance summary — returns `line_count`, `headline`, `preview`.

### `governance_visitors`

Recent governance visitors — returns `count`, `agents[]` (top 5).

### `governance_audit`

Aegis integrity audit — returns `integrity`, `chain_valid`, `signature_failures`, `chain_errors`.

## Calling Pattern

```bash
# From any MCP client — this is stock JSON-RPC 2.0 over stdio.
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"council_get_status","arguments":{"agent_id":"me"}}}' \
  | python -m tonesoul.mcp_server --toolset gateway
```

Each `tools/call` response has both:

- `content[0].text` — the compact JSON as a string
- `structuredContent` — the compact JSON as an object

Clients can consume either.

## What The Compact Outputs Intentionally Drop

For council verdicts, we strip: `summary`, `reasoning`, `evidence`, `transcript`, `votes`, `vote_profile`, `divergence_analysis`, `persona_audit`, `benevolence_audit`, `uncertainty_reasons`, and similar token-heavy fields.

If you need any of those, escalate to the tier-2 session-start bundle (`python scripts/start_agent_session.py --agent X`) instead. The MCP tool surface is deliberately bounded.
