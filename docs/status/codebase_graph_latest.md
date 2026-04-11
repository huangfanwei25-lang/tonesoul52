# ToneSoul Codebase Graph Analysis

Generated: 2026-04-11T19:40:30Z
Package: `tonesoul`

## Summary

| Metric | Value |
| --- | ---: |
| Modules | 237 |
| Lines | 73,218 |
| Classes | 459 |
| Functions | 2,531 |
| Import edges | 414 |
| Circular deps | 0 |
| Layer violations | 0 |
| Orphan modules | 0 |
| Community drifts | 19 |

## God Nodes (Top 20 by coupling)

Modules with the highest total degree (in + out). High coupling = high change risk.

| # | Module | Layer | In | Out | Total | Lines | Funcs |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `unified_pipeline` | uncategorized | 0 | 32 | **32** | 3,597 | 76 |
| 2 | `ystm.schema` | domain | 27 | 0 | **27** | 160 | 5 |
| 3 | `yss_pipeline` | uncategorized | 1 | 25 | **26** | 1,091 | 29 |
| 4 | `council.types` | governance | 19 | 0 | **19** | 159 | 2 |
| 5 | `council.runtime` | governance | 3 | 13 | **16** | 753 | 19 |
| 6 | `runtime_adapter` | uncategorized | 4 | 12 | **16** | 3,421 | 65 |
| 7 | `autonomous_cycle` | uncategorized | 1 | 14 | **15** | 362 | 12 |
| 8 | `memory.soul_db` | memory | 14 | 1 | **15** | 1,175 | 64 |
| 9 | `council.perspective_factory` | governance | 3 | 11 | **14** | 887 | 32 |
| 10 | `tonebridge` | surface | 1 | 11 | **12** | 119 | 0 |
| 11 | `yss_gates` | uncategorized | 3 | 9 | **12** | 940 | 20 |
| 12 | `ystm.demo` | domain | 4 | 8 | **12** | 400 | 7 |
| 13 | `governance.kernel` | governance | 4 | 7 | **11** | 603 | 20 |
| 14 | `council.base` | governance | 9 | 1 | **10** | 20 | 2 |
| 15 | `council.pre_output_council` | governance | 2 | 8 | **10** | 147 | 4 |
| 16 | `dream_engine` | uncategorized | 2 | 8 | **10** | 996 | 33 |
| 17 | `memory` | memory | 0 | 10 | **10** | 69 | 0 |
| 18 | `schemas` | uncategorized | 9 | 0 | **9** | 797 | 39 |
| 19 | `ystm.acceptance` | domain | 1 | 8 | **9** | 146 | 7 |
| 20 | `council` | governance | 2 | 6 | **8** | 53 | 0 |

## Subpackage Stats

| Subpackage | Layer | Files | Lines | Classes | Functions |
| --- | --- | ---: | ---: | ---: | ---: |
| `(root)` | — | 92 | 38,421 | 184 | 1144 |
| `backends` | infrastructure | 2 | 834 | 2 | 67 |
| `cli` | surface | 1 | 1 | 0 | 0 |
| `corpus` | evolution | 4 | 859 | 8 | 37 |
| `council` | governance | 27 | 6,213 | 46 | 227 |
| `deliberation` | governance | 7 | 1,888 | 18 | 86 |
| `evolution` | evolution | 4 | 1,128 | 5 | 46 |
| `gates` | governance | 2 | 398 | 6 | 13 |
| `gateway` | infrastructure | 3 | 189 | 4 | 16 |
| `governance` | governance | 5 | 1,565 | 12 | 42 |
| `inter_soul` | surface | 5 | 472 | 9 | 40 |
| `llm` | infrastructure | 5 | 1,375 | 7 | 73 |
| `loop` | orchestration | 4 | 622 | 16 | 23 |
| `market` | domain | 4 | 1,324 | 16 | 35 |
| `memory` | memory | 23 | 7,653 | 38 | 312 |
| `observability` | observability | 5 | 764 | 7 | 35 |
| `perception` | perception | 4 | 1,018 | 5 | 30 |
| `pipeline` | pipeline | 1 | 11 | 0 | 0 |
| `scribe` | domain | 4 | 1,801 | 7 | 61 |
| `semantic` | semantic | 3 | 184 | 3 | 18 |
| `shared` | shared | 3 | 249 | 6 | 7 |
| `tech_trace` | observability | 4 | 578 | 0 | 29 |
| `tonebridge` | surface | 12 | 3,505 | 39 | 130 |
| `ystm` | domain | 13 | 2,166 | 21 | 60 |

## Cross-Package Coupling (top edges)

| From | To | Edges |
| --- | --- | ---: |
| `(root)` | `ystm` | 24 |
| `(root)` | `memory` | 16 |
| `(root)` | `governance` | 9 |
| `governance` | `(root)` | 8 |
| `(root)` | `council` | 5 |
| `council` | `(root)` | 5 |
| `memory` | `(root)` | 4 |
| `(root)` | `llm` | 3 |
| `(root)` | `perception` | 3 |
| `(root)` | `scribe` | 3 |
| `(root)` | `backends` | 3 |
| `(root)` | `tech_trace` | 3 |
| `pipeline` | `(root)` | 3 |
| `(root)` | `gateway` | 2 |
| `(root)` | `deliberation` | 2 |
| `council` | `semantic` | 2 |
| `governance` | `llm` | 2 |
| `llm` | `(root)` | 2 |
| `loop` | `shared` | 2 |
| `(root)` | `gates` | 1 |
| `(root)` | `tonebridge` | 1 |
| `backends` | `(root)` | 1 |
| `corpus` | `deliberation` | 1 |
| `council` | `llm` | 1 |
| `council` | `memory` | 1 |

## Community Drifts

Modules whose import pattern suggests they belong to a different subpackage than their directory.

| Module | Directory | Community |
| --- | --- | --- |
| `backends.file_store` | backends | (root) |
| `backends.redis_store` | backends | (root) |
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
