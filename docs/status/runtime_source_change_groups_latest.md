# Runtime Source Change Groups Latest

- Generated at: `2026-03-08T15:40:43Z`
- Overall OK: `false`
- Dirty runtime-source entries: `130`
- Change groups: `8`
- Ungrouped entries: `0`

## Groups

1. **Repo Governance and Settlement** (`entries=24`)
   - Goal: Keep repo-level gates, settlement planners, and healthcheck contracts reviewable as one governance surface.
   - Action: Review healthcheck and settlement scripts as one changeset, because they define what counts as safe branch movement.
   - Action: Keep their tests and CI wiring paired so gate semantics do not drift from enforcement.
   - Categories: `scripts=12`, `tests=11`, `tooling=1`
   - Sample: `.github/workflows/test.yml`
   - Sample: `scripts/healthcheck.py`
   - Sample: `scripts/run_repo_healthcheck.py`
   - Sample: `scripts/verify_7d.py`
   - Sample: `scripts/verify_command_registry.py`
   - Sample: `scripts/verify_docs_consistency.py`
   - Sample: `tests/test_agent_discussion_tool.py`
   - Sample: `tests/test_run_repo_healthcheck.py`

2. **Skill and Registry Contracts** (`entries=6`)
   - Goal: Keep agent-skill governance and machine-readable registries aligned.
   - Action: Review skill docs, registry JSON, and validators together because they define the same contract surface.
   - Action: Settle this group before branch movement so agent-facing behavior does not drift from machine checks.
   - Categories: `scripts=2`, `skills=3`, `tests=1`
   - Sample: `.agent/skills/tonesoul_governance/SKILL.md`
   - Sample: `.agent/skills/tonesoul_philosophy/SKILL.md`
   - Sample: `scripts/skill_gate.py`
   - Sample: `scripts/verify_skill_registry.py`
   - Sample: `skills/registry.json`
   - Sample: `tests/test_verify_skill_registry.py`

3. **Governance Pipeline and LLM Runtime** (`entries=32`)
   - Goal: Keep governance, orchestration, council parsing, and LLM observability changes as one coupled runtime group.
   - Action: Review kernel, unified pipeline, LLM clients, and council parsing together because they share runtime decision contracts.
   - Action: Keep pipeline, governance, and LLM tests in the same changeset as the runtime files they validate.
   - Categories: `tests=15`, `tonesoul=17`
   - Sample: `tests/test_governance_kernel.py`
   - Sample: `tests/test_local_llm.py`
   - Sample: `tests/test_perspective_factory.py`
   - Sample: `tests/test_pipeline_compute_gate.py`
   - Sample: `tests/test_resistance.py`
   - Sample: `tests/test_unified_pipeline_v2_runtime.py`
   - Sample: `tests/test_variance_compressor.py`
   - Sample: `tests/test_work_classifier.py`

4. **Perception and Memory Ingest** (`entries=11`)
   - Goal: Keep environment perception, source selection, and memory-write seams reviewable as one ingest pipeline.
   - Action: Review perception, source registry, and memory write-gateway changes together because they form one ingest path.
   - Action: Keep registry checks and perception tests paired with the runtime modules they exercise.
   - Categories: `scripts=1`, `tests=4`, `tonesoul=6`
   - Sample: `scripts/verify_external_source_registry.py`
   - Sample: `tests/test_perception.py`
   - Sample: `tests/test_verify_external_source_registry.py`
   - Sample: `tonesoul/memory/__init__.py`
   - Sample: `tonesoul/perception/__init__.py`
   - Sample: `tonesoul/perception/stimulus.py`
   - Sample: `tonesoul/perception/web_ingest.py`
   - Sample: `tests/test_memory_write_gateway.py`

5. **Autonomous Verification Runtime** (`entries=41`)
   - Goal: Keep autonomous schedule, wake-up, dashboard, and weekly true-verification runners reviewable as one runtime chain.
   - Action: Review autonomous runtime modules with their runners and tests as one stack, because they share artifacts and cadence contracts.
   - Action: Treat task-scheduler wiring and true-verification summaries as part of the same operational runtime, not as detached scripts.
   - Categories: `scripts=13`, `tests=21`, `tonesoul=7`
   - Sample: `scripts/install_true_verification_task_scheduler.py`
   - Sample: `scripts/render_true_verification_task_scheduler.py`
   - Sample: `scripts/report_true_verification_task_status.py`
   - Sample: `scripts/run_autonomous_dream_cycle.py`
   - Sample: `scripts/run_autonomous_registry_long_run.py`
   - Sample: `scripts/run_autonomous_registry_schedule.py`
   - Sample: `scripts/run_dream_engine.py`
   - Sample: `scripts/run_dream_observability_dashboard.py`

6. **API Contract Surface** (`entries=4`)
   - Goal: Keep API entrypoints and server contract changes reviewable as one delivery surface.
   - Action: Review shared API core, chat route, and server wiring together because they define one external contract.
   - Action: Keep API security and contract tests attached to these runtime entrypoints.
   - Categories: `runtime_apps=3`, `tests=1`
   - Sample: `api/_shared/core.py`
   - Sample: `api/chat.py`
   - Sample: `apps/api/server.py`
   - Sample: `tests/test_api_phase_a_security.py`

7. **Supporting Runtime and Math** (`entries=11`)
   - Goal: Isolate supporting scripts, model probes, and math/runtime helpers from the core governance and autonomous stacks.
   - Action: Review support scripts and math helpers as one smaller follow-up set after the major runtime groups are stable.
   - Action: Do not let auxiliary probe or maintenance scripts blur the main governance/autonomy changesets.
   - Categories: `scripts=11`
   - Sample: `scripts/deduplicate_crystals.py`
   - Sample: `scripts/generate_stress_data.py`
   - Sample: `scripts/memory_compact.py`
   - Sample: `scripts/run_self_play_resonance.py`
   - Sample: `scripts/run_swarm_resonance_roleplay.py`
   - Sample: `scripts/tension_dashboard.py`
   - Sample: `scripts/test_delegation.py`
   - Sample: `scripts/test_ollama.py`

8. **Tooling and Editor Contract** (`entries=1`)
   - Goal: Keep local tooling drift explicit so it does not hide inside larger runtime groups.
   - Action: Review editor/tooling drift separately from runtime changes so developer ergonomics do not piggyback on feature work.
   - Categories: `tooling=1`
   - Sample: `.vscode/`
