# Task

## Program Board (2026-02-14)
- [x] Level 1
- [x] Level 2
- [x] Architecture Audit Phase 76 (7.2/10, 10 findings)
- [x] Level 3 (3a/3b/3c/3d)
- [x] Multi-persona evaluation framework (A/B/C + 5 metrics)
- [x] Phase A (7 days): auth fail-closed + endpoint throttling + debug lock
- [x] Phase B (14 days): pipeline cache + input validation + stats dedup
- [x] Phase C (30 days): CI blocking + docs freshness + frontend retry
- [x] Phase 64-67 (showcase/docs/research/notes) acceptance closure
- [x] Phase 82: Persona Swarm Framework (coordination gate + readiness artifact)
- [x] Phase 83: Swarm decision contract hardening (input schema + validation)
- [x] Phase 84: Swarm fail-fast + cost-tier governance
- [x] Phase 85: Swarm budget execution planner
- [x] Phase 86: Swarm CI automation and contracts
- [x] Phase 87: Swarm dispatch script hardening
- [x] Phase 88: Monthly consolidation includes swarm readiness
- [x] Phase 89: Repo healthcheck includes swarm readiness
- [x] Phase 90: Healthcheck artifact + docs-contract swarm hardening
- [x] Phase 91: Task ledger normalization + baseline sync
- [x] Phase 92: Guardian adversarial bypass closure (homophone/metaphor/code-switch)
- [x] Phase 93: Commit attribution docs-only exemption
- [x] Phase 94: External source trust policy + allowlist gate
- [x] Phase 95: External source registry CI workflow + status artifact automation
- [x] Phase 96: User-defined persona roles + attachment-aware persona memory injection
- [x] Phase 97: Persona attachment file excerpt loader (allowlist + traversal guard + prompt budget)
- [x] Phase 98: Persona payload schema validation (web route + backend API fail-closed)
- [x] Phase 99: Custom-role council contract coverage (factory + fallback semantics)
- [x] Phase 100: Architecture convergence v2 (Trinket protocol + swarm dispatcher + YSS alignment)
- [x] Phase 101: YuHun 1.0 multi-persona audit profile scaffold
- [x] Phase 102: Git/local repository stabilization planning baseline
- [x] Phase 103: Side-branch isolation playbook and local hygiene guard
- [x] Phase 104: Temporary script cleanup in mainline
- [x] Phase 105: Mainline audit refresh and execution planning baseline
- [x] Phase 136: Market Mirror Dream Engine (Qualitative Forecasting & Prompt Injection Defense)
**Latest validation**: `pytest -q` => `849 passed` (2026-02-21). Level 3 implementation tracked in `CODEX_TASK.md` v7.

## Phase 122: Wave-Score Core Memory Governance (OpenClaw-Memory) (2026-03-01)
- [x] Add governance `wave_score` (conflict_strength × stance_shift × boundary_cost × consequence_weight)
- [x] Persist governance metadata (`wave_score`, `wave_components`, `memory_tier`)
- [x] Add high-tension core-priority rerank in recall pipeline
- [x] Extend benchmark metrics with `core_wave_top1_rate` + strict gate threshold
- [x] Fix FAISS Windows non-ASCII path write/read by switching to serialized-index I/O
- [x] Add regression tests for non-ASCII db path and core-wave prioritization
**Success Criteria**: high-tension queries prioritize core boundary memories with auditable metadata and pass local benchmark/test gates.

## Phase 123: Mainline Sync of Wave-Score Governance (tonesoul52) (2026-03-01)
- [x] Sync `tonesoul/memory/openclaw/hippocampus.py` with wave-score governance model
- [x] Add metadata fields (`kind`, `wave`, `wave_score`, `wave_components`, `memory_tier`) and backward-compatible recall output metadata
- [x] Enable query-time rerank controls (`query_tension_mode`, `query_wave`, `query_wave_mode`) in mainline hippocampus
- [x] Sync `scripts/ask_my_brain.py` with wave-aware CLI flags, friction report, and validation scenarios
- [x] Add/extend tests for core-priority ranking, non-ASCII db path, and script-level validation helpers
**Success Criteria**: mainline and OpenClaw-Memory share the same core governance behavior and pass targeted openclaw memory/script tests.

## Phase 124: Swarm Long-Task Planning Bootstrap (2026-03-01)
- [x] Define long-task swarm input profile (`docs/experiments/persona_swarm_long_task_input_2026-03-01.json`)
- [x] Run strict swarm evaluation and publish snapshot (`docs/status/persona_swarm_long_task_latest.json`)
- [x] Produce execution roadmap (`docs/plans/swarm_long_task_plan_2026-03-01.md`)
- [x] Add status README index entry for long-task swarm snapshot
- [x] Add dedicated wrapper script for repeatable long-task swarm planning runs
**Success Criteria**: long-task planning starts from a strict-passing swarm snapshot and yields an executable multi-phase roadmap.

## Phase 125: RFC-013 Wiring + Memory Integration + Compute Gate Stabilization (2026-03-02)
- [x] Task A: `memory/consolidator.py` wired with crystallizer-safe fallback and result key `crystals_generated` (kept `crystals_formed` for compatibility).
- [x] Task B: Added handoff entrypoint script `scripts/ingest_handoffs.py` (import-verified, no real ingestion execution in this run).
- [x] Task C: Wired `tension_context` into `UnifiedPipeline` hippocampus recall path (backward-compatible signature update in OpenClaw Hippocampus).
- [x] Task D: Stabilized free-tier rate-limit behavior in integration tests (`tests/test_pipeline_compute_gate.py` 4/4 green).
- [x] Task E: Exposed persona audit in `CouncilVerdict.to_dict()` via `persona_audit` while preserving `persona_uniqueness_audit`.
- [x] RFC-013 guardrail: no edits to `nonlinear_predictor.py`, `variance_compressor.py`, `work_classifier.py`.
- [?] Phase 110 GA blocker A/B direct Compute-Gate A/B code marker is not explicit in `tonesoul/gates/compute.py`; release artifact references remain in historical records.
**Validation**:
- `python -m pytest tests/test_memory_crystallizer.py tests/test_memory_consolidator.py -q --tb=short` -> 11 passed
- `python -m pytest tests/test_tension_recall.py -q --tb=short` -> 3 passed
- `python -m pytest tests/test_pipeline_compute_gate.py -v --tb=short` -> 4 passed
- `python -m pytest tests/test_persona_audit.py tests/test_council_runtime.py tests/test_genesis_integration.py -q --tb=short` -> 25 passed

## Phase 126: Environment Perception Write Gateway (2026-03-07)
- [x] Add `tonesoul/memory/write_gateway.py` as the canonical environment-stimulus write seam
- [x] Persist `EnvironmentStimulus` into `soul.db` with `type=environment_stimulus` and `layer=working`
- [x] Enforce cross-session deduplication on `content_hash`
- [x] Add SQLite-focused tests for write, dedupe, and filtered retrieval
**Success Criteria**: perception output is durably written into `soul.db` without changing the external HTTP API surface or touching legacy `self_journal` write paths.
**Validation**:
- `python -m ruff check tonesoul/memory/write_gateway.py tonesoul/memory/__init__.py tests/test_memory_write_gateway.py` -> passed
- `python -m black --check tonesoul/memory/write_gateway.py tonesoul/memory/__init__.py tests/test_memory_write_gateway.py` -> passed
- `python -m pytest tests/test_memory_write_gateway.py tests/test_perception.py tests/test_handoff_ingester.py tests/test_layered_memory.py -q` -> 17 passed
- `python -m pytest tests/test_perception.py tests/test_memory_write_gateway.py -q` -> 12 passed
- `python -m pytest tests -q` -> 1242 passed

## Phase 127: Dream Engine v1 (2026-03-07)
- [x] Add an offline Dream Engine that reads persisted environment stimuli from `soul.db`
- [x] Collide stimuli with durable crystals and related memory recall
- [x] Delegate friction / governance recommendation to `GovernanceKernel`
- [x] Add optional LLM reflection generation with deterministic fallback
- [x] Add tests for selection, collision scoring, and no-model fallback
**Success Criteria**: Dream Engine can run without user prompts, consume Phase 6 perception output, and emit structured governance-ready results without changing external HTTP APIs or touching legacy self-journal writes.
**Validation**:
- `python -m ruff check tonesoul/dream_engine.py scripts/run_dream_engine.py tests/test_dream_engine.py tests/test_run_dream_engine.py tonesoul/perception/stimulus.py tests/test_memory_write_gateway.py tests/test_perception.py` -> passed
- `python -m black --check tonesoul/dream_engine.py scripts/run_dream_engine.py tests/test_dream_engine.py tests/test_run_dream_engine.py tonesoul/perception/stimulus.py tests/test_memory_write_gateway.py tests/test_perception.py` -> passed
- `python -m pytest tests/test_dream_engine.py tests/test_run_dream_engine.py tests/test_memory_write_gateway.py tests/test_perception.py -q` -> 18 passed
- `python -m pytest tests -q` -> 1248 passed

## Phase 128: Autonomous Wake-up Loop v1 (2026-03-07)
- [x] Add a thin autonomous wake-up loop that repeatedly invokes Dream Engine without embedding policy logic
- [x] Keep cycle outputs structured and machine-readable for later dashboard consumption
- [x] Add a CLI runner that supports interval-based execution and snapshot emission
- [x] Add tests for idle cycles, repeated cycles, and runner wiring
**Success Criteria**: Dream Engine can be scheduled as a self-driven loop through a stable seam, without changing external HTTP APIs or bypassing the existing governance/memory boundaries.
**Validation**:
- `python -m ruff check tonesoul/wakeup_loop.py scripts/run_dream_wakeup_loop.py tests/test_wakeup_loop.py tests/test_run_dream_wakeup_loop.py` -> passed
- `python -m black --check tonesoul/wakeup_loop.py scripts/run_dream_wakeup_loop.py tests/test_wakeup_loop.py tests/test_run_dream_wakeup_loop.py` -> passed
- `python -m pytest tests/test_wakeup_loop.py tests/test_run_dream_wakeup_loop.py -q` -> 5 passed
- `python -m pytest tests -q` -> 1253 passed

## Phase 129: Dream Observability Dashboard v1 (2026-03-07)
- [x] Add a robust extractor for friction / Lyapunov signals from `self_journal.jsonl`
- [x] Add wake-up history ingestion for cycle-level friction / convergence metrics
- [x] Generate static HTML + JSON dashboard artifacts without depending on the existing frontend app
- [x] Add tests for missing-source fallback, signal extraction, and artifact writing
**Success Criteria**: operators can inspect friction and Lyapunov trendlines from journal/history artifacts without reading raw logs, and the dashboard remains decoupled from runtime policy and legacy memory writes.
**Validation**:
- `python -m ruff check tonesoul/dream_observability.py scripts/run_dream_observability_dashboard.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py` -> passed
- `python -m black --check tonesoul/dream_observability.py scripts/run_dream_observability_dashboard.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py` -> passed
- `python -m pytest tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py -q` -> 6 passed
- `python -m pytest tests -q` -> 1259 passed
- `python scripts/run_dream_wakeup_loop.py --no-llm --max-cycles 1 --snapshot-path docs/status/dream_wakeup_snapshot_latest.json` -> generated idle snapshot
- `python scripts/run_dream_observability_dashboard.py --journal-path memory/self_journal.jsonl --wakeup-path docs/status/dream_wakeup_snapshot_latest.json --out-dir docs/status` -> generated latest HTML/JSON dashboard artifacts

## Phase 130: Autonomous Dream Cycle Runner v1 (2026-03-07)
- [x] Add a one-shot orchestration seam that composes perception ingest, stimulus processing, memory write, wake-up execution, and dashboard refresh
- [x] Keep the runner host-driven and file-based, without moving policy into the orchestrator
- [x] Support URL-driven ingestion but degrade gracefully when Crawl4AI or network inputs are unavailable
- [x] Add tests for no-URL idle runs, successful ingested stimulus runs, and CLI artifact wiring
**Success Criteria**: one command can advance the full Phase 7 loop from external inputs to updated wake-up/dashboard artifacts, while preserving the existing modular seams and memory guardrails.
**Validation**:
- `python -m ruff check tonesoul/autonomous_cycle.py scripts/run_autonomous_dream_cycle.py tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py` -> pass
- `python -m black --check tonesoul/autonomous_cycle.py scripts/run_autonomous_dream_cycle.py tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py` -> pass
- `python -m pytest tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py -q` -> 5 passed
- `python -m pytest tests -q` -> 1264 passed
- `python scripts/run_autonomous_dream_cycle.py --no-llm` -> `overall_ok: true`, refreshed idle snapshot/history/dashboard artifacts

## Phase 131: Curated Source Registry Bridge v1 (2026-03-07)
- [x] Add a perception-layer registry reader that selects approved external source URLs from `spec/external_source_registry.yaml`
- [x] Reuse the existing allowlist and review-freshness policy instead of creating a second source-governance path
- [x] Extend the autonomous cycle CLI to merge curated registry URLs with explicit `--url` and `--url-file` inputs
- [x] Emit registry selection metadata in CLI output so operators can see which curated sources were used or skipped
- [x] Add tests for id/category filtering, stale review rejection, and CLI merge behavior
**Success Criteria**: operators can run one autonomous cycle against reviewed external sources without manually copying URLs, while source governance remains centralized in the registry policy.
**Validation**:
- `python -m ruff check tonesoul/perception/source_registry.py tonesoul/perception/__init__.py scripts/verify_external_source_registry.py scripts/run_autonomous_dream_cycle.py tests/test_source_registry.py tests/test_run_autonomous_dream_cycle.py tests/test_verify_external_source_registry.py` -> pass
- `python -m black --check tonesoul/perception/source_registry.py tonesoul/perception/__init__.py scripts/verify_external_source_registry.py scripts/run_autonomous_dream_cycle.py tests/test_source_registry.py tests/test_run_autonomous_dream_cycle.py tests/test_verify_external_source_registry.py` -> pass
- `python -m pytest tests/test_source_registry.py tests/test_run_autonomous_dream_cycle.py tests/test_verify_external_source_registry.py tests/test_run_external_source_registry_check.py -q` -> 14 passed
- `python -m pytest tests -q` -> 1267 passed
- `python -c "...select_curated_registry_urls('spec/external_source_registry.yaml', limit=3)..."` -> `ok: true`, selected ids `osv`, `scorecard`

## Phase 132: Registry-Driven Schedule Profile Runner v1 (2026-03-07)
- [x] Add a thin schedule runner that rotates through approved registry entries and triggers one autonomous cycle per schedule tick
- [x] Persist schedule cursor/state so repeated invocations continue from the next curated source instead of restarting from the first entry
- [x] Keep source policy in `source_registry` and keep `AutonomousDreamCycleRunner` URL-driven; the schedule layer may only compose approved batches
- [x] Emit schedule-level snapshot/history artifacts so operators can inspect which curated sources were sampled over time
- [x] Add tests for cursor persistence, round-robin rotation, and CLI strict-mode behavior
**Success Criteria**: the system can be launched on a host schedule and autonomously rotate through reviewed external sources without manual URL entry or policy drift.
**Validation**:
- `python -m ruff check tonesoul/autonomous_schedule.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m black --check tonesoul/autonomous_schedule.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m pytest tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py -q` -> 6 passed
- `python scripts/run_autonomous_registry_schedule.py --registry-id osv --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 --no-llm` -> `overall_ok: true`, ingested `https://osv.dev/`, persisted schedule state/history/snapshot
- `python -m pytest tests -q` -> 1273 passed

## Phase 133: Schedule Profile Theory Spec v1 (2026-03-07)
- [x] Write a dedicated theory/spec document explaining why schedule profiles exist and how they differ from source trust, memory, and governance
- [x] Define profile axes: cadence, weight, revisit interval, failure backoff, and tension budget
- [x] Record the Cartesian decomposition so future policy work stays layered and explainable
**Success Criteria**: the next schedule-policy implementation can be derived from an explicit theory document rather than ad hoc scheduler heuristics.

## Phase 134: Schedule Profile Contract v1 (2026-03-07)
- [x] Add a machine-readable schedule profile spec with named profiles for baseline and category-focused autonomous runs
- [x] Implement a loader/resolver that merges profile defaults with explicit CLI overrides
- [x] Extend the registry schedule CLI to accept `--profile` without teaching the scheduler core how to parse YAML
- [x] Emit resolved profile metadata in CLI output so cadence choices remain explainable
- [x] Add tests for profile loading, unknown profile rejection, and override precedence
**Success Criteria**: operators can launch autonomous schedule runs via a named profile instead of repeating low-level cadence flags, while explicit CLI args still win over profile defaults.
**Validation**:
- `python -m ruff check tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m black --check tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m pytest tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py -q` -> 9 passed
- `python scripts/run_autonomous_registry_schedule.py --profile security_watch --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 --no-llm` -> `overall_ok: true`, resolved profile cadence and executed one real cycle from approved security sources
- `python -m pytest tests -q` -> 1276 passed

## Phase 135: Schedule Policy Memory v1 (2026-03-07)
- [x] Add `revisit_interval_cycles` and `failure_backoff_cycles` to the schedule profile contract
- [x] Persist per-entry operational state so schedule continuity can remember recent selection and source failures across host-triggered runs
- [x] Teach `AutonomousRegistrySchedule` to skip entries that are still cooling down, while keeping policy explainable in artifacts
- [x] Emit operational defer reasons in schedule output so humans can distinguish trust filtering from cadence/backoff filtering
- [x] Add tests for revisit cooldown, failure-triggered backoff, and profile override precedence
**Success Criteria**: the autonomous scheduler can avoid immediate source repetition and temporarily back off unstable sources without moving operational state into soul memory or weakening registry governance.
**Validation**:
- `python -m ruff check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m black --check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m pytest tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py -q` -> 11 passed
- `python scripts/run_autonomous_registry_schedule.py --profile security_watch --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 --no-llm` -> `overall_ok: true`, selected `scorecard`, persisted per-entry operational state with profile policy memory
- `python -m pytest tests -q` -> 1278 passed

## Phase 136: Deterministic Category Policy v1 (2026-03-07)
- [x] Extend the schedule profile contract with category weights and category-specific backoff multipliers
- [x] Keep selection deterministic by introducing weighted category cadence, not random sampling
- [x] Preserve explainability by emitting category policy traces in schedule artifacts
- [x] Keep cooldown/backoff in scheduler state only, never in `soul.db` or `self_journal.jsonl`
- [x] Add tests for weighted selection order, category backoff scaling, and CLI override precedence
**Success Criteria**: autonomous scheduling can prefer some categories more often than others without sacrificing deterministic replay, auditability, or the existing registry/governance boundaries.
**Validation**:
- `python -m ruff check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m black --check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m pytest tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py -q` -> 13 passed
- `python -m pytest tests -q` -> 1280 passed

## Phase 137: Cycle-Level Tension Budget Policy v1 (2026-03-07)
- [x] Add schedule profile support for cycle-level tension budget thresholds and cooldown cycles
- [x] Derive scheduler reactions from existing wake-up summary signals instead of recomputing governance
- [x] Persist category-level tension cooldown as operational state in schedule artifacts only
- [x] Emit explicit budget observations and cooldown reasons in schedule results
- [x] Add tests for threshold breach cooldown, category defer reporting, and CLI/profile override precedence
**Success Criteria**: the autonomous scheduler can temporarily cool a category after a high-tension wake-up cycle while preserving the boundary that governance computes tension and scheduling only reacts to the observed signal.
**Validation**:
- `python -m ruff check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m black --check tonesoul/autonomous_schedule.py tonesoul/schedule_profile.py scripts/run_autonomous_registry_schedule.py tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py` -> pass
- `python -m pytest tests/test_autonomous_schedule.py tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py -q` -> 14 passed
- `python -m pytest tests -q` -> 1281 passed

## Phase 138: Dream Engine Host Wiring + Observability + Wake-up Scheduler (2026-03-09)
- [x] Task A: route Dream Engine collision writes through `MemoryWriteGateway`
- [x] Task B: extend dream observability for write-gateway and collision/runtime counters
- [x] Task C: wire wake-up loop scheduling, consolidation cadence, and breaker-aware pauses
- [x] Task D: stage only task-related files and prepare one feature commit on `feat/env-perception`
- [x] Task E: summarize `docs/status/` artifact impact and validation results
**Success Criteria**: Dream collisions are durably written via the canonical gateway, observability exposes the new write/runtime counters, wake-up scheduling can autonomously chain dream cycles with bounded consolidation/breaker pauses, and the whole phase passes `python -m pytest tests/ -x --tb=short -q` => `1457 passed` plus `ruff check tonesoul tests`.

## Phase 106: Foundation Debt Burn-down (2026-02-22)
- [x] Decay query pre-filter：將 SQLite decay 查詢改為 DB 先過濾 + Python 精排，降低大資料集負擔
- [x] Evolution sync：新增 `evolution_results` 持久化路徑（Supabase migration + backend 寫入）
- [x] Frontend observability：在聊天審議面板顯示 `semantic_contradictions` / `semantic_graph_summary` / visual snapshot
- [x] Contract tests：補齊 API/DB 測試覆蓋上述路徑，避免回歸
- [x] Docs sync：同步 `docs/ARCHITECTURE_DEPLOYED.md` 與部署 schema 文檔狀態
**成功標準**: 相關測試綠燈，文件中的對應 TODO/checklist 改為已落地或可驗證狀態，且不破壞既有 chat/persistence 合約。

## Backlog Radar (Original Specs/Docs, 2026-02-14)
- [x] Sync and close pending Chat UI checklist in `spec/chat_ui_improvement_spec.md` (4/4 completed on 2026-02-14)
- [x] Execute/verify backend persistence acceptance list in `docs/plans/backend_persistence_acceptance_checklist.md` (passed 2026-02-14: `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com --timeout 40`)
- [x] Reconcile stale roadmap checkboxes in `docs/ARCHITECTURE_DEPLOYED.md` against implemented Phase 77-99 features
- [x] Prioritize semantic-control derivation backlog in `spec/tonesoul_improvement_derivation.md` and `spec/wfgy_semantic_control_spec.md`
- [x] Stage release/readiness checklists from `docs/RELEASE_v0.1.0_PLAN.md` and `docs/SMALL_BOAT_MVP.md` (`docs/plans/release_readiness_staging.md`)
- [x] Execute Release Stage 0 baseline gates (`pytest -v`, `black --check`, `ruff check`, `pytest tests/red_team -q`) on 2026-02-14
- [x] Generate vulnerability assessment artifact (`reports/security_vulnerability_assessment_latest.md`) on 2026-02-14
- [x] Sync README + deploy walkthrough docs (`README.md`, `docs/VERCEL_DEPLOY.md`) on 2026-02-14
- [x] Verify Stage 2 local Ollama baseline (`ollama list`, `LLM_BACKEND=ollama` smoke, `pytest tests/ -x -q`) on 2026-02-14
- [x] Prepare Stage 3 release artifacts (`docs/RELEASE_NOTES_v0.1.0.md`, `reports/coverage_latest.*`, `reports/test_coverage_latest.md`) on 2026-02-14
- [x] Final release action: create and push Git tag `v0.1.0` (2026-02-14)
- [x] Add Antigravity VM runbook automation scripts (`scripts/vm/bootstrap_antigravity_vm.sh`, `scripts/vm/run_antigravity_smoke.sh`) on 2026-02-14

## Phase 100: Architecture Convergence v2 (Trinket + Swarm)
- [x] Consolidated legacy RFC/draft into verified plan: `docs/ARCHITECTURE_CONVERGENCE_PLAN.md`
- [x] Added current-state correction (`UnifiedCore` is non-prod but still referenced; not immediate delete)
- [x] Added 841-test landscape + multi-persona audit baseline in convergence doc
- [x] Spec-first: define `TRINKET_PROTOCOL_SPEC` (Layer Decoupling / Is-Ought / Currency Audit / Responsibility Trace)
- [x] Runtime: add dispatcher state machine (`Resonance/Tension/Conflict`) with auditable metadata in `UnifiedPipeline`
- [x] Evolution alignment: bridge `yss_pipeline` context schema to unified runtime contract and populate non-null A/B/C evaluation artifacts
- [x] Zombie boundary: mark `UnifiedCore` as `legacy_non_runtime` with explicit replacement target
**Success Criteria**: v2 convergence plan is executable, testable, and reflected in blocking governance checks.

## Phase 101: YuHun 1.0 multi-persona audit profile scaffold
- [x] Added `spec/personas/yuhun_v1_multi_persona_audit.yaml`
- [x] Defined professional split across architecture/security/reliability/evidence/product stances
- [x] Included runtime-compatible `custom_roles` payload and swarm seed schema
- [x] Added discussion report: `reports/multi_persona_audit_discussion_2026-02-20.md`
**Success Criteria**: YuHun 1.0 has a reusable multi-persona audit profile with role-level professional differentiation.

## Phase 102: Git/local repository stabilization planning baseline
- [x] Captured current git baseline (`branch/head/dirty tree/recent additions`)
- [x] Added executable plan: `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`
- [x] Published Phase 1 artifacts:
  - `reports/git_local_baseline_2026-02-20.md`
  - `reports/git_worktree_classification_2026-02-20.md`
- [x] Started Phase 2 dry-run batch design:
  - `reports/git_phase2_commit_batch_draft_2026-02-20.md`
- [x] Execute Phase 1-4 cleanup and validation flow from plan
**Success Criteria**: repository state is auditable by category and cleanup can proceed phase-by-phase without mixing concerns.

## Phase 103: Side-branch isolation playbook and local hygiene guard
- [x] Added `docs/plans/side_branch_isolation_playbook_2026-02-21.md`
- [x] Documented side-branch decisions for `.agent/skills/local_llm/`, `tonesoul/adaptive_gate.py`, `tests/test_adaptive_gate.py`
- [x] Added local hygiene guard flow (`.git/info/exclude` + temporary isolation before mainline healthcheck)
**Success Criteria**: side-branch work can continue without causing false-negative mainline healthcheck failures.

## Phase 104: Temporary script cleanup in mainline
- [x] Removed stale one-off root scripts (`diagnostic_post.py`, `reply_tone_tension.py`, `test_api_post.py`)
- [x] Updated script and inventory docs (`SCRIPTS_README.md`, `reports/REPO_INVENTORY.md`)
- [x] Synced architecture backlog item (`docs/ARCHITECTURE_DEPLOYED.md` tmp-script cleanup)
**Success Criteria**: temporary one-off scripts no longer remain in tracked mainline root, and docs reflect current script surface.

## Phase 105: Mainline audit refresh and execution planning baseline
- [x] Added follow-up audit report (`reports/project_audit_report_2026-02-21_mainline_followup.md`)
- [x] Added mainline execution plan (`docs/plans/mainline_phase105_execution_plan_2026-02-21.md`)
- [x] Revalidated mainline command set under side-branch isolation constraints
**Success Criteria**: 主線下一階段任務有明確優先級、邊界、驗收標準，且不與支線工作混批。

## Phase 77: Level 3 Experimental
- [x] 3a Semantic Trigger
- [x] 3b Cross-session recovery
- [x] 3c Council evolution tracker
- [x] 3d Adversarial red/blue stub
**Result**: Level 3 code + tests completed in this round, then full suite revalidated (`755 passed, 3 xfailed`).

## Phase 78: Multi-persona evaluation framework (A/B/C + 5 metrics)
- [x] A/B/C comparison protocol
- [x] Five metrics: Task Quality / Safety Pass Rate / Consistency@Session / Disagreement Utility / Token+Latency Cost
- [x] Cost gate and promotion criteria

## Phase 82: Persona Swarm Framework
- [x] Persona swarm coordination harness + metric definitions
- [x] Persona swarm artifact and gate snapshot (`docs/status/persona_swarm_framework_latest.json`)
**Result**: Persona swarm readiness artifact published and referenced in convergence tracking.

## Phase 83: Swarm Decision Contract Hardening
- [x] Swarm decision contract fixed to `approve | block | revise | defer`
- [x] Runtime validation for `signal.vote` and `final_decision`
- [x] Input template and docs update (`docs/experiments/persona_swarm_input_template.json`)
**Result**: Swarm ingress no longer accepts ambiguous decision strings.

## Phase 84: Swarm Fail-Fast + Cost-Tier Governance
- [x] Guardian fail-fast in framework (high-confidence safety block => forced block)
- [x] Runner gate checks `guardian_fail_fast_consistency`
- [x] Runner emits `cost_profile` tier (`low/moderate/high/critical`) with agent budget
**Result**: Swarm runtime now has safety-first early-stop and budget-aware execution guidance.

## Phase 85: Swarm Budget Execution Planner
- [x] Two-pass runner flow: baseline full-signal eval -> budgeted execution eval
- [x] Cost-tier recommendation now maps to actual signal selection and execution plan
- [x] Gate now includes `execution_budget_respected` check
**Result**: Cost tier is no longer advisory only; it actively constrains swarm execution.

## Phase 86: Swarm CI Automation and Contracts
- [x] Added `.github/workflows/persona_swarm.yml` (push/pr + dispatch + schedule)
- [x] Uploads `docs/status/persona_swarm_framework_latest.json` and `persona_swarm.log`
- [x] Added workflow contract tests for persona swarm workflow
**Result**: Swarm governance artifact is now CI-generated and auditable.

## Phase 87: Swarm Dispatch Script Hardening
- [x] Added `scripts/run_persona_swarm_dispatch.py` for workflow_dispatch orchestration
- [x] Added input validation for missing `input_path`
- [x] Workflow now calls dispatch script instead of inline shell branching
**Result**: Manual swarm runs now have deterministic validation and clearer CI errors.

## Phase 88: Monthly Consolidation Includes Swarm Readiness
- [x] `run_monthly_consolidation.py` now runs `run_persona_swarm_framework.py --strict`
- [x] Added monthly consolidation contract test for `persona_swarm` check command
- [x] Updated status docs to reflect swarm readiness in monthly aggregate
**Result**: Monthly governance report now includes swarm readiness gate health.

## Phase 89: Repo Healthcheck Includes Swarm Readiness
- [x] `run_repo_healthcheck.py` now runs `run_persona_swarm_framework.py --strict`
- [x] Added healthcheck contract test for `persona_swarm` check command
- [x] Updated status docs to reflect swarm readiness in repo healthcheck aggregate
**Result**: Push/PR healthcheck now enforces swarm readiness in the blocking governance loop.

## Phase 90: Healthcheck Artifact + Docs-Contract Swarm Hardening
- [x] `repo_healthcheck.yml` artifact now uploads `docs/status/persona_swarm_framework_latest.json`
- [x] Added workflow contract coverage for healthcheck artifact path
- [x] Added `verify_docs_consistency` contract: `run_repo_healthcheck.py` must include `persona_swarm` strict check
**Result**: Repo healthcheck now preserves swarm output as CI evidence and prevents accidental swarm-check regression.

## Phase 91: Task Ledger Normalization + Baseline Sync
- [x] Synchronized baseline from `769 passed, 3 xfailed` to current `807 passed`
- [x] Resolved legacy unchecked carry-over in `task.md` historical section
- [x] Updated `docs/SMALL_BOAT_MVP.md` test-count reference (`807`)
**Result**: Task and docs now share one test baseline and no stale open checkbox drift in active ledger.

## Phase 92: Guardian Adversarial Bypass Closure
- [x] Guardian now blocks mixed-script homophone obfuscation (`炸dan`)
- [x] Guardian now blocks euphemistic + concealment harmful intent patterns
- [x] Guardian now blocks pinyin code-switch homicide phrase (`sha ren`)
- [x] Removed `xfail` from `tests/test_adversarial.py`
**Result**: Adversarial bypass tests are now strict pass; full suite no longer depends on xfail exceptions.

## Phase 93: Commit Attribution Docs-Only Exemption
- [x] `verify_commit_attribution.py` now evaluates changed files and supports docs-only exemption
- [x] Added unit tests for docs-only exemption and mixed-change non-exemption
- [x] Commit attribution remains blocking for non-docs commits without trailers
**Result**: Docs-only commits no longer fail CI attribution checks, while code commits still require `Agent/Trace-Topic`.

