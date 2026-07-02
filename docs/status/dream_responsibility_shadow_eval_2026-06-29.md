# Dream Responsibility Shadow Eval

Deterministic baseline for the OBSERVE-ONLY responsibility-gate shadow (PR #219).
It records what the gate WOULD decide for representative dream-collision payloads.
It is NOT enforcement, NOT real dream-cycle traffic, and makes no claim that
memory is gated or non-bypassable. Scenarios include deny cases on purpose.

- scenarios: **5**
- would-allow: **3** · would-deny: **2**
- verdict mismatches (failures): **0**

| scenario | category | expected would_execute | actual | gate reason | issue codes |
|---|---|---|---|---|---|
| grounded_collision | baseline-allow | yes | yes | fake policy allowed validated intent | - |
| lineage_only_evidence | boundary-lineage-counts-as-ref | yes | yes | fake policy allowed validated intent | - |
| title_fallback_claim | boundary-claim-falls-back-to-title | yes | yes | fake policy allowed validated intent | - |
| no_evidence_collision | deny-missing-evidence | no | no | validated intent required | empty_required_field |
| empty_claim_collision | deny-empty-claim | no | no | validated intent required | empty_required_field |
