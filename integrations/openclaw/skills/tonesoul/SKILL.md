---
name: ToneSoul Governance
version: 1.0.0
description: OpenClaw skills for ToneSoul governance and responsibility chain auditing.
author: Fan1234-1
---

# ToneSoul OpenClaw Skills

## Tools

- `benevolence_audit`
  - Entry: `integrations/openclaw/skills/tonesoul/benevolence.py::run`
  - Purpose: Execute CPT benevolence audit on proposed action text.
  - Required input: `proposed_action`
  - Optional input: `context_fragments`, `action_basis`, `current_layer`, `genesis_id`, `semantic_tension`

- `council_deliberate`
  - Entry: `integrations/openclaw/skills/tonesoul/council.py::run`
  - Purpose: Run ToneSoul multi-perspective deliberation and return structured verdict.
  - Required input: `draft_output`
  - Optional input: `context`, `user_intent`

## Registry

- Registration module: `integrations/openclaw/skills/tonesoul/registry.py`
- Public APIs:
  - `list_skills()`
  - `invoke_skill(name, payload)`

## Notes

- `GatewaySession` in `tonesoul/gateway/session.py` is already integrated with Genesis responsibility tier.
- Skill outputs are JSON-serializable dictionaries for direct gateway transport.