## Phase 94: External Source Trust Policy + Allowlist Gate
- [x] Added `spec/external_source_registry.yaml` with blocked short-link hosts + curated allowlist
- [x] Added `scripts/verify_external_source_registry.py` (`https` / host allowlist / review freshness / app URL checks)
- [x] Added `docs/EXTERNAL_SOURCE_TRUST_POLICY.md` and indexed it in `docs/INDEX.md`
- [x] Added tests for source registry verifier and wired strict check into `run_repo_healthcheck.py`
**Result**: External source usage now follows a default-deny posture with enforceable CI gate.

## Phase 95: External Source Registry CI + Status Artifact
- [x] Added `scripts/run_external_source_registry_check.py` to publish JSON + Markdown status artifacts
- [x] Added `.github/workflows/external_source_registry.yml` (push/pr + dispatch + schedule)
- [x] Added workflow contracts in `tests/test_workflow_contracts.py`
- [x] Added script coverage in `tests/test_run_external_source_registry_check.py`
- [x] Updated `docs/status/README.md` with new artifact and workflow references
**Result**: External source trust checks now run as a standalone CI lane with auditable artifacts.

## Phase 96: User-Defined Persona Roles + Attachment Context
- [x] Expanded `PersonaConfig` with `customRoles[]` (name/description/promptHint/attachments)
- [x] Added persona role templates and editable role/attachment UI in `apps/web/src/components/PersonaSettings.tsx`
- [x] Forwarded `persona.custom_roles` in chat transport payload from `apps/web/src/components/ChatInterface.tsx`
- [x] Extended backend persona memory injection in `tonesoul/unified_pipeline.py` to include custom role context
- [x] Added/updated tests: `apps/web/src/__tests__/personaSettings.test.ts`, `apps/web/src/__tests__/apiRoutes.chatTransport.test.ts`, `tests/test_visual_chain_prompt_injection.py`
**Result**: Persona roles are no longer fixed; users can define role cards and attach file paths as runtime context hints.

## Phase 97: Persona Attachment Excerpt Loader Hardening
- [x] Added attachment path normalization + allowlist check (`TONESOUL_PERSONA_ATTACHMENT_ALLOW_PREFIXES`)
- [x] Added path traversal/absolute-path rejection and repo-root containment guard
- [x] Added text-only extension filter + excerpt byte/char budget
- [x] Added per-request attachment excerpt budget (`TONESOUL_PERSONA_ATTACHMENT_MAX_FILES`) and cache
- [x] Added tests for allowed excerpt inclusion and disallowed path blocking
**Result**: Persona attachment paths can enrich prompt context safely without becoming arbitrary file-read exfiltration.

## Phase 98: Persona Payload Schema Validation
- [x] Added `persona` deep-shape validation in `apps/web/src/app/api/chat/route.ts`
- [x] Added backend fail-closed persona validator in `apps/api/server.py`
- [x] Enforced limits (`custom_roles <= 8`, `attachments <= 6` per role)
- [x] Added tests for invalid `persona.custom_roles` shape in web route and backend contract
**Result**: malformed persona payloads are now rejected early with `400 Invalid persona` instead of entering runtime.

## Phase 99: Custom-Role Council Contract Coverage
- [x] Added `tests/test_custom_role_council.py` to lock custom-role council semantics
- [x] Covered `create_from_custom_role` (name normalization, prompt hint, model override, fallback behavior)
- [x] Covered `create_custom_council` (invalid-entry skip, empty fallback to default council, model fanout)
- [x] Covered unknown-name `PerspectiveFactory.create(...)` fallback semantics and evaluation baseline
**Result**: custom-role council behavior is now regression-protected by dedicated contract tests.

## Execution Log (2026-02-14)
- [x] Phase A complete
- [x] Production read auth fail-closed
- [x] `/api/chat` and `/api/validate` throttling
- [x] Production debug lock (`TONESOUL_API_DEBUG` ignored in production)
- [x] AI Sleep stats dedup: `identify_patterns(..., exclude_promoted=True)` default enabled
- [x] Phase B complete
- [x] `/api/chat` pipeline cache (TTL + max-items + deterministic key)
- [x] `/api/session-report` and `/api/chat` history payload deep validation
- [x] Validation: `pytest -q` => `807 passed` (2026-02-13)
- [x] Phase C complete
- [x] CI blocking upgrades: `semantic_health` blocking council tests + `git_hygiene --strict` on push/PR
- [x] Docs freshness checks: `verify_docs_consistency` now enforces dynamic test-count reference in `docs/REPOSITORY_STRUCTURE.md`
- [x] Frontend retry/backoff: `/api/chat` route transient retry (`429/502/503/504`) with exponential delay
- [x] Phase 78 complete
- [x] Added `docs/experiments/MULTI_PERSONA_EVALUATION_FRAMEWORK.md` and `docs/status/multi_persona_eval_latest.json`
- [x] Phase 64-67 closure via web contracts
- [x] Added `apps/web/src/__tests__/publicSurface.contract.test.ts` (docs/showcase/notes)
- [x] Added `apps/web/src/__tests__/metadataRoutes.contract.test.ts` (sitemap/robots)
- [x] CI diagnostics upgrade in `.github/workflows/test.yml` (pytest logs + commit attribution artifact)
- [x] `semantic_health.yml` fixed: install `-e .[dev]`, blocking council log artifact, UTF-8 AXIOMS read
- [x] Validation: `npm --prefix apps/web run lint && npm --prefix apps/web run test && npm --prefix apps/web run build` (pass)
- [x] Validation: `pytest tests/test_workflow_contracts.py tests/test_verify_docs_consistency.py -q` => `14 passed`
- [x] Phase 82 complete
- [x] Added persona swarm framework artifact `docs/status/persona_swarm_framework_latest.json`
- [x] Validation: `python scripts/run_persona_swarm_framework.py --strict` => `pass`
- [x] Phase 83 complete
- [x] Added swarm decision contract validation in framework + runner
- [x] Validation: `pytest tests/test_swarm_framework.py tests/test_run_persona_swarm_framework.py -q` => `16 passed`
- [x] Phase 84 complete
- [x] Added guardian fail-fast governance output and runner cost-tier profile
- [x] Validation: `pytest tests/test_swarm_framework.py tests/test_run_persona_swarm_framework.py tests/test_verify_docs_consistency.py -q` => `27 passed`
- [x] Phase 85 complete
- [x] Added execution planner with baseline/budgeted dual evaluation in swarm runner
- [x] Validation: `pytest tests/test_swarm_framework.py tests/test_run_persona_swarm_framework.py tests/test_verify_docs_consistency.py -q` => `31 passed`
- [x] Phase 86 complete
- [x] Added persona swarm CI workflow and workflow contract coverage
- [x] Validation: `pytest tests/test_workflow_contracts.py tests/test_verify_docs_consistency.py tests/test_run_persona_swarm_framework.py tests/test_swarm_framework.py -q` => `39 passed`
- [x] Phase 87 complete
- [x] Added persona swarm dispatch runner + contract tests
- [x] Validation: `pytest tests/test_run_persona_swarm_dispatch.py tests/test_workflow_contracts.py tests/test_verify_docs_consistency.py -q` => `22 passed`
- [x] Phase 88 complete
- [x] Added `persona_swarm` check to monthly consolidation pipeline
- [x] Validation: `pytest tests/test_run_monthly_consolidation.py tests/test_verify_docs_consistency.py -q` => `15 passed`
- [x] Phase 89 complete
- [x] Added `persona_swarm` check to repo healthcheck pipeline
- [x] Validation: `pytest tests/test_run_repo_healthcheck.py tests/test_verify_docs_consistency.py tests/test_workflow_contracts.py -q` => `26 passed`
- [x] Phase 90 complete
- [x] Repo healthcheck workflow now uploads swarm status artifact
- [x] Validation: `pytest tests/test_run_repo_healthcheck.py tests/test_workflow_contracts.py tests/test_verify_docs_consistency.py -q` => `27 passed`
- [x] Phase 91 complete
- [x] Task/docs baseline synced to current `807 passed`
- [x] Validation: `python -m pytest tests -q` => `807 passed`
- [x] Phase 92 complete
- [x] Guardian anti-obfuscation rules shipped; adversarial xfails removed
- [x] Validation: `python -m pytest tests/test_guardian.py tests/test_adversarial.py tests/test_pre_output_council.py -q` => `21 passed`
- [x] Phase 93 complete
- [x] Commit attribution now supports docs-only exemption
- [x] Validation: `python -m pytest tests/test_verify_commit_attribution.py -q` => `4 passed`
- [x] Phase 94 complete
- [x] External source registry strict gate integrated into repo healthcheck runner
- [x] Validation: `python -m pytest tests -q` => `814 passed`
- [x] Phase 95 complete
- [x] External source registry standalone workflow + status artifact lane added
- [x] Validation: `python -m pytest tests -q` => `819 passed`
- [x] Phase 96 complete
- [x] User-defined persona roles now support role descriptions and attachment metadata in settings + transport
- [x] Validation: `npm --prefix apps/web run lint && npm --prefix apps/web run test` => `pass`
- [x] Validation: `python -m pytest tests/test_visual_chain_prompt_injection.py tests/test_unified_core.py -q` => `16 passed`
- [x] Phase 97 complete
- [x] Attachment excerpt loader now enforces allowlist + traversal guard + prompt budget
- [x] Validation: `python -m pytest tests/test_visual_chain_prompt_injection.py -q` => `6 passed`
- [x] Phase 98 complete
- [x] Persona payload validation now fail-closed in both Next route and Flask API
- [x] Validation: `npm --prefix apps/web run test -- src/__tests__/apiRoutes.invalidJson.test.ts src/__tests__/apiRoutes.chatTransport.test.ts src/__tests__/personaSettings.test.ts` => `23 passed`
- [x] Validation: `python -m pytest tests/test_api_server_contract.py tests/test_visual_chain_prompt_injection.py -q` => `20 passed`
- [x] Phase 99 complete
- [x] Added dedicated custom-role council contract tests for custom perspective creation and fallback semantics
- [x] Validation: `python -m pytest tests/test_custom_role_council.py -q` => `19 passed`
- [x] Validation: `python -m pytest -q` => `841 passed`
- [x] Phase 100 kickoff complete
- [x] Published verified convergence plan: `docs/ARCHITECTURE_CONVERGENCE_PLAN.md` (replaces legacy RFC-002 assumptions)
- [x] Convergence plan now includes runtime/evolution boundary corrections + test landscape + actionable roadmap
- [x] Phase 100 complete
- [x] Added `docs/governance/TRINKET_PROTOCOL_SPEC.md` (A/B/C dispatch + layer/trace contract)
- [x] `UnifiedPipeline` now emits auditable `dispatch_trace` into trajectory/verdict/API payload
- [x] Added YSS unified adapter (`build_unified_seed`, `run_pipeline_from_unified_request`) and `multi_persona_eval.json` artifact generation
- [x] Added `UnifiedCore.runtime_boundary()` and maintenance-mode deprecation warning (zombie-code boundaryization)
- [x] Validation: `python -m pytest -q` => `849 passed`
## Phase 79-81: Legacy Duplicates (Closed)
- [x] Legacy duplicate tracking blocks for Phase A/B/C removed from active queue.
- [x] Canonical status is tracked in Program Board + Execution Log above.
## Phase 76: 憭犖?澆?瑽祟?伐??交???蝯∴?
- [x] 隞亙?閫閫暺?Architect / Quality / Guardian / Git嚗??撠???
- [x] ?瑁? `run_repo_healthcheck --strict --allow-missing-discussion` ?????箇?嚗?39 tests嚗?- [x] ?日??嗆?撘梢????嚗? P0/P1/P2 ??
- [x] ?Ｗ?交??祟?亙??`docs/ARCHITECTURE_REVIEW_2026-02-13.md`
- [x] Phase A/B/C status consolidated into Program Board and Execution Log
## Phase 75: 閮?“??+ AI Sleep ?箏?嚗evel 2b + 2d嚗?- [x] ??`tonesoul/memory/decay.py` ?啣? `retrospective_score()` ??`apply_retrospective()` ?撘???蝔?- [x] ??`tonesoul/memory/soul_db.py` ??`query()` ?啣? `apply_reflection/current_topics/active_commitments` ?嚗sonl/Sqlite/Protocol ?郊嚗?- [x] ??`tonesoul/memory/consolidator.py` ?啣? `SleepResult`?_classify_for_promotion()`?sleep_consolidate()`
- [x] ??`apps/api/server.py` ??`/api/session-report` 銝脫 decay cleanup 敺? AI Sleep 閫貊
- [x] ?啣? `tests/test_retrospective_reflection.py` ??`tests/test_ai_sleep.py` 銝阡?
- [x] 撽? `pytest`嚗?2 tests嚗? `ruff/black` ??瑼Ｘ?函?
**??璅?**: 閮撅文?舀?※皜?+ ?“??+ Session 蝯??箏???畾萄?瘚?嚗??Ｘ? API contract 皜祈岫蝬剜?????
## Phase 74: ?垢?銝?湔批楚瑼ｇ?Button Safety Baseline嚗?- [x] ?日? `apps/web` ???`<button>` 鈭辣蝬??孛?潸楝敺?- [x] 蝯曹?鋆?蝻箏仃??`type="button"`嚗?靘?form 摰孵銝炊閫?submit
- [x] 靽??啗店憿?斗?蝔???mobile/touch嚗??嚗??hover-only 靘陷
- [x] 靽桀儔?????& ?芷鞈???皜?conversations ?撩???鋆? memory insights ?璈?key 皜
- [x] 隞?`test + lint + build` 摰撽??垢?舐??**??璅?**: ?垢銝餉?????冽?璈???銵銝?湛?銝?`apps/web` 皜祈岫???炎?亥?撱箇蔭????

## Phase 73: ?垢閰梢??芷?舐?找耨鋆?Mobile / Touch嚗?- [x] 靽桀儔 `ConversationList` ????靘陷 hover 撠????誑?芷撠店??憿?- [x] ?啣?撠店???詨憭暺??芸??嗅?嚗??格???- [x] 鋆???隤?撅祆改?`type="button"` / `aria-label`嚗???雿帘摰?- [x] 靽桀儔?予頛詨獢 IME嚗葉?摮?????Enter ?航隤日??憿?- [x] 撽? `apps/web` 皜祈岫??lint ?函?
**??璅?**: ?啣遣蝡?閰勗獢???璈??舀???雿?桐蒂?芷嚗??垢皜祈岫/??瑼Ｘ蝬剜?????

## Phase 72: Open-Source ?澈皜???憭?鈭?朣?- [x] 蝘駁隤文摨急摮翰??`temp_commit_page.html`嚗銝?閬??Ｚ???
- [x] `.gitignore` 鋆? `temp_commit_page.html`嚗??甈∟炊?漱
- [x] 撠?隞嗡葉??`file:///c:/...` ?祆?蝯?????寧 repo ?詨????
- [x] README ?啣? `Lingua-Animus Protocol (LAP)` ?憛?撠?瘝餌???
- [x] 靽格迤 `docs/status/monthly_consolidation_report.json` ??`project_root` 鈭Ⅳ摮葡
**??璅?**: ?澈?⊥?憿航?翰?扳情??隞園???臬 GitHub ?湔???敹祥??鈭? README 銝?氬?蝣澆霈?批?憿??

## Phase 71: Session 蝝??祟?賂?Memories / Audit Logs嚗?- [x] `/api/memories` ?舀 `session_id` query嚗???payload ??`session_id`
- [x] `/api/audit-logs` ?舀 `session_id` query嚗蒂靽? `conversation_id` ?芸?嚗?- [x] `SupabasePersistence` ?啣? session filter嚗list_memories(..., session_id)`?list_audit_logs(..., session_id)`
- [x] ?辣?郊嚗docs/API_SPEC.md`嚗?- [x] ?飛皜祈岫?游???
**??璅?**: 蝞∠?霈???session 蝭?嚗?銝憯??conversation ??閰Ｚ??箝?
## Phase 70: Read Auth ?舀?雿扯? Session 蝭拚
- [x] Playground ?啣? Read Token 蝞∠?嚗摮?皜/localStorage嚗?- [x] `/api/conversations` ?啣? `session_id` 蝭拚嚗erver + Supabase adapter嚗?- [x] API/撽?辣撠?嚗session_id` query?--read-token` 雿輻?孵?嚗?- [x] 鋆?敺垢皜祈岫嚗ession filter 頧??Supabase ?亥岷?蕪嚗?**??璅?**: ?霈??token 敺?Playground ?舀?蝥?雿?銝?閰勗?銵典??session ??撠??炎閬?
## Phase 69: 敺垢摰????閮??堆?Stepwise嚗?- [x] 霈?楝?望?甈?霅瘀?`/api/conversations*`?/api/audit-logs`?/api/memories`
- [x] `prior_tension` 瘜典嚗/api/chat` 霈??餈?撘萄?撖抵?銝血??pipeline/council context
- [x] ?辣撠?嚗耨甇?tri-persona 閮瑼楝敺?蝘餉? API ??憟?隤芣?
- [x] ?飛皜祈岫嚗憓?甈?閮?葫閰佗??Ｘ? persistence 皜祈岫蝬剜??函?
**??璅?**: 敺垢??霈?楝?勗?扼?摰??園???撠???嚗?皜祈岫?舫??暸???
## Phase 68: Backend Persistence 撽??蝣潭??- [x] 靽桀儔 `apps/api/server.py` 鈭Ⅳ摮葡?酉閫??銝衣雁??API 銵銝?
- [x] ?神 `docs/plans/backend_persistent_storage_plan.md`嚗TF-8 ?航???
- [x] ?啣? `scripts/verify_backend_persistence.py` 銝?菟??嗉??- [x] ?啣? `docs/plans/backend_persistence_acceptance_checklist.md` ??/?芸?撽皜
- [x] ??? `run_repo_healthcheck --allow-missing-discussion`嚗overall_ok=true`嚗?**??璅?**: Task C 撽瘚??舫??整?蝡舐鈭Ⅳ?餃??擃摨瑟炎?交敺拍???
## Phase 64: Marketing / Docs 閬死?游?嚗howcase ??Next.js嚗?- [x] 撠?`apps/showcase/` 頧 Next.js 頝舐嚗摰?`/showcase`嚗?靽??恐閮 / 7D / 霅唳? / ????閮瑽?- [x] `/docs` 憓? section anchors + 蝵桅?撠汗嚗?湔頝唾???Paradoxes / Protocols / 7D / Research嚗?**??璅?**: `/showcase` ??`/docs` ?甇?虜 SSR/CSR?apps/web` build/lint/test ?函?嚗?銝蔣??`/` App ???
## Phase 65: Docs ?蝯曹?嚗?蝛箄? + 憭拍征??+ ?蝝?
- [x] `/docs` ?隤踵?箸楛??蝛箇頂嚗#0a0e27`嚗蒂蝯曹?雿輻 sky/rose 雿銝餃撥隤輯
- [x] 撠? `SevenParadoxCards` / `SevenDimensionCards` ?蝟餉??航??改?靽格迤?Ｘ?鈭Ⅳ??嚗?**??璅?**: `/docs` 閬死銝?氬?摮霈??＊ layout shift嚗? build/lint/test ?函???
## Phase 66: Research Foundation ?嗆?嚗?撥?賊?嚗?- [x] 蝎曄陛 `/docs` ??Research Foundation 皜嚗靽???ToneSoul ?詨?璈?湔?賊?????**??璅?**: Research ?憛?銝璇?賢?蝑??舀? ToneSoul ?銝?擃??嗚?
## Phase 67: 蝘犖????/ Notes嚗?撠?函?嚗?- [x] ?啣? `/notes`嚗撠?蝣潔?霅瘀?嚗?閮凋?蝝 sitemap嚗obots 蝳迫蝝Ｗ?
- [x] Notes ?脣?嚗??⊥璈摮?嚗?靘???臬隞仿?璈?摰?**??璅?**: 瘝?撖Ⅳ?⊥??湔?汗?批捆嚗??唳??銝仃嚗?典???臬?遢??
## Phase 63: UnifiedCore 蝯??楚瑼ｇ?Step 1嚗?- [x] `tonesoul/unified_core.py` 撠?`process()` ???箇???甇仿?嚗ersona 閫???撐??蝞僕???鋆?
- [x] ??蝯??航??改?撟脤??拚??閮剖??詨虜?詨?嚗?靽?憭?憟?銝?
- [x] 鋆? `tests/test_unified_core.py`?tests/test_unified_core_properties.py` 撽??∪?甇?**??璅?**: UnifiedCore 蝚砌?頛芰?瑽?摰?嚗葫閰血蝬?銝?霈?Ｘ?銵??
## Phase 47: ?嗆?銵嚗0 / P1 / P2嚗?
### P0嚗????餃?鈭支?嚗?- [x] 皜 lint/format drift嚗uff + black --check ?函?嚗?- [x] scripts/run_repo_healthcheck.py --allow-missing-discussion ? overall_ok=true
- [x] root npm test ?臬銵?撠? python -m pytest tests/ -q嚗?- [x] live SDH 蝡臬蝡臬?嚗cripts/run_7d_isolated.py + --include-sdh pass嚗?- [x] ?啣? ConnectionResetError ?????飛皜祈岫嚗ests/test_run_7d_isolated.py嚗?**??璅?**: ?餃??批?鞈芷?瑼餅敺拙??函?嚗? SDH live smoke ???霅???
### P1嚗?望????蝬剛風憸券嚗?- [x] 瘙箄降 commit attribution 蝑嚗?瑼Ｘ HEAD / 瑼Ｘ N 蝑風??/ ??PR 憓?嚗?- [x] 撠?attribution 瘙箇??賢??CI嚗arning ??blocking 銝?游?嚗?- [x] apps/showcase/ 餈質馱蝑????急 .gitignore嚗?極雿邦?芷嚗?**??璅?**: 甇詨惇閬??銝?臬銵??伐?CI 銵???????氬?
### P2嚗撱嗅?嚗??澈銋暹楊嚗?- [x] 閬? Git object hygiene 摰?蝑嚗ount-objects / fsck 靘?瑼Ｘ嚗?- [x] 撠?梯??神?亦雁??隞塚??踹??活獢?游撐?? drift嚗?**??璅?**: ??隞嗅???銵?擗?憟?銝?憓??亙虜鈭支?鞎???
## Phase 48: Healthcheck ? Git Hygiene ?嗆?
- [x] 撠?`scripts/verify_git_hygiene.py` 蝝 `scripts/run_repo_healthcheck.py` ?身瑼Ｘ皜
- [x] ?游? `tests/test_run_repo_healthcheck.py`嚗?摰?git hygiene 瑼Ｘ摮
- [x] ?湔 `docs/status/README.md`嚗?朣摨瑟炎?亥?????**??璅?**: 銝?萄摨瑟炎?亙??閬?蝔??釭??git object-store ?亙熒摨佗?銝?隞嗉?皜祈岫憟?銝?氬?
## Phase 49: SDH 憭望??航?皜祆找耨鋆?- [x] 靽格迤 `scripts/verify_7d.py` ??SDH 憭望???憿舐內 stdout ?航炊??嚗tderr ?箇征??
- [x] ?啣? `tests/test_verify_7d.py` ?飛皜祈岫嚗??SDH 憭望? note ?活蝛箇
**??璅?**: `verify_7d` ??SDH 憭望? note ?臬??怠霈?航炊蝺揣嚗撠???皞?stderr ??stdout嚗?
## Phase 50: 閮?? Lessons 璅⊥??- [x] ?啣? `LESSONS_V1` 璅?甈??澆?嚗ummary/missed/causes/corrections/guardrails/evidence/signature嚗?- [x] ?啣? `tools/agent_discussion_tool.py append-lessons`嚗摰芋?踹神?交?蝔?- [x] 鋆??澆???CLI 撖怠皜祈岫嚗Ⅱ靽芋?輯撓?箔???**??璅?**: ?舐?桐??誘撠???飛蝝神???湔芋?選?銝衣皜祈岫??甈?蝯???
## Phase 51: Healthcheck SDH 蝡舫??舫?蝵桀?
- [x] `scripts/run_repo_healthcheck.py` ?啣? `--web-base/--api-base/--sdh-timeout` 銝西??喟策 `verify_7d`
- [x] ?游? `tests/test_run_repo_healthcheck.py`嚗?摰?SDH 蝡舫???timeout ???喲?
- [x] ?湔 `docs/status/README.md`嚗?靘??Ｙ垢??銵?靘?**??璅?**: healthcheck ??`--include-sdh` 璅∪??舫＊撘?摰?web/api 蝡舫???timeout嚗?摰?鞈?3000/5000??
## Phase 52: Repo Healthcheck CI ??頛詨?嗆?
- [x] `.github/workflows/repo_healthcheck.yml` ?啣? `workflow_dispatch` SDH ?嚗nclude_sdh/web_base/api_base/sdh_timeout/check_council_modes嚗?- [x] 靽? push/PR ?身頝臬?銝?嚗??孛?潭?????SDH ?
- [x] ?湔 `docs/status/README.md` 隤芣? manual dispatch ?舐頛詨
**??璅?**: CI ??閫貊?舐???SDH smoke嚗?銝蔣?踵??push/PR blocking 瘚???
## Phase 53: Repo Healthcheck Dispatch ?撽?
- [x] workflow_dispatch ?啣? `sdh_timeout` 甇??賊?霅????喲??
- [x] `include_sdh=false` 雿?靘?SDH ????warning 銝血蕭?亥撓??- [x] `include_sdh=true` 銝????桅? `web_base/api_base` ???warning
- [x] ?湔 `docs/status/README.md` 閮?銝膩撽?銵
**??璅?**: ??閫貊頛詨?航炊?賢 CI ?亥??單??航?嚗??暺炊?扎?
## Phase 54: Dispatch 憟??芸?摰?
- [x] `scripts/verify_docs_consistency.py` ?啣? repo healthcheck dispatch 憟?瑼Ｘ嚗nputs + validation + warning嚗?- [x] ?游? `tests/test_verify_docs_consistency.py` 閬? pass ??timeout-validation 蝻箏仃憭望?獢?
- [x] 靽? docs consistency gate ?舫??暸?
**??璅?**: repo healthcheck dispatch 閬?鋡?docs consistency gate ?箏?嚗?甇貉??湔??冽??CI 蝡憭望???
## Phase 55: Healthcheck ?楝敺銵?蝝?- [x] `verify_docs_consistency` 蝝 repo healthcheck ??push/pr default runner ??dispatch runner 瑼Ｘ
- [x] ?游? `tests/test_verify_docs_consistency.py`嚗憓撩憭?default runner ?仃??靘?- [x] 蝬剜? docs consistency ?皜砍蝬?**??璅?**: repo healthcheck ?璇銵楝敺??蝝??嚗???input 瑼Ｘ雿憭勗銵郊撽?
## Phase 56: Workflow 憟??函?皜祈岫
- [x] ?啣? `tests/test_workflow_contracts.py`嚗誑 YAML 閫??瑼Ｘ `repo_healthcheck.yml` dispatch inputs 憟?
- [x] ?啣??楝敺?runner 摮皜祈岫嚗ush/pr default + workflow_dispatch嚗?- [x] ?啣? dispatch validation/warning ?摰?皜祈岫
**??璅?**: workflow 憟?銝??docs 摮葡瑼Ｘ嚗蒂?蝡葫閰血?飛??亙仃??
## Phase 57: Dispatch ?摩?單??- [x] ?啣? `scripts/run_repo_healthcheck_dispatch.sh`嚗??workflow_dispatch ??SDH ?斗??霅?頛?- [x] `.github/workflows/repo_healthcheck.yml` ?寧 env bridge + ?單???- [x] 隤踵 workflow/docs consistency 憟??葫閰佗?撽??寧瑼Ｘ?單 + workflow ??暺?**??璅?**: dispatch 閬??葉?澆銝?單嚗orkflow YAML 蝬剜?????憟?皜祈岫?舫?飛??
## Phase 58: Dispatch Python ??銵皜祈岫
- [x] ?啣? `scripts/run_repo_healthcheck_dispatch.py`嚗nv -> command 蝯? + validation/warning嚗?- [x] workflow dispatch ?寧?湔?澆 Python dispatch script
- [x] ?啣? `tests/test_run_repo_healthcheck_dispatch.py`嚗?摰?timeout/error?arning?lag 蝯?銵
- [x] docs consistency / workflow contracts ?郊撠??啗?祈楝敺?**??璅?**: dispatch 銵?臬?砍隞?Python ?格葫??嚗?雿?shell ?啣??訾????葫閰衣???
## Phase 59: Dispatch Shell Wrapper ???- [x] 蝘駁 `scripts/run_repo_healthcheck_dispatch.sh`嚗???亙蝬剛風?
- [x] 靽? workflow ?蝙??`python scripts/run_repo_healthcheck_dispatch.py`
- [x] 撽? docs consistency / workflow contracts ?∪?甇?**??璅?**: repo healthcheck dispatch ?亙?桐???皜?頝刻?閮?郊憸券?雁??喋?
## Phase 60: Docs Consistency 蝯??圾??Step 1嚗?- [x] `verify_docs_consistency` ??repo healthcheck workflow 憟??寧 YAML 蝯?閫??
- [x] ?啣???批?甇豢葫閰佗?token ???冽 notes/摮葡??敺??箏?蝝?蝡?
- [x] 蝬剜??Ｘ? report key ??issue ??嚗???冽祥??蝔憯?**??璅?**: repo healthcheck 憟?銝???摮葡??斗嚗蒂?賡??token-based false positive??
## Phase 61: Docs Consistency 蝯??圾??Step 2嚗?- [x] dispatch script 憟?瑼Ｘ?寧頛璅∠?銝阡?霅?`build_command` 銵
- [x] 皜祈岫 fixture ?寧 Python dispatch 璅∠?嚗??shell token ??
- [x] 蝬剜? report key ??仃???臭?霈???瘝餌?隞?游?
**??璅?**: dispatch 憟?銝??血??孵? log token 摮葡嚗隞亙?瑁?銵雿摰?靘???
## Phase 62: Docs Consistency 蝯??圾??Step 3嚗?- [x] `monthly_consolidation` 憟??寧 YAML 蝯?閫??嚗chedule + runner + allow flag嚗?- [x] `git_hygiene` 憟??寧 YAML 蝯?閫??嚗chedule + runner + artifact upload嚗?- [x] ?啣? monthly/git_hygiene token-in-notes ??批?甇豢葫閰?**??璅?**: monthly / git_hygiene 憟?銝???銝脩１撌批銝剛炊?日?嚗??亙?撌乩?瘚?蝯?銝??祕?蔭??
## Phase 17: ?嗅偏銝??- [x] README ?湔嚗???Council / Genesis / Memory / Tools API + 敹恍???
- [x] 閮蝮賜?嚗神??`memory/self_journal.jsonl`嚗 Phase 14-16 ??蝣潔耨敺抬?
- [x] 隤祕璈閮剛?嚗hase 18 ??嚗?獢?docs/HONESTY_MECHANISM.md嚗?**??璅?**: README 摰?湔?elf_journal ?蝝??撖行??嗆??航?隢?閮剛?????
## Phase 18: 隤祕璈閮剛?嚗?獢?
- [x] ??verdict 閮剛?? `uncertainty_level`
- [x] 摰儔??銝??甇??頛詨?澆?
- [x] ?皜祈岫/撽??孵?嚗??蝡撖虫?嚗?**??璅?**: ?Ｗ銝隞賢閰祟?身閮?獢??辣???潘?嚗?脣銝?頛芾?隢?
## Phase 19: 隤祕璈撖虫?
- [x] `CouncilVerdict` ?啣?銝Ⅱ摰扳?雿?- [x] `verdict` 蝯??撓?箏??乩?蝣箏???- [x] `CouncilRuntime` 靘?`responsibility_tier` 隤踵銝Ⅱ摰?- [x] 皜祈岫閬??箇?銝Ⅱ摰扯?蝞?**??璅?**: ?Ｗ?舫?銵?銝Ⅱ摰扳?雿?蝯??撓?綽?銝行??箇?皜祈岫??
## Phase 21: API 蝯曹???Runtime Drift 靽格迤
- [x] Flask 鋆? conversation/consent 憟?銝西? web 撠?
- [x] Next API routes ?寧 backend-first嚗allback ?? transport failure
- [x] 頝舐瘥活隢???閫?? `TONESOUL_BACKEND_URL`
- [x] `verify_web_api.py` + CI `web_api_smoke` 摰??湧? smoke嚗 `--require-backend`嚗?- [x] 撖抵??辣?湔嚗reports/api_unification_audit_2026-02-06.md`?reports/facade_runtime_audit_2026-02-06.md`嚗?**??璅?**: web/backend 憟??舫??暸?霅?銝?fallback 銝??株 backend ?啣虜??
## Phase 22: ?垢?游?嚗脰?銝哨?
- [x] ?啣? `docs/API_SPEC.md`嚗絞銝敺?API 閬嚗?- [x] 撽? `apps/web` dev ??? `localhost:5000`嚗??smoke嚗?- [x] 撽? ChatInterface -> backend -> Council 瘚?嚗/api/chat` ?湧? smoke嚗?- [x] 撽? SessionReport -> backend 瘚?嚗/api/session-report` ?湧? smoke嚗?- [x] ?湔 Vercel ?啣?霈?蝵脰牧??`docs/VERCEL_DEPLOY.md`嚗?撟喳憟嚗?**??璅?**: Navigator ?垢?冽?啗粥蝯曹? API 憟?嚗??函蔡閮剖??辣?舐?亙??典 Vercel??
## Phase 24: 7D ?賢嚗?獢?
- [x] ?神 `docs/7D_AUDIT_FRAMEWORK.md`嚗TF-8 ?航??嚗?- [x] ?啣? `docs/7D_EXECUTION_SPEC.md`嚗?D -> checklist -> gate嚗?- [x] ?啣? `scripts/verify_7d.py`嚗?D ???亙嚗?- [x] 撱箇? `tests/red_team/` ?撠??葫閰阡?嚗DD嚗?- [x] 瘙箄降 `SDH` ?雁??soft-fail嚗? blocking嚗?- [x] 閮剖? `DDD` 鞈??圈悅摨?SLA嚗? 憭?stale 閬?嚗?- [x] 閮剛? `systemic betrayal user confirmation gate`嚗??游??折◢?芷?鈭活蝣箄?嚗?- [x] 撠?RDD ?游???10+ 撠?獢?嚗??20嚗?**??璅?**: 銝雁???臬銵炎?伐?銝?gate 蝑??CI 撅文?Ⅱ閫????
## Phase 25: ?漲?游??芸????辣憟?撘瑕?
- [x] ?啣? `.github/workflows/monthly_consolidation.yml`嚗???蝔?+ ??閫貊嚗?- [x] `scripts/verify_docs_consistency.py` 蝝?漲 workflow 憟?瑼Ｘ
- [x] 靽格迤 docs threshold 甇???賢?嚗宏?支?蝣?pattern嚗蝛拙? `tests/cases` 閫??嚗?- [x] ?湔 `tests/test_verify_docs_consistency.py` 閬??漲 workflow 摮/蝻箏仃??
- [x] ?湔 `docs/status/README.md` 隤芣??芸???皞? artifact ?Ｗ
**??璅?**: `verify_docs_consistency` ??`run_monthly_consolidation --strict` ?舐帘摰?嚗? status 靘??瑕??芸???蝔?
## Phase 26: ?漲?游? CI ?舫??暹找耨鋆?- [x] `scripts/run_monthly_consolidation.py` ?啣? `--allow-missing-discussion` ?嚗I 銋暹楊?啣??舫??橘?
- [x] ?漲 workflow ?瑁??寧 `--strict --allow-missing-discussion`
- [x] `scripts/verify_docs_consistency.py` ?啣?瑼Ｘ?漲 workflow ?臬撣?`--allow-missing-discussion`
- [x] ?啣? `tests/test_run_monthly_consolidation.py`嚗?摰?memory hygiene ?賭誘??銵
- [x] ?游? `tests/test_verify_docs_consistency.py`嚗??撩憭望?璅????憓?- [x] ?湔 `docs/status/README.md` ? CI-friendly ?瑁?蝭?
**??璅?**: ?漲 workflow ?函 `memory/agent_discussion*.jsonl` ?嗾瘛?checkout 隞??憟?瑼Ｘ??炎?乓?
## Phase 27: Escape Valve V1嚗??函?嚗?- [x] ?啣? `tonesoul/escape_valve.py`嚗頝舀頝臬 + 銝Ⅱ摰扯撓?綽?
- [x] `CouncilRuntime` ?游? Escape Valve嚗???`BLOCK` 隤儔銝?
- [x] 蝘駁 runtime ?航???情??瘥活 deliberation 雿輻 request-local valve嚗?- [x] ?舀 `context.escape_valve_failures` 雿?岫甇瑕蝔桀?嚗???霅瘀?
- [x] 閫貊??擃?蝣箏??批 high 銝西蕭??`escape_valve_triggered=*` ?
- [x] ?啣? `tests/test_escape_valve.py` ??`tests/test_escape_valve_runtime.py`
**??璅?**: Escape Valve ?航◤皜祈岫閫貊銝?蝜? BLOCK嚗頝刻?瘙??情???Ｘ?撖抵?皜祈岫靽?????
## Phase 28: Escape Valve API 憟???- [x] ?湔 `docs/API_SPEC.md`嚗?蝣?`POST /api/validate` ??Escape Valve 頛詨/頛詨憟?
- [x] ?游? `tests/test_api_server_contract.py`嚗alidate ?箸憟? + seeded trigger + 頝刻?瘙?憭援嚗?**??璅?**: API 撅文? Escape Valve 銵嚗?憟??辣?葫閰虫??氬?
## Phase 29: Escape Valve ?脫翰?刻?閫皜砍撥??- [x] ?啣? seed trust 璈嚗escape_valve_seed_trusted`嚗? untrusted seed 敹賜蝑
- [x] API ?啣? `TONESOUL_ALLOW_ESCAPE_SEED` ??嚗?閮剜?蝯???seed嚗?- [x] API 撠?trusted seed ?頛詨銝?嚗???50嚗? runtime 雿輻銝?嚗???20嚗?- [x] transcript ?啣? `escape_valve_observability` ??
- [x] ?啣? red-team 皜祈岫嚗ntrusted seed ?⊥?撘瑕閫貊?rusted seed 銝???
**??璅?**: ?身憭頛詨?⊥?撘瑕 Escape Valve嚗?閫貊/敹賜頝臬??閫皜祆?璅?撠?皜祈岫閬???
## Phase 30: ???帘摰?嚗隞日＊蝷綽?
- [x] `scripts/verify_7d.py` ?賭誘頛詨?寧蝛拙?憿舐內嚗python ...`嚗?憓楝敺?蝣潘?
- [x] `scripts/run_monthly_consolidation.py` ?賭誘頛詨?寧蝛拙?憿舐內嚗python ...`嚗?- [x] 鋆??賭誘憿舐內甇????葫閰?- [x] ??? `docs/status/*.json` 銝阡?霅霈??**??璅?**: ?漲?勗?銝剔? `command` ??7D 蝯??賭誘甈??刻楊?啣?嚗??ASCII 頝臬?嚗?蝬剜??航??瘥???

