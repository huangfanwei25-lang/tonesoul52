# Execution Report (M3)

- Generated at: 2025-12-26T03:53:20Z
- Context hash: cbbe3d0a96aa
- Frame plan: c388f810bdc3

## Summary
This report records execution metadata and pointers only.

## Inputs
- Task: Build YSTM demo
- Objective: Generate auditable artifacts

## Selected Frames
- analysis (score=1) roles=['Definer', 'Integrator']
- bridge (score=1) roles=['Bridge', 'Executor']

## Constraint Stack Snapshot
```
# Constraint Stack

- Generated at: 2025-12-26T03:53:20Z
- Context hash: cbbe3d0a96aa
- Frame plan: C:\Users\user\Desktop\倉庫\5.2\run\execution\20251226T035320104Z_887d83\frame_plan.json

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
```

## Outputs
- Placeholder: no generation performed in M3 skeleton.

## Audit Hooks
- Provide pointers to YSTM nodes/audit logs when available.

## Gate Results

- Generated at: 2025-12-26T03:53:20Z
- Overall: PASS

- context_lint: PASS | -
- router_replay: PASS | -
- constraint_consistency: PASS | -
- build_test_gate: PASS | -
- evidence_completeness: PASS | -
