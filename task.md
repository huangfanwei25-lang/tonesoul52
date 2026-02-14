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
**Latest validation**: `pytest -q` => `849 passed` (2026-02-14). Level 3 implementation tracked in `CODEX_TASK.md` v7.

## Backlog Radar (Original Specs/Docs, 2026-02-14)
- [ ] Sync and close pending Chat UI checklist in `spec/chat_ui_improvement_spec.md` (4 unchecked items)
- [ ] Execute/verify backend persistence acceptance list in `docs/plans/backend_persistence_acceptance_checklist.md` (16 unchecked items)
- [ ] Reconcile stale roadmap checkboxes in `docs/ARCHITECTURE_DEPLOYED.md` against implemented Phase 77-99 features
- [ ] Prioritize semantic-control derivation backlog in `spec/tonesoul_improvement_derivation.md` and `spec/wfgy_semantic_control_spec.md`
- [ ] Stage release/readiness checklists from `docs/RELEASE_v0.1.0_PLAN.md` and `docs/SMALL_BOAT_MVP.md`

## Phase 100: Architecture Convergence v2 (Trinket + Swarm)
- [x] Consolidated legacy RFC/draft into verified plan: `docs/ARCHITECTURE_CONVERGENCE_PLAN.md`
- [x] Added current-state correction (`UnifiedCore` is non-prod but still referenced; not immediate delete)
- [x] Added 841-test landscape + multi-persona audit baseline in convergence doc
- [x] Spec-first: define `TRINKET_PROTOCOL_SPEC` (Layer Decoupling / Is-Ought / Currency Audit / Responsibility Trace)
- [x] Runtime: add dispatcher state machine (`Resonance/Tension/Conflict`) with auditable metadata in `UnifiedPipeline`
- [x] Evolution alignment: bridge `yss_pipeline` context schema to unified runtime contract and populate non-null A/B/C evaluation artifacts
- [x] Zombie boundary: mark `UnifiedCore` as `legacy_non_runtime` with explicit replacement target
**Success Criteria**: v2 convergence plan is executable, testable, and reflected in blocking governance checks.

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


