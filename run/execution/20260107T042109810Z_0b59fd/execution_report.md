# Execution Report (M3)

- Generated at: 2026-01-07T04:21:09Z
- Context hash: 4a4577cd6c42
- Frame plan: 00a570c736a1

## Summary
This report records execution metadata and pointers only.

## Inputs
- Task: Test restructure
- Objective: Verify system works

## Selected Frames
- analysis (score=1) roles=['Definer', 'Integrator'] gov_roles=['steward', 'guardian']
- bridge (score=1) roles=['Bridge', 'Executor'] gov_roles=['steward']

## Rejected Frames
- risk (score=0, reason=score=0)
- audit (score=0, reason=score=0)

## Role Summary
- Operational roles: ['Bridge', 'Definer', 'Executor', 'Integrator']
- Governance roles: ['guardian', 'steward']
- Max governance level: 3

## Council Summary
- Decision: proceed (mode=normal)
- Weighted score: 1.0 | Dissent ratio: 0.0
- Risk roles: [] | Audit roles: []
Votes:
- guardian weight=3.0 stance=approve score=1.0
- steward weight=2.0 stance=approve score=1.0

## Constraint Stack Snapshot
```
# Constraint Stack

- Generated at: 2026-01-07T04:21:09Z
- Context hash: 4a4577cd6c42
- Frame plan: C:\Users\user\Desktop\倉庫\run\execution\20260107T042109810Z_0b59fd\frame_plan.json

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

## Action Set
- Decision mode: normal
- Allowed actions:
  - verify
  - cite
  - inquire
- Strict mode policy:
  - cautious: verify, inquire
  - lockdown: inquire
- Rationale: Minimal action set to reduce risk under strict modes.

## Mercy Objective
- Decision mode: normal
- Score: 0.225
- Weights:
  - benefit: 0.300
  - harm: -0.350
  - fairness: 0.150
  - traceability: 0.100
  - reversibility: 0.100
- Signals:
  - benefit: 0.50
  - harm: 0.40
  - fairness: 0.50
  - traceability: 0.80
  - reversibility: 0.60
- Rationale: Weighted objective balances benefit with harm reduction and governance traceability.
```

## Outputs
- Placeholder: no generation performed in M3 skeleton.

## Audit Hooks
- Provide pointers to YSTM nodes/audit logs when available.

## Gate Results

- Generated at: 2026-01-07T04:21:09Z
- Overall: PASS

- p0_gate: PASS | -

## P0 Non-Harm Gate
- Decision: pass | Passed: True
- Issues: -
