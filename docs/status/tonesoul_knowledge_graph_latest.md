# ToneSoul Knowledge Graph Latest

- generated_at: 2026-03-22T12:48:44Z
- node_count: 857
- edge_count: 1669
- lane_count: 8

## Retrieval Protocol
- `authority_first`: Open Authority before implementation when semantics or thresholds are unclear.
- `lane_before_file`: Resolve the lane first, then open concrete files inside that lane.
- `tests_and_status_after_code`: After reading implementation, confirm behavior via tests or latest status artifacts.
- `graph_not_database_first`: Use this passive graph as the first recovery surface before considering a graph database.

## Lanes
### Authority
- summary: Single-source-of-truth specs and canonical reading order.
- members:
  - `README.md`
  - `AI_ONBOARDING.md`
  - `docs/terminology.md`
  - `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
  - `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
  - `語魂系統GPTs_v1.1/01_術語與門檻單一規格.md`
  - `語魂系統GPTs_v1.1/02_執行治理規格_Runtime.md`
  - `語魂系統GPTs_v1.1/07_六層架構與實作對位.md`
  - `語魂系統GPTs_v1.1/10_哲學到程式_可驗證對照表.md`
  - `AXIOMS.json`
- neighbors: `runtime`, `governance`, `web`, `verification`

### Runtime Plane
- summary: Live request path from web entrypoints into ToneSoul orchestration.
- members:
  - `apps/web/src/app/api/chat/route.ts`
  - `apps/api/server.py`
  - `tonesoul/unified_pipeline.py`
  - `tonesoul/tension_engine.py`
  - `tonesoul/tonebridge/analyzer.py`
- neighbors: `authority`, `governance`, `memory`, `web`

### Council + Governance
- summary: Deliberation, gate decisions, and route governance.
- members:
  - `tonesoul/council/runtime.py`
  - `tonesoul/council/pre_output_council.py`
  - `tonesoul/council/verdict.py`
  - `tonesoul/governance/kernel.py`
  - `tonesoul/yss_gates.py`
  - `tonesoul/poav.py`
  - `docs/COUNCIL_RUNTIME.md`
- neighbors: `authority`, `runtime`, `memory`, `verification`

### Memory Plane
- summary: Semantic graph, crystallization, SoulDB, and boot-time recall.
- members:
  - `MEMORY.md`
  - `tonesoul/memory/semantic_graph.py`
  - `tonesoul/memory/crystallizer.py`
  - `tonesoul/memory/soul_db.py`
  - `tonesoul/memory/boot.py`
  - `docs/ANTIGRAVITY_CONTEXT_MEMORY.md`
- neighbors: `runtime`, `governance`, `evolution`, `verification`

### Evolution Plane
- summary: Offline reflection, wakeup loops, stale-rule verification, and consolidation.
- members:
  - `tonesoul/dream_engine.py`
  - `tonesoul/wakeup_loop.py`
  - `tonesoul/stale_rule_verifier.py`
  - `scripts/run_repo_semantic_atlas.py`
  - `docs/plans/semantic_memory_architecture.md`
- neighbors: `memory`, `verification`, `observability`

### Web Surface
- summary: Front-end transport, fallback, and soul-model rendering helpers.
- members:
  - `apps/web/src/app/api/chat/route.ts`
  - `apps/web/src/lib/soulEngine.ts`
  - `apps/web/src/lib/chatFallback.ts`
  - `apps/web/src/lib/soulAuditor.ts`
  - `apps/web/src/__tests__/chatFallback.test.ts`
- neighbors: `authority`, `runtime`, `verification`

### Verification
- summary: Tests and current status surfaces that prove the graph against reality.
- members:
  - `tests/test_council_runtime.py`
  - `tests/test_dream_engine.py`
  - `tests/test_exception_trace.py`
  - `scripts/run_repo_healthcheck.py`
  - `scripts/verify_7d.py`
  - `docs/status/README.md`
  - `docs/status/repo_healthcheck_latest.md`
  - `docs/status/l7_retrieval_contract_latest.md`
  - `docs/status/l8_distillation_boundary_latest.md`
- neighbors: `authority`, `governance`, `memory`, `web`, `observability`

### Observability
- summary: Machine snapshots and passive artifacts that help later agents recover state.
- members:
  - `docs/status/README.md`
  - `docs/status/repo_healthcheck_latest.md`
  - `docs/status/memory_governance_contract_latest.md`
  - `docs/status/tonesoul_system_manifesto.md`
  - `docs/status/l7_retrieval_contract_latest.md`
  - `docs/status/l8_distillation_boundary_latest.md`
  - `scripts/run_l7_l8_contract_artifacts.py`
  - `scripts/run_repo_semantic_atlas.py`
- neighbors: `verification`, `evolution`

## Top Anchors
| path | kind | degree |
| --- | --- | ---: |
| `task.md` | `doc` | 671 |
| `tonesoul/unified_pipeline.py` | `python_module` | 52 |
| `tonesoul/memory/soul_db.py` | `python_module` | 45 |
| `README.md` | `doc` | 42 |
| `AI_ONBOARDING.md` | `doc` | 31 |
| `語魂系統GPTs_v1.1/02_執行治理規格_Runtime.md` | `authority_doc` | 29 |
| `語魂系統GPTs_v1.1/10_哲學到程式_可驗證對照表.md` | `authority_doc` | 29 |
| `語魂系統GPTs_v1.1/07_六層架構與實作對位.md` | `authority_doc` | 27 |
| `docs/README.md` | `doc` | 24 |
| `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md` | `doc` | 23 |
| `apps/api/server.py` | `app_module` | 21 |
| `tonesoul/council/types.py` | `python_module` | 21 |