## Phase 31: SDH 蝺函Ⅳ蝛拙??找耨敺抬?ToneBridge嚗?- [x] 靽桀儔 `tonesoul/tonebridge/commitment_extractor.py` ?函撩撠?`jieba` ?? cp950 蝺函Ⅳ撏拇蔑
- [x] ?啣? cp950 import ?飛皜祈岫嚗??甈∪? import-time 頛詨?? `UnicodeEncodeError`
- [x] 撽? `scripts/run_7d_isolated.py`嚗 SDH嚗?甇詨蝬?**??璅?**: ?函 `jieba` ?憓?銝??楊蝣潮隤文???`/api/session-report` 500嚗? 7D ??湧?嚗 SDH嚗??函???
## Phase 32: VTP ?撠??Council Runtime嚗?- [x] ?啣? `tonesoul/council/vtp.py`嚗tatus: continue/defer/terminate + confession payload嚗?- [x] `CouncilRuntime` ?游? VTP 閰摯嚗???`BLOCK` 隤儔銝行憓?`transcript.vtp`
- [x] ?啣? VTP ?桀???runtime 皜祈岫嚗tests/test_vtp.py`, `tests/test_vtp_runtime.py`嚗?- [x] ?游? API ??皜祈岫??隞塚?`tests/test_api_server_contract.py`, `docs/API_SPEC.md`嚗?**??璅?**: VTP 閫貊/撱園/蝯迫銝車???望葫閰阡??橘?銝血 API ??銝剖閫皜研?

## Phase 33: VTP 蝝??脫翰?券?霅?- [x] ?啣? `tests/red_team/test_vtp_context_abuse.py`
- [x] 撽??芯縑隞?API payload ?⊥?撘瑕 VTP defer/terminate
- [x] 撽??賡??渡?甇?payload 隞◤ trust gate 敹賜
**??璅?**: 憭?芣?甈?瘙瘜 VTP flags 撘瑕?脣蝯迫瘚?嚗?銵?葫閰西???

## Phase 34: 憭誨??鈭斗飛撅祈?蝭?- [x] ?啣? `scripts/verify_commit_attribution.py`嚗炎??`Agent` / `Trace-Topic` trailers嚗?- [x] ?啣? `tests/test_verify_commit_attribution.py`
- [x] ?湔 `CONTRIBUTING.md` ?漱甇詨惇?澆???霅?隞?**??璅?**: ?曹澈雿澈隞賭?嚗ommit message ?賡?撣嗡誨??霅圈?靘?嚗?雿楊隞??鞎砌遙甇詨惇甇抒儔??

## Phase 35: CI ?航??扳??Commit Attribution嚗?- [x] `ToneSoul CI` ?啣? `commit_attribution` job
- [x] 瘥活 push ?芸?頛詨 HEAD attribution 閫??蝯?
- [x] 蝻箏仃 trailers ?誑 warning ?嚗??餅 CI嚗?**??璅?**: 甇詨惇鞈??臬 CI ?亥??湔餈質馱嚗?銝蔣?輻?漱隞?憟?

## Phase 36: Vercel 頛詨?啣虜靽株?嚗hat Route嚗?- [x] ?蝺??啣虜嚗tonesoul52.vercel.app/api/chat` ??`backend_mode=mock_fallback`嚗?- [x] `apps/web/src/app/api/chat/route.ts` ?寧?身蝳 transport mock fallback嚗?憿臬? `TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=1`嚗?- [x] ?啣? Vercel ?脣?嚗 `TONESOUL_BACKEND_URL` 蝻箏仃????localhost嚗?亙? `503` ?蔭?航炊
- [x] ?啣?皜祈岫 `apps/web/src/__tests__/apiRoutes.chatTransport.test.ts`嚗isabled fallback / explicit fallback / vercel misconfig嚗?- [x] ?湔 `docs/API_SPEC.md` ??`docs/VERCEL_DEPLOY.md` ??fallback 憟??蝵脰???**??璅?**: production 銝???蝡臬仃?航?暺? mock ?批捆嚗ercel ?蔭?航炊?臬??莎?銝?web build+tests ?券???
## Phase 37: ?典澈?亙熒瑼Ｘ??閫暺??- [x] 靽桀儔 `scripts/` ?Ｗ? lint/format ?萄?嚗analyze_journal.py`, `build_semantic_index.py` + black ?澆???
- [x] ?典??釭瑼Ｘ嚗ruff/black/pytest/web lint+test`嚗?頝蒂蝣箄??函?
- [x] ?? `verify_7d --include-sdh` 銝西?頝?live-service `verify_web_api` 撽? SDH 頝臬?
- [x] ?湔 `REPO_CONSOLIDATION.md`嚗極蝔??脣飛/?曉祕/AI 憭?摨血祟閮?+ 擃?CP 頝舐?嚗?**??璅?**: ?單撅文?鞈芸??蝛箝?D ?餅蝬剖漲蝬剜? 0 憭望?嚗??游?撖抵??辣????啣??蝯???
## Phase 38: 銝?萄摨瑟炎?亥? CI ?航???- [x] ?啣? `scripts/run_repo_healthcheck.py`嚗??ruff/black/pytest/web lint+test/verify_7d嚗?- [x] 頛詨 `docs/status/repo_healthcheck_latest.json` + `docs/status/repo_healthcheck_latest.md`
- [x] ?啣? `tests/test_run_repo_healthcheck.py`嚗隞斗?撱箝kip 璇辣?arkdown 頛詨嚗?- [x] ?啣? `.github/workflows/repo_healthcheck.yml`嚗locking + artifact upload嚗?- [x] ?湔 `docs/status/README.md` ??抵牧???瑁??孵?
**??璅?**: ?砍?臭??萄?敺摨瑟炎?亙翰?改?CI ?臭??喳霈/?舀??刻圾??artifact嚗?蝻?discussion 瑼??舐 `--allow-missing-discussion` 韏?CI-friendly 頝臬???

## Phase 39: Vercel Preflight Guard
- [x] ?啣? `scripts/verify_vercel_preflight.py`嚗ackend URL?allback policy???health probe嚗?- [x] ?啣? `tests/test_verify_vercel_preflight.py`嚗RL/fallback/health probe ?斗嚗?- [x] ?啣? `.github/workflows/vercel_preflight.yml`嚗workflow_dispatch` ?? preflight嚗?- [x] ?湔 `docs/VERCEL_DEPLOY.md` ??`docs/API_SPEC.md` ??preflight ?誘
**??璅?**: ?函蔡??典銝?誘?餅?擃◢?芷?蝵殷?localhost backend?ock fallback ???eport provider fallback ?芷???嚗蒂?臬?閬??? `/api/health` ??炎?乓?

## Phase 40: Multi-Model Council Runtime Wiring
- [x] `CouncilRuntime` ?冽憿臬??喳閬??蔭???`get_council_config()`
- [x] ?啣? `TONESOUL_COUNCIL_MODE` ?啣?霈嚗??`rules | hybrid | full_llm`嚗?閮?`hybrid`嚗?- [x] `model_registry` ?舀 `rules` ?亙?銝虫???`rules_only` ?詨捆
- [x] ?啣? runtime/model registry 皜祈岫閬?嚗?閮准lias?nvalid fallback?equest override嚗?**??璅?**: 敺垢?舫??啣?霈?? council 璅∪?嚗?憿臬? request 閮剖??芸?蝝??潛憓??賂?銵?葫閰虫?霅瑯?

## Phase 41: 閮?????摰?折??- [x] `memory/agent_discussion.py` ?啣????啣虜?菜葫嚗replacement_char` / `private_use_char`嚗?- [x] curated stream ?蕪?啣虜閮嚗???raw 甇瑕雿?情??券霈瘚?- [x] `scripts/verify_memory_hygiene.py` ?啣? `text_anomalies` 瑼Ｘ銝衣???blocking gate
- [x] 鋆??飛皜祈岫嚗tests/test_agent_discussion.py`, `tests/test_verify_memory_hygiene.py`嚗?**??璅?**: 閮?瑼蝬剜? JSON 蝯? + ???航??折???蝝?銝??蝣潸??臭??脣 curated 閮瘚?

## Phase 42: Council 璅∪??垢?臬???- [x] `/api/chat` ?舀 `council_mode` ??`perspective_config`嚗頛詨撽?嚗?- [x] `UnifiedPipeline.process(...)` 銝脫 council mode override ??`CouncilRequest.perspective_config`
- [x] ChatInterface ?啣? backend chat ??council mode 銝??詨銝血葆?亥?瘙?- [x] 鋆? API ???????交毽瘛葫閰佗??湔 `docs/API_SPEC.md`
**??璅?**: 雿輻??典?蝡臬???`rules/hybrid/full_llm` 銝阡? `/api/chat` ??嚗?銝?瘜撓?交?鋡?API ?Ⅱ?餅???

## Phase 43: Web Chat Route 憟??脣?
- [x] `apps/web/src/app/api/chat/route.ts` ?啣? `council_mode` / `perspective_config` ?撽???alias 甇????- [x] 皜? route 銝剜??蝣澆?瑕?銝莎?蝯曹??箏蝬剛風??憿????文?
- [x] 鋆? route 皜祈岫嚗nvalid payload ?餅? + `rules_only -> rules` 頧?嚗?**??璅?**: Next route ?券脣 backend ???⊥? payload嚗? council mode 頧?銵?葫閰阡?摰?

## Phase 44: Council Mode ???? E2E Smoke
- [x] ChatInterface `council_mode` ?豢?????localStorage嚗?- [x] CouncilRuntime transcript ?啣? `council_mode_observability`
- [x] `scripts/verify_web_api.py` ?啣? `--check-council-modes`嚗?霅?mode ????嚗?- [x] 鋆?皜祈岫嚗untime / verify_web_api helpers嚗?**??璅?**: ??敺??蝙?刻?council mode嚗??舐?桐? smoke ?誘撽? web->backend mode ????皜祆?雿?

## Phase 45: SDH ?芸???蝝?Mode Switch Gate嚗?- [x] `scripts/verify_7d.py` ??SDH 瑼Ｘ?身? `--check-council-modes`
- [x] CI `web_api_smoke` ?寧撘瑕撽? council mode ??
- [x] 鋆? `tests/test_verify_7d.py`嚗?摰?SDH ?賭誘??
- [x] ?湔 7D / API ?辣銝剔? smoke ?誘
**??璅?**: `include-sdh` ??CI smoke ?賣?撽? mode switch嚗??撽??箸???

## Phase 46: Healthcheck ??SDH ??撠?
- [x] `run_repo_healthcheck.py` ?啣? `--[no-]check-council-modes` 銝血? `verify_7d`
- [x] `verify_7d.py` ?啣? `--[no-]check-council-modes`嚗?閮剖??剁?
- [x] 鋆? `tests/test_run_repo_healthcheck.py` / `tests/test_verify_7d.py` ??皜祈岫
- [x] ?湔 `docs/status/README.md` ??live SDH ?瑁?蝭?
**??璅?**: healthcheck ?舫＊撘???mode-switch smoke嚗??身銵蝬剜??銝行?皜祈岫靽風??

## 撌脣?????嚗?- [x] Phase 1-2: Council 閮剛????- [x] Phase 3/10/16: Tools API schema + ToolResponse 璅???- [x] Phase 4/6/8/15: Memory wiring / SQLite / Observer
- [x] Phase 11-13: Demo API Server + Playground + run_demo
- [x] Phase 14: Genesis Intent + is_mine
- [x] ??撠銵刻???摰??辣
- [x] 鈭Ⅳ皜???UTF-8 蝯曹?
**??*: `CODEX_TASK.md`, `memory/handoff/2026-02-06_phase16_tools_progress.md`

## Phase 48: Ollama ??Key Fallback ?嗆?
- [x] `SettingsModal`嚗llama 憿舐內??API Key ?詨‵嚗耨甇?Test Info 憿舐內璇辣
- [x] `ChatInterface`嚗 `isApiKeyRequired` 憟?內??fallback ???斗嚗??Ollama 鋡怨炊?斤撩 key
- [x] ?啣? `apps/web/src/__tests__/settingsModal.test.ts`嚗?摰?provider key requirement 閬?
- [x] 撽嚗npm --prefix apps/web test`?npm --prefix apps/web run lint`?npm --prefix apps/web run build` ?冽??
**??璅?**: Ollama ?函 API Key 銝甇?虜雿 fallback provider嚗? UI 銝?憿舐內?航炊 API Key 霅衣內??



## Phase 107: Same-Origin Backend Recovery + Ollama MVP Gate
- [x] Added same-origin backend prefix routing in web API config (`/api/_backend`) to avoid Vercel self-recursion.
- [x] Added Python same-origin backend alias endpoints under `apps/web/api/_backend/**` with prefix-strip WSGI middleware.
- [x] Added missing web API routes: `/api/health`, `/api/conversations`, `/api/conversations/[id]`.
- [x] Updated Vercel-route tests for same-origin behavior (`apiRoutes.chatTransport`, `apiRoutes.transportFallback`, `apiRoutes.backendHealth`).
- [x] Updated preflight logic to support same-origin mode (`scripts/verify_vercel_preflight.py --same-origin`) with tests.
- [x] Added `scripts/verify_ollama_mvp.py` to validate model list, handshake, low/high tension routing, and regression gate.
- [x] Synced semantic-control implementation status in `spec/wfgy_semantic_control_spec.md` (Phase 1/2/3 + P0/P1/P2 all checked).
- [x] Synced derivation roadmap status in `spec/tonesoul_improvement_derivation.md` (Phase A/B/C + P0/P1/P2 all checked; CorrectionMemory marked simplified implementation).
- [x] Validation:
- [x] `npm --prefix apps/web run test -- src/__tests__/apiRoutes.chatTransport.test.ts src/__tests__/apiRoutes.transportFallback.test.ts src/__tests__/apiRoutes.backendHealth.test.ts`
- [x] `npm --prefix apps/web run build`
- [x] `pytest tests/test_verify_vercel_preflight.py -q`
- [x] `python scripts/verify_ollama_mvp.py --run-regression`
**成功標準**: Vercel same-origin backend path is code-complete (pending deploy verification), and Ollama MVP release checklist is executable + passing via one command.

## Phase 108: Elisa x ToneSoul Governance Integration Blueprint (2026-02-22)
- [x] Published integration blueprint: `docs/plans/elisa_tonesoul_governance_integration_2026-02-22.md`
- [x] Completed swarm multi-persona analysis (architecture/security/IDE UX/delivery) and merged into one execution plan.
- [x] Defined integration boundary using existing governance APIs (`/api/chat`, `/api/consent`, `/api/session-report`, `/api/backend-health`) with `council_mode` and `perspective_config`.
- [x] Defined fail-closed governance controls (preflight, policy gate, consent gate, audit trail) for Elisa IDE integration.
- [x] P0 implementation: Elisa payload profile + route contract tests + `verify_web_api.py` integration scenario.
- [x] P1 implementation: preflight Elisa checks + governance status surface.
- [x] P2 implementation: CI blocking smoke for Elisa integration contract.
- [x] P3 implementation: operational hardening (runbook/rollback/release checklist).
**Success Criteria**: A reproducible P0-P3 execution path exists with blocking CI gates and same-origin governance behavior preserved.

## Phase 109: Council Divergence Quality Baseline (2026-02-22)
- [x] Upgraded `build_divergence_analysis()` with structured quality metrics (score/band/conflict coverage/reasoning specificity/evidence coverage/confidence balance/role tension coverage).
- [x] Added role-level tension extraction (`role_tensions`) and decision distribution to prevent "fake disagreement" outputs.
- [x] Wired divergence quality into `/api/chat` deliberation payload (`deliberation.divergence_quality`) and improved chamber friction mapping using role tensions.
- [x] Added regression tests:
- [x] `tests/test_council_divergence_quality.py`
- [x] `tests/test_api_chat_council_mode.py::test_chat_deliberation_exposes_divergence_quality`
**Success Criteria**: Three-role chamber output includes machine-checkable dissent quality signals and API contract remains stable.

## Phase 110: v1.0 Release Gate (RC -> GA) (2026-02-24)
- [x] Baseline stability evidence collected:
- [x] `python scripts/verify_7d.py --include-sdh --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --sync` (`OVERALL=100`)
- [x] `python scripts/verify_web_api.py --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --same-origin`
- [x] `npm --prefix apps/web run build`
- [x] GitHub Actions run set for `fbbbbd1` is fully green (CI/ToneSoul CI/Repo Healthcheck/Pytest/Semantic Health etc.).
- [x] Published release decision file: `docs/plans/release_v1.0_go_nogo_2026-02-24.md`
- [x] Version metadata aligned to release-candidate:
- [x] `package.json` -> `1.0.0-rc.1`
- [x] `apps/web/package.json` -> `1.0.0-rc.1`
- [x] `pyproject.toml` -> `1.0.0rc1`
- [x] GA blocker A: complete Phase 108 P0-P2 (Elisa contract + CI blocking smoke).
- [x] GA blocker B: complete Phase 108 P3 (runbook + rollback + release checklist).
- [x] GA blocker C: produce `docs/RELEASE_NOTES_v1.0.0.md` and push tag `v1.0.0`.
**Success Criteria**: `v1.0.0` baseline is stable and traceable; GA release gates are fully closed.

## Phase 111: Post-Release Continuous Verification (2026-02-24)
- [x] Added global governance status polling and badge bar in `apps/web/src/components/ChatInterface.tsx`.
- [x] Strengthened Elisa payload boundary contract with `workspace.changed_files > 64` rejection test.
- [x] Added scheduled production monitor workflow: `.github/workflows/post_release_monitor.yml`.
- [x] Added workflow contract coverage for post-release monitor in `tests/test_workflow_contracts.py`.
- [x] Validation:
- [x] `npm --prefix apps/web run test -- src/__tests__/apiRoutes.invalidJson.test.ts`
- [x] `python -m pytest tests/test_workflow_contracts.py -q`
- [x] `npm --prefix apps/web run lint`
- [x] `npm --prefix apps/web run build`
- [x] `python scripts/verify_web_api.py --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --same-origin --elisa-scenario`
- [x] `python scripts/verify_vercel_preflight.py --strict --same-origin --probe-governance-status --web-base https://tonesoul52-ruby.vercel.app`
**Success Criteria**: Governance readiness is continuously visible in UI and continuously verified in CI/scheduled monitoring.

## Phase 112: Dual-Track Execution Profile Routing (2026-02-24)
- [x] Added `execution_profile` contract to web/backend chat routes (`interactive | engineering`).
- [x] Implemented profile inference:
- [x] explicit `execution_profile` wins
- [x] fallback inference: `elisa_context.source=elisa_ide -> engineering`
- [x] default: `interactive`
- [x] Implemented profile-driven default council routing when request does not specify mode/config:
- [x] `interactive -> council_mode=rules`
- [x] `engineering -> council_mode=full_llm`
- [x] Added/updated tests:
- [x] `apps/web/src/__tests__/apiRoutes.invalidJson.test.ts`
- [x] `apps/web/src/__tests__/apiRoutes.chatTransport.test.ts`
- [x] `tests/test_api_chat_council_mode.py`
- [x] `tests/red_team/test_api_type_confusion.py`
- [x] `tests/test_verify_web_api.py`
- [x] Updated API documentation: `docs/API_SPEC.md`.
- [x] Validation:
- [x] `npm --prefix apps/web run test -- src/__tests__/apiRoutes.invalidJson.test.ts src/__tests__/apiRoutes.chatTransport.test.ts`
- [x] `python -m pytest tests/test_api_chat_council_mode.py tests/red_team/test_api_type_confusion.py tests/test_verify_web_api.py -q`
**Success Criteria**: interactive/engineering profile is first-class in chat contract and deterministically maps to speed/quality defaults without breaking explicit overrides.

## Phase 113: Skill Contract Registry (2026-02-24)
- [x] Added `skills/registry.json` and `skills/registry.schema.json` as machine-readable skill metadata contract.
- [x] Added `scripts/verify_skill_registry.py` for registry/schema/frontmatter/hash/review-freshness validation.
- [x] Added regression tests in `tests/test_verify_skill_registry.py`.
- [x] Integrated skill-registry strict check into `scripts/run_repo_healthcheck.py`.
- [x] Synced docs references (`docs/status/README.md`, `docs/context_engineering_reference.md`).
**Success Criteria**: skill assets are enumerated, versioned, and integrity-verified in blocking governance checks.

## Phase 114: Skill Routing Precision + Prompt-Safety Gate (2026-02-24)
- [x] Strengthened `scripts/verify_skill_registry.py` with skill-id namespace guard (`claude` / `anthropic` reserved terms).
- [x] Added trigger quality checks (dedupe + prompt-markup ban + description trigger coverage).
- [x] Added frontmatter prompt-safety checks (`name` / `description` must not include `<` / `>`).
- [x] Added frontmatter description minimum length gate (`>= 40`) for routing precision.
- [x] Expanded regression tests in `tests/test_verify_skill_registry.py` for new fail-closed scenarios.
- [x] Validation:
- [x] `python -m pytest tests/test_verify_skill_registry.py -q`
- [x] `python -m ruff check scripts/verify_skill_registry.py tests/test_verify_skill_registry.py`
- [x] `python scripts/verify_skill_registry.py --strict`
**Success Criteria**: skill routing metadata is both integrity-checked and injection-hardened before entering blocking governance flow.

## Phase 115: Progressive-Disclosure Skill Contract (2026-02-24)
- [x] Added `tonesoul/council/skill_parser.py` with three-layer APIs:
- [x] `get_all_l1_routes()` (routing metadata only)
- [x] `get_l2_signature(skill_id)` (execution boundary/signature)
- [x] `get_l3_payload(skill_id)` (execution payload body)
- [x] Added `resolve_for_request(...)` flow enforcing `L1 match -> L2 profile/trust gate -> L3 load`.
- [x] Updated `tonesoul/council/runtime.py` dispatcher path to attach `skill_contract_observability` and inject bounded `skill_contract_guidance` only after L1/L2 pass.
- [x] Refactored skill registry contract to layered fields:
- [x] `skills/registry.schema.json`: added required `l1_routing` + `l2_signature`.
- [x] `skills/registry.json`: migrated existing skills from flat `name/triggers` to layered structure.
- [x] Migrated skill frontmatter:
- [x] `.agent/skills/local_llm/SKILL.md`
- [x] `.agent/skills/qa_auditor/SKILL.md`
- [x] Upgraded verifier `scripts/verify_skill_registry.py` to fail-closed on layered contract consistency (registry/frontmatter alignment, L1 trigger coverage, L2 profile+trust+schema checks).
- [x] Added/updated tests:
- [x] `tests/test_skill_parser.py`
- [x] `tests/test_verify_skill_registry.py`
- [x] `tests/test_council_runtime.py`
- [x] Validation:
- [x] `python -m ruff check tonesoul/council/skill_parser.py tonesoul/council/runtime.py scripts/verify_skill_registry.py tests/test_verify_skill_registry.py tests/test_skill_parser.py tests/test_council_runtime.py`
- [x] `python scripts/verify_skill_registry.py --strict`
- [x] `python -m pytest tests/test_skill_parser.py tests/test_verify_skill_registry.py tests/test_council_runtime.py tests/test_council_cli.py -q`
**Success Criteria**: skills now follow deterministic progressive disclosure with measurable L1 routing precision, explicit L2 boundary checks, and bounded L3 runtime loading.

## Phase 107: CI Cost-Tiering and Trigger Throttling (2026-02-28)
- [x] Define PR-light vs merge-medium execution policy in workflow triggers
- [x] Add concurrency cancel-in-progress to high-frequency workflows
- [x] Add path-based trigger filters to domain-specific workflows (semantic/persona/source/git)
- [x] Keep governance-required contracts intact (`push`/`pull_request` keys remain where required)
- [x] Re-run workflow contract checks after edits
**成功標準**: Workflow contracts與docs consistency檢查通過，PR事件的重複計算顯著下降，且不移除核心治理檢查。

