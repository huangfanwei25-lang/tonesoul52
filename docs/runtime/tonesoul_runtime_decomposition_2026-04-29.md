# ToneSoul Runtime Decomposition (2026-04-29)

> Purpose: name the structural tension between ToneSoul's mature conceptual layer and its centralized runtime, propose a port-based decomposition that maps onto current code reality, and define the smallest first seam that can be extracted without competing with the 14-day collaborator-beta wave.
> Status: planning aid only. **No code changes.** This doc must not outrank `task.md`, latest `docs/status/*`, code, or tests.
> Scope: Phase 0 of a three-phase Runtime Decomposition → Boundary Contract → Incremental Refactor program. Phase 1 (refactor execution) is deliberately deferred until after the 14-day beta wave Day 14 review.
> Authority posture: this doc proposes a *map*, not a rewrite. Implementations remain authoritative; this map exists to be falsified by them.
> Integration note: first committed after PR #37 made `strategy_mirror` shadow mode operator-activatable and fixed stale human/audit surfaces. If this map drifts, code and tests remain the current truth.
> Last updated: 2026-05-03.

---

## 0. Before the map — what this doc is for

ToneSoul today is two structures fused into one repository.

**The conceptual structure is mature.** Externalized cognitive architecture, the 13-layer body map under `__ts_layer__` self-declarations, the 8-layer request-flow convergence map, the evidence ladder (E1 test-backed → E5 philosophical), the Axioms, the public/private dual-track boundary, the spec under `docs/architecture/`. A reader picking up the project at the conceptual layer can find an honest, well-typed account of what ToneSoul claims to be.

**The runtime structure is still centralized.** `tonesoul/unified_pipeline.py` is **3300 lines**; its `process()` method spans roughly **1500 lines** containing **26+ inline-numbered phases** with numbering gaps (two phases labeled `4.`, no `12.`, jumping to `13.`) that betray organic growth never refactored. `tonesoul/runtime_adapter.py` is **2289 lines**. `apps/api/server.py` is **1956 lines**. `apps/web/src/components/ChatInterface.tsx` is **1756 lines**. The conceptual layers do not have one-to-one runtime modules — they live as inline phases in the centralized files.

This doc names that tension and offers a port-based decomposition that lets each conceptual layer become an independently testable boundary. **It does not propose to refactor anything in this PR.** It proposes a map; the actual extraction of seams is deferred to after the 14-day beta wave so refactor work does not compete with real-usage evidence collection.

If you read this doc only as architectural housekeeping, you will get a working decomposition but miss what it is for. The point is not "smaller modules"; the point is **letting each layer of governance the project already claims to have become a boundary that can be tested, replaced, or denied independently**. Without that, every claim about "the Council does X" or "the tension engine does Y" routes through one 1500-line function — meaning the conceptual layer is mostly aspirational at the runtime level.

The remaining sections describe the proposed decomposition and the order of work that respects the 14-day wave's attention budget.

---

## 1. The structural tension named

### 1.1 Evidence

| File | Lines | Role |
|---|---|---|
| `tonesoul/unified_pipeline.py` | 3300 | central process pipeline |
| `tonesoul/runtime_adapter.py` | 2289 | governance posture loader, claims, perspectives |
| `apps/api/server.py` | 1956 | HTTP entry, auth, rate limiting, all endpoints |
| `apps/web/src/components/ChatInterface.tsx` | 1756 | frontend chat surface |
| `tonesoul/council/pre_output_council.py` | ~245 | pre-output council (already small — counter-example) |
| `tonesoul/gse/strategy_mirror/detector.py` | ~215 | strategy mirror detector (counter-example) |

Line counts are a snapshot from `origin/master` after PR #37 (`399f4d4`). Regenerate them before using this doc to justify an extraction PR.

