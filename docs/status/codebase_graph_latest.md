# ToneSoul Codebase Graph Analysis

Generated: 2026-07-03T03:53:40Z
Package: `tonesoul`

## Summary

| Metric | Value |
| --- | ---: |
| Modules | 303 |
| Lines | 90,764 |
| Classes | 576 |
| Functions | 3,038 |
| Import edges | 541 |
| Circular deps | 0 |
| Layer violations | 0 |
| Orphan modules | 1 |
| Community drifts | 28 |
| Self-declared layer | 303 / 303 (100.0%) |
| Purpose declared | 301 / 303 (99.3%) |

## God Nodes (Top 20 by coupling)

Modules with the highest total degree (in + out). High coupling = high change risk.

| # | Module | Layer | Src | In | Out | Total | Purpose |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | `unified_pipeline` | pipeline | self_declared | 0 | 35 | **35** | Top-level runtime pipeline that wires perception, council, and output surfaces. |
| 2 | `ystm.schema` | shared | self_declared | 27 | 0 | **27** | YSTM pure-data schema: Node, WhereTime, and stable_hash used across governance, memory, and observability. |
| 3 | `council.types` | shared | self_declared | 24 | 1 | **25** | Shared type primitives (PerspectiveType, VoteDecision, verdicts) for the council subsystem. |
| 4 | `yss_pipeline` | pipeline | self_declared | 0 | 25 | **25** | Compose YSS gates, action set, and audit into one semantic-field pipeline pass. |
| 5 | `runtime_adapter` | pipeline | self_declared | 5 | 19 | **24** | Load/commit governance state across session boundaries; the model-agnostic runtime spine. |
| 6 | `council.runtime` | governance | self_declared | 4 | 15 | **19** | Run the multi-perspective council, return verdict + coherence + minority opinion. |
| 7 | `memory.soul_db` | memory | self_declared | 18 | 1 | **19** | SQLite-backed memory store with decay, layered retrieval, and source attribution. |
| 8 | `council.pre_output_council` | governance | self_declared | 3 | 15 | **18** | Convene the pre-output council: run perspectives, compute coherence, emit verdict and transcript. |
| 9 | `autonomous_cycle` | orchestration | self_declared | 1 | 14 | **15** | Drive the autonomous wake/sense/dream loop without a human trigger. |
| 10 | `council.perspective_factory` | governance | self_declared | 3 | 11 | **14** | Factory for pluggable council perspectives (rules / LLM / tool-verified). |
| 11 | `ystm.demo` | domain | self_declared | 5 | 8 | **13** | End-to-end YSTM demo: ingest segments, build terrain, render HTML/PNG/SVG outputs. |
| 12 | `tonebridge` | domain | self_declared | 1 | 11 | **12** | 5-stage psychological + semantic analysis engine: tone, trajectory, commitment, entropy, self-commit. |
| 13 | `cli.main` | surface | self_declared | 2 | 9 | **11** | Unified CLI entry point: dispatch operator subcommands to the right subsystem. |
| 14 | `dream_engine` | evolution | self_declared | 2 | 9 | **11** | Offline dream cycle: crystallize memory and update subjectivity layers between waking sessions. |
| 15 | `governance.kernel` | governance | self_declared | 4 | 7 | **11** | Governance kernel: decides how the pipeline behaves (routing, council convening, friction). |
| 16 | `memory` | memory | self_declared | 1 | 10 | **11** | Memory package: adversarial reflector, consolidation, vow promotion, subjectivity analysis, AAAK compaction, and freshness tracking. |
| 17 | `yss_gates` | governance | self_declared | 2 | 9 | **11** | Compose the YSS gate stack (DCS, POAV, frame router, seed, acceptance) into one policy pass. |
| 18 | `council.base` | shared | self_declared | 9 | 1 | **10** | Abstract IPerspective contract implemented by every council perspective. |
| 19 | `responsibility_runtime` | governance | self_declared | 1 | 9 | **10** | Responsibility runtime contracts for deterministic intent validation. |
| 20 | `council` | governance | self_declared | 3 | 6 | **9** | Council package: deliberation, verdict types, dossier, and swarm framework exports. |

## Orphan Modules (zero in-degree)

Nobody imports these. Potential dead code or standalone entry points.

- `unified_controller`

## Subpackage Stats

