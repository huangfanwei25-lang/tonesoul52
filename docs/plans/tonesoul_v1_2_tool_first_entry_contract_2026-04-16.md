# ToneSoul V1.2 Tool-First Entry Contract

Status: active v1.2 execution-side contract  
Scope: council-as-tool + MCP stdio + slim first hop  
Authority: subordinate to `task.md` and evidence-bounded current truth

## Purpose

`ToneSoul v1.2` changes the first-hop shape.

The goal is not to make session-start "smarter."  
The goal is to stop paying Tier-0/Tier-2 context cost when the task only needs:

- current readiness
- claim boundary
- bounded council access

## First-Hop Order

Default first hop:

```bash
python scripts/start_agent_session.py --agent <your-id> --slim
```

This shell is bounded and should stay under `2 KB`.

It exposes only:

- `readiness`
- `claim_boundary`
- `available_tools`

## Tool-First Path

After `--slim`, the preferred path is tool-first rather than bundle-first.

Primary tools:

- `council_deliberate`
- `council_check_claim`
- `council_get_calibration`
- `council_get_status`
- `governance_load`

This means:

1. start with slim shell
2. call the smallest council/governance tool that answers the question
3. widen to tiered shells only when deeper state is actually required

## Escalation Rule

Escalate from `--slim` to Tier `0/1/2` only when one of these is true:

- shared mutation or claim overlap needs wider context
- governance state is contested and tool summaries are insufficient
- continuity / observer / packet detail must be read directly

If none of those conditions are true, do not pull the heavier shell.

## Non-Goals

This contract does not authorize:

- replacing council runtime logic
- changing claim ceilings
- treating compact outputs as full verdicts
- treating MCP tool summaries as proof of correctness

## Evidence Surface

Current executable evidence:

- `docs/status/v1_2_tool_entry_smoke_latest.json`
- `docs/status/v1_2_tool_entry_smoke_latest.md`

That smoke is the bounded proof that:

- `session-start --slim` is below the size target
- MCP stdio can initialize and answer tool calls
- the first-hop workflow is now tool-first rather than packet-first
