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