## Phase 116: Philosophical Reflection Automation (2026-02-28)
- [x] Add machine-checkable philosophical reflection reporter (`scripts/run_philosophical_reflection_report.py`).
- [x] Define reflection/conflict/choice/tension signal metrics and `identity_choice_index`.
- [x] Emit status artifacts to `docs/status/philosophical_reflection_latest.{json,md}`.
- [x] Integrate strict philosophical reflection check into `scripts/run_repo_healthcheck.py`.
- [x] Extend workflow artifact upload in `.github/workflows/repo_healthcheck.yml`.
- [x] Add regression tests:
- [x] `tests/test_run_philosophical_reflection_report.py`
- [x] `tests/test_run_repo_healthcheck.py`
- [x] `tests/test_workflow_contracts.py`
- [x] Add engineering spec doc:
- [x] `docs/philosophy/philosophical_reflection_engineering_spec.md`
- [x] Update navigation/docs index:
- [x] `docs/philosophy/README.md`
- [x] Validation:
- [x] `python -m ruff check scripts/run_philosophical_reflection_report.py tests/test_run_philosophical_reflection_report.py scripts/run_repo_healthcheck.py tests/test_run_repo_healthcheck.py tests/test_workflow_contracts.py`
- [x] `python -m pytest tests/test_run_philosophical_reflection_report.py tests/test_run_repo_healthcheck.py tests/test_workflow_contracts.py -q`
**Success Criteria**: Philosophical reflection signals become first-class CI/governance artifacts and are reproducible from journal/discussion traces.

## Phase 117: Friction-Aware Routing + Adaptive Reflection Threshold (2026-02-28)
- [x] Add governance friction contract in `ComputeGate`:
- [x] `F = 0.45*Δt + 0.35*Δwave + 0.20*boundary_mismatch`
- [x] Support friction-driven council escalation in route evaluation.
- [x] Wire `UnifiedPipeline` pre-gate friction estimation from `prior_tension` + override-pressure signal.
- [x] Expose pre-gate tension/friction observability in dispatch trace.
- [x] Expand philosophical reflection tension extraction (`text_tension`, `t_ecs`, `delta_s_ecs`, etc.).
- [x] Add adaptive threshold mode (`adaptive_p85`) for low-scale historical tension distributions.
- [x] Add/update regression tests:
- [x] `tests/test_compute_gate.py`
- [x] `tests/test_pipeline_compute_gate.py`
- [x] `tests/test_run_philosophical_reflection_report.py`
- [x] Update engineering spec with friction + adaptive threshold formula.
**Success Criteria**: low-tension/high-friction requests can escalate to council with audit trace, and reflection report no longer collapses to zero high-tension events under low-scale corpora.

## Phase 118: Contract Freeze + Q2 Execution Kickoff (2026-02-28)
- [x] Add Q2 execution roadmap with dated phases and acceptance gates:
- [x] `docs/plans/roadmap_2026q2_memory_governance.md`
- [x] Introduce shared governance contract schema + example:
- [x] `spec/governance/memory_governance_contract_v1.schema.json`
- [x] `spec/governance/memory_governance_contract_v1.example.json`
- [x] Add machine-checkable contract validation runner:
- [x] `scripts/run_memory_governance_contract_check.py`
- [x] Add status artifacts:
- [x] `docs/status/memory_governance_contract_latest.{json,md}`
- [x] Integrate contract check into repo healthcheck:
- [x] `scripts/run_repo_healthcheck.py`
- [x] Update healthcheck workflow artifact upload + contract tests:
- [x] `.github/workflows/repo_healthcheck.yml`
- [x] `tests/test_workflow_contracts.py`
- [x] Add/extend regression tests:
- [x] `tests/test_run_memory_governance_contract_check.py`
- [x] `tests/test_run_repo_healthcheck.py`
- [x] Cross-repo field mapping document (`tonesoul52` <-> `OpenClaw-Memory`) with migration notes.
- [x] Shadow-vs-active friction routing calibration report.
**Success Criteria**: contract files are enforced by CI/healthcheck, and Q2 roadmap has concrete deliverables with measurable acceptance thresholds.

## Phase 119: Friction Replay Pipeline + Continuous Calibration (2026-02-28)
- [x] Add real replay exporter from memory traces:
- [x] `scripts/run_friction_shadow_replay_export.py`
- [x] Emit replay trace + status artifacts:
- [x] `memory/narrative/friction_shadow_eval.jsonl` (runtime generated, gitignored)
- [x] `docs/status/friction_shadow_replay_latest.{json,md}`
- [x] Integrate replay export into repo healthcheck before calibration:
- [x] `scripts/run_repo_healthcheck.py`
- [x] Update healthcheck workflow artifacts and contract tests:
- [x] `.github/workflows/repo_healthcheck.yml`
- [x] `tests/test_workflow_contracts.py`
- [x] Add dedicated CI workflow for periodic replay+calibration:
- [x] `.github/workflows/friction_shadow_calibration.yml`
- [x] Add/extend regression tests:
- [x] `tests/test_run_friction_shadow_replay_export.py`
- [x] `tests/test_run_repo_healthcheck.py`
- [x] `tests/test_workflow_contracts.py`
- [x] Update status docs:
- [x] `docs/status/README.md`
**Success Criteria**: replay inputs are reproducibly exported from real traces, calibration runs on those inputs in CI, and trend artifacts are continuously available for threshold tuning.

## Phase 120: Replay Drift Guardrail (2026-02-28)
- [x] Extend replay exporter with previous-snapshot drift analysis:
- [x] `scripts/run_friction_shadow_replay_export.py`
- [x] Add strict drift thresholds:
- [x] `max_avg_tension_drift`
- [x] `max_avg_friction_drift`
- [x] `max_high_friction_rate_drift`
- [x] `min_scenario_count_ratio`
- [x] Add drift summary into replay markdown artifact (`docs/status/friction_shadow_replay_latest.md`)
- [x] Add regression tests:
- [x] `tests/test_run_friction_shadow_replay_export.py`
- [x] Sync status docs:
- [x] `docs/status/README.md`
**Success Criteria**: replay export can fail-closed on abnormal distribution drift while keeping baseline runs green.

## Phase 121: Pragmatic Memory Topology Fit (2026-02-28)
- [x] Add machine-checkable topology recommendation report:
- [x] `scripts/run_memory_topology_fit_report.py`
- [x] Encode pragmatic decision dimensions:
- [x] governance need score (`friction`, unresolved topics, identity-choice stability)
- [x] resource budget score (`max_vram_gb`, `max_latency_ms`, profile)
- [x] candidate topology ranking (`flat` / `planar` / `hierarchical`)
- [x] Emit status artifacts:
- [x] `docs/status/memory_topology_fit_latest.{json,md}`
- [x] Integrate strict check into repo healthcheck:
- [x] `scripts/run_repo_healthcheck.py`
- [x] Update healthcheck workflow artifact upload + contract tests:
- [x] `.github/workflows/repo_healthcheck.yml`
- [x] `tests/test_workflow_contracts.py`
- [x] Add regression tests:
- [x] `tests/test_run_memory_topology_fit_report.py`
- [x] `tests/test_run_repo_healthcheck.py`
- [x] Sync status docs:
- [x] `docs/status/README.md`
**Success Criteria**: topology selection becomes reproducible and auditable under real governance signals, not metaphor-only preference.

## Phase 138: Incremental Commit Attribution Parity (2026-03-08)
- [x] Extract GitHub Actions incremental commit-attribution logic into shared `scripts/verify_incremental_commit_attribution.py`
- [x] Replace inline commit-range logic in `.github/workflows/test.yml` with the shared script
- [x] Add blocking local parity check to `scripts/run_repo_healthcheck.py`
- [x] Add regression tests:
- [x] `tests/test_verify_incremental_commit_attribution.py`
- [x] `tests/test_run_repo_healthcheck.py`
- [x] Document local parity commands in:
- [x] `docs/governance/COMMUNICATION_STANDARD.md`
- [x] `docs/status/README.md`
- [x] Validation:
- [x] `python -m ruff check scripts/verify_incremental_commit_attribution.py tests/test_verify_incremental_commit_attribution.py scripts/run_repo_healthcheck.py tests/test_run_repo_healthcheck.py`
- [x] `python -m black --check scripts/verify_incremental_commit_attribution.py tests/test_verify_incremental_commit_attribution.py scripts/run_repo_healthcheck.py tests/test_run_repo_healthcheck.py`
- [x] `python -m pytest tests/test_verify_incremental_commit_attribution.py tests/test_run_repo_healthcheck.py -q`
- [x] `python -m pytest tests -q`
- [x] Runtime check:
- [x] `python scripts/verify_incremental_commit_attribution.py --artifact-path docs/status/commit_attribution_local.json`
- [x] Current local incremental range (`origin/master..HEAD`) reports `missing_count=5`, so historical trailer debt is now visible before push instead of only inside GitHub Actions logs
**Success Criteria**: commit-attribution failures are reproducible locally with the same revision-range semantics as CI, and the report preserves per-revision context instead of failing as opaque workflow glue.

## Phase 139: Isolated Commit Trailer Debt Backfill (2026-03-08)
- [x] Confirm the historical debt scope: `origin/master..feat/env-perception` contains 5 commits missing `Agent` / `Trace-Topic`
- [x] Avoid rewriting the current dirty worktree branch in place
- [x] Use `git worktree` isolation to build a clean remediation branch from `origin/master`
- [x] Replay the 5 commits with backfilled attribution trailers onto `feat/env-perception-attribution-backfill`
- [x] Validate the new branch with incremental attribution report:
- [x] `docs/status/commit_attribution_backfill_branch.json`
- [x] Validate content equivalence by comparing tree hashes:
- [x] rewritten head tree = original `c225332^{tree}`
- [x] Remove the temporary worktree after verification, leaving only the remediation branch and evidence artifact
**Success Criteria**: trailer debt is cleared on a reviewable side branch without mutating the user's dirty working tree, and verification proves the rewrite changed commit metadata rather than repository content.

## Phase 140: Schema-Driven Council LLM Parsing (2026-03-08)
- [x] Inspect the gifted `tonesoul/schemas.py`, `tonesoul/safe_parse.py`, and `tonesoul/observability/` seams before changing runtime paths
- [x] Add a minimal `PerspectiveEvaluationResult` schema for council perspective LLM output
- [x] Replace manual JSON parsing in `tonesoul/council/perspective_factory.py` with `safe_parse.parse_llm_response()`
- [x] Keep a bounded text heuristic fallback for non-JSON model responses so existing local/cloud model behavior does not regress
- [x] Reuse the same parse seam for both Gemini and Ollama perspective evaluators
- [x] Add regression tests for:
- [x] schema normalization of uppercase decision values
- [x] markdown JSON parsing through `LLMPerspective`
- [x] non-JSON text fallback preservation
- [x] adjacent custom-role council compatibility
- [x] Validation:
- [x] `python -m ruff check tonesoul/schemas.py tonesoul/council/perspective_factory.py tests/test_schemas.py tests/test_perspective_factory.py`
- [x] `python -m black --check tonesoul/schemas.py tonesoul/council/perspective_factory.py tests/test_schemas.py tests/test_perspective_factory.py`
- [x] `python -m pytest tests/test_schemas.py tests/test_perspective_factory.py -q`
- [x] `python -m pytest tests/test_custom_role_council.py tests/test_perspective_factory.py tests/test_schemas.py -q`
**Success Criteria**: council LLM parsing is schema-first and reusable across Gemini/Ollama while preserving legacy text fallback for weak model outputs.

## Phase 141: Local LLM Usage Metering (2026-03-08)
- [x] Inspect local LLM clients for existing usage/token signals before wiring observability
- [x] Extend `tonesoul/llm/ollama_client.py` to capture `prompt_eval_count` / `eval_count` into `LLMCallMetrics`
- [x] Extend `tonesoul/llm/lmstudio_client.py` to capture OpenAI-compatible `usage` payloads into `LLMCallMetrics`
- [x] Add optional `TokenMeter` injection to both local clients without breaking existing constructors or factory helpers
- [x] Persist metered usage only when the upstream payload actually provides token counts
- [x] Expose last call metrics via `client.last_metrics`
- [x] Add regression tests for:
- [x] Ollama usage capture + token meter recording
- [x] Ollama no-usage behavior
- [x] LM Studio usage capture + token meter recording
- [x] LM Studio no-usage behavior
- [x] Preserve existing Ollama fallback/error tests
- [x] Validation:
- [x] `python -m ruff check tonesoul/llm/ollama_client.py tonesoul/llm/lmstudio_client.py tests/test_llm_observability.py tests/test_ollama_fallback.py tests/test_observability.py`
- [x] `python -m black --check tonesoul/llm/ollama_client.py tonesoul/llm/lmstudio_client.py tests/test_llm_observability.py tests/test_ollama_fallback.py tests/test_observability.py`
- [x] `python -m pytest tests/test_llm_observability.py tests/test_ollama_fallback.py tests/test_observability.py -q`
**Success Criteria**: local LLM clients emit real usage metrics into ToneSoul's observability layer when token counts are available, while remaining silent rather than fabricating numbers when upstream payloads omit usage.

## Phase 142: Runtime LLM Evidence Attachment (2026-03-08)
- [x] Extend `tonesoul/llm/router.py` to expose `last_metrics` from the active cached client
- [x] Add a thin `UnifiedPipeline` helper that attaches LLM runtime evidence into `dispatch_trace["llm"]`
- [x] Record only additive evidence:
- [x] `backend`
- [x] `model`
- [x] `usage` only when the current call emitted real metrics
- [x] Avoid fabricating usage on successful calls that return no counters
- [x] Add regression tests for:
- [x] router-level `last_metrics` passthrough
- [x] runtime trace with real usage payload
- [x] runtime trace without fabricated usage payload
- [x] Validation:
- [x] `python -m ruff check tonesoul/llm/router.py tonesoul/unified_pipeline.py tests/test_llm_router.py tests/test_unified_pipeline_v2_runtime.py`
- [x] `python -m black --check tonesoul/llm/router.py tonesoul/unified_pipeline.py tests/test_llm_router.py tests/test_unified_pipeline_v2_runtime.py`
- [x] `python -m pytest tests/test_llm_router.py tests/test_unified_pipeline_v2_runtime.py -q`
**Success Criteria**: client-side usage metrics become orchestration-level runtime evidence without changing external response contracts or inventing telemetry when the provider omits it.

## Phase 143: Dream/Wake-up LLM Evidence Chain (2026-03-08)
- [x] Record collision-level LLM evidence in `tonesoul/dream_engine.py` after reflection generation
- [x] Preserve the same evidence rule as runtime pipeline paths:
- [x] include `backend` and `model` when known
- [x] include `usage` only when the reflection client emitted real counters
- [x] Aggregate collision LLM evidence into cycle-level wake-up summary in `tonesoul/wakeup_loop.py`
- [x] Add cycle summary fields:
- [x] `llm_call_count`
- [x] `llm_prompt_tokens_total`
- [x] `llm_completion_tokens_total`
- [x] `llm_total_tokens`
- [x] `llm_backends`
- [x] Extend `tonesoul/dream_observability.py` to surface cycle-level LLM token evidence in JSON/HTML artifacts
- [x] Keep the dashboard passive by reading only wake-up summary fields instead of parsing deep collision bodies
- [x] Add regression tests for:
- [x] dream collision LLM observability attachment
- [x] wake-up cycle LLM token aggregation
- [x] dashboard extraction/rendering of wake-up LLM token metrics
- [x] runner compatibility for wake-up/dashboard artifacts
- [x] Validation:
- [x] `python -m ruff check tonesoul/dream_engine.py tonesoul/wakeup_loop.py tonesoul/dream_observability.py tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_dream_observability.py tests/test_run_dream_wakeup_loop.py tests/test_run_dream_observability_dashboard.py`
- [x] `python -m black --check tonesoul/dream_engine.py tonesoul/wakeup_loop.py tonesoul/dream_observability.py tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_dream_observability.py tests/test_run_dream_wakeup_loop.py tests/test_run_dream_observability_dashboard.py`
- [x] `python -m pytest tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_dream_observability.py tests/test_run_dream_wakeup_loop.py tests/test_run_dream_observability_dashboard.py -q`
**Success Criteria**: dream reflections emit auditable LLM evidence, wake-up cycles aggregate it without recomputing provider facts, and the observability dashboard surfaces cycle-level token usage without reading raw collision internals.

## Phase 144: Inference-Readiness Preflight (2026-03-08)
- [x] Add bounded `probe_completion()` support to local LLM clients without mutating normal `last_metrics`
- [x] Normalize readiness probes through `LLMRouter.inference_check()`
- [x] Extend `DreamEngine` cycle results with explicit `llm_preflight` evidence
- [x] Gate autonomous reflection generation on readiness probes by default while keeping an explicit skip path
- [x] Thread readiness controls through:
- [x] `scripts/run_dream_engine.py`
- [x] `scripts/run_dream_wakeup_loop.py`
- [x] `scripts/run_autonomous_dream_cycle.py`
- [x] `scripts/run_autonomous_registry_schedule.py`
- [x] Preserve boundary semantics:
- [x] discovery health is not treated as inference readiness
- [x] probe telemetry does not masquerade as production reflection usage
- [x] `--no-llm` disables both reflection and readiness probing
- [x] Add regression coverage for:
- [x] client probe timeout/success behavior
- [x] router readiness normalization
- [x] dream-cycle reflection skip on failed readiness
- [x] CLI skip-preflight plumbing across autonomous runners
- [x] Validation:
- [x] `python -m ruff check tonesoul/llm/ollama_client.py tonesoul/llm/lmstudio_client.py tonesoul/llm/router.py tonesoul/dream_engine.py tonesoul/autonomous_cycle.py scripts/run_dream_engine.py scripts/run_dream_wakeup_loop.py scripts/run_autonomous_dream_cycle.py scripts/run_autonomous_registry_schedule.py tests/test_llm_readiness.py tests/test_llm_router.py tests/test_dream_engine.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py`
- [x] `python -m black --check tonesoul/llm/ollama_client.py tonesoul/llm/lmstudio_client.py tonesoul/llm/router.py tonesoul/dream_engine.py tonesoul/autonomous_cycle.py scripts/run_dream_engine.py scripts/run_dream_wakeup_loop.py scripts/run_autonomous_dream_cycle.py scripts/run_autonomous_registry_schedule.py tests/test_llm_readiness.py tests/test_llm_router.py tests/test_dream_engine.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py`
- [x] `python -m pytest tests/test_llm_readiness.py tests/test_llm_router.py tests/test_dream_engine.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py tests/test_autonomous_cycle.py -q`
- [x] Post-probe regression:
- [x] `python -m pytest tests/test_llm_readiness.py tests/test_llm_router.py tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_dream_observability.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py tests/test_autonomous_cycle.py -q`
- [x] Full suite:
- [x] `python -m pytest tests -q`
**Success Criteria**: autonomous reflection paths distinguish backend discovery from real inference readiness, skip stalled local backends before long dream cycles, and emit explicit preflight evidence so later artifacts explain why reflection did or did not run.

## Phase 145: Preflight Deadline Budget (2026-03-08)
- [x] Make local probe budgets consume one shared deadline across model resolution and HTTP request execution
- [x] Replace scalar probe request timeouts with bounded connect/read timeout tuples derived from remaining budget
- [x] Ensure model discovery paths (`_get_model()` / `_ensure_model()`) respect remaining preflight budget instead of silently spending a second full timeout
- [x] Preserve existing external CLI/runtime contracts:
- [x] no new flags
- [x] no change to normal `generate()` / `chat()` APIs
- [x] no change to readiness artifact shape beyond more accurate latency behavior
- [x] Add deadline regression tests for:
- [x] LM Studio request timeout bounding
- [x] LM Studio model-resolution budget sharing
- [x] Ollama bounded request timeout behavior
- [x] Validation:
- [x] `python -m ruff check tonesoul/llm/lmstudio_client.py tonesoul/llm/ollama_client.py tests/test_llm_readiness.py`
- [x] `python -m black --check tonesoul/llm/lmstudio_client.py tonesoul/llm/ollama_client.py tests/test_llm_readiness.py`
- [x] `python -m pytest tests/test_llm_readiness.py -q`
- [x] broader regression:
- [x] `python -m pytest tests/test_llm_readiness.py tests/test_llm_router.py tests/test_llm_observability.py tests/test_ollama_fallback.py tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py tests/test_autonomous_cycle.py -q`
- [x] live runtime probe:
- [x] `python scripts/run_dream_wakeup_loop.py --interval-seconds 0 --max-cycles 1 --limit 1 --min-priority 0.0 --llm-probe-timeout-seconds 2 --snapshot-path docs/status/probe_deadline/dream_wakeup_snapshot.json --history-path memory/autonomous/probe_deadline_history.jsonl`
- [x] `python scripts/run_dream_observability_dashboard.py --journal-path memory/self_journal.jsonl --wakeup-path memory/autonomous/probe_deadline_history.jsonl --out-dir docs/status/probe_deadline`
**Success Criteria**: a declared preflight budget behaves like a real deadline rather than two hidden timeouts glued together, and runtime artifacts show bounded timeout latency without inflating reflection usage.

## Phase 146: Router Deadline Accounting (2026-03-08)
- [x] Make `LLMRouter.inference_check()` spend backend selection time from the same preflight budget used by the client probe
- [x] Pass only remaining budget into `probe_completion()` after backend resolution
- [x] Fail fast when selection itself exhausts the declared budget
- [x] Expose preflight latency decomposition without changing the outer readiness contract:
- [x] `latency_ms` as total router+probe preflight latency
- [x] `selection_latency_ms`
- [x] `probe_latency_ms` when the probe reports it
- [x] Add regression coverage for:
- [x] remaining-budget handoff to the probe
- [x] selection-exhausted timeout path
- [x] total latency composition
- [x] Validation:
- [x] `python -m ruff check tonesoul/llm/router.py tests/test_llm_router.py`
- [x] `python -m black --check tonesoul/llm/router.py tests/test_llm_router.py`
- [x] `python -m pytest tests/test_llm_router.py -q`
- [x] broader autonomy regression:
- [x] `python -m pytest tests/test_llm_readiness.py tests/test_llm_router.py tests/test_dream_engine.py tests/test_wakeup_loop.py tests/test_run_dream_engine.py tests/test_run_dream_wakeup_loop.py tests/test_run_autonomous_dream_cycle.py tests/test_run_autonomous_registry_schedule.py tests/test_autonomous_cycle.py -q`
- [x] live runtime probe:
- [x] `python scripts/run_dream_wakeup_loop.py --interval-seconds 0 --max-cycles 1 --limit 1 --min-priority 0.0 --llm-probe-timeout-seconds 2 --snapshot-path docs/status/probe_router_deadline/dream_wakeup_snapshot.json --history-path memory/autonomous/probe_router_deadline_history.jsonl`
- [x] `python scripts/run_dream_observability_dashboard.py --journal-path memory/self_journal.jsonl --wakeup-path memory/autonomous/probe_router_deadline_history.jsonl --out-dir docs/status/probe_router_deadline`
**Success Criteria**: `timeout_seconds` becomes a true end-to-end router preflight budget, and runtime evidence can explain how much time was spent on backend discovery versus the probe itself.

## Phase 147: Scheduler Latency Policy (2026-03-08)
- [x] Promote `dream_result.llm_preflight` into wake-up summary fields so downstream policy reads only cycle summaries
- [x] Extend wake-up summary with:
- [x] `llm_preflight_latency_ms`
- [x] `llm_preflight_selection_latency_ms`
- [x] `llm_preflight_probe_latency_ms`
- [x] `llm_preflight_timeout_count`
- [x] `llm_preflight_reason`
- [x] Extend schedule profile contract with optional latency thresholds:
- [x] `tension_max_llm_preflight_latency_ms`
- [x] `tension_max_llm_selection_latency_ms`
- [x] `tension_max_llm_probe_latency_ms`
- [x] `tension_max_llm_timeout_count`
- [x] Wire the same thresholds through `run_autonomous_registry_schedule.py`
- [x] Make `AutonomousRegistrySchedule` react to wake-up summary latency facts without reading raw dream internals
- [x] Persist last observed preflight latency/timeout facts in category state for auditability
- [x] Extend dream observability JSON/HTML to surface:
- [x] preflight total latency
- [x] selection latency
- [x] probe latency
- [x] preflight timeout count
- [x] recent-cycle latency/reason columns
- [x] Validation:
- [x] `python -m ruff check tonesoul/wakeup_loop.py tonesoul/schedule_profile.py tonesoul/autonomous_schedule.py tonesoul/dream_observability.py scripts/run_autonomous_registry_schedule.py tests/test_wakeup_loop.py tests/test_schedule_profile.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py tests/test_dream_observability.py`
- [x] `python -m black --check tonesoul/wakeup_loop.py tonesoul/schedule_profile.py tonesoul/autonomous_schedule.py tonesoul/dream_observability.py scripts/run_autonomous_registry_schedule.py tests/test_wakeup_loop.py tests/test_schedule_profile.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py tests/test_dream_observability.py`
- [x] `python -m pytest tests/test_wakeup_loop.py tests/test_schedule_profile.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py tests/test_dream_observability.py -q`
- [x] Live profile run:
- [x] `python scripts/run_autonomous_registry_schedule.py --profile security_watch --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 --llm-probe-timeout-seconds 2 --history-path memory/autonomous/probe_schedule_latency_policy/dream_wakeup_history.jsonl --snapshot-path docs/status/probe_schedule_latency_policy/dream_wakeup_snapshot.json --dashboard-out-dir docs/status/probe_schedule_latency_policy --schedule-snapshot-path docs/status/probe_schedule_latency_policy/autonomous_registry_schedule_latest.json --schedule-history-path memory/autonomous/probe_schedule_latency_policy/registry_schedule_history.jsonl --schedule-state-path memory/autonomous/probe_schedule_latency_policy/registry_schedule_state.json`
**Success Criteria**: scheduler cooldown policy can distinguish backend selection latency from inference probe latency using wake-up summary evidence alone, and the same evidence is visible in the observability dashboard and persisted schedule state.

## Phase 148: Runtime LLM Backoff Split (2026-03-08)
- [x] Split schedule tension-budget breaches into governance-side reasons and LLM-runtime reasons
- [x] Keep category cooldown scoped to governance-side breaches only
- [x] Introduce global `llm_backoff` state in schedule state for LLM latency/timeout breaches
- [x] While LLM backoff is active, keep source rotation running but force degraded execution:
- [x] `generate_reflection=False`
- [x] `require_inference_ready=False`
- [x] Preserve last observed latency facts when a degraded cycle emits no fresh wake-up summary, instead of overwriting category state with `None`
- [x] Validation:
- [x] `python -m ruff check tonesoul/autonomous_schedule.py tests/test_autonomous_schedule.py`
- [x] `python -m black --check tonesoul/autonomous_schedule.py tests/test_autonomous_schedule.py`
- [x] `python -m pytest tests/test_autonomous_schedule.py -q`
- [x] broader regression:
- [x] `python -m pytest tests/test_wakeup_loop.py tests/test_schedule_profile.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py -q`
**Success Criteria**: pure LLM runtime instability should degrade reflective execution globally without freezing source categories, and the last observed latency evidence must remain auditable until a fresh wake-up summary replaces it.

## Phase 149: Schedule Governance Observability (2026-03-08)
- [x] Extend dream observability to accept optional schedule artifacts:
- [x] `schedule_history_path`
- [x] `schedule_state_path`
- [x] Surface two distinct schedule curves instead of one blended governance story:
- [x] governance cooldown applied/deferred
- [x] LLM backoff requested/active
- [x] Keep missing schedule artifacts backward compatible:
- [x] existing journal+wakeup dashboard callers must still work unchanged
- [x] registry-schedule runner should refresh the enriched dashboard automatically after each schedule tick
- [x] Add regression coverage for JSON payload, HTML output, and runner contract
- [x] Validation:
- [x] `python -m ruff check tonesoul/dream_observability.py tonesoul/autonomous_schedule.py scripts/run_dream_observability_dashboard.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py tests/test_autonomous_schedule.py`
- [x] `python -m black --check tonesoul/dream_observability.py tonesoul/autonomous_schedule.py scripts/run_dream_observability_dashboard.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py tests/test_autonomous_schedule.py`
- [x] `python -m pytest tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py tests/test_autonomous_schedule.py -q`
- [x] broader regression:
- [x] `python -m pytest tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py tests/test_wakeup_loop.py tests/test_schedule_profile.py tests/test_autonomous_schedule.py tests/test_run_autonomous_registry_schedule.py tests/test_dream_observability.py tests/test_run_dream_observability_dashboard.py -q`
- [x] historical artifact regeneration:
- [x] `python scripts/run_dream_observability_dashboard.py --journal-path memory/self_journal.jsonl --wakeup-path memory/autonomous/probe_schedule_latency_policy/dream_wakeup_history.jsonl --schedule-history-path memory/autonomous/probe_schedule_latency_policy/registry_schedule_history.jsonl --schedule-state-path memory/autonomous/probe_schedule_latency_policy/registry_schedule_state.json --out-dir docs/status/probe_schedule_governance_dashboard`
**Success Criteria**: the dashboard can explain whether the system is cooling source categories for governance reasons or globally degrading reflection for runtime reasons, using schedule artifacts directly rather than reconstructing policy from raw traces.

## Phase 150: LLM Backoff Activation Verification (2026-03-08)
- [x] Run a fresh post-Phase-149 schedule probe with zero interval so the same artifact captures:
- [x] the cycle that requests global LLM backoff
- [x] the next cycle that executes under active backoff
- [x] Confirm the dashboard distinguishes:
- [x] `schedule_llm_backoff_requested`
- [x] `schedule_llm_backoff_active`
- [x] Confirm governance cooldown can coexist with runtime backoff without collapsing into one status
- [x] Live verification:
- [x] `python scripts/run_autonomous_registry_schedule.py --profile security_watch --interval-seconds 0 --max-cycles 2 --entries-per-cycle 1 --urls-per-cycle 1 --llm-probe-timeout-seconds 2 --history-path memory/autonomous/probe_schedule_governance_live2/dream_wakeup_history.jsonl --snapshot-path docs/status/probe_schedule_governance_live2/dream_wakeup_snapshot.json --dashboard-out-dir docs/status/probe_schedule_governance_live2 --schedule-snapshot-path docs/status/probe_schedule_governance_live2/autonomous_registry_schedule_latest.json --schedule-history-path memory/autonomous/probe_schedule_governance_live2/registry_schedule_history.jsonl --schedule-state-path memory/autonomous/probe_schedule_governance_live2/registry_schedule_state.json`
- [x] Artifact inspection:
- [x] `docs/status/probe_schedule_governance_live2/dream_observability_latest.json`
- [x] `docs/status/probe_schedule_governance_live2/dream_observability_latest.html`
**Success Criteria**: one live schedule artifact must show `requested` on the triggering cycle and `active` on the subsequent degraded cycle, so runtime backoff is verified as a temporal state transition rather than a static flag.

## Phase 151: Pure Runtime Probe Profile (2026-03-08)
- [x] Package the proven Phase 150 runtime scenario as a named schedule profile instead of a fragile CLI recipe
- [x] Add `runtime_probe_watch` to `spec/registry_schedule_profiles.yaml`
- [x] Keep governance thresholds deliberately relaxed:
- [x] `tension_max_friction_score = 1.0`
- [x] `tension_max_lyapunov_proxy = 1.0`
- [x] `tension_max_council_count = 99`
- [x] Preserve tight runtime thresholds:
- [x] `tension_max_llm_preflight_latency_ms = 1800`
- [x] `tension_max_llm_selection_latency_ms = 700`
- [x] `tension_max_llm_probe_latency_ms = 1200`
- [x] `tension_max_llm_timeout_count = 0`
- [x] Add regression coverage for profile loading and resolved defaults
- [x] Validation:
- [x] `python -m ruff check tests/test_schedule_profile.py`
- [x] `python -m black --check tests/test_schedule_profile.py`
- [x] `python -m pytest tests/test_schedule_profile.py tests/test_run_autonomous_registry_schedule.py -q`
- [x] Live verification:
- [x] `python scripts/run_autonomous_registry_schedule.py --profile runtime_probe_watch --interval-seconds 0 --max-cycles 2 --llm-probe-timeout-seconds 2 --history-path memory/autonomous/probe_runtime_profile_live/dream_wakeup_history.jsonl --snapshot-path docs/status/probe_runtime_profile_live/dream_wakeup_snapshot.json --dashboard-out-dir docs/status/probe_runtime_profile_live --schedule-snapshot-path docs/status/probe_runtime_profile_live/autonomous_registry_schedule_latest.json --schedule-history-path memory/autonomous/probe_runtime_profile_live/registry_schedule_history.jsonl --schedule-state-path memory/autonomous/probe_runtime_profile_live/registry_schedule_state.json`
- [x] Artifact inspection:
- [x] `docs/status/probe_runtime_profile_live/autonomous_registry_schedule_latest.json`
- [x] `docs/status/probe_runtime_profile_live/dream_observability_latest.json`

