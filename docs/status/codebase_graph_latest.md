# ToneSoul Codebase Graph Analysis

Generated: 2026-04-17T18:42:48Z
Package: `tonesoul`

## Summary

| Metric | Value |
| --- | ---: |
| Modules | 254 |
| Lines | 77,526 |
| Classes | 496 |
| Functions | 2,653 |
| Import edges | 453 |
| Circular deps | 0 |
| Layer violations | 40 |
| Orphan modules | 0 |
| Community drifts | 20 |

## God Nodes (Top 20 by coupling)

Modules with the highest total degree (in + out). High coupling = high change risk.

| # | Module | Layer | In | Out | Total | Lines | Funcs |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `unified_pipeline` | pipeline | 0 | 34 | **34** | 3,627 | 78 |
| 2 | `ystm.schema` | domain | 27 | 0 | **27** | 160 | 5 |
| 3 | `yss_pipeline` | pipeline | 1 | 25 | **26** | 1,091 | 29 |
| 4 | `runtime_adapter` | pipeline | 5 | 17 | **22** | 2,538 | 54 |
| 5 | `council.types` | governance | 21 | 0 | **21** | 159 | 2 |
| 6 | `council.runtime` | governance | 4 | 14 | **18** | 771 | 19 |
| 7 | `memory.soul_db` | memory | 16 | 1 | **17** | 1,175 | 64 |
| 8 | `autonomous_cycle` | orchestration | 1 | 14 | **15** | 362 | 12 |
| 9 | `council.perspective_factory` | governance | 3 | 11 | **14** | 887 | 32 |
| 10 | `tonebridge` | surface | 1 | 11 | **12** | 119 | 0 |
| 11 | `yss_gates` | governance | 3 | 9 | **12** | 940 | 20 |
| 12 | `ystm.demo` | domain | 4 | 8 | **12** | 400 | 7 |
| 13 | `council.pre_output_council` | governance | 2 | 9 | **11** | 149 | 4 |
| 14 | `governance.kernel` | governance | 4 | 7 | **11** | 603 | 20 |
| 15 | `council.base` | governance | 9 | 1 | **10** | 20 | 2 |
| 16 | `dream_engine` | evolution | 2 | 8 | **10** | 996 | 33 |
| 17 | `memory` | memory | 0 | 10 | **10** | 69 | 0 |
| 18 | `schemas` | shared | 9 | 0 | **9** | 797 | 39 |
| 19 | `ystm.acceptance` | domain | 1 | 8 | **9** | 146 | 7 |
| 20 | `council` | governance | 2 | 6 | **8** | 53 | 0 |

## Layer Boundary Violations

Imports that cross layer boundaries in disallowed directions.

| Source | Source Layer | → | Target | Target Layer |
| --- | --- | --- | --- | --- |
| `tonesoul` | shared | → | `unified_controller` | pipeline |
| `audit_interface` | observability | → | `ystm.schema` | domain |
| `autonomous_cycle` | orchestration | → | `perception.stimulus` | perception |
| `autonomous_cycle` | orchestration | → | `perception.web_ingest` | perception |
| `autonomous_schedule` | orchestration | → | `perception.source_registry` | perception |
| `constraint_stack` | governance | → | `action_set` | pipeline |
| `constraint_stack` | governance | → | `mercy_objective` | evolution |
| `constraint_stack` | governance | → | `ystm.schema` | domain |
| `council.runtime` | governance | → | `benevolence` | evolution |
| `evidence_collector` | observability | → | `ystm.schema` | domain |
| `governance` | governance | → | `benevolence` | evolution |
| `governance.kernel` | governance | → | `resistance` | evolution |
| `intent_verification` | governance | → | `ystm.schema` | domain |
| `mcp_server` | infrastructure | → | `council.compact` | governance |
| `mcp_server` | infrastructure | → | `council.calibration` | governance |
| `mcp_server` | infrastructure | → | `council.runtime` | governance |
| `mcp_server` | infrastructure | → | `runtime_adapter` | pipeline |
| `memory.boot` | memory | → | `runtime_adapter` | pipeline |
| `memory_manager` | memory | → | `ystm.schema` | domain |
| `mercy_objective` | evolution | → | `ystm.schema` | domain |
| `observer_window` | observability | → | `consumer_contract` | governance |
| `observer_window` | observability | → | `hot_memory` | memory |
| `openclaw_auditor` | observability | → | `benevolence` | evolution |
| `persona_dimension` | evolution | → | `ystm.schema` | domain |
| `reflection` | evolution | → | `ystm.schema` | domain |