The pattern: **older subsystems accreted into single large files; newer subsystems (PR #32/#33/#37 strategy_mirror; Phase 864c deliberation_trace) ship as small focused modules**. The strategy_mirror sub-package shipped by PR #32 is 4 small files totaling under 1000 lines; PR #37 made its shadow-mode path operator-activatable and corrected post-enforcement human/audit surfaces. The structural example exists; the question is whether older subsystems can follow it.

### 1.2 The 26-phase pipeline — UnifiedPipeline.process() phase markers

`tonesoul/unified_pipeline.py` lines 1841–3300, in source order:

| Approx line | Phase comment (verbatim where Chinese) | Conceptual stage |
|---|---|---|
| 1869 | `Phase V: Compute Gate (Revenue / API Protection)` | ingress |
| 2089 | `Cross-Session Recovery (first non-fast path call only)` | ingress |
| 2095 | `注入 Adapter（persona + context）` | ingress |
| 2099 | `0. 重建 Third Axiom 狀態` | ingress |
| 2103 | `0.5 重建軌跡分析器狀態` | ingress |
| 2107 | `0.6 Scenario Envelope (Bull/Base/Bear)` | ingress |
| 2110 | `1. ToneBridge 分析用戶` | context assembly |
| 2119 | `2. Trajectory 分析` | context assembly |
| 2161 | `2.1 Unified Tension Computation` | tension/friction |
| 2193 | `Phase 544: attach drift summary to dispatch trace` | tension/friction + observability |
| 2229 | `Governance Reflex Arc` | tension/friction |
| 2377 | `2.4 Phase 545: AlertEscalation — L1/L2/L3` | tension/friction |
| 2454 | `2.5 ToneSoul 2.0: 內在審議` | pre-output governance (early) |
| 2560 | `2.6 Phase 545: L2/L3 graduated response` | pre-output governance (early) |
| 2599 | `3. 第三公理：載入承諾堆疊` | context assembly |
| 2610 | `3.5 注入早期矛盾警告` | context assembly |
| 2613 | `3.6 GraphRAG Context Retrieval` | context assembly |
| 2624 | `3.7 Semantic Trigger (high-tension recurrence check)` | context assembly |
| 2631 | `3.8 Hippocampus Subconscious Retrieval` | context assembly |
| 2746 | `4. 生成增強 prompt` | draft generation |
| 2755 | `4. LLM 生成回應` *(numbering duplicated)* | draft generation |
| 2840 | `6. Reflection Loop + Council 審議` *(skipped 5)* | pre-output governance (main) |
| 3065 | `7. 第三公理：語場斷裂偵測` | memory commit (validation) |
| 3080 | `8. 第三公理：提取新的 SelfCommit` | memory commit |
| 3096 | `9. 更新記憶單元` | memory commit |
| 3121 | `10. 更新記憶單元` *(duplicate "update memory unit")* | memory commit |
| 3138 | `11. 產生內部敘事摘要` | memory commit |
| 3148 | `13. 收集 Third Axiom 資料` *(no 12)* | memory commit |

**Numbering anomalies (two `4.`, missing `5.`, missing `12.`, two "update memory unit" steps) are themselves data**: they show this method has been edited many times without renumbering, which is a strong signal that no boundary contract has been imposed on its growth. Phases get inserted by need, not by structural plan.

---

## 2. Eight-port decomposition

The 7 ports proposed by Codex 2026-04-29, plus an 8th (Sub-agent Coordination) that closes a gap none of the 7 cover. Each port is a candidate boundary for future extraction; none yet exists as a distinct module hierarchy.

For each port: **what runs in it / owner module(s) / evidence level / test entry / unified_pipeline.py line range**.

### 2.1 Port — Ingress / ComputeGate

What runs in it: HTTP entry, auth, rate limiting, tier resolution, fast-path vs full-path routing, cross-session recovery, adapter injection, third-axiom-state and trajectory-analyzer rebuild, scenario envelope.

Owner modules:
- `apps/api/server.py` (1956 lines — multi-port, dominant at this layer)
- `tonesoul/gates/compute.py` (`ComputeGate`, `RoutingPath`)
- `tonesoul/runtime_adapter.py` first half (`load()`, `_attach_reflex_state`, `_record_footprint`)
- inline phases in `unified_pipeline.py:1869–2107`

Evidence level: **E3** (runtime-present; tested via `tests/test_runtime_adapter*.py` + `tests/test_api_phase_a_security.py`)

Test entry: `tests/test_runtime_adapter.py` + `tests/red_team/test_api_red_team_baseline.py` + `tests/test_api_phase_a_security.py`

unified_pipeline.py range: lines 1869–2107 (~240 lines inline)

### 2.2 Port — Context Assembly

What runs in it: ToneBridge analysis (tone, motive, scenario), trajectory analysis, commitment-stack load, early-contradiction warnings, GraphRAG retrieval, semantic-trigger recurrence check, hippocampus subconscious retrieval.

Owner modules:
- `tonesoul/tonebridge/` (analyzer, commitment_extractor, entropy_engine, personas, rupture_detector, scenario_envelope, self_commit, session_reporter)
- `tonesoul/yuhun/context_assembler.py` (newer port-style module)
- GraphRAG retrieval (location not yet centralized)
- inline phases in `unified_pipeline.py:2110–2119, 2599–2631`

Evidence level: **E3** (runtime-present; ToneBridge tested; YUHUN context_assembler has its own test file; GraphRAG integration thinner)

Test entry: `tests/test_tonebridge*.py`, `tests/test_yuhun_context_assembler.py`, scattered

unified_pipeline.py range: lines 2110–2119 + 2599–2631 (~50 lines inline, but called functions are substantial)

### 2.3 Port — Tension / Friction

What runs in it: unified tension computation, drift summary attachment, Governance Reflex Arc, AlertEscalation L1/L2/L3 graduated response.

Owner modules:
- `tonesoul/tension_engine.py` (502 lines — already has its own module)
- `tonesoul/drift_monitor.py` (242 lines — already has its own module)
- `tonesoul/semantic_control.py` (Coupler, LambdaObserver, SemanticZone)
- inline phases in `unified_pipeline.py:2161–2453, 2560–2598`

Evidence level: **E1** (test-backed: `tests/test_tension_engine.py`, etc.)

Test entry: `tests/test_tension_engine.py`, `tests/test_drift_monitor.py`, `tests/test_semantic_control.py`

unified_pipeline.py range: lines 2161–2453 + 2560–2598 (~330 lines inline)

### 2.4 Port — Draft Generation

What runs in it: enhanced prompt assembly, LLM call (router + backend fallback), response parsing.

Owner modules:
- `tonesoul/llm/` (router, providers)
- inline prompt assembly in `unified_pipeline.py:2746–2839`

Evidence level: **E3**

Test entry: `tests/test_llm_router.py` (or similar)

unified_pipeline.py range: lines 2746–2839 (~90 lines inline)

### 2.5 Port — PreOutput Governance

What runs in it: pre-output council deliberation, perspective evaluation, coherence computation, verdict generation, deliberation_trace, **strategy_mirror scan + signature attachment + force-downgrade (after PR #32/#33/#37)**, benevolence audit, persona audit, VTP, POAV, contracts.

Owner modules:
- `tonesoul/council/pre_output_council.py` (~245 lines, well-modularized)
- `tonesoul/council/perspectives/*` (Guardian, Analyst, Critic, Advocate, Axiomatic)
- `tonesoul/council/verdict.py` (generate_verdict)
- `tonesoul/council/deliberation_trace.py` (Phase 864c)
- `tonesoul/gse/strategy_mirror/*` (PR #32/#33/#37 — newest module set)
- `tonesoul/council/benevolence_audit.py`
- `tonesoul/council/persona_audit.py`
- inline call in `unified_pipeline.py:2454–2559, 2840–3064`

Evidence level: **E1** for council core and current `strategy_mirror` runtime wiring/tests; **E3** for beta-wave behavioral claims that still require real session evidence; **E4** for some benevolence/persona claims

Test entry: `tests/test_pre_output_council*.py`, `tests/test_strategy_mirror_*.py`, `tests/test_council_*.py`

unified_pipeline.py range: lines 2454–2559 + 2840–3064 (~330 lines inline)

**This is the most-recently-touched port** (PR #32/#33/#37 just shipped). Decomposition work here should wait for stabilization, per §5.

### 2.6 Port — Memory Commit

What runs in it: speech-field rupture detection, SelfCommit extraction, memory unit updates (twice — likely needs deduplication), inner narrative summary, Third Axiom data collection, journal/crystal/decay/handoff.

Owner modules:
- `tonesoul/memory/*` (self_journal.py, crystallizer.py, soul_db.py, decay.py)
- `tonesoul/memory/consolidator.py`
- inline phases in `unified_pipeline.py:3065–3300`

Evidence level: **E1** for journal/crystals; **E3** for SelfCommit extraction; **E4** for "warm retrieval" (per `project_followup_warm_memory_retrieval_2026-04-28.md` — this is Phase 5 candidate work)

Test entry: `tests/test_memory_*.py`, `tests/test_crystallizer.py`

unified_pipeline.py range: lines 3065–3300 (~235 lines inline, including the duplicate "update memory unit" issue)

### 2.7 Port — Observability

What runs in it: dispatch_trace, drift_summary attachment, Aegis hash chain (provenance), session_traces, status artifacts (codebase_graph_latest, persona_track_record, healthcheck), structured logging.

Owner modules:
- `tonesoul/observability/*`
- `tonesoul/runtime_adapter.py` write_perspective / write_checkpoint / write_compaction / write_subject_snapshot (lines 509–700)
- `.aegis/` chain head + Ed25519 keypairs
- `docs/status/*_latest.{json,md}` (regenerated artifacts)

Evidence level: **E1** for Aegis (Phase 866 hardened); **E3** for dispatch_trace; **E3** for status artifacts

Test entry: `tests/test_aegis*.py`, `tests/test_observability_*.py`

unified_pipeline.py range: cross-cutting (attached at multiple points; not a single inline range)

### 2.8 Port — Sub-agent Coordination *(addition vs Codex's 7)*

What runs in it: agent claims and releases, perspective writes between agents, checkpoint writes, compaction handoff, session lifecycle (start_agent_session / end_agent_session), commit attribution gate, multi-agent gateway, AGENTS.md / CLAUDE.md operational contracts.

Owner modules:
- `tonesoul/runtime_adapter.py` `claim_task` / `release_task_claim` / `list_active_claims` / `write_perspective` / `write_compaction` / etc.
- `scripts/start_agent_session.py` / `scripts/end_agent_session.py`
- `scripts/gateway.py`
- `memory/handoff/`
- `CLAUDE.md` + `AGENTS.md` (operational protocols, not code, but governance contracts)
- `.github/workflows/commit_attribution_check.yml` (CI-enforced)

Evidence level: **E3** for claim/release runtime; **E1** for commit-attribution CI gate; **E4** for agent-handoff narrative continuity (handoff files describe pattern but don't enforce)

Test entry: `tests/test_runtime_adapter.py` (claims/perspectives), `tests/test_commit_attribution_check.py` (CI gate), no integration test for full agent-handoff cycle yet

unified_pipeline.py range: not directly inline — this port is *outside* `process()` because it operates at the **session** level, not the **request** level. That distinction is itself the rationale for treating it as its own port.

**Why this is the 8th port (and not a layer of one of the other 7):** the #32/#33/#37 work involved Claude Opus 4.7, Codex (independent reviewer/implementer), and Fan-Wei (operator) collaborating across multiple sessions on a single coherent feature. The coordination of that collaboration is currently distributed across `runtime_adapter.py` claim functions, the session-start/end scripts, and the AGENTS.md / CLAUDE.md operational protocols. There is no single owner module. Treating it as a port surfaces it as a runtime concern, not just a cultural pattern. **This may be ToneSoul's most differentiated runtime axis** — most AI runtime systems do not treat multi-agent collaboration as a first-class subsystem.

---

## 3. Reconciliation with existing taxonomies

ToneSoul already has two layer-models. Adding an 8-port decomposition without explicit reconciliation would violate `README.md` §2 "one durable design center" discipline and turn the codebase into a layer zoo.

### 3.1 vs the 13-layer body map

The body map (`docs/status/codebase_graph_latest.md`, generated by `scripts/analyze_codebase_graph.py`) classifies every module by import-dependency layer: `surface`, `governance`, `evolution`, `memory`, `domain`, `semantic`, `observability`, `perception`, `infrastructure`, `pipeline`, `shared`.

**The 8 ports are orthogonal to body-map layers:** ports describe *runtime stages a request flows through*, body-map layers describe *import-dependency strata modules sit in*. A single port can cross multiple body-map layers; a single body-map layer (`governance`) can host code that runs in multiple ports.

| Port | Primary body-map layers it touches |
|---|---|
| Ingress / ComputeGate | `surface`, `infrastructure`, `pipeline`, `governance` |
| Context Assembly | `semantic`, `perception`, `memory`, `domain` |
| Tension / Friction | `governance`, `semantic`, `evolution` |
| Draft Generation | `pipeline`, `infrastructure`, `domain` |
| PreOutput Governance | `governance` (dominant), `evolution`, `shared` |
| Memory Commit | `memory`, `governance`, `evolution` |
| Observability | `observability` (dominant), cross-cutting |
| Sub-agent Coordination | `infrastructure`, `governance`, `shared` |

### 3.2 vs the 8-layer request-flow convergence map

The 8-layer request-flow (`docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`) classifies a request's journey: ingress → sensing → ... → attachment.

**The 8 ports are a coarser slice of the same axis as request-flow layers**. Where request-flow has 8 distinct stages, ports collapse some adjacent stages into one extractable module-boundary. For example, the request-flow's "sensing" + "interpretation" stages both map into the Context Assembly port.

The two axes (body-map × request-flow) are already documented as orthogonal (per Phase 863 work). Ports add a **third axis: extraction granularity** — how big is the smallest unit of refactor we are willing to commit to. A port is an extraction-target, not a logical layer.

### 3.3 Why the three axes don't compete

- **Body map** answers: *which import layer is this module in?*
- **Request-flow** answers: *which stage of one request's journey is this code reached during?*
- **Ports** answers: *what is the smallest module-boundary I can extract this concern into without breaking the rest?*

These are three different questions. Each has its place. This decomposition doc should be indexed with explicit "this is a third axis, not a replacement" language so future readers do not collapse the three.

---

## 4. First seam recommendation

### 4.1 Recommendation: extract Context Assembly first (not PreOutput Governance)

Codex 2026-04-29 proposed two candidates: `pre-output governance finalization` or `context assembly`. Recommendation here: **Context Assembly first**, for three reasons:

1. **Pre-output governance just stabilized.** PR #32 + PR #33 shipped GSE Phase 2 spec / catalog / detector / council integration / scan-enforce flag split; PR #37 added operator env activation for shadow mode and fixed stale human/audit surfaces after enforcement. Refactoring this port immediately = three concurrent layers of change (spec + new code + refactor) on the same code paths. Cognitive load high; regression risk real.

2. **Context Assembly is more isolated.** ToneBridge, YUHUN context_assembler, GraphRAG retrieval are largely independent of council; the inline phases at lines 2110–2119 and 2599–2631 of `unified_pipeline.py` could be extracted into a `tonesoul/context_assembly/` sub-package without touching council code.

3. **Context Assembly's tests are already partly modular.** `tests/test_yuhun_context_assembler.py` and `tests/test_tonebridge*.py` exist. The extraction can preserve existing test entries; it doesn't require new test scaffolding.

### 4.2 Specific extractable interface

A `tonesoul/context_assembly/` package would expose:

```python
class ContextAssembly:
    def assemble(
        self,
        user_message: str,
        history: List[Dict],
        prior_tension: Optional[Dict] = None,
    ) -> AssembledContext:
        """Run ToneBridge analysis, trajectory analysis, commitment-stack
        load, GraphRAG retrieval, semantic trigger check, hippocampus
        retrieval. Return AssembledContext dataclass with all fields the
        downstream pipeline currently reads inline."""
```

Where `AssembledContext` is a frozen dataclass that captures exactly the fields `unified_pipeline.process()` currently builds across lines 2110–2631 in scattered local variables. Extraction = copy phase logic into the new module, replace the inline blocks with a single `context = self._context_assembly.assemble(...)` call.

### 4.3 Risk + mitigation

| Risk | Mitigation |
|---|---|
| AssembledContext misses a field that downstream phases read | Before extraction: grep all `self._` and local-variable reads in lines 2632–2745 to enumerate exactly what the downstream Tension/Friction port consumes |
| ToneBridge analyzer state leaks between assembly and downstream | Make `ContextAssembly` stateless; pass all session state in explicitly |
| GraphRAG initialization is currently lazy in pipeline | Surface initialization explicitly in `ContextAssembly.__init__`; document as required prerequisite |
| Test entry breakage during extraction | Run existing `test_tonebridge*.py` + `test_yuhun_context_assembler.py` before each commit step; add integration test calling new `ContextAssembly` against a fixed user_message + history fixture |

---

## 5. Phased rollout (timing alignment with 14-day beta wave)

The 14-day beta wave (`docs/plans/01_active/tonesoul_beta_wave_14day_2026-04-28.md`) has explicit stop conditions including §8 "side experiments begin competing with collaborator-beta for attention". Runtime decomposition is not strictly a side experiment — it is mainline architectural work — but **attention is finite**. The wave's evidence collection requires stable runtime; refactoring during Day 3-9 risks both regression and operator distraction.

| Phase | Action | Window | Constraint |
|---|---|---|---|
| **0** (now → wave Day 1-2) | This doc lands. **No code changes.** Doc reviewed by Codex independently if possible. | 2026-05-03 → wave Day 1 | doc-only |
| **1** (wave Day 3-14) | **Code freeze on runtime decomposition work.** Wave runs against current centralized runtime. Bug fixes allowed only when surfaced by wave evidence. | 14-day beta wave duration | freeze except critical fixes |
| **2** (post Day 14 review) | Day 14 evidence review identifies which port has the most painful real-usage friction. **That port is the first seam, not Context Assembly automatically.** §4 above is a default recommendation; real evidence overrides it. | After wave Day 14 | evidence-driven |

**The deliberate inversion in Phase 2:** §4 above recommends Context Assembly first based on architectural reasoning. **If the 14-day wave evidence shows that the worst pain is in PreOutput Governance (e.g. Council friction confusing participants), then PreOutput Governance jumps the queue.** The wave is the arbiter, not this doc.

This is the same discipline as `docs/plans/01_active/tonesoul_beta_wave_14day_2026-04-28.md` §9 Honest Read: *"ToneSoul is still conditional-go, but now we know exactly why — that is a valid success state."* For runtime decomposition, the equivalent is: *"We have a map; we have a default first-seam recommendation; the wave decides which one is actually first."*

---

## 6. Open questions

1. **Is "Sub-agent Coordination" really a port, or is it cross-cutting infrastructure?** Argument for port: it has its own owner modules (runtime_adapter session functions, scripts/, .aegis/), its own test entries, its own evidence level. Argument against: ports describe runtime stages a request flows through; sub-agent coordination operates at session level not request level. This doc treats it as a port for visibility, but the question is open.

2. **Does PreOutput Governance count as one port or two?** It contains both council deliberation (perspectives + coherence + verdict) AND strategy_mirror (a more recent self-observation layer). PR #32/#33/#37 framed strategy_mirror as a sub-layer with operational scan/enforce controls. Should it become its own port (`Self-Observation`), making 9 ports total? Open until Phase 2 — let the wave evidence decide.

3. **Where does the LLM router fit?** Draft Generation port currently covers it, but the router is shared between draft generation and (potentially) self-evaluation calls. May deserve its own micro-port. Defer to Phase 2.

4. **Memory Commit's two "update memory unit" phases** (lines 3096 + 3121 with duplicate label) — is one redundant, or are they semantically distinct? Read both before extraction; this is a likely cleanup-while-refactoring item.

5. **Frontend (`apps/web/`) decomposition scope.** The 1756-line `ChatInterface.tsx` is a frontend issue largely orthogonal to backend ports. This doc deliberately scopes only Python runtime; frontend gets its own decomposition doc later. **Open question**: should the two be joined or kept separate? Recommended: separate. Frontend has different change cadence and different reviewer pool.

6. **Reconciliation table maintenance.** §3.1 maps ports to body-map layers. This map will rot as code evolves. Should `scripts/analyze_codebase_graph.py` extend to also emit a port-mapping snapshot? Open.

---

## 7. Coda — the bet underneath this layer

This doc bets on something specific: **that ToneSoul's value depends on each conceptual layer becoming an independently testable, replaceable, deniable boundary at runtime — not just at the spec layer.**

The conceptual layer's claim: "Council deliberates before output." If that claim is fulfilled by 330 lines inline in a 1500-line method, the claim is technically true and operationally fragile. Anyone trying to swap in a different council, run councilless mode for testing, or measure where council overhead lives must navigate the centralized pipeline first. **The conceptual claim survives the runtime; the runtime is not built to honour the conceptual claim.**

The 8-port decomposition is the structural commitment that *each layer of governance the project claims* is a real boundary, not just a section header. When that commitment is made:

- testing each port in isolation becomes possible
- swapping a port (different LLM router, different council, different memory store) becomes a small change instead of a fork
- denying a port (run a deliberately council-less ToneSoul to see what Council actually adds) becomes a feasible experiment
- the multi-agent collaboration story (§2.8 Sub-agent Coordination) gets a runtime owner instead of living in operational protocol files

If the eventual refactor (Phase 2 after wave) does not produce these capabilities, this doc has failed even if every port is "extracted" by line count. The line-count metric is not the bet. The bet is on **deniability** — can each governance claim be independently turned off, observed, or replaced — because that's what makes the conceptual layer load-bearing instead of decorative.

If a future agent reads this doc and finds only port boundaries without that deniability test, this doc has done half its job. The other half lives in whatever Phase 2 ships under the discipline `docs/plans/01_active/tonesoul_beta_wave_14day_2026-04-28.md` §9 calls *evidence-driven, not aspiration-driven*.

The current centralized runtime is not a failure — it is what mature conceptual work looks like before it gets compiled into testable seams. This doc proposes the compile step.

> *Authored by Claude Opus 4.7 in collaboration with Codex (architectural framing) and Fan-Wei Huang (timing constraint per 14-day wave). Phase 0 of the Runtime Decomposition program. Phase 1 (refactor execution) deliberately deferred.*
