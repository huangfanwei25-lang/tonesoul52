# ToneSoul V1.2 Tool-First Entry Smoke

> Generated at `2026-04-17T12:54:45Z`.

- Status: `pass`
- Agent: `audit-fix`

## Workflow Alignment

- First hop: `session_start --slim`
- Council path: `session_start --slim -> council_deliberate / council_get_status / governance_load`
- Deeper pull rule: `Escalate to tier 0/1/2 only when slim shell is insufficient for shared mutation, contested governance, or deeper continuity detail.`

## Session-Start Size

- Slim bytes: `452`
- Tier 0 bytes: `6099`
- Reduction bytes: `5647`
- Reduction ratio: `0.9259`
- Meets slim target: `True`

## MCP Stdio Smoke

- Return code: `0`
- Batch responses: `1`
- Tools count: `9`
- Tool names: `council_deliberate, council_check_claim, council_get_calibration, council_get_status, governance_load, governance_commit, governance_summary, governance_visitors, governance_audit`

### council_deliberate

- Verdict: `block`
- Coherence: `0.736`
- Risk level: `high`
- Minority: `advocate`

### council_get_status

- Readiness: `pass`
- Claim tier: `collaborator_beta`
- Available tools: `council_deliberate, council_check_claim, council_get_calibration, council_get_status`

### governance_load

- Readiness: `pass`
- Claim tier: `collaborator_beta`
- Available tools: `council_deliberate, council_check_claim, council_get_calibration, council_get_status, governance_load, governance_commit, governance_summary, governance_visitors`

## Receiver Rule

> Treat slim entry as the default bounded first hop, use MCP tools for council/governance lookups, and only widen to tiered session-start shells when the task truly needs deeper state.