... and 15 more

## Subpackage Stats

| Subpackage | Layer | Files | Lines | Classes | Functions |
| --- | --- | ---: | ---: | ---: | ---: |
| `(root)` | — | 97 | 39,276 | 192 | 1180 |
| `backends` | infrastructure | 2 | 899 | 2 | 72 |
| `cli` | surface | 1 | 1 | 0 | 0 |
| `corpus` | evolution | 4 | 859 | 8 | 37 |
| `council` | governance | 30 | 7,111 | 46 | 261 |
| `deliberation` | governance | 7 | 1,888 | 18 | 86 |
| `evolution` | evolution | 4 | 1,128 | 5 | 46 |
| `gates` | governance | 2 | 400 | 6 | 13 |
| `gateway` | infrastructure | 3 | 189 | 4 | 16 |
| `governance` | governance | 5 | 1,586 | 12 | 42 |
| `inter_soul` | surface | 5 | 472 | 9 | 40 |
| `llm` | infrastructure | 5 | 1,375 | 7 | 73 |
| `loop` | orchestration | 4 | 622 | 16 | 23 |
| `market` | domain | 4 | 1,324 | 16 | 35 |
| `memory` | memory | 25 | 8,110 | 39 | 327 |
| `observability` | observability | 5 | 764 | 7 | 35 |
| `perception` | perception | 4 | 1,018 | 5 | 30 |
| `pipeline` | pipeline | 1 | 11 | 0 | 0 |
| `scribe` | domain | 4 | 1,801 | 7 | 61 |
| `semantic` | semantic | 3 | 184 | 3 | 18 |
| `shared` | shared | 3 | 249 | 6 | 7 |
| `tech_trace` | observability | 4 | 578 | 0 | 29 |
| `tonebridge` | surface | 12 | 3,505 | 39 | 130 |
| `ystm` | domain | 13 | 2,166 | 21 | 60 |
| `yuhun` | semantic | 7 | 2,010 | 28 | 32 |

## Cross-Package Coupling (top edges)

| From | To | Edges |
| --- | --- | ---: |
| `(root)` | `ystm` | 24 |
| `(root)` | `memory` | 17 |
| `(root)` | `governance` | 9 |
| `(root)` | `council` | 8 |
| `council` | `(root)` | 8 |
| `governance` | `(root)` | 8 |
| `memory` | `(root)` | 4 |
| `(root)` | `llm` | 3 |
| `(root)` | `perception` | 3 |
| `(root)` | `scribe` | 3 |
| `(root)` | `backends` | 3 |
| `(root)` | `tech_trace` | 3 |
| `pipeline` | `(root)` | 3 |
| `(root)` | `gateway` | 2 |
| `(root)` | `yuhun` | 2 |
| `(root)` | `deliberation` | 2 |
| `council` | `semantic` | 2 |
| `governance` | `llm` | 2 |
| `llm` | `(root)` | 2 |
| `loop` | `shared` | 2 |
| `yuhun` | `(root)` | 2 |
| `(root)` | `gates` | 1 |
| `(root)` | `tonebridge` | 1 |
| `backends` | `(root)` | 1 |
| `corpus` | `deliberation` | 1 |

## Community Drifts

Modules whose import pattern suggests they belong to a different subpackage than their directory.

| Module | Directory | Community |
| --- | --- | --- |
| `backends.file_store` | backends | (root) |
| `backends.redis_store` | backends | (root) |
| `council.calibration` | council | (root) |
| `escape_valve` | (root) | council |
| `gates` | gates | (root) |
| `gates.compute` | gates | (root) |
| `governance` | governance | (root) |
| `governance.kernel` | governance | (root) |
| `governance.reflex` | governance | (root) |
| `governance.reflex_config` | governance | (root) |
| `governance.retro` | governance | memory |
| `memory.hippocampus` | memory | (root) |
| `memory.semantic_graph` | memory | (root) |
| `memory.visual_chain` | memory | (root) |
| `perception.web_ingest` | perception | (root) |
| `pipeline` | pipeline | (root) |
| `safe_parse` | (root) | council |
| `tech_trace.validate` | tech_trace | (root) |
| `ystm.schema` | ystm | (root) |
| `ystm_demo` | (root) | ystm |