## Phase 152: Runtime Preflight Entrypoint (2026-03-08)
- [x] Add a thin dedicated runner:
- [x] `scripts/run_runtime_probe_watch.py`
- [x] Keep policy anchored in `runtime_probe_watch` instead of duplicating scheduler logic
- [x] Write `preflight_profile` into the schedule snapshot artifact so the entrypoint identity survives beyond stdout
- [x] Make the dedicated preflight runner default to a fresh sample:
- [x] clear prior wake-up history
- [x] clear prior schedule history/state
- [x] clear prior dashboard latest artifacts
- [x] keep explicit `--reuse-state` as the opt-in escape hatch
- [x] Add parser/runner regression coverage:
- [x] `tests/test_run_runtime_probe_watch.py`
- [x] Validation:
- [x] `python -m ruff check scripts/run_runtime_probe_watch.py tests/test_run_runtime_probe_watch.py`
- [x] `python -m black --check scripts/run_runtime_probe_watch.py tests/test_run_runtime_probe_watch.py`
- [x] `python -m pytest tests/test_run_runtime_probe_watch.py tests/test_run_autonomous_registry_schedule.py tests/test_schedule_profile.py -q`
- [x] Live verification:
- [x] `python scripts/run_runtime_probe_watch.py --strict`
- [x] Artifact inspection:
- [x] `docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json`
- [x] `docs/status/runtime_probe_watch/dream_observability_latest.json`

## Phase 153: Runtime-Gated Long Run (2026-03-08)
- [x] Add a dedicated long-run wrapper:
- [x] `scripts/run_autonomous_registry_long_run.py`
- [x] Gate the real registry schedule on `runtime_probe_watch`
- [x] Block the long run when runtime probe returns `overall_ok = false`
- [x] Keep explicit skip semantics:
- [x] `--skip-runtime-probe-watch`
- [x] auto-skip when `--no-llm` disables reflection entirely
- [x] Keep preflight and long-run concerns separate:
- [x] preflight remains a dedicated runner
- [x] generic registry schedule runner remains unchanged
- [x] Align runtime budgets by default:
- [x] if the long-run probe timeout is not explicitly set, inherit `--preflight-llm-probe-timeout-seconds`
- [x] keep explicit `--llm-probe-timeout-seconds` as the final operator override
- [x] Add regression coverage:
- [x] `tests/test_run_autonomous_registry_long_run.py`
- [x] Validation:
- [x] `python -m ruff check scripts/run_autonomous_registry_long_run.py tests/test_run_autonomous_registry_long_run.py`
- [x] `python -m black --check scripts/run_autonomous_registry_long_run.py tests/test_run_autonomous_registry_long_run.py`
- [x] `python -m pytest tests/test_run_autonomous_registry_long_run.py -q`
- [x] combined wrapper/profile regression:
- [x] `python -m pytest tests/test_run_runtime_probe_watch.py tests/test_run_autonomous_registry_long_run.py tests/test_run_autonomous_registry_schedule.py tests/test_schedule_profile.py -q`
- [x] Live verification:
- [x] `python scripts/run_autonomous_registry_long_run.py --profile security_watch --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 ... --strict`
- [x] Fresh live verification:
- [x] `python scripts/run_autonomous_registry_long_run.py --profile security_watch --max-cycles 1 --entries-per-cycle 1 --urls-per-cycle 1 ...fresh artifact paths... --strict`

## Phase 154: Weekly True Verification Entrypoint (2026-03-08)
- [x] Add a first-class weekly experiment wrapper:
- [x] `scripts/run_true_verification_experiment.py`
- [x] Keep the lower orchestration seam intact:
- [x] delegate runtime gating to `run_autonomous_registry_long_run.py`
- [x] do not duplicate `runtime_probe_watch` policy or schedule logic
- [x] Encode the intended Phase 7 operating envelope as wrapper defaults:
- [x] `profile = security_watch`
- [x] `experiment_days = 7`
- [x] `wake_interval_hours = 3`
- [x] derive `planned_cycles = ceil(days * 24 / wake_interval_hours)` when `--max-cycles` is not explicitly set
- [x] Give the weekly experiment a stable artifact identity:
- [x] long-run artifacts rooted at `docs/status/true_verification_weekly` and `memory/autonomous/true_verification_weekly`
- [x] preflight artifacts isolated under `.../true_verification_weekly/preflight`
- [x] wrapper summary written to `docs/status/true_verification_weekly/true_verification_experiment_latest.json`
- [x] Default the weekly entrypoint to a fresh sample:
- [x] clear prior long-run history/state/latest dashboard artifacts unless `--reuse-experiment-state` is explicitly set
- [x] Add regression coverage:
- [x] `tests/test_run_true_verification_experiment.py`
- [x] Validation:
- [x] `python -m ruff check scripts/run_true_verification_experiment.py tests/test_run_true_verification_experiment.py`
- [x] `python -m black --check scripts/run_true_verification_experiment.py tests/test_run_true_verification_experiment.py`
- [x] `python -m pytest tests/test_run_true_verification_experiment.py -q`
- [x] combined wrapper regression:
- [x] `python -m pytest tests/test_run_true_verification_experiment.py tests/test_run_autonomous_registry_long_run.py tests/test_run_runtime_probe_watch.py tests/test_schedule_profile.py -q`

## Phase 155: Host-Driven Weekly Tick (2026-03-08)
- [x] Add a host-driven single-tick runner for the weekly experiment:
- [x] `scripts/run_true_verification_host_tick.py`
- [x] Keep the orchestration boundary clean:
- [x] delegate runtime gate + real schedule cycle to `run_autonomous_registry_long_run.py`
- [x] do not move local runtime assumptions into GitHub Actions
- [x] Encode the host-driven contract:
- [x] one invocation = one preflight + one real schedule cycle
- [x] `max_cycles = 1`
- [x] `interval_seconds = 0`
- [x] keep the weekly artifact roots under `true_verification_weekly`
- [x] Add explicit operator control for experiment reset:
- [x] `--fresh-experiment-state` clears weekly long-run artifacts before the tick
- [x] Keep the host schedule intent visible in artifacts:
- [x] write `true_verification_host_tick_latest.json`
- [x] carry declared `experiment_days` and `wake_interval_hours` into the tick summary
- [x] Add regression coverage:
- [x] `tests/test_run_true_verification_host_tick.py`
- [x] Add operator-facing runbook:
- [x] `docs/plans/true_verification_host_schedule_runbook_2026-03-08.md`
- [x] Update status artifact README with the new experiment/tick surfaces
- [x] Validation:
- [x] `python -m ruff check scripts/run_true_verification_host_tick.py tests/test_run_true_verification_host_tick.py docs/status/README.md`
- [x] `python -m black --check scripts/run_true_verification_host_tick.py tests/test_run_true_verification_host_tick.py`
- [x] `python -m pytest tests/test_run_true_verification_host_tick.py -q`
- [x] combined wrapper regression:
- [x] `python -m pytest tests/test_run_true_verification_host_tick.py tests/test_run_true_verification_experiment.py tests/test_run_autonomous_registry_long_run.py tests/test_run_runtime_probe_watch.py tests/test_schedule_profile.py -q`

## Phase 156: Task Scheduler Template (2026-03-08)
- [x] Add a versioned Windows Task Scheduler template generator:
- [x] `scripts/render_true_verification_task_scheduler.py`
- [x] Keep task registration separate from runtime semantics:
- [x] generate XML + summary metadata
- [x] do not auto-register tasks during development
- [x] keep the actual experiment contract in `run_true_verification_host_tick.py`
- [x] Encode the host cadence into the template:
- [x] repeat every `3` hours
- [x] repeat duration `7` days
- [x] execution time limit `2` hours
- [x] wire the task command to `python .../run_true_verification_host_tick.py --strict`
- [x] Add regression coverage:
- [x] `tests/test_render_true_verification_task_scheduler.py`
- [x] Update the host schedule runbook and status README with the generated XML/JSON artifacts
- [x] Add task-scheduler addendum doc:
- [x] `docs/plans/true_verification_task_scheduler_template_addendum_2026-03-08.md`
- [x] Validation:
- [x] `python -m ruff check scripts/render_true_verification_task_scheduler.py tests/test_render_true_verification_task_scheduler.py docs/plans/true_verification_host_schedule_runbook_2026-03-08.md docs/status/README.md`
- [x] `python -m black --check scripts/render_true_verification_task_scheduler.py tests/test_render_true_verification_task_scheduler.py`
- [x] `python -m pytest tests/test_render_true_verification_task_scheduler.py tests/test_run_true_verification_host_tick.py tests/test_run_true_verification_experiment.py tests/test_run_autonomous_registry_long_run.py tests/test_run_runtime_probe_watch.py tests/test_schedule_profile.py -q`
- [x] Generate a concrete template artifact:
- [x] `python scripts/render_true_verification_task_scheduler.py --start-boundary 2026-03-08T18:00 --strict`

## Phase 157: Safe Task Installer (2026-03-08)
- [x] Add a default-dry-run installer for the weekly Task Scheduler definition:
- [x] `scripts/install_true_verification_task_scheduler.py`
- [x] Keep render and install concerns separated:
- [x] optional template refresh before install
- [x] dry-run by default
- [x] require explicit `--apply` before invoking `schtasks`
- [x] Write a dedicated installer summary artifact:
- [x] `docs/status/true_verification_weekly/true_verification_task_scheduler_install_latest.json`
- [x] Keep install evidence explicit:
- [x] include resolved command
- [x] include linked render payload
- [x] include stdout/stderr/returncode when apply mode is used
- [x] Preserve renderer defaults through the installer layer:
- [x] installer default `author` must inherit the renderer default instead of serializing `"None"`
- [x] Add regression coverage:
- [x] `tests/test_install_true_verification_task_scheduler.py`
- [x] Add installer addendum doc:
- [x] `docs/plans/true_verification_task_scheduler_install_addendum_2026-03-08.md`
- [x] Update host schedule runbook and status README with the safe installer flow
- [x] Validation:
- [x] `python -m ruff check scripts/install_true_verification_task_scheduler.py tests/test_install_true_verification_task_scheduler.py docs/plans/true_verification_task_scheduler_install_addendum_2026-03-08.md docs/plans/true_verification_host_schedule_runbook_2026-03-08.md docs/status/README.md`
- [x] `python -m black --check scripts/install_true_verification_task_scheduler.py tests/test_install_true_verification_task_scheduler.py`
- [x] `python -m pytest tests/test_install_true_verification_task_scheduler.py tests/test_render_true_verification_task_scheduler.py tests/test_run_true_verification_host_tick.py tests/test_run_true_verification_experiment.py tests/test_run_autonomous_registry_long_run.py tests/test_run_runtime_probe_watch.py tests/test_schedule_profile.py -q`
- [x] Generate a concrete dry-run install artifact:
- [x] `python scripts/install_true_verification_task_scheduler.py --strict`

## Phase 158: Task Scheduler Applied (2026-03-08)
- [x] Apply the weekly True Verification Task Scheduler task via the safe installer:
- [x] `python scripts/install_true_verification_task_scheduler.py --apply --strict`
- [x] Confirm the host mutation succeeded:
- [x] installer summary shows `mode = applied`
- [x] installer stdout confirms `SUCCESS: The scheduled task "ToneSoul True Verification Weekly" has successfully been created.`
- [x] Read back the registered task from Task Scheduler:
- [x] `schtasks /Query /TN "ToneSoul True Verification Weekly" /XML`
- [x] Verify the live registered task matches the governed contract:
- [x] `StartBoundary = 2026-03-08T14:30:00`
- [x] `Interval = PT3H`
- [x] `Duration = P7D`
- [x] `ExecutionTimeLimit = PT2H`
- [x] `Command = ...\\.venv\\Scripts\\python.exe`
- [x] `Arguments = "...\\scripts\\run_true_verification_host_tick.py" --strict`

## Phase 159: Weekly Status Readback Hygiene (2026-03-08)
- [x] Stop test pollution from writing into live weekly artifact roots:
- [x] `tests/test_run_true_verification_experiment.py`
- [x] `tests/test_run_true_verification_host_tick.py`
- [x] Add host-tick-aware status reporting:
- [x] `scripts/report_true_verification_task_status.py`
- [x] ignore `true_verification_experiment_latest.json` when `host_trigger_mode = single_tick`
- [x] Add regression coverage:
- [x] `tests/test_report_true_verification_task_status.py`
- [x] Validation:
- [x] `python -m pytest tests/test_governance_kernel.py tests/test_report_true_verification_task_status.py tests/test_run_true_verification_experiment.py tests/test_run_true_verification_host_tick.py -q`

## Phase 160: Governance Override Pressure Correction (2026-03-08)
- [x] Remove the dead-code shape inside `tonesoul/governance/kernel.py::_contains_override_pressure()`
- [x] Preserve the precise regex path instead of letting the earlier broad substring return shadow it
- [x] Add a false-positive regression:
- [x] `"I can't ignore this feeling"` must not count as override pressure
- [x] Validation:
- [x] `python -m pytest tests/test_governance_kernel.py -q`

## Phase 161: Quiet Host Task Wrapper (2026-03-08)
- [x] Add a scheduler-only quiet wrapper:
- [x] `scripts/run_true_verification_host_tick_task.py`
- [x] Keep manual and host launch surfaces separate:
- [x] manual debugging stays on `run_true_verification_host_tick.py`
- [x] Task Scheduler uses the quiet wrapper to suppress import-time warnings and runtime stdout/stderr chatter
- [x] Move render/install defaults to the quiet wrapper:
- [x] `scripts/render_true_verification_task_scheduler.py`
- [x] `scripts/install_true_verification_task_scheduler.py`
- [x] Add regression coverage:
- [x] `tests/test_run_true_verification_host_tick_task.py`
- [x] `tests/test_render_true_verification_task_scheduler.py`
- [x] `tests/test_install_true_verification_task_scheduler.py`
- [x] Re-apply the live Task Scheduler definition and read back the host contract:
- [x] `Arguments = "...\\scripts\\run_true_verification_host_tick_task.py" --strict`
- [x] manual trigger no longer exits with `0xC000013A`
- [x] final live readback shows `LastTaskResult = 0`

## Mainline Backlog After Phase 161
- [x] `P1` Fix `WebIngestor.ingest_urls_sync()` event-loop blocking risk on Windows / loop-thread callers
- [x] `P2` Add direct missing-branch tests for `LLMRouter.inference_check()` (`no_client`, `probe_unsupported`, `probe_exception`, normalize branches)
- [x] `P2` Migrate `LLMRouteDecision` / `GovernanceDecision` from ad-hoc dataclasses toward `tonesoul/schemas.py`

## Phase 162: WebIngestor Event-Loop Fail-Fast (2026-03-08)
- [x] Remove the unsafe thread-handoff sync wrapper from `tonesoul/perception/web_ingest.py`
- [x] Make `ingest_urls_sync()` fail fast inside a running event loop
- [x] Preserve the sync convenience path for true non-async callers
- [x] Add direct regressions:
- [x] sync call works outside an event loop
- [x] sync call raises with guidance inside a running event loop
- [x] Re-verify adjacent autonomous caller seams:
- [x] `tests/test_autonomous_cycle.py`
- [x] `tests/test_run_autonomous_dream_cycle.py`
- [x] Validation:
- [x] `python -m pytest tests/test_perception.py tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py -q`

## Phase 163: LLMRouter Inference Check Branch Coverage (2026-03-08)
- [x] Add direct tests for `LLMRouter.inference_check()` uncovered branches
- [x] cover `no_client`
- [x] cover `probe_unsupported`
- [x] cover `probe_exception`
- [x] cover non-dict probe-result normalization
- [x] cover non-primitive model normalization
- [x] Keep tests environment-independent:
- [x] patch resolver paths instead of assuming the host has no local backend
- [x] Validation:
- [x] `python -m pytest tests/test_llm_router.py -q`

## Phase 164: Autonomous Cycle Sync Boundary Audit (2026-03-08)
- [x] Audit repo call sites for `ingest_urls_sync()`
- [x] Confirm the only production caller is the synchronous `AutonomousDreamCycleRunner.run()` seam
- [x] Confirm current scripts/schedule layers invoke that runner synchronously rather than from async contexts
- [x] Add an orchestration-level regression:
- [x] `runner.run()` raises clearly when URL ingestion is attempted inside a running event loop
- [x] Leave an explicit sync-boundary note in `tonesoul/autonomous_cycle.py`
- [x] Validation:
- [x] `python -m pytest tests/test_autonomous_cycle.py tests/test_run_autonomous_dream_cycle.py -q`

## Phase 165: Governance Decision Schema Convergence (2026-03-08)
- [x] Move `LLMRouteDecision` and `GovernanceDecision` into `tonesoul/schemas.py`
- [x] Keep `tonesoul.governance.kernel` exporting the same names
- [x] Preserve current attribute-based caller contract:
- [x] `.backend`
- [x] `.client`
- [x] `.reason`
- [x] Add schema coverage:
- [x] route backend normalization
- [x] nested governance decision parsing
- [x] kernel routing now returns the schema-backed route decision type
- [x] Validation:
- [x] `python -m pytest tests/test_schemas.py tests/test_governance_kernel.py tests/test_llm_router.py -q`

## Phase 166: Routing Trace Contract Alignment (2026-03-08)
- [x] Add a canonical routing-trace helper to `tonesoul/governance/kernel.py`
- [x] Make `UnifiedPipeline` use the same routing-trace shape on fast and non-fast paths
- [x] Preserve backward compatibility:
- [x] keep top-level `dispatch_trace.route`
- [x] keep top-level `dispatch_trace.journal_eligible`
- [x] keep top-level `dispatch_trace.reason`
- [x] add nested `dispatch_trace.routing_trace` as the canonical sub-trace
- [x] Add regressions:
- [x] kernel routing-trace helper shape
- [x] fast-path routing trace mirrors top-level fields
- [x] premium/council path routing trace mirrors top-level fields and carries `reason`
- [x] Validation:
- [x] `python -m pytest tests/test_governance_kernel.py tests/test_pipeline_compute_gate.py tests/test_unified_pipeline_v2_runtime.py -q`
- [x] Residual warning backlog cleared:
- [x] `tonesoul/deliberation/engine.py` no longer reproduces `DeprecationWarning: There is no current event loop` in targeted validation (`tests/test_deliberation_engine.py` + `tests/test_unified_pipeline_v2_runtime.py`, 2026-03-09)

## Phase 167: Weekly Artifact Payload Slimming (2026-03-08)
- [x] Add a shared summary helper:
- [x] `tonesoul/true_verification_summary.py`
- [x] Keep detailed evidence in the underlying schedule/preflight artifacts
- [x] Make host-facing latest summaries write compact payloads instead of embedding full `results/state` bodies:
- [x] `scripts/run_true_verification_host_tick.py`
- [x] `scripts/run_true_verification_experiment.py`
- [x] `scripts/report_true_verification_task_status.py`
- [x] Add focused regressions:
- [x] `tests/test_true_verification_summary.py`
- [x] `tests/test_run_true_verification_host_tick.py`
- [x] `tests/test_run_true_verification_experiment.py`
- [x] `tests/test_report_true_verification_task_status.py`
- [x] Validation:
- [x] `python -m pytest tests/test_true_verification_summary.py tests/test_run_true_verification_experiment.py tests/test_run_true_verification_host_tick.py tests/test_report_true_verification_task_status.py -q`
- [x] Live artifact refresh:
- [x] rerun `scripts/report_true_verification_task_status.py`
- [x] rewrite existing `true_verification_host_tick_latest.json` to the new summary contract
- [x] Size outcome:
- [x] `true_verification_task_status_latest.json`: `475.54 KB -> 16.78 KB`
- [x] `true_verification_host_tick_latest.json`: `311.41 KB -> 11.45 KB`

## Phase 168: Weekly Summary Readback Chain Regression (2026-03-08)
- [x] Add an integrated weekly-chain regression:
- [x] `tests/test_true_verification_weekly_chain.py`
- [x] Prove `run_true_verification_host_tick.py` writes a compact summary instead of raw nested payloads
- [x] Prove `report_true_verification_task_status.py` can read that compact summary plus a raw schedule snapshot and keep both compact
- [x] Make the summary helper idempotent across readback layers:
- [x] preserve `result_count`
- [x] preserve `latest_result`
- [x] preserve summarized state counters on second-pass summarization
- [x] Validation:
- [x] `python -m pytest tests/test_true_verification_weekly_chain.py tests/test_true_verification_summary.py tests/test_run_true_verification_experiment.py tests/test_run_true_verification_host_tick.py tests/test_report_true_verification_task_status.py -q`

## Phase 169: True Verification Operator Runbook Refresh (2026-03-08)
- [x] Update `docs/plans/true_verification_host_schedule_runbook_2026-03-08.md`
- [x] Document the compact-summary contract explicitly
- [x] Add the current operator reading ritual:
- [x] task status first
- [x] host tick second
- [x] dashboard third
- [x] detailed artifacts only on anomaly
- [x] Add anomaly triage guidance for:
- [x] task registration failure
- [x] runtime probe block
- [x] governance breach
- [x] LLM backoff / runtime degradation
- [x] Update `docs/status/README.md` so artifact descriptions match the compact summary reality
- [x] Validation:
- [x] `rg -n "delegated gate/preflight/schedule payload|delegated preflight/schedule payload|delegated runtime gate result" docs/plans/true_verification_host_schedule_runbook_2026-03-08.md docs/status/README.md`

## Phase 170: Full Regression Closure (2026-03-08)
- [x] Run full suite after the accumulated shared-contract changes:
- [x] `python -m pytest tests -q`
- [x] Result:
- [x] `1402 passed, 3 warnings`
- [x] Warning surface remained explainable:
- [x] Hypothesis plugin directory warning
- [x] `requests` dependency version warning
- [x] `UnifiedCore` maintenance-mode deprecation warning

## Phase 171: Deliberation Event-Loop Warning Cleanup (2026-03-08)
- [x] Replace deprecated sync-loop probing in `tonesoul/deliberation/engine.py`
- [x] Keep runtime behavior unchanged:
- [x] no running loop -> use `asyncio.run(...)`
- [x] running loop -> fall back to sequential sync path
- [x] Add direct regressions:
- [x] `tests/test_deliberation_engine.py`
- [x] Validate adjacent runtime seam:
- [x] `tests/test_unified_pipeline_v2_runtime.py`
- [x] Validation:
- [x] `python -m pytest tests/test_deliberation_engine.py tests/test_unified_pipeline_v2_runtime.py -q`

## Phase 172: Weekly True Verification Into Repo Healthcheck (2026-03-08)
- [x] Add a fixed repo-healthcheck inspection seam for weekly True Verification:
- [x] `scripts/report_true_verification_task_status.py --strict`
- [x] Keep repo healthcheck CLI unchanged
- [x] Encode host semantics explicitly:
- [x] Windows host -> blocking live task-status check
- [x] non-Windows host -> explicit `skip` with reason
- [x] Extend focused regressions:
- [x] `tests/test_run_repo_healthcheck.py`
- [x] `tests/test_verify_docs_consistency.py`
- [x] Extend docs-consistency runner contract:
- [x] missing weekly check now fails the repo-healthcheck runner report
- [x] Update `docs/status/README.md` so repo healthcheck docs mention the host-aware weekly status readback
- [x] Validation:
- [x] `python -m pytest tests/test_run_repo_healthcheck.py tests/test_verify_docs_consistency.py -q`
- [x] `python -m ruff check scripts/run_repo_healthcheck.py scripts/verify_docs_consistency.py tests/test_run_repo_healthcheck.py tests/test_verify_docs_consistency.py`
- [x] `python -m black --check scripts/run_repo_healthcheck.py scripts/verify_docs_consistency.py tests/test_run_repo_healthcheck.py tests/test_verify_docs_consistency.py`
- [x] Live host proof:
- [x] `python scripts/report_true_verification_task_status.py --strict`

## Phase 173: External Source Registry Direct-Entry Repair (2026-03-08)
- [x] Reproduce the repo-healthcheck failure:
- [x] `python scripts/verify_external_source_registry.py --strict` failed with `ModuleNotFoundError: No module named 'tonesoul'`
- [x] Fix the direct script entrypoint:
- [x] add repo-root bootstrap to `scripts/verify_external_source_registry.py`
- [x] Preserve existing validation logic; only repair the script execution seam
- [x] Add a real direct-entry regression:
- [x] `tests/test_verify_external_source_registry.py` now launches the script through `subprocess.run(...)`
- [x] Validation:
- [x] `python -m pytest tests/test_verify_external_source_registry.py tests/test_run_external_source_registry_check.py -q`
- [x] `python -m ruff check scripts/verify_external_source_registry.py tests/test_verify_external_source_registry.py`
- [x] `python -m black --check scripts/verify_external_source_registry.py tests/test_verify_external_source_registry.py`
- [x] Live proof:
- [x] `python scripts/verify_external_source_registry.py --strict`

## Phase 174: Skill Registry Coverage Closure + BOM Tolerance (2026-03-08)
- [x] Reproduce the repo-healthcheck failure:
- [x] `python scripts/verify_skill_registry.py --strict` reported two discovered skills missing from `skills/registry.json`
- [x] Add registry entries for:
- [x] `.agent/skills/tonesoul_governance/SKILL.md`
- [x] `.agent/skills/tonesoul_philosophy/SKILL.md`
- [x] Add machine-readable frontmatter for those two legacy skills:
- [x] `l1_routing`
- [x] `l2_signature`
- [x] `trust`/integrity data via registry entries
- [x] Fix verifier robustness:
- [x] `_parse_frontmatter()` now tolerates UTF-8 BOM instead of rejecting otherwise-valid YAML frontmatter
- [x] Add regression:
- [x] `tests/test_verify_skill_registry.py` covers BOM-prefixed frontmatter parsing
- [x] Validation:
- [x] `python scripts/verify_skill_registry.py --strict`
- [x] `python -m pytest tests/test_verify_skill_registry.py -q`
- [x] `python -m ruff check scripts/verify_skill_registry.py tests/test_verify_skill_registry.py`
- [x] `python -m black --check scripts/verify_skill_registry.py tests/test_verify_skill_registry.py`

## Phase 175: DDD Freshness Closeout Ritual (2026-03-08)
- [x] Keep the 7D contract strict:
- [x] do not weaken `DDD_FRESHNESS`
- [x] make remediation explicit instead
- [x] Tighten the operator path:
- [x] `scripts/verify_7d.py` stale / missing / invalid-timestamp notes now point to `tools/agent_discussion_tool.py append-lessons`
- [x] `docs/7D_EXECUTION_SPEC.md` now states that `DDD_FRESHNESS` is driven by `memory/agent_discussion_curated.jsonl`, not by `task.md` / reflection / crystals
- [x] `docs/status/README.md` now repeats the same operator doctrine at the repo-healthcheck entrypoint
- [x] Prove the seam:
- [x] add direct `DDD_FRESHNESS` fresh/stale regressions in `tests/test_verify_7d.py`
- [x] prove `append-lessons` mirrors to curated discussion in `tests/test_agent_discussion_tool.py`
- [x] Refresh the real discussion channel:
- [x] append one `LESSONS_V1` closeout entry to `memory/agent_discussion.jsonl` mirrored into `memory/agent_discussion_curated.jsonl`
- [x] Validation:
- [x] `python -m ruff check scripts/verify_7d.py tests/test_verify_7d.py tests/test_agent_discussion_tool.py`
- [x] `python -m black --check scripts/verify_7d.py tests/test_verify_7d.py tests/test_agent_discussion_tool.py`
- [x] `python -m pytest tests/test_verify_7d.py tests/test_agent_discussion_tool.py -q`
- [x] Freshness proof:
- [x] latest curated discussion topic = `phase175-repo-healthcheck-convergence-2026-03-08`
- [x] latest curated discussion age ~= `0` days

## Phase 176: Commit Attribution Branch Equivalence Proof (2026-03-08)
- [x] Keep the git repair strategy non-destructive:
- [x] do not rewrite the dirty working branch in place
- [x] prove the safe alternate base first
- [x] Extend `scripts/verify_incremental_commit_attribution.py`:
- [x] add optional `--equivalent-ref`
- [x] report `equivalence.head_tree`
- [x] report `equivalence.compare_tree`
- [x] report `equivalence.tree_equal`
- [x] Add regressions:
- [x] `tests/test_verify_incremental_commit_attribution.py` covers tree-equivalent and tree-different cases
- [x] Update operator docs:
- [x] `docs/status/README.md` now documents the optional equivalence block and `commit_attribution_backfill_branch.json`
- [x] Refresh the real artifact:
- [x] `python scripts/verify_incremental_commit_attribution.py --head-sha feat/env-perception-attribution-backfill --equivalent-ref HEAD --artifact-path docs/status/commit_attribution_backfill_branch.json --strict`
- [x] Proof outcome:
- [x] `missing_count = 0`
- [x] `equivalence.tree_equal = true`
- [x] `head_tree = compare_tree = 1a879968fcefbb32afac2745f86b6227ac5167b0`
- [x] Validation:
- [x] `python -m ruff check scripts/verify_incremental_commit_attribution.py tests/test_verify_incremental_commit_attribution.py`
- [x] `python -m black --check scripts/verify_incremental_commit_attribution.py tests/test_verify_incremental_commit_attribution.py`
- [x] `python -m pytest tests/test_verify_incremental_commit_attribution.py -q`

## Phase 177: Safe Commit Attribution Base-Switch Planner (2026-03-08)
- [x] Add a non-destructive planner:
- [x] `scripts/plan_commit_attribution_base_switch.py`
- [x] planner proves:
- [x] current missing-trailer count
- [x] backfill missing-trailer count
- [x] tree equivalence
- [x] dirty worktree state
- [x] planner emits a recommendation instead of mutating refs
- [x] Recommendation states are explicit:
- [x] `no_switch_needed`
- [x] `backfill_branch_not_viable`
- [x] `manual_review_required`
- [x] `defer_until_worktree_clean`
- [x] `continue_from_backfill_branch`
- [x] Add regressions:
- [x] `tests/test_plan_commit_attribution_base_switch.py`
- [x] dirty tree -> defer
- [x] clean + tree_equal + clean backfill -> continue from backfill
- [x] tree mismatch -> manual review
- [x] main writes artifact
- [x] Update operator docs:
- [x] `docs/status/README.md`
- [x] `docs/governance/COMMUNICATION_STANDARD.md`
- [x] `docs/plans/commit_attribution_base_switch_addendum_2026-03-08.md`
- [x] Live proof:
- [x] `python scripts/plan_commit_attribution_base_switch.py --artifact-path docs/status/commit_attribution_base_switch_latest.json`
- [x] Outcome:
- [x] `recommendation = defer_until_worktree_clean`
- [x] `current_missing_count = 5`
- [x] `backfill_missing_count = 0`
- [x] `tree_equal = true`
- [x] `worktree.entry_count = 202`

