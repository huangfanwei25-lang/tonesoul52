> **P2 of the Judgment-Readiness Program (autonomous, 2026-06-15).** Auditor-facing
> architecture map of the real repo (5 clusters, 24 reduction candidates), with an
> honest LIVE / DORMANT-intentional / DEAD-candidate / DUPLICATE inventory. **Every
> deletion below is a PROPOSAL ONLY — none is executed; all are gated on human review
> per `docs/SUCCESSOR_MAP.md` ("no one imports it" != "safe to delete").** Reachability
> claims were re-verified against the working tree, not taken on faith.

# ToneSoul — Architecture & Drift-Reduction (Auditor Legibility, P2)

**Date:** 2026-06-15 · **Scope:** 5 cluster maps (governance_council, memory_continuity, perception_dream_evolution, yss_yuhun_gse, llm_infra_corpus) · **Status:** judgment-readiness P2 — **all deletions below are PROPOSALS ONLY.**

**Verification basis.** Load-bearing claims in this doc were re-checked against the working tree, not taken on faith: `yss_gates.poav_gate` live at `unified_pipeline.py:644` ✓; `evidence_detector` live via two-dot import `analyst.py:6` ✓; `tonesoul.evolution` live via `apps/api/server.py:31` + `api/_shared/core.py:24` + CI ✓; `strategy_mirror` flags default-OFF with enforce⇒scan coupling (`soul_config.py:198-227`) ✓; `_get_dpr()`/`_get_context_assembler()` have **zero call sites repo-wide** (dead hook) ✓; `tonesoul.corpus` has **zero non-test production importers** ✓; the two 2026-06-07 honesty sensors have **test-only importers** ✓.

---

## (1) Architecture Overview — one screen

ToneSoul is an **AI accountability framework**: it does not make answers *better*, it makes them *challengeable and auditable before they ship*. The load-bearing claim is structural ("structure-of-restraint"), **not** semantic — the truth/vow/epistemic sensors are lexical, English-centric heuristics blind to zh-TW (PR3, AXIOMS v1.2.0), and the post-verdict `independent_verifier` defaults OFF (fail-open). An auditor must carry this caveat: "governance" here means *evidence is surfaced and refusal is possible*, not *truth is guaranteed*.

**Request flow through the live spine (newcomer path):**

```
        ┌─────────────────────── tonesoul/soul_config.py ───────────────────────┐
        │   single source of every threshold: POAV 0.92/0.70, coherence, vow,    │
        │   GSE strategy_mirror flags (default OFF)                              │
        └───────────────────────────────────────────────────────────────────────┘
                                        │ read by ↓
  request ──► unified_pipeline.py  (GOD NODE #1, 153KB, out-degree 34 — the runtime spine)
                │
                ├─(1) perception/governance gate:  yss_gates.poav_gate  (high 0.92 / normal 0.70)
                ├─(2) GovernanceKernel  →  llm/router  →  {ollama | lmstudio | gemini}  (only path to a real LLM)
                ├─(3) VowEnforcer (vow_system.py, lexical/EN-centric)  +  reflex/drift  +  de_escalation framing
                ├─(4) CouncilRuntime.deliberate()  →  PreOutputCouncil.validate():
                │        epistemic_label  →  6 perspectives (analyst/critic/guardian/
                │        advocate/semantic_analyst/axiomatic_inference)  →  coherence  →
                │        verdict  →  [independent_verifier: OFF by default]
                │        [strategy_mirror rhetorical scan: opt-in, OFF by default]
                ├─(5) subconscious recall:  memory/openclaw/hippocampus.recall (every request;
                │        root memory/hippocampus = CorrectiveMemory, gated by _enable_corrective_recall)
                └─(6) persist:  runtime_adapter.commit()  →  AegisShield.protect_trace (hash-chain + Ed25519,
                         fail-VISIBLE since PR4)  →  memory.pipeline.run_session_end_pipeline  →
                         soul_db (SQLite/JSONL, time-decayed, source-attributed)
```