| Subpackage | Layer | Files | Lines | Classes | Functions |
| --- | --- | ---: | ---: | ---: | ---: |
| `(root)` | — | 100 | 41,276 | 200 | 1211 |
| `axioms` | — | 2 | 376 | 3 | 14 |
| `backends` | infrastructure | 2 | 905 | 2 | 72 |
| `cli` | surface | 3 | 344 | 0 | 12 |
| `cognition` | — | 2 | 353 | 4 | 13 |
| `council` | governance | 40 | 11,357 | 67 | 356 |
| `deliberation` | governance | 7 | 1,922 | 18 | 86 |
| `evolution` | evolution | 4 | 1,155 | 5 | 46 |
| `gates` | governance | 2 | 406 | 6 | 13 |
| `gateway` | infrastructure | 3 | 198 | 4 | 16 |
| `governance` | governance | 7 | 1,795 | 12 | 48 |
| `gse` | — | 8 | 1,030 | 7 | 69 |
| `inter_soul` | surface | 5 | 496 | 9 | 40 |
| `llm` | infrastructure | 5 | 1,457 | 7 | 73 |
| `loop` | orchestration | 4 | 634 | 16 | 23 |
| `market` | domain | 4 | 1,342 | 16 | 35 |
| `memory` | memory | 33 | 10,777 | 55 | 426 |
| `observability` | observability | 7 | 1,143 | 10 | 42 |
| `perception` | perception | 4 | 1,030 | 5 | 30 |
| `responsibility_runtime` | — | 10 | 1,554 | 22 | 56 |
| `reviewer` | — | 4 | 524 | 3 | 19 |
| `scribe` | domain | 4 | 1,815 | 7 | 61 |
| `semantic` | semantic | 3 | 193 | 3 | 18 |
| `shared` | shared | 4 | 289 | 7 | 8 |
| `tech_trace` | observability | 4 | 590 | 0 | 29 |
| `tonebridge` | domain | 12 | 3,543 | 39 | 130 |
| `ystm` | domain | 13 | 2,215 | 21 | 60 |
| `yuhun` | semantic | 7 | 2,045 | 28 | 32 |

## Cross-Package Coupling (top edges)

| From | To | Edges |
| --- | --- | ---: |
| `(root)` | `ystm` | 24 |
| `(root)` | `memory` | 18 |
| `(root)` | `governance` | 12 |
| `governance` | `(root)` | 10 |
| `(root)` | `council` | 8 |
| `council` | `(root)` | 8 |
| `council` | `memory` | 5 |
| `memory` | `(root)` | 5 |
| `cli` | `(root)` | 4 |
| `council` | `semantic` | 4 |
| `(root)` | `llm` | 3 |
| `(root)` | `perception` | 3 |
| `(root)` | `scribe` | 3 |
| `(root)` | `backends` | 3 |
| `(root)` | `tech_trace` | 3 |
| `cli` | `council` | 3 |
| `(root)` | `gateway` | 2 |
| `(root)` | `shared` | 2 |
| `(root)` | `deliberation` | 2 |
| `council` | `shared` | 2 |
| `council` | `gse` | 2 |
| `governance` | `llm` | 2 |
| `llm` | `(root)` | 2 |
| `loop` | `shared` | 2 |
| `yuhun` | `(root)` | 2 |

## Community Drifts

Modules whose import pattern suggests they belong to a different subpackage than their directory.

| Module | Directory | Community |
| --- | --- | --- |
| `backends.file_store` | backends | (root) |
| `backends.redis_store` | backends | (root) |
| `cli` | cli | (root) |
| `cli.__main__` | cli | (root) |
| `cli.main` | cli | (root) |
| `council.calibration` | council | (root) |
| `escape_valve` | (root) | council |
| `gates` | gates | (root) |
| `gates.compute` | gates | (root) |
| `governance` | governance | (root) |
| `governance.de_escalation` | governance | (root) |
| `governance.kernel` | governance | (root) |
| `governance.reflex` | governance | (root) |
| `governance.reflex_config` | governance | (root) |
| `governance.responsibility_audit` | governance | (root) |
| `governance.retro` | governance | memory |
| `memory.hippocampus` | memory | (root) |
| `memory.semantic_graph` | memory | (root) |
| `memory.visual_chain` | memory | (root) |
| `perception.web_ingest` | perception | (root) |
