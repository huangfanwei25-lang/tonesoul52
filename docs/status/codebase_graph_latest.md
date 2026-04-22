# ToneSoul Codebase Graph Analysis

Generated: 2026-04-22T03:07:02Z
Package: `tonesoul`

## Summary

| Metric | Value |
| --- | ---: |
| Modules | 257 |
| Lines | 79,485 |
| Classes | 500 |
| Functions | 2,694 |
| Import edges | 456 |
| Circular deps | 0 |
| Layer violations | 0 |
| Orphan modules | 1 |
| Community drifts | 20 |
| Self-declared layer | 44 / 257 (17.1%) |
| Purpose declared | 44 / 257 (17.1%) |

## God Nodes (Top 20 by coupling)

Modules with the highest total degree (in + out). High coupling = high change risk.

| # | Module | Layer | Src | In | Out | Total | Purpose |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | `unified_pipeline` | pipeline | self_declared | 0 | 34 | **34** | Top-level runtime pipeline that wires perception, council, and output surfaces. |
| 2 | `ystm.schema` | shared | self_declared | 27 | 0 | **27** | YSTM pure-data schema: Node, WhereTime, and stable_hash used across governance, memory, and observability. |
| 3 | `yss_pipeline` | pipeline | self_declared | 1 | 25 | **26** | Compose YSS gates, action set, and audit into one semantic-field pipeline pass. |
| 4 | `runtime_adapter` | pipeline | self_declared | 5 | 17 | **22** | Load/commit governance state across session boundaries; the model-agnostic runtime spine. |
| 5 | `council.types` | shared | self_declared | 21 | 0 | **21** | Shared type primitives (PerspectiveType, VoteDecision, verdicts) for the council subsystem. |
| 6 | `council.runtime` | governance | self_declared | 4 | 14 | **18** | Run the multi-perspective council, return verdict + coherence + minority opinion. |
| 7 | `memory.soul_db` | memory | self_declared | 16 | 1 | **17** | SQLite-backed memory store with decay, layered retrieval, and source attribution. |
| 8 | `autonomous_cycle` | orchestration | self_declared | 1 | 14 | **15** | Drive the autonomous wake/sense/dream loop without a human trigger. |
| 9 | `council.perspective_factory` | governance | self_declared | 3 | 11 | **14** | Factory for pluggable council perspectives (rules / LLM / tool-verified). |
| 10 | `council.pre_output_council` | governance | self_declared | 2 | 10 | **12** | Convene the pre-output council: run perspectives, compute coherence, emit verdict and transcript. |
| 11 | `tonebridge` | domain | self_declared | 1 | 11 | **12** | 5-stage psychological + semantic analysis engine: tone, trajectory, commitment, entropy, self-commit. |
| 12 | `yss_gates` | governance | self_declared | 3 | 9 | **12** | Compose the YSS gate stack (DCS, POAV, frame router, seed, acceptance) into one policy pass. |
| 13 | `ystm.demo` | domain | self_declared | 4 | 8 | **12** | End-to-end YSTM demo: ingest segments, build terrain, render HTML/PNG/SVG outputs. |
| 14 | `governance.kernel` | governance | self_declared | 4 | 7 | **11** | Governance kernel: decides how the pipeline behaves (routing, council convening, friction). |
| 15 | `council.base` | shared | self_declared | 9 | 1 | **10** | Abstract IPerspective contract implemented by every council perspective. |
| 16 | `dream_engine` | evolution | self_declared | 2 | 8 | **10** | Offline dream cycle: crystallize memory and update subjectivity layers between waking sessions. |
| 17 | `memory` | memory | self_declared | 0 | 10 | **10** | Memory package: adversarial reflector, consolidation, vow promotion, and subjectivity analysis. |
| 18 | `council` | governance | self_declared | 3 | 6 | **9** | Council package: deliberation, verdict types, dossier, and swarm framework exports. |
| 19 | `schemas` | shared | self_declared | 9 | 0 | **9** | Pydantic data contracts shared across council, LLM, and governance layers. |
| 20 | `ystm.acceptance` | domain | self_declared | 1 | 8 | **9** | YSTM acceptance test harness: run_acceptance() validates terrain pipeline self-consistency end-to-end. |

## Orphan Modules (zero in-degree)

Nobody imports these. Potential dead code or standalone entry points.

- `unified_controller`

## Subpackage Stats

| Subpackage | Layer | Files | Lines | Classes | Functions |
| --- | --- | ---: | ---: | ---: | ---: |
| `(root)` | — | 97 | 39,337 | 192 | 1180 |
| `backends` | infrastructure | 2 | 899 | 2 | 72 |
| `cli` | surface | 1 | 4 | 0 | 0 |
| `corpus` | evolution | 4 | 862 | 8 | 37 |
| `council` | governance | 33 | 8,908 | 50 | 302 |
| `deliberation` | governance | 7 | 1,893 | 18 | 86 |
| `evolution` | evolution | 4 | 1,131 | 5 | 46 |
| `gates` | governance | 2 | 403 | 6 | 13 |
| `gateway` | infrastructure | 3 | 192 | 4 | 16 |
| `governance` | governance | 5 | 1,599 | 12 | 42 |
| `inter_soul` | surface | 5 | 475 | 9 | 40 |
| `llm` | infrastructure | 5 | 1,378 | 7 | 73 |
| `loop` | orchestration | 4 | 625 | 16 | 23 |
| `market` | domain | 4 | 1,327 | 16 | 35 |
| `memory` | memory | 25 | 8,121 | 39 | 327 |
| `observability` | observability | 5 | 767 | 7 | 35 |
| `perception` | perception | 4 | 1,021 | 5 | 30 |
| `pipeline` | pipeline | 1 | 14 | 0 | 0 |
| `scribe` | domain | 4 | 1,804 | 7 | 61 |
| `semantic` | semantic | 3 | 187 | 3 | 18 |
| `shared` | shared | 3 | 252 | 6 | 7 |
| `tech_trace` | observability | 4 | 581 | 0 | 29 |
| `tonebridge` | domain | 12 | 3,508 | 39 | 130 |
| `ystm` | domain | 13 | 2,184 | 21 | 60 |
| `yuhun` | semantic | 7 | 2,013 | 28 | 32 |

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