**Five subsystems, by health:**

| Subsystem | Health | One-line |
|---|---|---|
| governance_council | **LIVE core** | pre-output deliberation/restraint; legible spine, *split* (re-exports 3 root modules) |
| memory_continuity | **LIVE spine + parked periphery** | "continuity via artifacts not model memory"; spine clean, 32-file `memory/` dir confusing |
| llm + backends + soul_config | **LIVE, well-factored** | the only LLM path; two-driver store; single threshold file |
| perception_dream_evolution | **3 liveness tiers** | dream loop DORMANT, but `evolution/` (API) + `source_registry` (CI) quietly load-bearing |
| yss_yuhun_gse | **1 live + 1 opt-in + large parked** | `yss_gates` live, `strategy_mirror` opt-in, most of yuhun/gse/inter_soul parked |
| corpus + honesty sensors | **build-and-forgotten / staged** | `corpus/` never wired; 2 honesty sensors staged ahead of wiring |

**God nodes / change-risk concentrations:** `unified_pipeline.py` (153KB, #1), `runtime_adapter.py` (100KB, #5), `soul_db.py` (43KB, #7), `council/runtime.py` (#6), `autonomous_cycle.py` (#8, dormant). Coupling on the live spine is mostly via *small lazy local imports*, which keeps blast radius contained despite file size.

---

## (2) Inventory — LIVE / DORMANT-intentional / DEAD-candidate / DUPLICATE

Reachability evidence is the *runtime call site*, not the import alone (the central lesson: import ≠ invocation; "no one imports" ≠ dead).

### LIVE (in runtime path)

| Module | Reachability evidence |
|---|---|
| `unified_pipeline.py` | runtime spine, god-node #1 |
| `soul_config.py` | 7 production importers; defines POAV 0.92/0.70 (verified) |
| `vow_system.py` | `unified_pipeline.py:764` `.enforce(draft)`@774 + 12 importers |
| `governance/{kernel,reflex,reflex_config,de_escalation,responsibility_audit,retro,__init__}.py` | all on pipeline or runtime_adapter/CLI call sites |
| `yss_gates.py` | **`unified_pipeline.py:644 poav_gate` — verified live** (SUCCESSOR_MAP §1 #1 hazard) |
| `council/runtime.py`, `pre_output_council.py`, `perspective_factory.py`, all 6 `perspectives/*` | `validate()` deliberation sequence; perspectives via factory:40-45 |
| `council/evidence_detector.py` | **`analyst.py:6 from ..evidence_detector` — verified live** (two-dot, grep-invisible) |
| `council/{types,epistemic_labeler,coherence,verdict,self_journal,evolution,dossier,model_registry,swarm_framework,base,summary_generator}.py` | live council line; `types` = 31 importers |
| `council/{calibration,calibration_bucket_b,outcome_persistence,persistence}.py` | v0b calibration sub-line; *not* duplicates (distinct specs/stores) |
| `council/independent_verifier.py` | call site live (`pre_output_council:160`), **default `verifier=None` = behaviorally dormant/fail-open** |
| `gse/strategy_mirror/*` | **conditionally live**: `pre_output_council:258-259`, gated `strategy_mirror_scan_enabled` (default False, verified) |
| `runtime_adapter.py`, `aegis_shield.py`, `soul_db.py`, `memory/{decay,pipeline,write_gateway,provenance_chain,self_memory,intent_reconstructor,crystallizer,handoff_ingester,sovereignty_gate,semantic_graph,visual_chain}.py` | memory spine; aegis fail-visible since PR4 |
| `memory/openclaw/hippocampus.py` | `unified_pipeline.py:2642` recall every request (canonical) |
| `memory/subjectivity_*` family + `consolidator`/`journal_consolidator`/`reviewed_promotion`/`stats` | exported via `__init__` + driven by `scripts/run_subjectivity_*` / consolidation paths |
| `perception/source_registry.py` | **most-exercised cluster member** — CI workflow `external_source_registry.yml` + `repo_healthcheck.yml` |
| `evolution/{context_distiller,corpus_builder,corpus_schema}.py` | **verified live via deployed API** `apps/api/server.py:31` + `api/_shared/core.py:24` + CI |
| `llm/{router,ollama_client,gemini_client,lmstudio_client,__init__}.py` | kernel/server/scribe/dream/pipeline call sites; only path to an LLM |
| `backends/{file_store,redis_store}.py` | `store.py:122/132` facade selection + ~12 scripts + runtime_adapter |

### DORMANT-intentional (kept on purpose — cite why)

| Module(s) | Why kept | Marker status |
|---|---|---|
| `council/atomic_claims.py`, `convergence.py` | tested + documented council refinements, never wired into `validate()`; "forgotten gems, not rot" (SUCCESSOR_MAP §0/§6) | **no marker** → legibility gap |
| `memory/boot.py` (`memory_boot`) | complete tested session-start orchestrator wired to live modules; confirm-then-wire | documented as boot entry |
| `memory/{freshness,aaak,hybrid_search,session_resonance}.py` | parked staleness/compaction/retrieval substrate; staleness-defense story the project explicitly cares about | **no marker** |
| `stale_rule_verifier.py` | reachable only via DORMANT dream loop (`dream_engine.py:18`) | belongs on dream-loop dormant row |
| Phase-7 stack: `dream_engine`, `autonomous_cycle`, `wakeup_loop`, `autonomous_schedule`, `perception/{stimulus,web_ingest}`, `scribe/*` | built+tested (1457 green), ran once 2026-03-08, revived 2026-06-14; **empirical: no intrinsic motivation, Scribe hallucinates** | SUCCESSOR_MAP §6 ✓ |
| `yuhun/{world_sense,sleep_bridge,vod,shadow_doc,__init__}.py` | cohesive 30-test YUHUN Core, parked design surface | partial (YSS-STATUS on some) |
| `gse/element.py`+`registry.py`+`clusters/*.json` | GSE Phase-1 ontology; only `test_gse.py` imports — strongest unreferenced, but parked asset | **needs marker** |
| `inter_soul/*` | zero production importers; SUCCESSOR_MAP §6 parks for Phase 8 multi-agent | **no marker** → re-discovery risk |
| `observability/{logger,env_config,action_audit,execution_honesty,self_claim_audit,token_meter,__init__}.py` | infra seam + 2 recent (2026-06-07) honesty sensors staged ahead of wiring; `token_meter` wired-but-unfed (TYPE_CHECKING only) | **honesty sensors: no marker** |

### DEAD-candidate (genuinely unreachable today — deletion CANDIDATES, human-gated)

| Module | Reachability check | Confidence unreachable |
|---|---|---|
| `corpus/{pipeline,consent,storage,__init__}.py` | **verified: zero non-test importers** repo-wide; git log = lint/annotation only, never a wiring commit; lazy-loads a real `InternalDeliberation` so *wireable*, not broken | HIGH (~0.9) |
| **Dead hook (branch, not module):** `unified_pipeline._get_dpr` / `_get_context_assembler` | **verified: zero `_get_dpr()`/`_get_context_assembler()` call sites**; `self._dpr`/`self._context_assembler` set, never read; hook added 2026-04-13 (6a20ecf), consumption never wired | HIGH (~0.9) |
| `yuhun/dpr.py`, `yuhun/context_assembler.py` (as runtime features) | reachable *only* through the dead hook above; otherwise test-only + `__init__` re-export. **Corrects SUCCESSOR_MAP §6 "partly LIVE": import exists, invocation does not** | HIGH that the *runtime branch* is dead; modules themselves are test-covered substrate |

> Note: no module here is recommended for deletion — see §3. "Dead-candidate" = *the branch/feature is unreachable*, which is a wire-or-remove decision, not a delete-on-sight.

### DUPLICATE (overlapping name/API — not necessarily mergeable)

| Pair | Verdict |
|---|---|
| `memory/hippocampus.py` (root) vs `memory/openclaw/hippocampus.py` | **both live**: openclaw = primary recall (`:2642`); root = CorrectiveMemory (`:2694`, gated `_enable_corrective_recall`). Consolidation candidate, **not** deletion |
| repo-root shims `memory/{self_memory,provenance_chain,consolidator}.py` | **intentional** PR1 packaging compat shims, guarded by `tests/test_packaging_repo_root_import_guard.py`. Deleting re-breaks PR1 |
| `backends/{file_store,redis_store}` + `store.py` | **strategy pattern, not duplication** — do not collapse |
| `decay.py` vs `freshness.py` (shared `exp(-λt)`) | **different objects** (records vs zones) — shared math, not copy-paste |
| `calibration` vs `calibration_bucket_b`; `persistence` vs `outcome_persistence` | **deliberate layered/distinct** (v0a→v0b; verdict-store vs calibration-log) |

**Naming-collision traps an external reader will hit (no code issue, pure legibility):**
- `evolution` × 2: `tonesoul/evolution/` (live, API) vs `council.evolution` (council weights). A grep conflates them.
- `corpus` × 2: `tonesoul/corpus/` (dead) vs `evolution/corpus_builder.py` (live).
- `yuhun` × 3: `tonesoul/yuhun/` vs top-level `yuhun.*` (temp/, packaging-excluded) vs `apps/cli/yuhun_cli.py`.
- `yss`: `yss_gates` is the lone live survivor; `yss_pipeline` is the dead orchestrator.

---

## (3) Drift-Reduction Proposals — ranked by (safety × surface reduction)

Each is **PROPOSAL ONLY — needs human review per SUCCESSOR_MAP**. None is marked to-be-executed. Ranking favors *high-safety legibility fixes* first (zero behavior change), then *behavior-touching* items.

**P1 — Add dormancy markers (zero code-behavior change, highest safety).**
*What:* add `# DORMANT: <reason>` / `# COUNCIL-STATUS: unwired-refinement` / `# MEMORY-STATUS: unwired` markers (parity with the existing `# YSS-STATUS: unwired` convention) to the marker-less parked modules: `council/{atomic_claims,convergence}`, `memory/{freshness,aaak,hybrid_search,session_resonance}`, `inter_soul/*`, `gse/element.py`+`registry.py`, and the 2 honesty sensors `observability/{execution_honesty,self_claim_audit}`.
*Reachability check:* all verified zero non-test importers; markers are comments only.
*Surface reduction:* eliminates the #1 recurring failure — the next sweep re-discovers these cold and risks wrong-delete or wrong-rebuild.
*Confidence:* HIGH (safe + useful). **PROPOSAL ONLY — needs human review per SUCCESSOR_MAP.**

**P2 — Document the "looks-live-in-docs, parked-in-code" gaps in SUCCESSOR_MAP (doc-only).**
*What:* (a) add `stale_rule_verifier.py` + `memory/freshness.py` to the Phase-7 dream-engine dormant row, explicitly "reachable only via dormant dream loop." (b) Add `corpus/`, `council/{atomic_claims,convergence}`, `inter_soul/*`, root `gse/` to a §6 dormant-subsystems table.
*Reachability check:* verified — staleness defenses wire only through `dream_engine.py:18` (dormant).
*Surface reduction:* closes the silent-drift gap SUCCESSOR_MAP §6 itself warns about; no code touched.
*Confidence:* HIGH / zero-risk. **PROPOSAL ONLY — needs human review per SUCCESSOR_MAP.**

**P3 — Fix the contradictory `__ts_purpose__` in `yuhun/dpr.py` (metadata-only).**
*What:* change `__ts_purpose__` from "DPR (Dense Passage Retrieval): semantic retrieval" to match the docstring "Dynamic Priority Router / complexity-conflict routing."
*Reachability check:* code (`RoutingDecision FAST_PATH/COUNCIL_PATH`, `complexity_score`) confirms router, not retrieval; in-scope of SUCCESSOR_MAP §4 PR5b annotation cleanup.
*Confidence:* 0.95 (behavior-neutral). An auditor trusting the annotation would mis-describe the module today. **PROPOSAL ONLY — needs human review per SUCCESSOR_MAP.**

**P4 — Resolve the dead YUHUN hook in `unified_pipeline.py:190-210` (behavior-touching, wire-OR-remove).**
*What:* either **(a) WIRE** `_get_dpr`/`_get_context_assembler` into the pipeline so DPR routing actually runs (closes the 2026-04-13 tech-debt commit 6a20ecf as intended), **or (b) REMOVE** the two dead getters (keeping the `yuhun` package as test-covered substrate). **Do NOT do both; do NOT pick (b) silently if owner intends (a).**
*Reachability check:* **verified — zero `_get_dpr()`/`_get_context_assembler()` call sites repo-wide**; `self._dpr`/`self._context_assembler` set but never read.
*Confidence:* 0.9 the branch is dead (small residual risk of dynamic dispatch not found). **PROPOSAL ONLY — owner decides wire-vs-remove — needs human review per SUCCESSOR_MAP.**

**P5 — Decide `corpus/` (largest coherent dead surface; revive-OR-archive, NOT delete-on-sight).**
*What:* mark `corpus/` `# DORMANT: built for web-frontend corpus collection, never wired` and place on the dormant-subsystems map for an owner revive/archive decision.
*Reachability check:* **verified — zero non-test references** (grep over tonesoul/scripts/apps/api/examples/tools/*.toml/*.yaml); no importlib/string import; git log = lint+annotation only.
*Confidence:* unreachable HIGH (~0.9); **safe-to-DELETE only MEDIUM** — it is a coherent, tested, privacy-first consent+storage unit (the exact "forgotten gem" §6 warns against blind-deleting) and may be the intended frontend data path. **PROPOSAL: mark dormant, not delete. PROPOSAL ONLY — needs human review per SUCCESSOR_MAP.**

**P6 — Consolidate the two `Hippocampus` impls (refactor, preserve corrective path).**
*What:* fold root `memory/hippocampus.py` (CorrectiveMemory) onto one impl with `openclaw/hippocampus.py`.
*Reachability check:* both live — openclaw `:2642` (every request), root `:2694` (gated `_enable_corrective_recall`). This is a CONSOLIDATION, **not** a deletion; the corrective path MUST be preserved.
*Confidence:* LOW that it is safe to touch without a runtime test pass on the corrective branch. **PROPOSAL ONLY — needs human review per SUCCESSOR_MAP.**

**P7 — Rename/relocate proposals to break naming collisions (human-gated, touches live API).**
*What:* (a) rename `tonesoul/evolution/` → `self_evolution/` or `learning/` to disambiguate from `council.evolution`; (b) gather scattered Phase-7 modules under `tonesoul/autonomous/` or `tonesoul/dream/`; (c) cross-reference or relocate the split governance spine (`benevolence`/`escape_valve`/`vow_system` at root but imported as `governance.*`).
*Reachability check:* (a) touches 2 live import sites (`apps/api/server.py:31`, `api/_shared/core.py:24`) + CI + tests; (b) ~15 scripts/tests of import churn; (c) `vow_system` has 12+ importers and PR1 already showed root-module relocation breaks packaging (`test_packaging_repo_root_import_guard.py`).
*Confidence:* legibility benefit MEDIUM; **execution risk HIGH** — treat as ARCHITECTURE_BOUNDARIES work, not cleanup. **PROPOSAL ONLY — do NOT execute — needs human review per SUCCESSOR_MAP.**

**Explicit NON-candidates (clearing false positives so an auditor does not over-reduce):** `yss_gates` (live POAV gate), `evidence_detector` (live via relative import), `strategy_mirror` (opt-in live, default-OFF ≠ dead), `token_meter` (deliberate optional seam), `backends/store.py` (strategy pattern), root-shims (PR1-guarded), `decay`/`freshness` (different objects), `calibration_bucket_b`/`outcome_persistence` (distinct, not dup-of-older). **None should be merged or deleted.**

---

## (4) Honest legibility verdict

**Genuinely well-architected (clean for an external reader):**
- **The live spine reads like a spec.** `pre_output_council.validate()` (label → perspectives → coherence → verdict → verifier) and the `runtime_adapter → aegis → memory.pipeline → soul_db` commit path are coherent and well-commented; the PR4 fail-visible block in `runtime_adapter` is genuinely educational.
- **`soul_config.py` is exemplary** — one file, every threshold, each block cites its Axiom; an auditor can trace the POAV 0.92/0.70 gate straight from SUCCESSOR_MAP to `RiskConfig` to the call site.
- **`llm/` is a clean router-over-three-backends pattern; `backends/` a clean two-driver pattern.**
- **The Phase-7 dormancy candor is a model of honesty** — SUCCESSOR_MAP §6 + the 2026-06-14 revival doc document not just that it's parked but the *empirical finding* that the AI shows no intrinsic motivation and the Scribe hallucinates. That is the right way to record a parked experiment.
- **`strategy_mirror`** is well-documented (governance-enforces vs mirror-observes, default-off opt-in, spec reference).

**Accreted / confusing (where an external reader will get lost):**
- **Split governance spine** — `governance/__init__.py` re-exports 3 modules (`benevolence`, `escape_valve`, `vow_system`) that physically live at repo root; council depends on two directly. Grepping only `governance/` + `council/` under-counts the cluster.
- **Relative-import reachability trap** — `evidence_detector` is grep-invisible (live only via a two-dot import). This is the SUCCESSOR_MAP §0 "no one imports it ≠ dead" failure mode, one level deeper.
- **`memory/` is 32 files across 4 concerns with no sub-grouping** — the `subjectivity_*` family alone is ~7 files / 110KB that look like one feature exploded.
- **Import ≠ invocation, twice over** — `yuhun` dpr/context_assembler are *imported* into the pipeline but *never invoked* (dead hook); `token_meter` is imported by the LLM clients but *never fed*. Reading the import alone overstates liveness in both cases.
- **Four name collisions** (`evolution`, `corpus`, `yuhun`, `yss`) where the same word spans live and dead/parked code.
- **Markerless parked code** — the worst legibility gap: the modules with zero importers (`atomic_claims`, `convergence`, `inter_soul/*`, root `gse/`, the 2 honesty sensors) carry *no* dormancy marker, so their parked-vs-dead status is invisible from the file itself and the next agent re-derives it cold (this is what P1 fixes).
- **God nodes as standing change-risk** — `unified_pipeline.py` (153KB) and `runtime_adapter.py` (100KB) are themselves legibility costs, partly mitigated by lazy local imports keeping coupling small.

**Bottom line:** the *load-bearing core is legible and honestly mapped*; the drift is concentrated in (a) parked subsystems lacking status markers and (b) naming collisions — both addressable with zero-behavior-change legibility fixes (P1–P3) before any structural move. The only genuinely unreachable code (`corpus/`, the YUHUN dead hook) is a *wire-or-archive owner decision*, not rot to delete. No inflation: nothing here makes ToneSoul's sensors semantically stronger than the lexical/EN-centric heuristics they are.

**Relevant absolute paths:** `C:\Users\user\Desktop\倉庫\docs\SUCCESSOR_MAP.md` · `C:\Users\user\Desktop\倉庫\tonesoul\unified_pipeline.py` (lines 190-210 dead hook, 644 poav_gate) · `C:\Users\user\Desktop\倉庫\tonesoul\soul_config.py` (198-227) · `C:\Users\user\Desktop\倉庫\tonesoul\council\perspectives\analyst.py:6` · `C:\Users\user\Desktop\倉庫\tonesoul\corpus\` · `C:\Users\user\Desktop\倉庫\apps\api\server.py:31` · `C:\Users\user\Desktop\倉庫\api\_shared\core.py:24`