## Phase 178: Repo Healthcheck Recovery Advice Wiring (2026-03-08)
- [x] Keep `commit_attribution` blocking semantics unchanged
- [x] Add an advisory layer instead of a second gate
- [x] `scripts/run_repo_healthcheck.py` now:
- [x] detects failing `commit_attribution`
- [x] runs `scripts/plan_commit_attribution_base_switch.py`
- [x] stores advisory detail under `recovery_advice`
- [x] writes/refreshes `docs/status/commit_attribution_base_switch_latest.json`
- [x] Extend markdown rendering:
- [x] add `## Recovery Advice` section
- [x] show recommendation + rationale + suggested commands
- [x] Add regressions:
- [x] `tests/test_run_repo_healthcheck.py` covers:
- [x] no advisory when `commit_attribution` passes
- [x] planner wiring when `commit_attribution` fails
- [x] markdown rendering of recovery advice
- [x] Validation:
- [x] `python -m ruff check scripts/run_repo_healthcheck.py tests/test_run_repo_healthcheck.py`
- [x] `python -m black --check scripts/run_repo_healthcheck.py tests/test_run_repo_healthcheck.py`
- [x] `python -m pytest tests/test_run_repo_healthcheck.py tests/test_plan_commit_attribution_base_switch.py tests/test_verify_incremental_commit_attribution.py -q`

## Phase 179: Dirty Worktree Category Planning (2026-03-08)
- [x] Upgrade `scripts/plan_commit_attribution_base_switch.py`
- [x] classify dirty paths into stable categories
- [x] report `worktree.category_counts`
- [x] report `cleanup_priority`
- [x] keep the planner non-destructive
- [x] Add regressions:
- [x] `tests/test_plan_commit_attribution_base_switch.py` now proves category parsing
- [x] dirty-worktree plan includes ordered cleanup advice
- [x] Refresh live artifact:
- [x] `python scripts/plan_commit_attribution_base_switch.py --artifact-path docs/status/commit_attribution_base_switch_latest.json`
- [x] Live outcome now explains the current blockage:
- [x] `generated_status = 48`
- [x] `tests = 48`
- [x] `scripts = 34`
- [x] `tonesoul = 30`
- [x] `docs = 18`
- [x] Validation:
- [x] `python -m ruff check scripts/plan_commit_attribution_base_switch.py tests/test_plan_commit_attribution_base_switch.py`
- [x] `python -m black --check scripts/plan_commit_attribution_base_switch.py tests/test_plan_commit_attribution_base_switch.py`
- [x] `python -m pytest tests/test_plan_commit_attribution_base_switch.py -q`

## Phase 180: Observability Import Fallback + 7D Gate Recovery (2026-03-08)
- [x] Read the public/private memory boundary docs before touching runtime:
- [x] `docs/plans/dual_repo_boundary_manifest_2026-02-21.md`
- [x] `docs/plans/dual_repo_guardrails_2026-02-21.md`
- [x] Confirm the boundary remains unchanged:
- [x] public side stays in `tonesoul/`, `tests/`, `scripts/`, `docs/status/`
- [x] private side still includes `memory/self_journal.jsonl`, `memory/agent_discussion*.jsonl`, `memory/vectors/`, `.agent/`, `obsidian-vault/`
- [x] Diagnose the real `audit_7d` blocker instead of trusting stale artifact history
- [x] Re-run:
- [x] `python -m pytest tests/test_escape_valve.py tests/test_escape_valve_runtime.py -q`
- [x] `python -m pytest tests/test_genesis_integration.py tests/test_provenance_chain.py -q`
- [x] `python -m pytest tests/test_api_server_contract.py -q`
- [x] Findings:
- [x] `XDD`, `GDD`, `CDD` are green again
- [x] the persistent blocker moved to `TDD`
- [x] the real import-time failure was `ModuleNotFoundError: structlog`
- [x] Fix `tonesoul/observability/logger.py` so structured logging degrades gracefully when `structlog` is absent
- [x] Keep `tonesoul.observability` public API unchanged
- [x] Validate the seam:
- [x] `python -m ruff check tonesoul/observability/logger.py tests/test_observability.py`
- [x] `python -m black --check tonesoul/observability/logger.py tests/test_observability.py`
- [x] `python -m pytest tests/test_observability.py tests/test_autonomous_cycle.py -q`
- [x] Full regression:
- [x] `python -m pytest tests -q -x`
- [x] `1420 passed`
- [x] Re-run repo governance gates:
- [x] `python scripts/verify_7d.py`
- [x] `audit_7d` now passes
- [x] `python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion`
- [x] `repo_healthcheck` now only fails on historical `commit_attribution`

## Phase 181: Dirty Worktree Settlement Report (2026-03-08)
- [x] Keep branch movement non-destructive
- [x] Reuse the existing commit-attribution planner's worktree categories instead of inventing a second taxonomy
- [x] Extend `scripts/plan_commit_attribution_base_switch.py` with reusable worktree helpers
- [x] Add `scripts/run_worktree_settlement_report.py`
- [x] Convert dirty paths into settlement lanes:
- [x] `refreshable_artifacts`
- [x] `private_memory_review`
- [x] `public_contract_docs`
- [x] `runtime_source_changes`
- [x] `experimental_misc_review`
- [x] Emit fresh artifacts:
- [x] `docs/status/worktree_settlement_latest.json`
- [x] `docs/status/worktree_settlement_latest.md`
- [x] Document the operator entrypoint:
- [x] `docs/status/README.md`
- [x] `docs/plans/worktree_settlement_mainline_addendum_2026-03-08.md`
- [x] Add regressions:
- [x] `tests/test_run_worktree_settlement_report.py`
- [x] dirty report groups entries into lanes
- [x] clean worktree returns `overall_ok=true`
- [x] strict mode writes artifacts and exits non-zero while settlement is incomplete
- [x] Validation:
- [x] `python -m ruff check scripts/plan_commit_attribution_base_switch.py scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py`
- [x] `python -m black scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py`
- [x] `python -m pytest tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py tests/test_run_repo_healthcheck.py -q`
- [x] Live proof:
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] Live outcome:
- [x] `entry_count = 209`
- [x] `active_lane_count = 5`
- [x] largest lane is `runtime_source_changes = 122`
- [x] branch movement remains blocked until settlement completes

## Phase 182: Status Artifact Taxonomy Refinement (2026-03-08)
- [x] Fix over-broad `docs/status/` classification in `scripts/plan_commit_attribution_base_switch.py`
- [x] Keep generated artifacts machine-classified:
- [x] nested `docs/status/*/` runtime artifact folders
- [x] flat `*.json`, `*.jsonl`, `*.html`, `*.csv`, `*.mmd`
- [x] flat `*_latest.md` and `*_report.md`
- [x] Reclassify authored status docs back to `docs`
- [x] especially `docs/status/README.md`
- [x] Add regression:
- [x] `tests/test_plan_commit_attribution_base_switch.py` proves README and manifesto-style docs are not `generated_status`
- [x] Validation:
- [x] `python -m ruff check scripts/plan_commit_attribution_base_switch.py tests/test_plan_commit_attribution_base_switch.py scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py`
- [x] `python -m black --check scripts/plan_commit_attribution_base_switch.py tests/test_plan_commit_attribution_base_switch.py scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py`
- [x] `python -m pytest tests/test_plan_commit_attribution_base_switch.py tests/test_run_worktree_settlement_report.py -q`
- [x] Live refresh:
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] Live outcome:
- [x] `generated_status` dropped from `50` to `47`
- [x] `docs` rose from `19` to `22`
- [x] `docs/status/README.md` now appears in `public_contract_docs`, not `refreshable_artifacts`

## Phase 183: Refreshable Artifact Lane Decomposition (2026-03-08)
- [x] Add `scripts/run_refreshable_artifact_report.py`
- [x] Read dirty worktree entries through the existing planner taxonomy
- [x] Limit scope to `generated_status` + `reports`
- [x] Classify refreshable lane entries into:
- [x] `known_generated`
- [x] `manual_report_input`
- [x] `status_folder`
- [x] `generated_status_artifact`
- [x] Map known producers back to concrete commands where the repo already has a stable generator
- [x] Include `reports/model_comparison_latest.* -> python experiments/compare_model_reports.py`
- [x] Keep `reports/analysis_gpt53.md` and `reports/analysis_gpt54.md` as manual review inputs
- [x] Add regressions:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] known generated artifacts become `regenerate`
- [x] manual report inputs become `manual_review`
- [x] non-refreshable docs like `docs/status/README.md` stay out of the report
- [x] strict mode writes artifacts and exits non-zero while the lane is still dirty
- [x] Update operator docs:
- [x] `docs/status/README.md`
- [x] Validation:
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py scripts/plan_commit_attribution_base_switch.py scripts/run_worktree_settlement_report.py`
- [x] `python -m black scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py -q`
- [x] Live proof:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] Live outcome:
- [x] `entry_count = 51`
- [x] `regenerate_count = 28`
- [x] `manual_review_count = 2`
- [x] `inspect_count = 21`
- [x] `reports/analysis_gpt53.md` and `reports/analysis_gpt54.md` are no longer implicitly treated as disposable refreshable output

## Phase 184: Refreshable Namespace Convergence (2026-03-08)
- [x] Extend `scripts/run_refreshable_artifact_report.py` with stable producers for root dream/runtime artifacts
- [x] Map generic latest artifacts back to concrete producers:
- [x] `docs/status/autonomous_registry_schedule_latest.json`
- [x] `docs/status/dream_wakeup_snapshot_latest.json`
- [x] `docs/status/dream_observability_latest.*`
- [x] `docs/status/commit_attribution_backfill_branch.json`
- [x] Add namespace semantics instead of treating all status folders as opaque inspect items
- [x] `docs/status/runtime_probe_watch/` -> managed operational namespace
- [x] `docs/status/true_verification_weekly/` -> managed operational namespace
- [x] `docs/status/probe_*/` -> archiveable historical probe namespace
- [x] Classify the report's own `refreshable_artifact_report_latest.*` outputs as self-regenerating artifacts
- [x] Update operator docs:
- [x] `docs/status/README.md`
- [x] Add regressions:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] known namespace regeneration is distinct from direct file regeneration
- [x] historical probe folders become `archive_or_drop`
- [x] Validation:
- [x] `python -m black --check scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py -q`
- [x] Live proof:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] Live outcome:
- [x] `entry_count = 53`
- [x] `regenerate_count = 35`
- [x] `namespace_regenerate_count = 2`
- [x] `archive_or_drop_count = 14`
- [x] `inspect_count = 0`
- [x] `probe_*` is no longer mixed with live operational namespaces or orphan-artifact ambiguity

## Phase 185: Private Memory Review Convergence (2026-03-08)
- [x] Add `scripts/run_private_memory_review_report.py`
- [x] Read dirty `memory` entries through the existing planner taxonomy
- [x] Classify private memory artifacts by settlement semantics instead of treating `memory = 5` as one opaque blocker
- [x] `memory/architecture_reflection_*.md` -> `mirror_then_archive`
- [x] `memory/crystals.jsonl` -> `mirror_then_archive`
- [x] `memory/antigravity_*.md` -> `archive_to_private`
- [x] `memory/autonomous/` -> `archive_to_private`
- [x] Add regressions:
- [x] `tests/test_run_private_memory_review_report.py`
- [x] mirrorable governance memory and private journals have different dispositions
- [x] `memory/autonomous/` is treated as private runtime evidence, not as an inspect bucket
- [x] Update operator docs:
- [x] `docs/status/README.md`
- [x] Validation:
- [x] `python -m black scripts/run_private_memory_review_report.py tests/test_run_private_memory_review_report.py`
- [x] `python -m ruff check scripts/run_private_memory_review_report.py tests/test_run_private_memory_review_report.py`
- [x] `python -m pytest tests/test_run_private_memory_review_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py -q`
- [x] Live proof:
- [x] `python scripts/run_private_memory_review_report.py`
- [x] Live outcome:
- [x] `entry_count = 5`
- [x] `mirror_then_archive_count = 2`
- [x] `archive_to_private_count = 3`
- [x] `inspect_count = 0`
- [x] private memory is no longer a generic worktree blocker; it is now an explicit archive-vs-mirror decision

## Phase 186: Runtime Source Grouping Convergence (2026-03-08)
- [x] Add `scripts/run_runtime_source_change_report.py`
- [x] Group runtime-lane categories into reviewable change groups instead of one opaque `runtime_source_changes` lane
- [x] Cover the live runtime lane with explicit groups:
- [x] `repo_governance_and_settlement`
- [x] `skill_and_registry_contracts`
- [x] `governance_pipeline_and_llm`
- [x] `perception_and_memory_ingest`
- [x] `autonomous_verification_runtime`
- [x] `api_contract_surface`
- [x] `supporting_runtime_and_math`
- [x] `tooling_and_editor_contract`
- [x] Drive `ungrouped_runtime_drift` to zero on the live worktree
- [x] Add regressions:
- [x] `tests/test_run_runtime_source_change_report.py`
- [x] grouped runtime paths land in the expected changesets
- [x] true unknown runtime files still surface as `ungrouped_runtime_drift`
- [x] strict mode writes artifacts and exits non-zero while runtime-source drift remains
- [x] Update operator docs:
- [x] `docs/status/README.md`
- [x] `docs/plans/runtime_source_grouping_addendum_2026-03-08.md`
- [x] Validation:
- [x] `python -m black --check scripts/run_runtime_source_change_report.py tests/test_run_runtime_source_change_report.py`
- [x] `python -m ruff check scripts/run_runtime_source_change_report.py tests/test_run_runtime_source_change_report.py`
- [x] `python -m pytest tests/test_run_runtime_source_change_report.py tests/test_run_private_memory_review_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py -q`
- [x] Live proof:
- [x] `python scripts/run_runtime_source_change_report.py`
- [x] Live outcome:
- [x] `entry_count = 128`
- [x] `group_count = 8`
- [x] `ungrouped_count = 0`
- [x] the largest runtime groups are now explicit review units instead of one anonymous dirty lane

## Phase 187: Repo Governance Settlement Truth (2026-03-08)
- [x] Add `scripts/run_repo_governance_settlement_report.py`
- [x] Read repo-governance convergence from existing truth artifacts instead of creating another heavyweight healthcheck
- [x] Compose:
- [x] `docs/status/repo_healthcheck_latest.json`
- [x] `docs/status/commit_attribution_base_switch_latest.json`
- [x] `docs/status/runtime_source_change_groups_latest.json`
- [x] Distinguish settlement states:
- [x] `green`
- [x] `runtime_blocked`
- [x] `runtime_green_metadata_blocked`
- [x] Expose when `commit_attribution` is the only failing gate and the backfill branch is already tree-equivalent
- [x] Add regressions:
- [x] `tests/test_run_repo_governance_settlement_report.py`
- [x] metadata-only blocker case
- [x] non-metadata blocker case
- [x] strict mode writes artifacts and exits non-zero while not fully green
- [x] Wire the new report back into repo settlement tooling:
- [x] `scripts/run_runtime_source_change_report.py`
- [x] `scripts/run_refreshable_artifact_report.py`
- [x] `docs/status/README.md`
- [x] Fix the follow-on hygiene regression in the same phase:
- [x] register `private_memory_review_latest.*` and `runtime_source_change_groups_latest.*` as refreshable known-generated artifacts
- [x] keep `refreshable_artifact_report_latest.inspect_count = 0`
- [x] Add theory note:
- [x] `docs/plans/repo_governance_settlement_addendum_2026-03-08.md`
- [x] Validation:
- [x] `python -m black --check scripts/run_repo_governance_settlement_report.py tests/test_run_repo_governance_settlement_report.py scripts/run_refreshable_artifact_report.py scripts/run_runtime_source_change_report.py tests/test_run_runtime_source_change_report.py`
- [x] `python -m ruff check scripts/run_repo_governance_settlement_report.py tests/test_run_repo_governance_settlement_report.py scripts/run_refreshable_artifact_report.py scripts/run_runtime_source_change_report.py tests/test_run_runtime_source_change_report.py`
- [x] `python -m pytest tests/test_run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_runtime_source_change_report.py tests/test_run_private_memory_review_report.py tests/test_run_worktree_settlement_report.py tests/test_plan_commit_attribution_base_switch.py -q`
- [x] Live proof:
- [x] `python scripts/run_repo_governance_settlement_report.py`
- [x] `python scripts/run_runtime_source_change_report.py`
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] Live outcome:
- [x] `repo_healthcheck`: `19 pass`, `1 fail`
- [x] only failing check: `commit_attribution`
- [x] settlement status: `runtime_green_metadata_blocked`
- [x] repo governance group: `24` dirty entries
- [x] runtime source groups: `entry_count = 130`, `group_count = 8`, `ungrouped_count = 0`
- [x] refreshable artifact report: `entry_count = 59`, `regenerate_count = 41`, `inspect_count = 0`
- [x] repo governance convergence is now machine-readable and no longer collapses runtime truth into metadata debt

## Phase 188: Schema-Backed LLM Observability Contract (2026-03-09)
- [x] Narrow the next `governance_pipeline_and_llm` phase to one internal contract seam
- [x] Do not touch external response shape for `dispatch_trace["llm"]` or dream collision observability
- [x] Add canonical schema-backed builders in `tonesoul/schemas.py`
- [x] `LLMUsageTrace`
- [x] `LLMObservabilityTrace`
- [x] Normalize runtime LLM observability through one builder in both producers:
- [x] `UnifiedPipeline._attach_llm_observability()`
- [x] `DreamEngine._build_llm_observability()`
- [x] Keep emitted payload backward-compatible:
- [x] `backend`
- [x] `model`
- [x] optional `usage`
- [x] Add regressions:
- [x] `tests/test_schemas.py`
- [x] metrics-backed observability payload
- [x] fallback-model path without fabricated usage
- [x] Re-run runtime regressions that depend on the same payload shape:
- [x] `tests/test_unified_pipeline_v2_runtime.py`
- [x] `tests/test_dream_engine.py`
- [x] Record the larger deferred risk rather than widening this phase:
- [x] `CouncilVerdict` schema name still does not equal the external runtime/API verdict payload
- [x] Add theory note:
- [x] `docs/plans/llm_observability_contract_addendum_2026-03-09.md`
- [x] Validation:
- [x] `python -m black tonesoul/schemas.py tonesoul/unified_pipeline.py tonesoul/dream_engine.py tests/test_schemas.py`
- [x] `python -m ruff check tonesoul/schemas.py tonesoul/unified_pipeline.py tonesoul/dream_engine.py tests/test_schemas.py`
- [x] `python -m pytest tests/test_schemas.py tests/test_unified_pipeline_v2_runtime.py tests/test_dream_engine.py -q`
- [x] Live outcome:
- [x] one canonical builder now owns the internal `llm` observability shape across pipeline and dream runtime
- [x] targeted regressions stayed green: `35 passed`
- [x] the runtime trace seam was tightened without changing its externally consumed payload shape

## Phase 189: Council Structured Parse Boundary Recovery (2026-03-09)
- [x] Narrow the next `governance_pipeline_and_llm` phase to one verdict-affecting seam
- [x] Preserve weak-model text fallback while preventing valid structured JSON from falling through into keyword parsing
- [x] Replace greedy JSON object extraction in `tonesoul/safe_parse.py` with balanced extraction
- [x] Add regressions:
- [x] `tests/test_schemas.py`
- [x] valid JSON plus trailing brace-bearing noise still parses the structured object
- [x] `tests/test_perspective_factory.py`
- [x] a perspective vote stays `APPROVE` when trailing `{OBJECT}` text follows valid JSON
- [x] Keep non-JSON text fallback behavior intact
- [x] Add theory note:
- [x] `docs/plans/council_structured_parse_boundary_addendum_2026-03-09.md`
- [x] Record the seam as runtime-behavioral, not just observability/hygiene
- [x] Validation:
- [x] `python -m black --check tonesoul/safe_parse.py tests/test_schemas.py tests/test_perspective_factory.py`
- [x] `python -m ruff check tonesoul/safe_parse.py tests/test_schemas.py tests/test_perspective_factory.py`
- [x] `python -m pytest tests/test_schemas.py tests/test_perspective_factory.py -q`
- [x] Combined safety regression:
- [x] `python -m pytest tests/test_schemas.py tests/test_unified_pipeline_v2_runtime.py tests/test_dream_engine.py tests/test_perspective_factory.py -q`
- [x] Live outcome:
- [x] structured council parsing now prefers the first valid balanced JSON object
- [x] trailing `OBJECT` noise no longer overrides a valid structured `APPROVE` vote
- [x] combined targeted regressions stayed green: `49 passed`

## Phase 191: Council Structured / Runtime Verdict Boundary (2026-03-09)
- [x] Narrow the next `governance_pipeline_and_llm` phase to the internal-vs-runtime council verdict validation seam
- [x] Reframe the structured schema as `CouncilStructuredVerdict` in `tonesoul/schemas.py`
- [x] Keep `CouncilVerdict` importable as a compatibility alias
- [x] Make the structured verdict schema fail fast on runtime-only fields via `extra="forbid"`
- [x] Add regressions:
- [x] structured schema rejects outward runtime-style verdict payloads
- [x] legacy `CouncilVerdict` alias still works for structured callers
- [x] runtime verdict normalization remains stable for:
- [x] `tests/test_unified_pipeline_v2_runtime.py`
- [x] `tests/test_api_chat_council_mode.py`
- [x] Fix the dormant `UnifiedPipeline` import blocker surfaced by broader validation
- [x] repair broken indentation under `if semantic_graph_summary:`
- [x] Add theory note:
- [x] `docs/plans/council_structured_runtime_boundary_addendum_2026-03-09.md`
- [x] Validation:
- [x] `python -m black --check tonesoul/schemas.py tonesoul/unified_pipeline.py tests/test_schemas.py tests/test_unified_pipeline_v2_runtime.py tests/test_api_chat_council_mode.py`
- [x] `python -m ruff check tonesoul/schemas.py tonesoul/unified_pipeline.py tests/test_schemas.py tests/test_unified_pipeline_v2_runtime.py tests/test_api_chat_council_mode.py`
- [x] `python -m pytest tests/test_schemas.py tests/test_unified_pipeline_v2_runtime.py tests/test_api_chat_council_mode.py -q`
- [x] Full regression:
- [x] `python -m pytest tests -q`
- [x] Live outcome:
- [x] internal structured verdict validation no longer silently accepts outward runtime verdict payloads
- [x] outward `council_verdict` runtime/API shape stayed compatible
- [x] full regression stayed green: `1445 passed`

## Phase 192: Memory Subjectivity Layer Model (2026-03-09)
- [x] Write a theory note for ToneSoul memory subjectivity instead of widening runtime code first
- [x] Define the canonical promotion ladder:
- [x] `event -> meaning -> tension -> vow -> identity`
- [x] Clarify what each layer means and what it must not be confused with
- [x] Tie the ladder back to existing memory governance seams:
- [x] `provenance`
- [x] `confidence`
- [x] `promotion_gate`
- [x] `decay_policy`
- [x] Clarify the public/private boundary:
- [x] raw journals, `soul.db`, scheduler state, and transient artifacts are not automatically identity memory
- [x] Record the architectural implication:
- [x] `MemoryWriteGateway` is an admissibility seam, not a final identity writer
- [x] Add theory note:
- [x] `docs/plans/memory_subjectivity_layer_addendum_2026-03-09.md`
- [x] Validation:
- [x] `rg -n "event -> meaning -> tension -> vow -> identity|provenance|promotion_gate|decay_policy|MemoryWriteGateway" docs/plans/memory_subjectivity_layer_addendum_2026-03-09.md task.md`

## Phase 193: Memory Subjectivity Contract Split (2026-03-10)
- [x] Write an implementation addendum before changing runtime code
- [x] Record the key architectural split:
- [x] `MemoryLayer` remains the storage axis
- [x] `subjectivity_layer` becomes a separate semantic promotion axis
- [x] Define the minimal shared contract:
- [x] `subjectivity_layer`
- [x] `confidence`
- [x] `provenance`
- [x] `promotion_gate`
- [x] `decay_policy`
- [x] `source_record_ids`
- [x] Map the contract onto current seams:
- [x] `MemoryWriteGateway`
- [x] `SoulDB`
- [x] `Consolidator`
- [x] `DreamEngine`
- [x] `schemas.py`
- [x] Record the migration order so the repo does not widen runtime and storage semantics in one step
- [x] Add implementation note:
- [x] `docs/plans/memory_subjectivity_contract_addendum_2026-03-10.md`
- [x] Validation:
- [x] `rg -n "subjectivity_layer|MemoryLayer|MemoryWriteGateway|SoulDB|Consolidator|DreamEngine|schemas.py|promotion_gate|decay_policy" docs/plans/memory_subjectivity_contract_addendum_2026-03-10.md task.md`

## Phase 194: Subjectivity Layer Schema + Gateway Guard (2026-03-10)
- [x] Add schema-backed subjectivity contract in `tonesoul/schemas.py`
- [x] Define `SubjectivityLayer`
- [x] Define `MemorySubjectivityPayload.normalize_fields()`
- [x] Keep the seam narrow:
- [x] validate only subjectivity-related fields
- [x] do not widen `SoulDB` schema yet
- [x] teach `MemoryWriteGateway` to normalize subjectivity fields before persistence
- [x] fail closed on invalid subjectivity payloads
- [x] block direct `vow` / `identity` writes unless a review-strength `promotion_gate` is present
- [x] add regressions:
- [x] `tests/test_schemas.py`
- [x] subjectivity field normalization
- [x] invalid layer rejection
- [x] `tests/test_write_gateway.py`
- [x] normalized tension write
- [x] vow rejected without review gate
- [x] vow accepted with review gate
- [x] invalid subjectivity layer rejected by gateway
- [x] Focused validation:
- [x] `python -m pytest tests/test_schemas.py tests/test_write_gateway.py tests/test_memory_write_gateway.py -q --tb=short`
- [x] `ruff check tonesoul/schemas.py tonesoul/memory/write_gateway.py tests/test_schemas.py tests/test_write_gateway.py tests/test_memory_write_gateway.py`

## Phase 195: Context + Long-Horizon Memory Alignment (2026-03-10)
- [x] Write one explicit context / roadmap note so memory-subjectivity work does not fragment across addenda
- [x] Record the current validated baseline:
- [x] subjectivity philosophy + contract split + gateway guard are complete
- [x] full regression baseline is `1463 passed`
- [x] Record what is not done yet:
- [x] no producer wiring yet
- [x] no reviewed promotion lane yet
- [x] no `SoulDB` schema widening yet
- [x] no subjectivity-aware retrieval yet
- [x] Define the long-horizon order:
- [x] producer wiring
- [x] reviewable promotion
- [x] retrieval/reporting
- [x] optional persistence/index upgrade
- [x] private-lane integration
- [x] Cross-check the plan against `MEMORY.md`
- [x] public repo keeps contract/schema/tests/docs
- [x] private repo keeps raw memory corpus and sensitive runtime evidence
- [x] Cross-check current repo reality against `private_memory_review`
- [x] `memory/crystals.jsonl` remains `mirror_then_archive`, not precedent for more public memory data
- [x] Add roadmap note:
- [x] `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
- [x] Validation:
- [x] `rg -n "1463 passed|MEMORY.md|memory/crystals.jsonl|mirror_then_archive|subjectivity_layer|MemoryLayer|producer wiring|reviewable promotion|SoulDB" docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md task.md docs/status/private_memory_review_latest.md`

## Phase 196: Subjectivity Producer Wiring (2026-03-10)
- [x] Keep the next runtime step narrow:
- [x] producer wiring only
- [x] no `vow` / `identity` auto-promotion
- [x] wire `DreamEngine` persisted collisions to emit subjectivity candidates:
- [x] `subjectivity_layer = tension`
- [x] `source_record_ids = [stimulus_record_id]`
- [x] candidate `promotion_gate`
- [x] candidate `decay_policy`
- [x] wire `sleep_consolidate()` promoted payloads to emit subjectivity candidates:
- [x] preserve existing `subjectivity_layer` if already present
- [x] otherwise infer `event` / `meaning` / `tension` without changing storage-layer classification
- [x] add candidate `promotion_gate`
- [x] add source linkage when `record_id` exists
- [x] add regressions:
- [x] `tests/test_dream_engine.py`
- [x] persisted collision carries subjectivity candidate fields
- [x] `tests/test_ai_sleep.py`
- [x] promoted payload gains subjectivity candidate fields
- [x] existing subjectivity layer is preserved through consolidation
- [x] Focused validation:
- [x] `python -m pytest tests/test_dream_engine.py tests/test_ai_sleep.py tests/test_schemas.py tests/test_write_gateway.py -q --tb=short`
- [x] `ruff check tonesoul/dream_engine.py tonesoul/memory/consolidator.py tests/test_dream_engine.py tests/test_ai_sleep.py`

## Phase 197: Reviewable Tension-to-Vow Lane (2026-03-10)
- [x] Keep the next step explicit:
- [x] no auto-promotion into `vow`
- [x] define reviewable promotion metadata in `tonesoul/schemas.py`
- [x] add `SubjectivityPromotionStatus`
- [x] add `SubjectivityPromotionGate`
- [x] require `review_basis` for review-strength `vow` writes in `MemoryWriteGateway`
- [x] add reviewed promotion helpers in `tonesoul/memory/consolidator.py`
- [x] `build_reviewed_vow_payload(...)`
- [x] `promote_reviewed_tension_to_vow(...)`
- [x] keep the contract split explicit:
- [x] `subjectivity_layer` becomes `vow`
- [x] storage `layer` becomes `factual`
- [x] reject non-tension sources for reviewed vow promotion
- [x] add regressions:
- [x] `tests/test_schemas.py`
- [x] review metadata normalization
- [x] `tests/test_write_gateway.py`
- [x] vow review gate without `review_basis` is rejected
- [x] `tests/test_ai_sleep.py`
- [x] reviewed vow payload builder works
- [x] reviewed vow persistence through gateway works
- [x] non-tension reviewed promotion is rejected
- [x] Add implementation note:
- [x] `docs/plans/memory_subjectivity_reviewable_promotion_addendum_2026-03-10.md`
- [x] Focused validation:
- [x] `python -m pytest tests/test_schemas.py tests/test_write_gateway.py tests/test_ai_sleep.py -q --tb=short`
- [x] `ruff check tonesoul/schemas.py tonesoul/memory/write_gateway.py tonesoul/memory/consolidator.py tonesoul/memory/__init__.py tests/test_schemas.py tests/test_write_gateway.py tests/test_ai_sleep.py`

## Phase 198: Subjectivity Retrieval + Reporting (2026-03-10)
- [x] Keep Phase C observational:
- [x] no HTTP/API widening
- [x] no subjectivity-ranked recall yet
- [x] add internal reporting helpers in `tonesoul/memory/subjectivity_reporting.py`
- [x] `summarize_subjectivity_distribution(...)`
- [x] `list_subjectivity_records(...)`
- [x] define unresolved tension as:
- [x] `subjectivity_layer == tension`
- [x] and `promotion_gate` below review-strength status
- [x] export reporting helpers from `tonesoul/memory/__init__.py`
- [x] add regressions:
- [x] `tests/test_subjectivity_reporting.py`
- [x] distribution summary includes memory-layer / subjectivity-layer / promotion-status counts
- [x] unresolved tension inspection filters reviewed tension traces out
- [x] Add implementation note:
- [x] `docs/plans/memory_subjectivity_reporting_addendum_2026-03-10.md`
- [x] Keep context roadmap current:
- [x] `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
- [x] Focused validation:
- [x] `python -m pytest tests/test_subjectivity_reporting.py tests/test_ai_sleep.py tests/test_schemas.py tests/test_write_gateway.py -q --tb=short`
- [x] `ruff check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/__init__.py tests/test_subjectivity_reporting.py`

## Phase 199: Runtime Subjectivity Summary Wiring (2026-03-10)
- [x] Keep the next step as runtime reporting only:
- [x] no new retrieval policy
- [x] no HTTP/API widening
- [x] teach `sleep_consolidate()` to emit `subjectivity_summary` inside `SleepResult`
- [x] keep `layer_summary` intact
- [x] reuse `summarize_subjectivity_distribution(...)` instead of duplicating counting logic
- [x] teach `AutonomousWakeupLoop` to surface high-signal subjectivity counts:
- [x] `consolidation_unresolved_tension_count`
- [x] `consolidation_vow_count`
- [x] add regressions:
- [x] `tests/test_ai_sleep.py`
- [x] `SleepResult` includes subjectivity summary after consolidation
- [x] `tests/test_wakeup_loop.py`
- [x] wakeup summary includes unresolved tension / vow counts from consolidation payload
- [x] Add implementation note:
- [x] `docs/plans/memory_subjectivity_runtime_summary_addendum_2026-03-10.md`
- [x] Keep context roadmap current:
- [x] `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
- [x] Focused validation:
- [x] `python -m pytest tests/test_ai_sleep.py tests/test_wakeup_loop.py tests/test_subjectivity_reporting.py -q --tb=short`
- [x] `ruff check tonesoul/memory/consolidator.py tonesoul/wakeup_loop.py tests/test_ai_sleep.py tests/test_wakeup_loop.py`

