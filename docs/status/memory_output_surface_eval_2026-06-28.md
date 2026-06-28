# Memory Output Surface Eval

Deterministic eval for trace-backed memory-write acknowledgements. The surface may
only render a memory-write claim when the enforcer result and trace both show an
executed `memory.write.propose` decision.

- scenarios: **4**
- failures: **0**

| scenario | expected status | actual status | expected claim check | actual claim check | ok |
|---|---|---|---|---|---|
| executed_write | memory_write_acknowledged | memory_write_acknowledged | backed_by_trace | backed_by_trace | yes |
| denied_write | memory_write_denied | memory_write_denied | no_memory_claim | no_memory_claim | yes |
| read_intent | not_memory_write | not_memory_write | no_memory_claim | no_memory_claim | yes |
| tampered_executed_flag | memory_write_denied | memory_write_denied | no_memory_claim | no_memory_claim | yes |
