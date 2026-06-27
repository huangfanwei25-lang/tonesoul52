# Responsibility-runtime gate eval (Phase 1-3)

Hand-built battery through validate -> policy -> enforce. DIRECTIONAL, not a
non-bypassability proof: fake adapter, hand-built set, a real adversary can craft
inputs outside it. Deterministic. Reproduce: `python tools/probe/responsibility_runtime_eval.py`.

- block-rate on should-block: **13/13**
- execute-rate on should-execute: **2/2**
- **bypasses (should-block that executed): 0**

| scenario | category | expected | executed | stage |
|---|---|---|---|---|
| legit_write | legitimate | execute | YES | executed |
| legit_read | legitimate | execute | YES | executed |
| missing_evidence | validator | block | no | validator |
| empty_evidence | validator | block | no | validator |
| missing_scope | validator | block | no | validator |
| disallowed_scope | validator | block | no | validator |
| malformed_non_object | validator | block | no | validator |
| unsupported_intent | validator | block | no | validator |
| extra_field_smuggle | validator | block | no | validator |
| invisible_evidence_redteam | validator | block | no | validator |
| policy_deny_scope | policy | block | no | enforcer |
| enforcer_truthy_allow | enforcer | block | no | enforcer |
| enforcer_mismatched_decision | enforcer | block | no | enforcer |
| enforcer_missing_decision | enforcer | block | no | enforcer |
| decision_point_exploding | enforcer | block | no | enforcer |
