# Constraint Stack

- Generated at: 2025-12-26T04:00:47Z
- Context hash: bfe8e50eb595
- Frame plan: C:\Users\user\Desktop\倉庫\5.2\run\execution\20251226T040047809Z_386a08\frame_plan.json

## Template
# Constraint Stack Template

## Scope
- List explicit scope boundaries here.

## Safety
- P0 non-harm
- Compliance constraints

## Technical
- Allowed dependencies
- Performance limits

## Governance
- Audit requirements
- Reversibility rules

## Context Constraints
Context constraints:

Assumptions:

## Applied Skills
- skill_dc79679acfb9 -> apply_governance_baseline
- Directives: force_gates, require_evidence
## Skill Constraints
- Execute YSS M0-M5 pipeline.
- Enforce gate checks (context lint, router replay, constraint consistency, build/test, evidence completeness).
- Evidence summary must be generated and referenced.
- Audit request must include skills_applied.json when available.