## Phase 200: Consolidated Implementation Plan + Scope Boundary (2026-03-10)
- [x] Stop scattering subjectivity execution logic across parallel addenda
- [x] write one canonical plan-of-record document:
- [x] `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`
- [x] consolidate:
- [x] execution order
- [x] deferred directions
- [x] reasons for deferral
- [x] write explicit scope boundary:
- [x] what this work is
- [x] what this work is not
- [x] why it is not yet an AGI claim
- [x] keep the context roadmap aligned with the new plan-of-record:
- [x] `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
- [x] keep the addenda as background rationale, not competing plans
- [x] fold the Phase 140 / RMM / `CODEX_TASK.md` reading back into the plan-of-record
- [x] keep one explicit builder note in the plan so the current architectural instinct is recorded
- [x] Full validation before doc-only commit:
- [x] `python -m pytest tests/ -x --tb=short -q`
- [x] `ruff check tonesoul tests`

## Phase 201: Mirror Schema Contract (2026-03-10)
- [x] Start Phase 140 sequentially from Task A
- [x] extend `tonesoul/schemas.py` with:
- [x] `MirrorDelta`
- [x] `DualTrackResponse`
- [x] keep the contract narrow:
- [x] reuse existing `TensionSnapshot`
- [x] reuse existing `GovernanceDecision`
- [x] keep `subjectivity_flags` on `SubjectivityLayer`
- [x] normalize `final_choice` to `raw | governed | synthesized`
- [x] export the new schema models in `__all__`
- [x] add schema regressions in `tests/test_schemas.py`
- [x] nested mirror delta serializes cleanly
- [x] dual-track response stays JSON-safe

## Phase 202: ToneSoulMirror Core (2026-03-10)
- [x] Continue Phase 140 sequentially into Task B
- [x] add `tonesoul/mirror.py`
- [x] implement `ToneSoulMirror.reflect(...)`
- [x] keep the mirror deterministic:
- [x] no new LLM calls
- [x] graceful fallback when engine/kernel is unavailable
- [x] governed projection only differs when governance threshold is crossed
- [x] implement `_apply_governance(...)`
- [x] implement `_compute_delta(...)`
- [x] keep mirror output on existing contracts:
- [x] `DualTrackResponse`
- [x] `MirrorDelta`
- [x] add regressions in `tests/test_mirror.py`
- [x] passthrough low-tension path
- [x] triggered high-tension path
- [x] graceful no-engine fallback
- [x] dual-track payload stays JSON-serializable

## Phase 203: UnifiedPipeline Mirror Step (2026-03-10)
- [x] Continue Phase 140 sequentially into Task C
- [x] keep mirror wiring opt-in with `mirror_enabled=False` by default
- [x] add lazy runtime mirror construction in `UnifiedPipeline`
- [x] run mirror after response shaping, without introducing any new LLM call
- [x] surface mirror traces in runtime payloads:
- [x] `dispatch_trace["mirror"]`
- [x] `trajectory_analysis["mirror"]`
- [x] `trajectory_analysis["mirror_delta"]`
- [x] keep final response aligned with mirror final choice when enabled
- [x] move `trajectory.add_turn(...)` to record the post-mirror final response
- [x] add regressions in `tests/test_unified_pipeline_v2_runtime.py`
- [x] default path does not invoke mirror
- [x] enabled path surfaces mirror delta and governed final response

## Phase 204: Mirror Memory Recording (2026-03-10)
- [x] Continue Phase 140 sequentially into Task D
- [x] keep mirror persistence behind an explicit helper:
- [x] `ToneSoulMirror.record_delta(...)`
- [x] only persist when `mirror_triggered=True`
- [x] route writes through `MemoryWriteGateway`
- [x] keep payload inside existing subjectivity contract:
- [x] `type=mirror_delta`
- [x] `subjectivity_layer=tension`
- [x] candidate `promotion_gate`
- [x] explicit provenance + evidence
- [x] add regressions in `tests/test_mirror.py`
- [x] untriggered delta skips writes
- [x] triggered delta writes a gateway-valid payload

## Phase 205: Mirror + Subjectivity Soul-Lens Settlement (2026-03-10)
- [x] settle the current branch context after Phase 140 completion
- [x] update the canonical plan of record:
- [x] `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`
- [x] record the Yuhun / soul-lens reading of what mirror changed
- [x] make the new runtime boundary explicit:
- [x] mirror is a reflective surface, not a second generator
- [x] mirror traces can become candidate tension memory
- [x] mirror does not grant vow / identity legitimacy
- [x] update the context roadmap snapshot:
- [x] `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
- [x] fold Phase 140 completion into current validated baseline and runtime meaning

## Phase 206: Canonical Reviewed-Promotion Workflow Foundation (2026-03-10)
- [x] start `Step 1` from the implementation plan of record
- [x] define a canonical review actor contract in `tonesoul/schemas.py`
- [x] define a canonical reviewed-promotion decision artifact in `tonesoul/schemas.py`
- [x] add a dedicated workflow seam in `tonesoul/memory/reviewed_promotion.py`
- [x] centralize:
- [x] `build_reviewed_promotion_decision(...)`
- [x] `build_reviewed_promotion_payload(...)`
- [x] `replay_reviewed_promotion(...)`
- [x] route legacy consolidator helper functions through the canonical workflow
- [x] preserve backward compatibility for:
- [x] `build_reviewed_vow_payload(...)`
- [x] `promote_reviewed_tension_to_vow(...)`
- [x] add regressions:
- [x] `tests/test_reviewed_promotion.py`
- [x] extend `tests/test_schemas.py`
- [x] reviewed promotion decision serializes cleanly
- [x] approved reviewed promotion replays through `MemoryWriteGateway`

## Phase 207: Subjectivity Operator Entry Surface (2026-03-10)
- [x] start `Step 2` from the implementation plan of record
- [x] add an explicit operator report seam:
- [x] `scripts/run_subjectivity_report.py`
- [x] emit JSON/Markdown artifacts for:
- [x] subjectivity distribution
- [x] unresolved tensions
- [x] reviewed vow count and recent reviewed vow rows
- [x] keep scope narrow:
- [x] no HTTP/API widening
- [x] no retrieval policy change
- [x] register the new `docs/status` artifacts in `scripts/run_refreshable_artifact_report.py`
- [x] add regressions:
- [x] `tests/test_run_subjectivity_report.py`
- [x] report warns cleanly when `soul.db` is absent
- [x] strict mode fails when unresolved tension remains pending review

## Phase 208: Google Always-On Overlap Settlement (2026-03-10)
- [x] read the Google `always-on-memory-agent` comparison through the current subjectivity plan
- [x] keep the external overlap as one input to the canonical plan, not a competing roadmap
- [x] update `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`
- [x] add a narrow position:
- [x] what can save time now
- [x] what remains deferred
- [x] what should not be copied into ToneSoul
- [x] tie the practical borrowing lane to `Step 3: Retrieval Shadow Mode`
- [x] keep `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md` aligned with the new overlap reading
- [x] preserve the existing guardrails:
- [x] no ungated direct memory writes
- [x] no UI-first detour
- [x] no multimodal expansion ahead of retrieval legitimacy
- [x] validation before doc-only commit:
- [x] `python -m pytest tests/ -x --tb=short -q`
- [x] `ruff check tonesoul tests`

## Phase 209: Retrieval Shadow Query Foundation (2026-03-10)
- [x] start `Step 3` from the implementation plan of record
- [x] keep scope observational:
- [x] no live recall rerank changes
- [x] no HTTP/API widening
- [x] add a read-only shadow retrieval seam:
- [x] `tonesoul/memory/subjectivity_shadow.py`
- [x] compare baseline `SoulDB.search()` candidates against subjectivity-aware shadow ordering
- [x] support narrow shadow profiles:
- [x] `classified_first`
- [x] `tension_first`
- [x] `reviewed_vow_first`
- [x] add an explicit operator runner:
- [x] `scripts/run_subjectivity_shadow_query.py`
- [x] emit JSON/Markdown artifacts with:
- [x] baseline results
- [x] shadow results
- [x] overlap / promoted / demoted ids
- [x] layer distribution deltas
- [x] add regressions:
- [x] `tests/test_subjectivity_shadow.py`
- [x] `tests/test_run_subjectivity_shadow_query.py`
- [x] keep the Google overlap narrow:
- [x] borrow query/report shape
- [x] do not borrow ungated memory mutation
- [x] validation before commit:
- [x] `python -m pytest tests/ -x --tb=short -q`
- [x] `ruff check tonesoul tests scripts`

## Phase 210: Retrieval Shadow Pressure Metrics (2026-03-10)
- [x] continue `Step 3` without touching live recall
- [x] add a batch pressure aggregation seam:
- [x] `build_subjectivity_shadow_pressure_report(...)`
- [x] aggregate across multiple queries:
- [x] `changed_query_rate`
- [x] `top1_changed_rate`
- [x] `pressure_query_rate`
- [x] `avg_classified_lift`
- [x] tension / reviewed-vow top1 gain counts
- [x] add an operator runner:
- [x] `scripts/run_subjectivity_shadow_pressure_report.py`
- [x] support explicit queries, query files, and a safe default query set
- [x] register latest pressure artifacts in `scripts/run_refreshable_artifact_report.py`
- [x] add regressions:
- [x] `tests/test_subjectivity_shadow.py`
- [x] `tests/test_run_subjectivity_shadow_pressure_report.py`
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] keep scope narrow:
- [x] no persistence/index widening
- [x] no live recall reranking
- [x] validation before commit:
- [x] `python -m pytest tests/ -x --tb=short -q`
- [x] `ruff check tonesoul tests scripts`

## Phase 211: Context Compression Handoff Snapshot (2026-03-10)
- [x] add one compact restart snapshot:
- [x] `docs/status/codex_subjectivity_handoff_2026-03-10.md`
- [x] record:
- [x] current branch / head
- [x] canonical read order after restart
- [x] completed phases 208-210
- [x] latest validation baseline
- [x] next step decision gate
- [x] dirty files to leave untouched
- [x] validation before doc-only commit:
- [x] `python -m pytest tests/ -x --tb=short -q`
- [x] `ruff check tonesoul tests scripts`

## Phase 212: Subjectivity Operator Review + Settlement (2026-03-10)
- [x] write one implementation addendum before runtime changes:
- [x] `docs/plans/memory_subjectivity_operator_review_settlement_addendum_2026-03-10.md`
- [x] keep scope operational:
- [x] no auto-promotion into `vow`
- [x] no `SoulDB` schema widening for subjectivity columns
- [x] add an explicit operator runner:
- [x] `scripts/run_reviewed_promotion.py`
- [x] allow review of a concrete tension record by `record_id`
- [x] preserve review actor + review basis + decision status in an auditable ledger artifact
- [x] replay approved reviewed promotions through `MemoryWriteGateway`
- [x] keep rejected / deferred reviews auditable without writing a `vow`
- [x] teach subjectivity reporting to distinguish:
- [x] unresolved tension
- [x] settled-by-review tension
- [x] reviewed vow rows
- [x] add regressions:
- [x] `tests/test_reviewed_promotion.py`
- [x] `tests/test_subjectivity_reporting.py`
- [x] `tests/test_run_reviewed_promotion.py`
- [x] `tests/test_run_subjectivity_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_reviewed_promotion.py tests/test_subjectivity_reporting.py tests/test_run_reviewed_promotion.py tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m pytest tests/test_schemas.py tests/test_reviewed_promotion.py tests/test_subjectivity_reporting.py tests/test_run_reviewed_promotion.py tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m ruff check tonesoul/schemas.py tonesoul/memory/reviewed_promotion.py tonesoul/memory/subjectivity_reporting.py tonesoul/memory/__init__.py scripts/run_reviewed_promotion.py scripts/run_subjectivity_report.py tests/test_schemas.py tests/test_reviewed_promotion.py tests/test_subjectivity_reporting.py tests/test_run_reviewed_promotion.py tests/test_run_subjectivity_report.py`
- [x] `python -m black --check tonesoul/schemas.py tonesoul/memory/reviewed_promotion.py tonesoul/memory/subjectivity_reporting.py tonesoul/memory/__init__.py scripts/run_reviewed_promotion.py scripts/run_subjectivity_report.py tests/test_schemas.py tests/test_reviewed_promotion.py tests/test_subjectivity_reporting.py tests/test_run_reviewed_promotion.py tests/test_run_subjectivity_report.py`

## Phase 213: Formal Memory Subjectivity Review Criteria (2026-03-10)
- [x] write one official criteria document:
- [x] `docs/plans/memory_subjectivity_review_criteria_2026-03-10.md`
- [x] make the document normative, not exploratory:
- [x] this is current policy, not a draft
- [x] ground the approval rule in:
- [x] `E0: Choice Before Identity`
- [x] `Axiom 4: Non-Zero Tension Principle`
- [x] `subjectivity_illusion: true`
- [x] define formal criteria for:
- [x] `approved`
- [x] `deferred`
- [x] `rejected`
- [x] make one additional guardrail explicit:
- [x] recurrence alone is insufficient without directional choice
- [x] same-source repetition is insufficient without context diversity
- [x] define grouping-first review guidance before line-by-line review
- [x] encode edge-case guardrails for:
- [x] counterfactual clarity
- [x] opposing directions inside one cluster
- [x] repeated evidence under an existing active vow
- [x] keep scope narrow:
- [x] no schema widening
- [x] no live retrieval rerank
- [x] no UI-first detour
- [x] update canonical subjectivity planning docs to point at the criteria file as the active policy
- [x] run doc-level verification with `rg`

## Phase 214: Subjectivity Tension Grouping + Triage (2026-03-10)
- [x] write one grouping addendum before runtime changes:
- [x] `docs/plans/memory_subjectivity_tension_grouping_addendum_2026-03-10.md`
- [x] keep scope read-only:
- [x] no memory mutation
- [x] no schema widening
- [x] no live retrieval rerank
- [x] add a grouping helper:
- [x] `tonesoul/memory/subjectivity_triage.py`
- [x] group unresolved tensions by:
- [x] collision lineage
- [x] topic surface
- [x] normative direction
- [x] friction band
- [x] temporal spread
- [x] expose multi-direction topics so review cannot silently merge divergent directions
- [x] add an explicit operator runner:
- [x] `scripts/run_subjectivity_tension_grouping.py`
- [x] emit JSON/Markdown artifacts with:
- [x] unresolved row count
- [x] semantic group count
- [x] lineage group count
- [x] triage recommendation per semantic group
- [x] register latest grouping artifacts in `scripts/run_refreshable_artifact_report.py`
- [x] add regressions:
- [x] `tests/test_subjectivity_triage.py`
- [x] `tests/test_run_subjectivity_tension_grouping.py`
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_triage.py tests/test_run_subjectivity_tension_grouping.py tests/test_run_refreshable_artifact_report.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_triage.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_triage.py tests/test_run_subjectivity_tension_grouping.py tests/test_run_refreshable_artifact_report.py`
- [x] generate the latest grouping artifact from real `memory/soul.db`
- [x] real queue result: `32 unresolved -> 2 semantic groups -> 7 lineage groups`
- [x] real triage result: `1 reject_review` group + `1 defer_review` group

## Phase 215: Subjectivity Group Review Lane (2026-03-10)
- [x] make the semantic group an executable review unit instead of a report-only unit
- [x] add a dry-run/apply operator script:
- [x] `scripts/run_subjectivity_group_review.py`
- [x] reuse the canonical reviewed-promotion seam instead of inventing a second write path
- [x] allow one decision to be applied across all rows in one semantic group
- [x] keep the output stdout-only because it mutates review state
- [x] add regressions:
- [x] `tests/test_run_subjectivity_group_review.py`
- [x] patch direct script execution seams so operator scripts work from the repo root:
- [x] `scripts/run_subjectivity_tension_grouping.py`
- [x] `scripts/run_subjectivity_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_subjectivity_group_review.py tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_subjectivity_group_review.py tests/test_run_subjectivity_group_review.py scripts/run_subjectivity_report.py tests/test_run_subjectivity_report.py`
- [x] run one real low-risk group review against `memory/soul.db`
- [x] reject the `12`-row same-source OSV data-sources cluster
- [x] rerun latest report artifacts after the real review
- [x] post-review real state: `20 unresolved tension`, `12 settled tension`, `0 reviewed vow`
- [x] decide whether the remaining `20`-row broader OSV homepage cluster should be written as explicit `deferred`, or stay observational until report surfaces deferred-pending counts

## Phase 216: Subjectivity Review Batch Artifact (2026-03-10)
- [x] write one addendum before runtime changes:
- [x] `docs/plans/memory_subjectivity_review_batch_artifact_addendum_2026-03-10.md`
- [x] keep scope read-only:
- [x] no review-state mutation
- [x] no schema widening
- [x] no live retrieval rerank
- [x] add one queue helper:
- [x] `tonesoul/memory/subjectivity_review_batch.py`
- [x] convert semantic groups into operator review packets with:
- [x] default review status if confirmed
- [x] representative record ids by lineage
- [x] reusable review basis template
- [x] add one operator runner:
- [x] `scripts/run_subjectivity_review_batch.py`
- [x] emit refreshable JSON/Markdown artifacts for the current review queue
- [x] register latest batch artifacts in `scripts/run_refreshable_artifact_report.py`
- [x] add regressions:
- [x] `tests/test_subjectivity_review_batch.py`
- [x] `tests/test_run_subjectivity_review_batch.py`
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_refreshable_artifact_report.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_review_batch.py tonesoul/memory/__init__.py scripts/run_subjectivity_review_batch.py scripts/run_refreshable_artifact_report.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_review_batch.py tonesoul/memory/__init__.py scripts/run_subjectivity_review_batch.py scripts/run_refreshable_artifact_report.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_refreshable_artifact_report.py`
- [x] generate the latest review-batch artifact from real `memory/soul.db`
- [x] latest queue result after the already-settled same-source reject cluster: `20 unresolved -> 1 defer_review group -> 6 representative record ids`

## Phase 217: Deferred-Pending Reporting Surface (2026-03-10)
- [x] write one reporting addendum before runtime changes:
- [x] `docs/plans/memory_subjectivity_deferred_pending_reporting_addendum_2026-03-10.md`
- [x] keep scope report-only:
- [x] no schema widening
- [x] no live retrieval rerank
- [x] no automatic settlement
- [x] teach subjectivity distribution to expose effective pending state for unresolved tensions:
- [x] `deferred_tension_count`
- [x] `unresolved_by_status`
- [x] row-level `pending_status`
- [x] update operator report artifacts to render the new deferred-pending surface
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_group_review.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_reporting.py scripts/run_subjectivity_report.py scripts/run_subjectivity_group_review.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_group_review.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_reporting.py scripts/run_subjectivity_report.py scripts/run_subjectivity_group_review.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_group_review.py`
- [x] write the remaining `20`-row OSV homepage group as explicit `deferred`
- [x] rerun the latest subjectivity report artifact from real `memory/soul.db`
- [x] post-report real state: `20 unresolved tension`, `20 deferred tension`, `12 settled tension`, `0 reviewed vow`

## Phase 218: Deferred Revisit Queue Intelligence (2026-03-11)
- [x] write one queue addendum before runtime changes:
- [x] `docs/plans/memory_subjectivity_deferred_revisit_queue_addendum_2026-03-11.md`
- [x] keep scope read-only:
- [x] no auto-settlement
- [x] no auto-reject
- [x] no auto-promotion
- [x] teach the review batch artifact to expose deferred revisit signals:
- [x] `pending_status_counts`
- [x] `latest_review_timestamp`
- [x] `latest_row_timestamp`
- [x] `rows_after_latest_review`
- [x] `revisit_readiness`
- [x] add regressions:
- [x] `tests/test_subjectivity_review_batch.py`
- [x] `tests/test_run_subjectivity_review_batch.py`
- [x] `tests/test_subjectivity_reporting.py`
- [x] `tests/test_run_subjectivity_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] rerun the latest grouping / review-batch / subjectivity-report artifacts from real `memory/soul.db`
- [x] live queue on `2026-03-11`: `44 unresolved -> 2 semantic groups -> 10 lineage groups`
- [x] current unresolved status mix: `24 candidate` + `20 deferred`
- [x] current revisit readiness: `{n/a: 1, needs_revisit: 1}`

## Phase 219: Prior Decision Carry-Forward Queue Annotation (2026-03-11)
- [x] write one carry-forward addendum before locking the new report semantics:
- [x] `docs/plans/memory_subjectivity_carry_forward_queue_annotation_addendum_2026-03-11.md`
- [x] keep scope read-only:
- [x] no auto-settlement
- [x] no auto-reapply of historical decisions
- [x] no auto-promotion
- [x] teach the review batch artifact to annotate prior reviewed context only when provenance overlaps:
- [x] same `topic`
- [x] same `direction`
- [x] overlapping `source_url` or `stimulus_lineage`
- [x] stop using `friction_band` as a hard carry-forward equality key
- [x] separate active carry-forward status from mixed historical status:
- [x] `prior_decision_status_counts`
- [x] `historical_prior_decision_status_counts`
- [x] add a positive reviewed carry-forward surface:
- [x] `prior_approved_match`
- [x] add regressions for:
- [x] missing-provenance rows staying `fresh_group`
- [x] friction-band boundary drift not erasing prior reject context
- [x] latest deferred decision overriding older reject history at the annotation layer
- [x] prior approved/reviewed decisions surfacing as positive carry-forward context
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] rerun the latest real review-batch artifact from `memory/soul.db`
- [x] live queue on `2026-03-11` now reads: `52 unresolved -> 2 semantic groups -> 11 lineage groups`
- [x] live carry-forward result: `{prior_reject_match: 1, prior_deferred_match_needs_revisit: 1}`

## Phase 220: Candidate-Only Deferred Revisit Lane (2026-03-11)
- [x] write one operator addendum before narrowing revisit write scope:
- [x] `docs/plans/memory_subjectivity_group_review_pending_filter_addendum_2026-03-11.md`
- [x] keep scope narrow:
- [x] no change to `approved / deferred / rejected` semantics
- [x] no automatic carry-forward
- [x] no auto-settlement
- [x] teach `scripts/run_subjectivity_group_review.py` to filter the selected semantic group by current `pending_status`
- [x] support at least:
- [x] `candidate`
- [x] `deferred`
- [x] keep the semantic group as the review unit, but allow the write scope to target only the fresh unresolved slice
- [x] add regressions:
- [x] dry-run selection of `pending_status=candidate`
- [x] apply `deferred` only to the fresh candidate slice inside an already-deferred group
- [x] focused validation:
- [x] `python -m pytest tests/test_run_subjectivity_group_review.py -q --tb=short`
- [x] `python -m ruff check scripts/run_subjectivity_group_review.py tests/test_run_subjectivity_group_review.py`
- [x] `python -m black --check scripts/run_subjectivity_group_review.py tests/test_run_subjectivity_group_review.py`
- [x] run one real candidate-only revisit against `memory/soul.db`
- [x] selector:
- [x] topic = `A distributed vulnerability database for Open Source`
- [x] direction = `governance_escalation`
- [x] friction_band = `medium`
- [x] pending_status = `candidate`
- [x] decision:
- [x] keep the group `deferred` because recurrence is real but still confined to one source loop
- [x] real revisit result:
- [x] `25` fresh candidate rows rewritten as `deferred`
- [x] use the same filtered lane to settle the fresh same-source reject slice:
- [x] selector:
- [x] topic = `[](https://google.github.io/osv.dev/data/#data-sources) Data sources`
- [x] direction = `governance_escalation`
- [x] friction_band = `low`
- [x] pending_status = `candidate`
- [x] decision:
- [x] `15` fresh candidate rows explicitly `rejected`
- [x] latest live state after refresh:
- [x] `45 unresolved tension`
- [x] `45 deferred tension`
- [x] `0 candidate tension`
- [x] `27 settled tension`
- [x] `0 reviewed vow`
- [x] latest review-batch state after refresh:
- [x] `1 semantic group -> 11 lineage groups`
- [x] `revisit_readiness_counts = {holding_deferred: 1}`
- [x] `carry_forward_annotation_counts = {prior_deferred_match: 1}`

## Phase 221: Deferred Context Surface And Reopened Queue Reconciliation (2026-03-11)
- [x] write one reporting addendum before widening the operator surface:
- [x] `docs/plans/memory_subjectivity_deferred_context_surface_addendum_2026-03-11.md`
- [x] keep scope read-only at the reporting layer:
- [x] no semantic change to `approved / deferred / rejected`
- [x] no synthetic revisit logic
- [x] no auto-settlement or auto-promotion
- [x] surface latest active deferred context from canonical review logs on the main operator artifacts:
- [x] unresolved rows now expose `review_basis`
- [x] unresolved rows now expose `review_notes`
- [x] unresolved rows now expose `review_actor_id`, `review_actor_type`, `review_actor_display_name`
- [x] review-batch groups now expose `latest_review_basis`
- [x] review-batch groups now expose `latest_review_notes`
- [x] review-batch groups now expose `latest_review_actor_id`, `latest_review_actor_type`, `latest_review_actor_display_name`
- [x] add focused regressions for deferred-context surfacing:
- [x] `python -m pytest tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_report.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_reporting.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_report.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py`
- [x] focused validation result: `19 passed`
- [x] refresh live artifacts after the reporting surface change
- [x] reopened live queue observed at `2026-03-11T10:05:08Z`:
- [x] `53 unresolved tension`
- [x] `45 deferred tension`
- [x] `8 candidate tension`
- [x] `27 settled tension`
- [x] `0 reviewed vow`
- [x] reopened review-batch state:
- [x] `2 semantic groups -> 13 lineage groups`
- [x] `revisit_readiness_counts = {n/a: 1, needs_revisit: 1}`
- [x] `carry_forward_annotation_counts = {prior_reject_match: 1, prior_deferred_match_needs_revisit: 1}`
- [x] use the candidate-only group-review lane again to reconcile the fresh slices without touching older deferred rows
- [x] real OSV homepage revisit:
- [x] selector:
- [x] topic = `A distributed vulnerability database for Open Source`
- [x] direction = `governance_escalation`
- [x] friction_band = `medium`
- [x] pending_status = `candidate`
- [x] result:
- [x] `5` fresh candidate rows rewritten as `deferred`
- [x] real same-source reject cleanup:
- [x] selector:
- [x] topic = `[](https://google.github.io/osv.dev/data/#data-sources) Data sources`
- [x] direction = `governance_escalation`
- [x] friction_band = `low`
- [x] pending_status = `candidate`
- [x] result:
- [x] `3` fresh candidate rows explicitly `rejected`
- [x] latest live state after refresh at `2026-03-11T10:07:29Z`:
- [x] `50 unresolved tension`
- [x] `50 deferred tension`
- [x] `0 candidate tension`
- [x] `30 settled tension`
- [x] `0 reviewed vow`
- [x] latest review-batch state after refresh:
- [x] `1 semantic group -> 12 lineage groups`
- [x] `revisit_readiness_counts = {holding_deferred: 1}`
- [x] `carry_forward_annotation_counts = {prior_deferred_match: 1}`

## Phase 222: Dream Collision Producer Duplicate Guard (2026-03-11)
- [x] write one addendum before changing producer behavior:
- [x] `docs/plans/memory_subjectivity_producer_duplicate_guard_addendum_2026-03-11.md`
- [x] keep the first upstream guard intentionally narrow:
- [x] suppress only fresh `dream_collision` writes whose active unresolved signature already exists
- [x] signature = normalized `topic + source_url`
- [x] if `source_url` is missing, fall back to `topic + source lineage`
- [x] do not reinterpret historical settled decisions as permanent suppression
- [x] expose enough row context for producer-side guards to reuse canonical unresolved reporting:
- [x] `type`
- [x] `title`
- [x] `topic`
- [x] `source_url`
- [x] implement the duplicate guard inside `DreamEngine` persistence:
- [x] same unresolved source loop now increments `write_gateway.skipped` instead of writing another tension row
- [x] collisions skipped by the guard now carry `observability.write_status = skipped`
- [x] collisions skipped by the guard now carry `observability.write_skip_reason = active_unresolved_signature`
- [x] preserve admissibility for new evidence from a different source loop
- [x] add focused regressions for both sides of the rule:
- [x] same-source unresolved duplicate is suppressed
- [x] same-topic cross-source signal is still written
- [x] focused validation:
- [x] `python -m pytest tests/test_dream_engine.py tests/test_subjectivity_reporting.py tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m ruff check tonesoul/dream_engine.py tonesoul/memory/subjectivity_reporting.py tests/test_dream_engine.py`
- [x] `python -m black --check tonesoul/dream_engine.py tonesoul/memory/subjectivity_reporting.py tests/test_dream_engine.py`
- [x] focused validation result: `19 passed`
- [x] current live queue metrics remain timestamped artifacts, not retroactive proof of the new guard
- [x] no real `memory/soul.db` dream cycle has been run under the new guard yet
- [x] operational conclusion:
- [x] review semantics stay where they are
- [x] the next reduction in queue churn should come from producer suppression on future cycles, not from rewriting existing unresolved rows

## Phase 222: Duplicate Pressure Surface (2026-03-11)
- [x] write one observability addendum before classifying upstream pressure:
- [x] `docs/plans/memory_subjectivity_duplicate_pressure_surface_addendum_2026-03-11.md`
- [x] keep scope read-only:
- [x] no queue settlement
- [x] no row suppression
- [x] no schema widening
- [x] no change to `approved / deferred / rejected`
- [x] surface duplicate-pressure signals on semantic groups:
- [x] `same_source_loop`
- [x] `rows_per_lineage`
- [x] `rows_per_cycle`
- [x] `duplicate_pressure`
- [x] `duplicate_pressure_reason`
- [x] `producer_followup`
- [x] surface duplicate-pressure summaries on grouping and review-batch artifacts:
- [x] `duplicate_pressure_counts`
- [x] `producer_followup_counts`
- [x] render these signals on operator-facing markdown:
- [x] `docs/status/subjectivity_tension_groups_latest.md`
- [x] `docs/status/subjectivity_review_batch_latest.md`
- [x] add focused regressions:
- [x] high single-source loop pressure on internal batch builder
- [x] high single-source loop pressure on review-batch artifact output
- [x] high single-source loop pressure on grouping artifact output
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] focused validation result: `25 passed`
- [x] refresh live artifacts after the new pressure surface landed
- [x] latest live state after refresh at `2026-03-11T10:13:51Z`:
- [x] `50 unresolved tension`
- [x] `50 deferred tension`
- [x] `0 candidate tension`
- [x] `30 settled tension`
- [x] `0 reviewed vow`
- [x] latest duplicate-pressure reading:
- [x] `duplicate_pressure_counts = {high: 1}`
- [x] `producer_followup_counts = {upstream_dedup_candidate: 1}`
- [x] remaining OSV homepage group now reads:
- [x] `same_source_loop = true`
- [x] `rows_per_lineage = 4.17`
- [x] `rows_per_cycle = 1.67`
- [x] `duplicate_pressure = high`
- [x] `producer_followup = upstream_dedup_candidate`
- [x] operational conclusion:
- [x] the remaining debt is now explicitly upstream duplicate/noise pressure, not unresolved review semantics

