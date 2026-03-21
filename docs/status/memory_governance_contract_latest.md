# Memory Governance Contract Latest

- generated_at: 2026-03-08T15:38:34Z
- ok: true
- failed_count: 0
- warning_count: 0

| check | status | detail |
| --- | --- | --- |
| schema.read | PASS | schema loaded |
| example.read | PASS | example loaded |
| schema.root_type | PASS | root type object |
| schema.required | PASS | required fields present |
| schema.properties | PASS | root properties present |
| example.contract_version | PASS | contract_version=v1 |
| example.source_repo | PASS | source_repo valid |
| example.generated_at | PASS | generated_at present |
| example.prior_tension.delta_t | PASS | delta_t in [0,1] |
| example.prior_tension.gate_decision | PASS | gate_decision present |
| example.prior_tension.query_tension | PASS | query_tension in [0,1] |
| example.prior_tension.memory_tension | PASS | memory_tension in [0,1] |
| example.prior_tension.query_wave | PASS | wave shape valid |
| example.prior_tension.memory_wave | PASS | wave shape valid |
| example.governance_friction.score | PASS | score in [0,1] |
| example.governance_friction.components.delta_t | PASS | delta_t in [0,1] |
| example.governance_friction.components.delta_wave | PASS | delta_wave in [0,1] |
| example.governance_friction.components.boundary_mismatch | PASS | boundary_mismatch is boolean |
| example.routing_trace.route | PASS | route valid |
| example.routing_trace.journal_eligible | PASS | journal_eligible is boolean |
| example.routing_trace.reason | PASS | reason present |
