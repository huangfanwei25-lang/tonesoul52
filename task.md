# Task

## Task.md Scope Guard (2026-04-01)
- `task.md` only tracks current accepted programs, active short boards, and already-ratified follow-through.
- External theory imports, speculative ecosystem borrowing, and unratified side-roadmaps must live under `docs/plans/` until they are explicitly pulled into the live short board.
- If a later agent discovers a useful outside idea, park it in a separate plan file first; do not overwrite the active bucket rotation here.

---

## Active Program: Launch Readiness And Design Legibility (2026-03-30)
> Merged from: Launch Maturity Go/No-Go + Design Center & Successor Continuation

- Program Goal: make ToneSoul honestly launchable as collaborator-beta, with a legible design center and explicit go/no-go criteria.
- Execution Guardrails:
  - Prefer real repeated validation and honest backend defaults over abstract theory lanes.
  - Keep public claims bounded by evidence level: tested, runtime-present, descriptive-only, and document-backed must remain distinct.
  - One durable design center over several overlapping "overview" files.
- Phase 721: ~~consolidate launch baseline~~ **done** (`docs/plans/tonesoul_launch_baseline_2026-04-08.md`)
- Phase 722: run repeated live continuity validation waves (bounded wave + 3 strong external/non-creator passes across 3 task shapes exist; keep public launch deferred, keep launch claims bounded, and refresh Phase 726 review before any widening)
- Phase 723: ~~backend decision~~ **done** (file-backed, see `tonesoul_coordination_backend_decision_2026-03-30.md`)
- Phase 724: ~~consolidate one current launch-operations surface~~ **done** (`docs/status/phase724_launch_operations_surface_2026-04-15.md`)
- Phase 725: ~~public-claim honesty gate~~ **done** (`claim_boundary` in session-start tier 0+2)
- Phase 726: ~~collaborator-beta go/no-go review~~ **done** (`docs/status/phase726_go_nogo_2026-04-08.md`, refreshed by `docs/status/phase726_go_nogo_2026-04-15.md`)
- Phase 729: ~~design center~~ **done** (`DESIGN.md`, 293 lines)
- Phase 730: add one 3-day execution program so the next agent can continue without reopening settled wording
- Phase 731: ~~compress entry-surface ownership and first-hop routing~~ **done** (`README.md`, `docs/foundation/README.md`, `docs/README.md`, `docs/INDEX.md`, `docs/AI_QUICKSTART.md`, `AI_ONBOARDING.md`)
- Phase 732: ~~sync Chinese public entry and retire dead historical-spec links from active entry contracts~~ **done** (`README.zh-TW.md`, entry contracts, historical-spec maps`)
- Phase 733: ~~publish repo-aligned continuation work plan v2~~ **done** (`docs/plans/tonesoul_work_plan_v2_2026-04-14.md`)
- Phase 734: ~~add high-traffic filename and entry index for render-safe lookup~~ **done** (`docs/foundation/FILENAME_AND_ENTRY_INDEX.md`, foundation/render guidance)
- Phase 735: ~~refresh collaborator-beta preflight after the repeated Phase 722 dual-surface pass~~ **done** (`scripts/run_collaborator_beta_preflight.py`, `docs/status/collaborator_beta_preflight_latest.{json,md}`)
- Phase 736: ~~publish fresh current-truth handoff after repeated Phase 722 evidence landed~~ **done** (`docs/status/codex_handoff_2026-04-14.md`)
- Phase 737: ~~publish a third bounded Phase 722 preflight-refresh pack and refresh launch-readiness continuation pointers~~ **done** (`docs/plans/tonesoul_non_creator_external_cycle_preflight_refresh_{pack,note_template}_2026-04-15.md`, `docs/README.md`)
- Phase 738: ~~publish fresh handoff after the third Phase 722 task shape landed~~ **done** (`docs/status/codex_handoff_2026-04-15.md`)
- Phase 739: ~~publish one 8-hour 1.0 execution program for the current launch line~~ **done** (`docs/plans/tonesoul_8hour_execution_program_2026-04-15.md`)
- Phase 740: ~~teach collaborator-beta preflight to recognize the Phase 722 preflight-refresh evidence family~~ **done** (`scripts/run_collaborator_beta_preflight.py`, `tests/test_run_collaborator_beta_preflight.py`)
- Phase 741: ~~refresh current-truth handoff after the first preflight-refresh attempt and detector fix~~ **done** (`docs/status/codex_handoff_2026-04-15.md`, `docs/status/phase722_external_preflight_refresh_cycle_2026-04-15.md`)
- Phase 742: ~~land the third clean Phase 722 preflight-refresh rerun and refresh canonical preflight truth~~ **done** (`docs/status/phase722_external_preflight_refresh_cycle_2026-04-15_rerun.md`, `docs/status/collaborator_beta_preflight_latest.{json,md}`)
- Phase 743: ~~refresh the collaborator-beta go/no-go review against the three-clean-cycle evidence base~~ **done** (`docs/status/phase726_go_nogo_2026-04-15.md`)
- Phase 744: ~~advance collaborator-beta preflight next-move routing past the refreshed Phase 726 review~~ **done** (`scripts/run_collaborator_beta_preflight.py`, `tests/test_run_collaborator_beta_preflight.py`)
- Phase 745: ~~publish a refreshed current launch-operations surface for collaborator beta~~ **done** (`docs/status/phase724_launch_operations_surface_2026-04-15.md`)
- Phase 746: ~~reroute collaborator-beta discovery surfaces to the refreshed Phase 724 operations anchor~~ **done** (`docs/README.md`, `docs/INDEX.md`, `scripts/run_collaborator_beta_preflight.py`)
- Phase 747: ~~refresh launch-line handoff after Phase 724 landed~~ **done** (`docs/status/codex_handoff_2026-04-15.md`)
- Phase 856: ~~harden backend durability, write-auth parity, and 500-redaction across runtime + API surfaces~~ **done** (`tonesoul/backends/file_store.py`, `tonesoul/runtime_adapter.py`, `api/_shared/{core.py,http_utils.py}`, `api/{chat.py,validate.py,health.py}`, `apps/api/server.py`, `tests/test_runtime_adapter.py`, `tests/test_store.py`, `tests/test_api_phase_a_security.py`, `tests/test_serverless_shared_core.py`, `tests/red_team/test_api_red_team_baseline.py`)
- Phase 857: ~~record 2026-04-18 commit-attribution red-light as a process lesson after PR #11 was merged before CI could complete, leaving 55d9e34 and 64c94df without `Agent:`/`Trace-Topic:` trailers on master; decline to reintroduce the enforcement anchor since 93bf6a0 deliberately removed it, and restore master to a green state via one forward commit that carries proper trailers~~ **done** (`task.md`)
- Phase 858: ~~give the body map honest classification so the analyzer stops collapsing ~92 root modules into a single "uncategorized" bucket~~ **done** (`scripts/analyze_codebase_graph.py`, `tests/test_analyze_codebase_graph.py`, `docs/status/codebase_graph_latest.{json,md}`)
  - Findings surfaced once the map became honest (each is a real signal, not a classifier bug, and belongs to a later scoping pass, not this patch):
    - `ystm.schema` is imported by 17 layers outside `domain` — it has already become a shared type primitive; candidate move is `tonesoul/shared/schema.py` or a thin re-export.
    - `governance` reaches into `evolution` (`council.runtime → benevolence`, `governance.kernel → resistance`) and `pipeline` (`constraint_stack → action_set`); either `ALLOWED_DEPS` widens to legitimize, or the deps invert via an interface.
    - `observability` imports into `memory`, `governance`, `domain`, `evolution` — defensible (observers observe) but should be encoded in `ALLOWED_DEPS` rather than living as perpetual violations.
    - `orchestration → perception` (`autonomous_cycle`, `autonomous_schedule`) looks like a legitimate downward dep that `ALLOWED_DEPS` just does not list yet.
    - `mcp_server` is the only `infrastructure` module that reaches up into `governance` + `pipeline`; that reflects its gateway-surface role and may deserve a `surface`/`gateway` reclassification in a follow-up.
- Phase 859: ~~teach the body map the intended shape so the analyzer stops flagging architectural truths as violations: promote `ystm.schema` to `shared` via a per-module override (no physical move), and widen `ALLOWED_DEPS` so `orchestration → perception`, `observability → {memory, governance, domain, evolution, semantic, perception}`, and `semantic → {governance, observability}` are legitimized rather than perpetually red~~ **done** (`scripts/analyze_codebase_graph.py`, `tests/test_analyze_codebase_graph.py`, `docs/status/codebase_graph_latest.{json,md}`)
  - Result: layer violations dropped 40 → 19. The remaining 19 are the genuinely inverted deps that still need an architectural decision (governance reaching into evolution/pipeline/domain, the mcp_server gateway sitting in infrastructure, pipeline→surface on `unified_pipeline → tonebridge`, package root re-exports).
- Phase 860: ~~let each module declare its own layer and purpose so the body map is driven by intent-at-source rather than by a central curated map: teach the analyzer to read `__ts_layer__` / `__ts_purpose__` module-level string constants via AST, record a `layer_source` provenance field (self_declared / override / root_map / subpackage / fallback), surface the declared `purpose` in the god-nodes table, track annotation coverage in the summary, and annotate 15 top god nodes as a representative sample~~ **done** (`scripts/analyze_codebase_graph.py`, `tests/test_analyze_codebase_graph.py`, `tonesoul/{unified_pipeline,runtime_adapter,yss_pipeline,autonomous_cycle,yss_gates,dream_engine,schemas}.py`, `tonesoul/council/{types,base,runtime,perspective_factory,pre_output_council}.py`, `tonesoul/governance/kernel.py`, `tonesoul/memory/soul_db.py`, `tonesoul/ystm/demo.py`, `docs/status/codebase_graph_latest.{json,md}`)
  - Result: baseline annotation coverage 15/254 (5.9%) with every top-coupling module carrying a declared layer + human-readable purpose line. Three-tier classifier priority: `self_declared > override > root_map > subpackage > fallback`. The shift from central curation to per-module self-declaration reclassified `council.types` and `council.base` (governance → shared), `ystm.demo` (domain → surface), `schemas` (governance → shared), which surfaced 4 additional honest violations; total remains in the same ballpark (19 → 23) but each is now attributable to a deliberately declared layer rather than a bulk-mapped default.
- Phase 861: ~~make the docs-level index agree with the body map so AIs stop being routed to 3.5-week-old conceptual documents when they need a file-level layer/purpose lookup: add a "Code-Level Lookup" lane + routing rule to `docs/INDEX.md` that points file-level queries at `docs/status/codebase_graph_latest.md` and explicitly de-ranks `CORE_MODULES.md` for that use case, and rewrite `docs/ARCHITECTURE_BOUNDARIES.md` so the outer 3-partition view (surfaces / governed runtime / persistent state) is reconciled with the inner 13-layer body-map taxonomy plus the real `ALLOWED_DEPS` table~~ **done** (`docs/INDEX.md`, `docs/ARCHITECTURE_BOUNDARIES.md`)
  - Result: two canonical surfaces (`INDEX.md`, `ARCHITECTURE_BOUNDARIES.md`) now treat `docs/status/codebase_graph_latest.md` as the authoritative source for code-level claims, and the stale 3-layer `application / governance / infrastructure` framing has been replaced with the 13-layer body-map taxonomy that the CI gate actually enforces. Distinguishes `memory/` (top-level persistent state dir) from `tonesoul/memory/` (runtime memory layer) so the same word no longer names two different things.
- Phase 862: ~~cross-link the remaining three narrative docs (`CORE_MODULES.md`, `KNOWLEDGE_GRAPH.md`, `FILE_PURPOSE_MAP.md`) to the body map with explicit routing callouts, and measure whether a cold agent actually uses the new routing~~ **done** (`docs/CORE_MODULES.md`, `docs/KNOWLEDGE_GRAPH.md`, `docs/FILE_PURPOSE_MAP.md`)
  - Each of the three docs now carries a `⚠️ Routing` block at the top that (a) declares what the doc is really for (conceptual subsystem narrative / theory→impl map / naming conventions) and (b) redirects file-level lookups to `docs/status/codebase_graph_latest.md`.
  - Cold-agent routing test (Explore agent, prompted without any hints, asked to answer *"what does tonesoul/yss_pipeline.py do / which layer / deps?"*): the agent went `README.md → tonesoul/yss_pipeline.py → architecture/…SUBSYSTEM_GUIDE.md → architecture/…EIGHT_LAYER_CONVERGENCE_MAP.md → tests/test_yss_pipeline.py + grep`. It correctly read the `__ts_layer__ = "pipeline"` self-declaration on the .py file (Phase 860 paid off at source) but **never consulted the body map** (`docs/status/codebase_graph_latest.md`), nor `INDEX.md` / `ARCHITECTURE_BOUNDARIES.md`. It also anchored on the older 8-layer `EIGHT_LAYER_CONVERGENCE_MAP.md` rather than the 13-layer body-map taxonomy.
  - Two honest findings from the test that still need follow-up: (1) agents dropping cold into the repo hit `README.md → <target>.py` before any `docs/` surface, so a body-map pointer on `README.md` / `tonesoul/__init__.py` / `DESIGN.md` would actually change routing; (2) `architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md` is a third layer model (8-layer) orthogonal to the two already reconciled in Phase 861 — it should either be retired, or explicitly labeled as a theoretical lens with a cross-link to the body-map's 13-layer taxonomy.
- Phase 863: ~~put body-map pointers at the cold-entry surfaces a cold agent actually hits first (`README.md`, `tonesoul/__init__.py`, `DESIGN.md`), and reconcile `TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md` with the 13-layer body map by labeling it as an orthogonal request-flow axis rather than a competing taxonomy~~ **done** (`README.md`, `tonesoul/__init__.py`, `DESIGN.md`, `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`)
  - `README.md`: added a second "AI Agent (file-level lookup)" row to the Choose Your Entry table that routes `"what does tonesoul/<x>.py do / which layer / who depends on it?"` directly to `docs/status/codebase_graph_latest.md` and explicitly de-ranks `docs/CORE_MODULES.md` for this question class.
  - `tonesoul/__init__.py`: expanded the one-line package docstring to point at `docs/status/codebase_graph_latest.md` for per-module lookup and at `docs/ARCHITECTURE_BOUNDARIES.md` for import rules; placed here because cold agents reading source before docs will now see the pointer at the package-root docstring.
  - `DESIGN.md`: added a `⚠️` callout near the top distinguishing "why the system is shaped this way at all" (this doc) from "what does this file do" (body map), so agents opening the design center no longer use it as a file lookup.
  - `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`: kept as canonical (it is referenced from `docs/INDEX.md`) but added a `⚠️` disclaimer at the top declaring it a **request-flow axis** (ingress → sensing → … → attachment) orthogonal to the **import-dependency axis** of the 13-layer body map; explains that one request can cross several body-map layers and one body-map layer can serve several request-flow stages, so the two views do not compete.
  - Routing rule for agents now reads cleanly across four cold-entry surfaces: `README` → file-level lookup lane → body map; `tonesoul/__init__.py` → body map pointer; `DESIGN.md` → body map pointer; `EIGHT_LAYER_CONVERGENCE_MAP.md` → labeled as orthogonal axis with a link back to the body map.

## Active Program: Agent Workspace And IDE Translation (2026-04-06)
- Program Goal: translate ToneSoul's tiered runtime surfaces into an operator workspace / IDE.
- Execution Guardrails:
  - Prefer view-model adapters and render budgets over raw packet dumps.
  - Preserve CLI parity and label discipline.
- Status: baseline dashboard operator-shell lane landed through Phase 784; bounded tool-entry contract hardening landed in Phase 855 after an audit-found MCP/runtime gap. Freeze this bucket unless a concrete workspace misread, role-parity regression, or operator-shell contradiction reopens it.
- Landed follow-through:
  - Phase 769: ~~adapt `apps/dashboard` workspace into the first operator shell~~ **done** (`apps/dashboard/frontend/pages/workspace.py`)
  - Phase 774: ~~realign dashboard status panel to tier model~~ **done** (`apps/dashboard/frontend/components/status_panel.py`)
  - Phase 780: ~~add one bounded operator walkthrough pack~~ **done** (`docs/plans/tonesoul_operator_walkthrough_pack_2026-04-06.md`, `apps/dashboard/frontend/utils/session_start.py`, `apps/dashboard/frontend/pages/workspace.py`)
  - Phase 784: ~~add one bounded retrieval-preview strip~~ **done** (`apps/dashboard/frontend/pages/workspace.py`, `apps/dashboard/frontend/utils/search.py`)
  - Phase 855: ~~harden v1.2 tool-entry MCP contract against batch-input and malformed commit payload regressions~~ **done** (`tonesoul/mcp_server.py`, `scripts/run_v1_2_tool_entry_smoke.py`, `tests/test_mcp_server.py`, `tests/test_run_v1_2_tool_entry_smoke.py`)
- Historical supporting phases already landed: 770-773, 781-783.
- Reopen rule: do not treat this bucket as an active short board again unless the dashboard/operator shell starts misreading authority, retrieval provenance, or tier boundaries.

## Active Program: Knowledge Layer Foundation (2026-04-06)
> Trimmed from: Research-Driven Memory Interop And Knowledge Layer

- Program Goal: define the boundary between raw sources, compiled knowledge, and operator retrieval so they stop blurring.
- Status: core boundary lane landed through Phase 791; defer live retrieval/runtime expansion until a later program reopens it.
- Follow-through:
  - Phase 787: ~~define knowledge-layer source taxonomy and parking policy~~ **done** (`docs/architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md`)
  - Phase 788: ~~define compiled-knowledge landing-zone spec~~ **done** (`docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md`)
  - Phase 789: ~~define bounded operator-retrieval query contract~~ **done** (`docs/architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md`)
  - Phase 790: ~~establish first Foundation Layer entry pack~~ **done** (`docs/foundation/README.md` + 6 thin guides)
  - Phase 791: ~~publish four-pressure convergence map~~ **done** (`docs/plans/tonesoul_four_pressure_point_convergence_map_2026-04-14.md`)
  - Phase 792: ~~land measurable four-pressure audit + structured quickstart smoke demo~~ **done** (`scripts/run_tonesoul_convergence_audit.py`, `examples/quickstart.py --json`)
  - Phase 793: ~~tighten formula honesty taxonomy and calibrate pseudo-formula audit~~ **done** (`README.md`, `docs/GLOSSARY.md`, `docs/MATH_FOUNDATIONS.md`, `scripts/run_tonesoul_convergence_audit.py`)
  - Phase 794: ~~extract runtime adapter normalization seam~~ **done** (`tonesoul/runtime_adapter_normalization.py`, `tests/test_runtime_adapter_normalization.py`)
  - Phase 795: ~~extract runtime adapter routing seam~~ **done** (`tonesoul/runtime_adapter_routing.py`, `tests/test_runtime_adapter_routing.py`)
  - Phase 796: ~~extract runtime adapter subject-refresh seam~~ **done** (`tonesoul/runtime_adapter_subject_refresh.py`, `tests/test_runtime_adapter_subject_refresh.py`)
- Deferred: cross-consumer drift validation (786), surface-versioning (785), launch-health trend (778), internal-state observability (779) -- revisit after knowledge boundary is clear

## Active Program: Self-Improvement Loop v0 (2026-04-06)
- Program Goal: let ToneSoul improve bounded operator/runtime surfaces through explicit evaluation, experiment lineage, and promotion discipline.
- Execution Guardrails:
  - Treat this as bounded improvement for operator surfaces, not identity-rewrite.
  - Keep `R-memory`, `compiled knowledge`, `experiment lineage`, and `canonical governance truth` visibly separate.
- Foundation: evaluator harness, experiment registry, mutation-space contract, analyzer gate, promotion-ready result surface, dashboard cue, shell boundary guard
- Trial Execution Pattern: `admit candidate -> run trial -> classify result -> register in lineage`
- Progress: **18 trials promoted, 1 parked** (as of 2026-04-16, per `docs/status/self_improvement_trial_wave_latest.json`)
- Current posture: no new admitted candidate is currently visible in the latest status surface; reuse the existing promotion limits and replay rules instead of inventing a new candidate ad hoc.
- Next: admit one next bounded candidate only if it improves operator/runtime packaging without reopening governance, identity, or transport mythology. Each trial still follows `admit -> run -> classify -> register`; no need to list each one as a separate phase.

---

## Water-Bucket Snapshot (2026-04-08)

**Baseline reached:**
- Session-start / session-end / packet / delta / readiness / receiver-guard continuity
- Subject snapshot + bounded subject refresh + working-style continuity
- Council dossier / descriptive confidence / suppression visibility / council-realism
- Cross-surface receiver parity + evidence/readout posture
- README / authority-lane / evidence-lane / stale-source cleanup
- Whole-system guide + cold-audit / fail-stop / anchor posture contract
- Context-injection prompt adoption (`value_accumulator`, `self_commit`, unified runtime framing)
- Collaborator-beta preflight, entry-validation, discoverable beta-facing status surfaces
- Low-drift anchor / observer-window baseline
- Outer-shell preflight chain for shared edits, publish/push, task-board parking
- Self-improvement foundation + 18 promoted trials
- Governance-depth routing (light/standard/full) + grounding check + verification fail-stop
- Cross-agent consistency wave (7/7 checks passing)
- Multi-agent review rounds 1+2: 17/18 findings fixed (only #14 vow semantic analysis deferred)

**Current short board:**
- Self-improvement loop: admit one next bounded candidate only if it improves operator/runtime packaging without reopening governance, identity, or transport mythology
- Launch readiness: current collaborator-beta launch-operations surface is consolidated; keep it aligned and do not widen launch claims until blocked overclaims move
- Real-world usage validation: three clean external/non-creator bounded cycles now exist across three task shapes; collaborator beta remains CONDITIONAL GO, public launch stays deferred, and launch claims stay evidence-bounded

**Archived programs:**
- R-Memory Maturation Roadmap (Phase 654-698) -- baseline-frozen
- Cross-Surface Consistency And Theme Rotation (Phase 713-719) -- baseline-frozen
- Consistency-First Governance Depth (Phase 848-854) -- fully closed
- See `docs/chronicles/` for details

## Archive Index

> Completed phases are archived in `docs/chronicles/`:

- [task_archive_phase_001-100.md](docs/chronicles/task_archive_phase_001-100.md) -- Phase 76-100
- [task_archive_phase_101-200.md](docs/chronicles/task_archive_phase_101-200.md) -- Phase 106-200
- [task_archive_phase_201-300.md](docs/chronicles/task_archive_phase_201-300.md) -- Phase 201-300
- [task_archive_phase_301-400.md](docs/chronicles/task_archive_phase_301-400.md) -- Phase 301-400
- [task_archive_phase_401-500.md](docs/chronicles/task_archive_phase_401-500.md) -- Phase 401-500
- [task_archive_phase_501-600.md](docs/chronicles/task_archive_phase_501-600.md) -- Phase 501-569
- [task_archive_phase_570-854.md](docs/chronicles/task_archive_phase_570-854.md) -- Phase 570-854 (2026-03-20 to 2026-04-08)