## Phase 223: Group Review Context Reuse Lane (2026-03-11)
- [x] write one operator-tooling addendum before reducing repeated review transcription:
- [x] `docs/plans/memory_subjectivity_group_review_context_reuse_addendum_2026-03-11.md`
- [x] keep the lane explicit:
- [x] no auto-settlement
- [x] no silent carry-forward write
- [x] no batch `vow` promotion
- [x] expose the latest matched review status directly on batch surfaces:
- [x] `latest_review_status`
- [x] add one explicit CLI reuse path on group review:
- [x] `scripts/run_subjectivity_group_review.py --reuse-latest-decision`
- [x] resolve the reused decision from the matched review-batch group:
- [x] `latest_review_status`
- [x] `latest_review_basis`
- [x] `latest_review_notes`
- [x] fail loudly when no prior reviewed context exists
- [x] reject ambiguous mixing of reuse with explicit `status` / `review_basis` / `notes`
- [x] add focused regressions:
- [x] batch report surfaces `latest_review_status`
- [x] markdown artifact renders `latest_review_status`
- [x] group review can dry-run a candidate-only slice by reusing the latest matched decision
- [x] group review reuse fails when no prior reviewed context exists
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_group_review.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_group_review.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_group_review.py`
- [x] `python -m black tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_group_review.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_group_review.py`
- [x] focused validation result: `26 passed`
- [x] refresh live artifacts after the lane landed:
- [x] `python scripts/run_subjectivity_report.py --db-path memory/soul.db`
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] live state remained:
- [x] `50 unresolved tension`
- [x] `50 deferred tension`
- [x] `0 candidate tension`
- [x] `30 settled tension`
- [x] `0 reviewed vow`
- [x] run one live dry-run against the only remaining OSV homepage group:
- [x] selector:
- [x] topic = `A distributed vulnerability database for Open Source`
- [x] direction = `governance_escalation`
- [x] friction_band = `medium`
- [x] pending_status = `candidate`
- [x] decision source:
- [x] `latest_matched_review`
- [x] dry-run result:
- [x] reused decision resolved to `deferred`
- [x] selected row count = `0`
- [x] warning confirmed the queue is currently `holding_deferred`, not freshly reopened

## Phase 224: Reviewed Rejection Producer Guard (2026-03-11)
- [x] write one addendum before extending producer suppression beyond active unresolved rows:
- [x] `docs/plans/memory_subjectivity_reviewed_rejection_producer_guard_addendum_2026-03-11.md`
- [x] keep the second producer guard intentionally narrow:
- [x] only suppress a fresh `dream_collision` when the latest reviewed decision for the same `topic + source_url + lineage` is `rejected`
- [x] do not suppress a new source loop
- [x] do not suppress a second independent lineage cluster on the same source loop
- [x] do not reinterpret deferred history as permanent suppression
- [x] implement the reviewed-rejection guard inside `DreamEngine` persistence:
- [x] add `prior_rejected_signature` lookup based on latest reviewed dream-collision status per exact signature
- [x] collisions skipped by the new guard now carry `observability.write_status = skipped`
- [x] collisions skipped by the new guard now carry `observability.write_skip_reason = prior_rejected_signature`
- [x] add focused regressions for both sides of the rule:
- [x] same topic + same source_url + same lineage is skipped after latest reviewed rejection
- [x] same topic + same source_url + new lineage is still written
- [x] focused validation:
- [x] `python -m pytest tests/test_dream_engine.py -q --tb=short`
- [x] `python -m ruff check tonesoul/dream_engine.py tests/test_dream_engine.py`
- [x] `python -m black tonesoul/dream_engine.py tests/test_dream_engine.py`
- [x] focused validation result: `10 passed`
- [x] live verification uncovered and then closed the real gap:
- [x] first live run at `2026-03-11T10:26:48Z` wrote `1` fresh `Data sources` row and skipped `2` homepage collisions
- [x] that proved the first producer guard was working for active unresolved homepage pressure but not for already-rejected same-lineage re-entry
- [x] the reopened `Data sources` candidate was then explicitly settled via reuse lane:
- [x] `aaa6dd6a-2075-4cff-891a-7aed00688d06` -> `rejected`
- [x] queue returned to `50 unresolved tension`, `50 deferred tension`, `31 settled tension`, `0 candidate tension`
- [x] second live run at `2026-03-11T10:30:16Z` then confirmed the new guard:
- [x] selected topic = `[](https://google.github.io/osv.dev/data/#data-sources) Data sources`
- [x] `write_gateway = {written: 0, skipped: 1, rejected: 0}`
- [x] `skip_reasons = [prior_rejected_signature]`
- [x] final live state remained:
- [x] `50 unresolved tension`
- [x] `50 deferred tension`
- [x] `31 settled tension`
- [x] `0 candidate tension`
- [x] `0 reviewed vow`

## Phase 225: History Density Compaction Surface (2026-03-11)
- [x] write one addendum before changing how the last deferred loop is shown to operators:
- [x] `docs/plans/memory_subjectivity_history_density_compaction_surface_addendum_2026-03-11.md`
- [x] keep scope read-only:
- [x] no row rewrite
- [x] no auto-settlement
- [x] no producer-rule change
- [x] no change to `approved / deferred / rejected`
- [x] extend semantic-group observability with lineage density signals:
- [x] `repeated_lineage_count`
- [x] `dense_lineage_count`
- [x] `singleton_lineage_count`
- [x] `max_lineage_record_count`
- [x] `lineage_record_histogram`
- [x] pass time-window context through the review batch:
- [x] `first_seen`
- [x] `last_seen`
- [x] `history_density_summary`
- [x] add one operator-facing read-only follow-up signal on stable deferred loops:
- [x] `density_compaction_candidate`
- [x] `density_compaction_reason`
- [x] `operator_followup = read_only_density_compaction_candidate`
- [x] render the new density surface on latest artifacts:
- [x] `docs/status/subjectivity_tension_groups_latest.md`
- [x] `docs/status/subjectivity_review_batch_latest.md`
- [x] add focused regressions:
- [x] grouping/report surfaces lineage density histogram
- [x] holding deferred batch group surfaces history density summary
- [x] holding deferred high-pressure batch group surfaces read-only density compaction follow-up
- [x] needs-revisit batch group shows `rows_after_latest_review` inside the history summary
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_triage.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] focused validation result: `27 passed`
- [x] refresh live artifacts after the new surface landed:
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] `python scripts/run_subjectivity_tension_grouping.py --db-path memory/soul.db`
- [x] live state remained:
- [x] `50 unresolved tension`
- [x] `50 deferred tension`
- [x] `31 settled tension`
- [x] `0 candidate tension`
- [x] `0 reviewed vow`
- [x] latest live density reading on the remaining OSV homepage loop:
- [x] `lineage_record_histogram = {1:1, 2:1, 3:1, 4:1, 5:8}`
- [x] `repeated_lineage_count = 11`
- [x] `dense_lineage_count = 10`
- [x] `first_seen = 2026-03-10T05:08:05Z`
- [x] `last_seen = 2026-03-11T08:08:13Z`
- [x] `history_density_summary = 50 row(s) across 30 cycle(s) / 12 lineage(s) ... no new rows since latest review`
- [x] `operator_followup_counts = {read_only_density_compaction_candidate: 1}`
- [x] operational conclusion:
- [x] the remaining queue debt is now explicitly a stable same-source deferred history stack
- [x] the next work should reduce upstream duplicate pressure or add a more compact historical lens, not reopen review semantics

## Phase 226: Operator Lens View (2026-03-11)
- [x] write one addendum before compressing batch readability:
- [x] `docs/plans/memory_subjectivity_operator_lens_view_addendum_2026-03-11.md`
- [x] keep scope read-only and view-only:
- [x] no writer change
- [x] no review semantic change
- [x] no new decision category
- [x] add one short operator lens to review-batch groups:
- [x] `queue_posture`
- [x] `revisit_trigger`
- [x] `operator_lens_summary`
- [x] surface posture summary counts:
- [x] `queue_posture_counts`
- [x] render a compact operator-first section on review-batch markdown:
- [x] `## Queue Postures`
- [x] `## Operator Lens`
- [x] keep low-level fields intact under the full review-group section
- [x] add focused regressions:
- [x] holding deferred groups read as `stable_deferred_history`
- [x] needs-revisit groups read as `deferred_revisit_queue`
- [x] active duplicate-pressure groups still read as `active_deferred_queue`
- [x] markdown renders posture counts and operator-lens lines
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] focused validation result: `21 passed`
- [x] refresh live review-batch artifact after the new lens landed:
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] confirm the remaining OSV homepage group now reads first as `stable_deferred_history`, not just as raw density metrics
- [x] latest live lens at `2026-03-11T11:26:36Z`:
- [x] `queue_posture_counts = {stable_deferred_history: 1}`
- [x] `operator_lens_summary = stable deferred history; 50 row(s) compress to 12 lineage(s) / 30 cycle(s) ...`
- [x] `revisit_trigger = Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.`

## Phase 227: Operator Status Line Surface (2026-03-11)
- [x] write one addendum before shrinking the operator lens into a copyable single line:
- [x] `docs/plans/memory_subjectivity_operator_status_line_addendum_2026-03-11.md`
- [x] keep scope view-only:
- [x] no semantic change
- [x] no writer change
- [x] no replacement of detailed fields
- [x] add one compact status surface on review-batch groups:
- [x] `revisit_trigger_code`
- [x] `operator_status_line`
- [x] elevate the compact surface into the batch handoff layer:
- [x] `primary_status_line`
- [x] `status_lines`
- [x] render the new single-line section on markdown:
- [x] `## Status Lines`
- [x] add focused regressions:
- [x] holding deferred groups emit `second_source_context_or_material_split`
- [x] needs-revisit groups emit `new_rows_since_latest_review`
- [x] active deferred groups emit `more_context_required`
- [x] markdown renders the copyable status line
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] focused validation result: `21 passed`
- [x] refresh live review-batch artifact after the status-line surface landed:
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] confirm the remaining OSV homepage group now exposes one copyable single-line status surface
- [x] latest live single-line surface at `2026-03-11T13:48:28Z`:
- [x] `operator_status_line = stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- [x] the same line now sits at the batch top level:
- [x] `primary_status_line`
- [x] `status_lines = [primary_status_line]`
- [x] batch now also exposes a first-class handoff block:
- [x] `handoff.queue_shape = stable_history_only`
- [x] `handoff.requires_operator_action = false`
- [x] `handoff.primary_status_line = primary_status_line`

## Phase 228: Grouping Handoff Surface (2026-03-11)
- [x] write one addendum before aligning grouping with the batch handoff shape:
- [x] `docs/plans/memory_subjectivity_grouping_handoff_surface_addendum_2026-03-11.md`
- [x] keep the grouping handoff triage-only:
- [x] no review-language leakage
- [x] no inferred settlement
- [x] add grouping-level handoff fields:
- [x] `handoff`
- [x] `primary_status_line`
- [x] `status_lines`
- [x] add per-group triage shorthand:
- [x] `group_shape`
- [x] render the same handoff-first layout on grouping markdown:
- [x] `## Handoff`
- [x] `## Status Lines`
- [x] add focused regressions:
- [x] action-required grouping surfaces a top-level handoff block
- [x] high duplicate same-source grouping surfaces `monitoring_queue`
- [x] empty grouping surface returns `empty_queue`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_triage.py tests/test_run_subjectivity_tension_grouping.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_triage.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_triage.py tests/test_run_subjectivity_tension_grouping.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_triage.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_triage.py tests/test_run_subjectivity_tension_grouping.py`
- [x] focused validation result: `9 passed`
- [x] refresh live grouping artifact after the handoff surface landed:
- [x] `python scripts/run_subjectivity_tension_grouping.py --db-path memory/soul.db`
- [x] confirm the live grouping handoff reads as triage-level `monitoring_queue`, not review-level settlement
- [x] latest live grouping handoff at `2026-03-11T14:08:48Z`:
- [x] `handoff.queue_shape = monitoring_queue`
- [x] `handoff.requires_operator_action = false`
- [x] `primary_status_line = high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate`

## Phase 229: Report Handoff Surface (2026-03-11)
- [x] write one addendum before aligning the broad subjectivity report with the new handoff style:
- [x] `docs/plans/memory_subjectivity_report_handoff_surface_addendum_2026-03-11.md`
- [x] keep scope artifact-level only:
- [x] no metric redefinition
- [x] no writer change
- [x] no new promotion semantics
- [x] add report-level handoff fields:
- [x] `handoff`
- [x] `primary_status_line`
- [x] `status_lines`
- [x] classify report posture in report language:
- [x] `empty_report`
- [x] `observational_only`
- [x] `settled_or_reviewed`
- [x] `deferred_monitoring`
- [x] `action_required`
- [x] render the same top-level layout on markdown:
- [x] `## Handoff`
- [x] `## Status Lines`
- [x] add focused regressions:
- [x] empty report surfaces `empty_report`
- [x] unresolved candidate report surfaces `action_required`
- [x] deferred-only report surfaces `deferred_monitoring`
- [x] settled reviewed report surfaces `settled_or_reviewed`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_subjectivity_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_subjectivity_report.py tests/test_run_subjectivity_report.py`
- [x] `python -m black --check scripts/run_subjectivity_report.py tests/test_run_subjectivity_report.py`
- [x] refresh live subjectivity report artifact after the handoff surface landed:
- [x] `python scripts/run_subjectivity_report.py --db-path memory/soul.db`
- [x] confirm the live report reads as `deferred_monitoring`, not just as raw unresolved counts
- [x] latest live report handoff at `2026-03-11T14:46:12Z`:
- [x] `handoff.queue_shape = deferred_monitoring`
- [x] `handoff.requires_operator_action = false`
- [x] `primary_status_line = deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`

## Phase 230: Shared Handoff Surface Utility (2026-03-11)
- [x] write one addendum before deduplicating the handoff plumbing:
- [x] `docs/plans/memory_subjectivity_shared_handoff_surface_utility_addendum_2026-03-11.md`
- [x] keep queue-shape semantics local to each artifact:
- [x] report still owns `deferred_monitoring`
- [x] grouping still owns `monitoring_queue`
- [x] batch still owns `stable_history_only`
- [x] add one shared utility layer for structural handoff work only:
- [x] normalize `status_lines`
- [x] select `primary_status_line`
- [x] build top-level `handoff`
- [x] render markdown `## Handoff`
- [x] render markdown `## Status Lines`
- [x] wire the utility into all three surfaces:
- [x] `scripts/run_subjectivity_report.py`
- [x] `scripts/run_subjectivity_tension_grouping.py`
- [x] `scripts/run_subjectivity_review_batch.py`
- [x] `tonesoul/memory/subjectivity_triage.py`
- [x] `tonesoul/memory/subjectivity_review_batch.py`
- [x] add focused utility regressions:
- [x] `tests/test_subjectivity_handoff.py`
- [x] re-run handoff-focused validation:
- [x] `python -m pytest tests/test_subjectivity_handoff.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py tests/test_subjectivity_review_batch.py tests/test_subjectivity_triage.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_handoff.py tonesoul/memory/subjectivity_review_batch.py tonesoul/memory/subjectivity_triage.py scripts/run_subjectivity_report.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_handoff.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_handoff.py tonesoul/memory/subjectivity_review_batch.py tonesoul/memory/subjectivity_triage.py scripts/run_subjectivity_report.py scripts/run_subjectivity_review_batch.py scripts/run_subjectivity_tension_grouping.py tests/test_subjectivity_handoff.py tests/test_run_subjectivity_report.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_tension_grouping.py`
- [x] refresh live artifacts after the shared utility landed:
- [x] `python scripts/run_subjectivity_report.py --db-path memory/soul.db`
- [x] `python scripts/run_subjectivity_tension_grouping.py --db-path memory/soul.db`
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] confirm the live surfaces stayed semantically stable after deduplication:
- [x] report still reads `deferred_monitoring`
- [x] grouping still reads `monitoring_queue`
- [x] batch still reads `stable_history_only`

## Phase 231: Refreshable Handoff Previews (2026-03-11)
- [x] write one addendum before lifting subjectivity handoff lines into the refreshable lane:
- [x] `docs/plans/memory_subjectivity_refreshable_handoff_preview_addendum_2026-03-11.md`
- [x] keep the refreshable lane preview-only:
- [x] it may mirror existing handoff surfaces
- [x] it may not invent new queue semantics
- [x] teach `scripts/run_refreshable_artifact_report.py` to load latest JSON previews when available:
- [x] derive canonical preview paths from dirty `.json` / `.md` pairs
- [x] extract `queue_shape` and `primary_status_line` from top-level or nested artifact payloads
- [x] expose `handoff_previews`
- [x] expose `summary.handoff_preview_count`
- [x] render markdown `## Handoff Previews`
- [x] add focused regression coverage:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] refreshable report dedupes `.md` / `.json` to one preview surface
- [x] refreshable report can read both broad report and nested batch payloads
- [x] focused validation:
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m black --check scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] refresh live refreshable artifact report:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] latest live refreshable handoff preview at `2026-03-11T15:05:33Z`:
- [x] `summary.handoff_preview_count = 3`
- [x] report preview reads `deferred_monitoring`
- [x] grouping preview reads `monitoring_queue`
- [x] batch preview reads `stable_history_only`

## Phase 232: Worktree Settlement Handoff Previews (2026-03-11)
- [x] write one addendum before lifting refreshable subjectivity previews into the settlement lane:
- [x] `docs/plans/memory_subjectivity_worktree_settlement_handoff_preview_addendum_2026-03-11.md`
- [x] keep settlement previewing mirror-only:
- [x] settlement may reuse refreshable handoff previews
- [x] settlement may not invent new subjectivity queue semantics
- [x] teach `scripts/run_worktree_settlement_report.py` to attach refreshable subjectivity previews:
- [x] load `handoff_previews` from the refreshable artifact report
- [x] expose them on the `refreshable_artifacts` lane
- [x] expose `summary.refreshable_handoff_preview_count`
- [x] render refreshable preview lines inside the settlement markdown lane
- [x] add focused settlement regressions:
- [x] `tests/test_run_worktree_settlement_report.py`
- [x] settlement refreshable lane now carries preview count and preview entries
- [x] focused validation:
- [x] `python -m pytest tests/test_run_worktree_settlement_report.py tests/test_run_refreshable_artifact_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m black --check scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] refresh live worktree settlement artifact:
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] latest live settlement preview at `2026-03-11T15:14:08Z`:
- [x] `summary.refreshable_handoff_preview_count = 3`
- [x] refreshable settlement lane previews report `deferred_monitoring`
- [x] refreshable settlement lane previews grouping `monitoring_queue`
- [x] refreshable settlement lane previews batch `stable_history_only`

## Phase 233: Repo Governance Handoff Mirror (2026-03-11)
- [x] write one addendum before lifting settlement previews into repo governance:
- [x] `docs/plans/memory_subjectivity_repo_governance_handoff_preview_addendum_2026-03-11.md`
- [x] keep governance previewing mirror-only:
- [x] governance may reuse worktree settlement previews
- [x] governance may not reinterpret queue posture as a governance gate
- [x] teach `scripts/run_repo_governance_settlement_report.py` to mirror settlement preview state:
- [x] add optional `worktree_settlement_path`
- [x] expose `worktree_settlement.refreshable_handoff_preview_count`
- [x] expose `worktree_settlement.handoff_previews`
- [x] render markdown `## Worktree Settlement Mirror`
- [x] warn only when the worktree settlement artifact is missing
- [x] add focused governance regressions:
- [x] `tests/test_run_repo_governance_settlement_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_repo_governance_settlement_report.py tests/test_run_worktree_settlement_report.py tests/test_run_refreshable_artifact_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_repo_governance_settlement_report.py tests/test_run_repo_governance_settlement_report.py scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] `python -m black --check scripts/run_repo_governance_settlement_report.py tests/test_run_repo_governance_settlement_report.py scripts/run_worktree_settlement_report.py tests/test_run_worktree_settlement_report.py scripts/run_refreshable_artifact_report.py tests/test_run_refreshable_artifact_report.py`
- [x] refresh live repo governance settlement artifact:
- [x] `python scripts/run_repo_governance_settlement_report.py`
- [x] latest live governance mirror at `2026-03-11T15:15:54Z`:
- [x] `worktree_settlement.refreshable_handoff_preview_count = 3`
- [x] governance mirror previews report `deferred_monitoring`
- [x] governance mirror previews grouping `monitoring_queue`
- [x] governance mirror previews batch `stable_history_only`

## Phase 234: Historical Figure Audit (2026-03-11)
- [x] recover the historical-figure audit lane as a real formal addendum instead of leaving a garbled draft:
- [x] `docs/plans/memory_subjectivity_historical_figure_audit_addendum_2026-03-11.md`
- [x] keep this phase audit-only:
- [x] no runtime persona promotion
- [x] no subjectivity writer change
- [x] no automatic criteria mutation
- [x] anchor the audit in historically grounded source material and current review criteria:
- [x] positive, mixed, interpretive, and negative cases
- [x] explicit fail-closed framing for negative controls
- [x] map the figure set to current branch blind spots:
- [x] coherence vs legitimacy
- [x] restraint as direction
- [x] minority truth vs context diversity
- [x] traceability vs accountable choice
- [x] exception rhetoric vs governance gate
- [x] coherent evil vs admissible vow
- [x] identify the highest-risk policy gap without silently changing the policy:
- [x] the active `approved` criteria still lack an explicit `axiomatic admissibility` gate
- [x] add one reusable audit corpus seed for future swarm or council use:
- [x] `docs/experiments/historical_viewpoint_audit_seed_2026-03-11.json`
- [x] keep the seed out of `spec/personas/` for now:
- [x] it is audit corpus, not runtime persona config
- [x] basic validation:
- [x] read back both new files as UTF-8
- [x] confirm `replacement_char_count = 0`
- [x] confirm `contains_bom = False`

## Phase 235: Axiomatic Admissibility Gate (2026-03-11)
- [x] write one addendum before tightening the official approval policy:
- [x] `docs/plans/memory_subjectivity_axiomatic_admissibility_gate_addendum_2026-03-11.md`
- [x] update the active review criteria document itself, not only the audit rationale:
- [x] `docs/plans/memory_subjectivity_review_criteria_2026-03-10.md`
- [x] make `axiomatic admissibility` an explicit mandatory criterion before `approved`
- [x] keep this phase policy-first:
- [x] no runtime automation
- [x] no writer mutation
- [x] no schema widening
- [x] align the operator prompt surface with the new policy:
- [x] `tonesoul/memory/subjectivity_review_batch.py`
- [x] `review_basis_template` now prompts for P0/P1 admissibility
- [x] add focused regression updates:
- [x] `tests/test_subjectivity_review_batch.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_review_batch.py tests/test_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_review_batch.py tests/test_subjectivity_review_batch.py`

## Phase 236: Review Batch Admissibility Checklist Surface (2026-03-11)
- [x] write one addendum before choosing the canonical operator surface:
- [x] `docs/plans/memory_subjectivity_review_batch_admissibility_checklist_addendum_2026-03-11.md`
- [x] keep admissibility as reviewer aid, not replay metadata:
- [x] no `ReviewedPromotionDecision` schema change
- [x] no group-review semantic expansion
- [x] no automatic admissibility classifier
- [x] add one shared helper for admissibility checklist generation:
- [x] `tonesoul/memory/subjectivity_admissibility.py`
- [x] wire the helper into the review batch artifact:
- [x] `tonesoul/memory/subjectivity_review_batch.py`
- [x] each `review_group` now exposes `axiomatic_admissibility_checklist`
- [x] batch summary now exposes `admissibility_gate_posture_counts`
- [x] batch summary now exposes `admissibility_focus_counts`
- [x] render the new surface in markdown:
- [x] `scripts/run_subjectivity_review_batch.py`
- [x] `## Admissibility Gate Counts`
- [x] `## Admissibility Focus Counts`
- [x] per-group admissibility posture / risk tags / operator prompt
- [x] add focused regressions:
- [x] `tests/test_subjectivity_review_batch.py`
- [x] `tests/test_run_subjectivity_review_batch.py`
- [x] keep group-review boundary green:
- [x] `tests/test_run_subjectivity_group_review.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_group_review.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_admissibility.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_admissibility.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`

## Phase 237: Admissibility Status Line Surface (2026-03-11)
- [x] write one addendum before shrinking checklist state into a resumable line:
- [x] `docs/plans/memory_subjectivity_admissibility_status_line_addendum_2026-03-11.md`
- [x] keep the full checklist intact:
- [x] status line is additive, not a replacement
- [x] add compact per-group admissibility line:
- [x] `admissibility_status_line`
- [x] add top-level batch admissibility handoff fields:
- [x] `admissibility_primary_status_line`
- [x] `admissibility_status_lines`
- [x] render markdown section:
- [x] `## Admissibility Status Lines`
- [x] add focused regression updates:
- [x] `tests/test_subjectivity_review_batch.py`
- [x] `tests/test_run_subjectivity_review_batch.py`
- [x] keep group-review boundary green:
- [x] `tests/test_run_subjectivity_group_review.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py tests/test_run_subjectivity_group_review.py -q --tb=short`
- [x] `python -m ruff check tonesoul/memory/subjectivity_admissibility.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] `python -m black --check tonesoul/memory/subjectivity_admissibility.py tonesoul/memory/subjectivity_review_batch.py scripts/run_subjectivity_review_batch.py tests/test_subjectivity_review_batch.py tests/test_run_subjectivity_review_batch.py`
- [x] refresh live review-batch artifact:
- [x] `python scripts/run_subjectivity_review_batch.py --db-path memory/soul.db`
- [x] latest live admissibility status line at `2026-03-11T15:55:43Z`:
- [x] `admissibility_primary_status_line = admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Phase 238: Admissibility Preview Mirror (2026-03-12)
- [x] write one addendum before mirroring admissibility upward:
- [x] `docs/plans/memory_subjectivity_admissibility_preview_mirror_addendum_2026-03-12.md`
- [x] keep this phase mirror-only:
- [x] no subjectivity recomputation in settlement scripts
- [x] no new governance gate
- [x] no writer change
- [x] extend refreshable preview extraction:
- [x] `scripts/run_refreshable_artifact_report.py`
- [x] preview objects now carry `admissibility_primary_status_line`
- [x] summary now carries `admissibility_preview_count`
- [x] extend worktree settlement mirror:
- [x] `scripts/run_worktree_settlement_report.py`
- [x] refreshable lane previews now carry `admissibility_primary_status_line`
- [x] summary now carries `refreshable_admissibility_preview_count`
- [x] extend repo governance mirror:
- [x] `scripts/run_repo_governance_settlement_report.py`
- [x] worktree settlement mirror now carries `refreshable_admissibility_preview_count`
- [x] mirrored previews now carry `admissibility_primary_status_line`
- [x] add focused regressions:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] `tests/test_run_worktree_settlement_report.py`
- [x] `tests/test_run_repo_governance_settlement_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] refresh live artifacts:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] `python scripts/run_repo_governance_settlement_report.py`
- [x] latest live refreshable mirror at `2026-03-11T16:06:45Z`:
- [x] `summary.handoff_preview_count = 3`
- [x] `summary.admissibility_preview_count = 1`
- [x] latest live worktree settlement mirror at `2026-03-11T16:06:56Z`:
- [x] `summary.refreshable_handoff_preview_count = 3`
- [x] `summary.refreshable_admissibility_preview_count = 1`
- [x] latest live repo governance mirror at `2026-03-11T16:06:59Z`:
- [x] `worktree_settlement.refreshable_handoff_preview_count = 3`
- [x] `worktree_settlement.refreshable_admissibility_preview_count = 1`
- [x] mirrored batch admissibility preview now surfaces the still-open blocker:
- [x] `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Phase 239: Subjectivity Focus Preview Card (2026-03-12)
- [x] write one addendum before collapsing the preview list into a shorter recovery card:
- [x] `docs/plans/memory_subjectivity_focus_preview_card_addendum_2026-03-12.md`
- [x] keep this phase mirror-only:
- [x] no subjectivity recomputation
- [x] no new settlement rule
- [x] no writer or review-criteria mutation
- [x] extend refreshable report with one explicit focus card:
- [x] `scripts/run_refreshable_artifact_report.py`
- [x] top-level `subjectivity_focus_preview`
- [x] markdown section `## Subjectivity Focus`
- [x] extend worktree settlement mirror with the same focus card:
- [x] `scripts/run_worktree_settlement_report.py`
- [x] top-level `subjectivity_focus_preview`
- [x] markdown section `## Subjectivity Focus Mirror`
- [x] extend repo governance settlement with the mirrored focus card:
- [x] `scripts/run_repo_governance_settlement_report.py`
- [x] `worktree_settlement.subjectivity_focus_preview`
- [x] markdown section `## Subjectivity Focus Mirror`
- [x] add focused regressions:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] `tests/test_run_worktree_settlement_report.py`
- [x] `tests/test_run_repo_governance_settlement_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] refresh live artifacts:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] `python scripts/run_repo_governance_settlement_report.py`
- [x] latest live refreshable focus card at `2026-03-11T16:11:52Z`
- [x] latest live worktree focus card at `2026-03-11T16:12:04Z`
- [x] latest live repo governance focus card at `2026-03-11T16:12:10Z`
- [x] mirrored focus card currently resolves to `docs/status/subjectivity_review_batch_latest.json`
- [x] queue posture remains `stable_history_only`
- [x] admissibility posture remains `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

## Phase 240: Requires-Operator-Action Preview Mirror (2026-03-12)
- [x] write one addendum before mirroring leaf action posture upward:
- [x] `docs/plans/memory_subjectivity_requires_operator_action_preview_mirror_addendum_2026-03-12.md`
- [x] keep this phase mirror-only:
- [x] no inference from `queue_shape`
- [x] no new operator gate
- [x] no subjectivity recomputation
- [x] extend refreshable previews:
- [x] `scripts/run_refreshable_artifact_report.py`
- [x] preview objects now carry `requires_operator_action`
- [x] `subjectivity_focus_preview` now carries `requires_operator_action`
- [x] extend worktree settlement mirror:
- [x] `scripts/run_worktree_settlement_report.py`
- [x] mirrored preview rows now carry `requires_operator_action`
- [x] top-level `subjectivity_focus_preview` now carries `requires_operator_action`
- [x] extend repo governance mirror:
- [x] `scripts/run_repo_governance_settlement_report.py`
- [x] `worktree_settlement.handoff_previews[*].requires_operator_action`
- [x] `worktree_settlement.subjectivity_focus_preview.requires_operator_action`
- [x] add focused regressions:
- [x] `tests/test_run_refreshable_artifact_report.py`
- [x] `tests/test_run_worktree_settlement_report.py`
- [x] `tests/test_run_repo_governance_settlement_report.py`
- [x] focused validation:
- [x] `python -m pytest tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py -q --tb=short`
- [x] `python -m ruff check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] `python -m black --check scripts/run_refreshable_artifact_report.py scripts/run_worktree_settlement_report.py scripts/run_repo_governance_settlement_report.py tests/test_run_refreshable_artifact_report.py tests/test_run_worktree_settlement_report.py tests/test_run_repo_governance_settlement_report.py`
- [x] refresh live artifacts:
- [x] `python scripts/run_refreshable_artifact_report.py`
- [x] `python scripts/run_worktree_settlement_report.py`
- [x] `python scripts/run_repo_governance_settlement_report.py`
- [x] latest live refreshable mirror at `2026-03-11T16:16:35Z`
- [x] latest live worktree mirror at `2026-03-11T16:16:46Z`
- [x] latest live repo governance mirror at `2026-03-11T16:16:51Z`
- [x] mirrored focus preview still resolves to `docs/status/subjectivity_review_batch_latest.json`
- [x] mirrored `requires_operator_action = false` across preview rows and focus card
