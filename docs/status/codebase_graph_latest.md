# ToneSoul Codebase Graph Analysis

Generated: 2026-04-18T03:38:31Z
Package: `tonesoul`

## Summary

| Metric | Value |
| --- | ---: |
| Modules | 254 |
| Lines | 77,601 |
| Classes | 496 |
| Functions | 2,653 |
| Import edges | 453 |
| Circular deps | 0 |
| Layer violations | 23 |
| Orphan modules | 0 |
| Community drifts | 20 |
| Self-declared layer | 15 / 254 (5.9%) |
| Purpose declared | 15 / 254 (5.9%) |

## God Nodes (Top 20 by coupling)

Modules with the highest total degree (in + out). High coupling = high change risk.

| # | Module | Layer | Src | In | Out | Total | Purpose |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | `unified_pipeline` | pipeline | self_declared | 0 | 34 | **34** | Top-level runtime pipeline that wires perception, council, and output surfaces. |
| 2 | `ystm.schema` | shared | override | 27 | 0 | **27** | — |
| 3 | `yss_pipeline` | pipeline | self_declared | 1 | 25 | **26** | Compose YSS gates, action set, and audit into one semantic-field pipeline pass. |
| 4 | `runtime_adapter` | pipeline | self_declared | 5 | 17 | **22** | Load/commit governance state across session boundaries; the model-agnostic runtime spine. |
| 5 | `council.types` | shared | self_declared | 21 | 0 | **21** | Shared type primitives (PerspectiveType, VoteDecision, verdicts) for the council subsystem. |
| 6 | `council.runtime` | governance | self_declared | 4 | 14 | **18** | Run the multi-perspective council, return verdict + coherence + minority opinion. |
| 7 | `memory.soul_db` | memory | self_declared | 16 | 1 | **17** | SQLite-backed memory store with decay, layered retrieval, and source attribution. |
| 8 | `autonomous_cycle` | orchestration | self_declared | 1 | 14 | **15** | Drive the autonomous wake/sense/dream loop without a human trigger. |
| 9 | `council.perspective_factory` | governance | self_declared | 3 | 11 | **14** | Factory for pluggable council perspectives (rules / LLM / tool-verified). |
| 10 | `tonebridge` | surface | subpackage | 1 | 11 | **12** | — |
| 11 | `yss_gates` | governance | self_declared | 3 | 9 | **12** | Compose the YSS gate stack (DCS, POAV, frame router, seed, acceptance) into one policy pass. |
| 12 | `ystm.demo` | surface | self_declared | 4 | 8 | **12** | End-to-end YSTM demo: ingest segments, build terrain, render HTML/PNG/SVG surfaces. |
| 13 | `council.pre_output_council` | governance | self_declared | 2 | 9 | **11** | Convene the pre-output council: run perspectives, compute coherence, emit verdict and transcript. |
| 14 | `governance.kernel` | governance | self_declared | 4 | 7 | **11** | Governance kernel: decides how the pipeline behaves (routing, council convening, friction). |
| 15 | `council.base` | shared | self_declared | 9 | 1 | **10** | Abstract IPerspective contract implemented by every council perspective. |
| 16 | `dream_engine` | evolution | self_declared | 2 | 8 | **10** | Offline dream cycle: crystallize memory and update subjectivity layers between waking sessions. |
| 17 | `memory` | memory | subpackage | 0 | 10 | **10** | — |
| 18 | `schemas` | shared | self_declared | 9 | 0 | **9** | Pydantic data contracts shared across council, LLM, and governance layers. |
| 19 | `ystm.acceptance` | domain | subpackage | 1 | 8 | **9** | — |
| 20 | `council` | governance | subpackage | 2 | 6 | **8** | — |

## Layer Boundary Violations

Imports that cross layer boundaries in disallowed directions.

| Source | Source Layer | → | Target | Target Layer |
| --- | --- | --- | --- | --- |
| `tonesoul` | shared | → | `unified_controller` | pipeline |
| `constraint_stack` | governance | → | `action_set` | pipeline |
| `constraint_stack` | governance | → | `mercy_objective` | evolution |
| `council.runtime` | governance | → | `benevolence` | evolution |
| `governance` | governance | → | `benevolence` | evolution |
| `governance.kernel` | governance | → | `resistance` | evolution |
| `mcp_server` | infrastructure | → | `council.compact` | governance |
| `mcp_server` | infrastructure | → | `council.calibration` | governance |
| `mcp_server` | infrastructure | → | `council.runtime` | governance |
| `mcp_server` | infrastructure | → | `runtime_adapter` | pipeline |
| `memory.boot` | memory | → | `runtime_adapter` | pipeline |
| `risk_calculator` | governance | → | `working_style` | evolution |
| `tension_engine` | governance | → | `nonlinear_predictor` | domain |
| `tension_engine` | governance | → | `resistance` | evolution |
| `tension_engine` | governance | → | `variance_compressor` | domain |
| `unified_pipeline` | pipeline | → | `tonebridge` | surface |
| `yss_gates` | governance | → | `dcs` | domain |
| `yss_gates` | governance | → | `frame_router` | pipeline |
| `yss_gates` | governance | → | `ystm.acceptance` | domain |
| `yss_pipeline` | pipeline | → | `ystm.demo` | surface |
| `ystm` | domain | → | `ystm.demo` | surface |
| `ystm.acceptance` | domain | → | `ystm.demo` | surface |
| `ystm_demo` | domain | → | `ystm.demo` | surface |

## Subpackage Stats

| Subpackage | Layer | Files | Lines | Classes | Functions |
| --- | --- | ---: | ---: | ---: | ---: |
| `(root)` | — | 97 | 39,309 | 192 | 1180 |
| `backends` | infrastructure | 2 | 899 | 2 | 72 |
| `cli` | surface | 1 | 1 | 0 | 0 |
| `corpus` | evolution | 4 | 859 | 8 | 37 |
| `council` | governance | 30 | 7,136 | 46 | 261 |
| `deliberation` | governance | 7 | 1,888 | 18 | 86 |
| `evolution` | evolution | 4 | 1,128 | 5 | 46 |
| `gates` | governance | 2 | 400 | 6 | 13 |
| `gateway` | infrastructure | 3 | 189 | 4 | 16 |
| `governance` | governance | 5 | 1,591 | 12 | 42 |
| `inter_soul` | surface | 5 | 472 | 9 | 40 |
| `llm` | infrastructure | 5 | 1,375 | 7 | 73 |
| `loop` | orchestration | 4 | 622 | 16 | 23 |
| `market` | domain | 4 | 1,324 | 16 | 35 |
| `memory` | memory | 25 | 8,115 | 39 | 327 |
| `observability` | observability | 5 | 764 | 7 | 35 |
| `perception` | perception | 4 | 1,018 | 5 | 30 |
| `pipeline` | pipeline | 1 | 11 | 0 | 0 |
| `scribe` | domain | 4 | 1,801 | 7 | 61 |
| `semantic` | semantic | 3 | 184 | 3 | 18 |
| `shared` | shared | 3 | 249 | 6 | 7 |
| `tech_trace` | observability | 4 | 578 | 0 | 29 |
| `tonebridge` | surface | 12 | 3,505 | 39 | 130 |
| `ystm` | domain | 13 | 2,173 | 21 | 60 |
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
