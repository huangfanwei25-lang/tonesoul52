# Successor Cognitive Map — read this before deleting, refactoring, or "cleaning up"

> Last Updated: 2026-07-03 (all §1 rows re-verified against master d428191; three line
> numbers had drifted and were refreshed — line numbers in this map WILL drift again,
> so verify by grepping the import string, not by trusting the cached `:NNN`.)
> Audience: the next AI agent (or human) who picks up this repo cold.
> Purpose: the single page that prevents the failure that almost happened on
> 2026-06-13 — a "consolidation" PR that nearly deleted `yss_gates`, a module
> that *looks* dead but is the runtime POAV gate inside the #1 god node.

This map exists because **continuity in this project is carried by artifacts,
not by a model's memory** (DESIGN.md Invariant 2), and **identity is carried by
accountable choice-point records, not model memory** (DESIGN.md E0). A model
label can disappear mid-project; the repo must still be safely continuable. If you are a fresh
agent, this page + `task.md` + `docs/status/codebase_graph_latest.md` are your
cognitive baseline.

---

## 0. The one rule that would have prevented the near-miss

**"Nobody imports it" is not the same as "safe to delete."** Before removing
*any* module, run reachability against the real runtime entry points — do not
trust a stale analysis, a name that sounds obsolete, or a 2-day-old note. The
project has hit the "trusted a stale `X is current` record" failure 5+ times
across different surfaces (git refs, codebase graph, scope assumptions, code
schema, and now module liveness). Catching it once does not make you immune;
it recurs on a new surface every time.

Verification recipe (cheap, do it every time):

```bash
# 1. Direct importers of a module across the WHOLE repo (not just tonesoul/)
grep -rn "import <module>\|from .*<module> import\|<module>\." \
  --include="*.py" tonesoul scripts apps api tests tools examples

# 2. Dynamic/lazy imports hide in strings — check these too
grep -rn "importlib\|__import__\|\"tonesoul\.<module>\"" --include="*.py" .

# 3. Is it reachable from a runtime entry point?
#    Entry points: unified_pipeline, runtime_adapter, council/*, gateway/*,
#    cli/*, mcp_server, api/*, and any scripts/*.py with a main()/__main__.
#    The analyzer also computes this: docs/status/codebase_graph_latest.json
```

For a bulk deletion, spend the tokens on independent verification (the
2026-06-13 PR5 used 4 parallel verifier agents). It caught 6 modules wrongly
assumed deletable. The cost of one wrong deletion (a broken runtime shipped to
master) dwarfs the cost of verifying.

---

## 1. Deletion-hazard quick reference (the load-bearing surprises)

These modules **look retired but are live runtime / CLI dependencies.** Do not
delete or "consolidate" them without re-verifying against current code:

| Module | Looks like | Actually | Proof |
|---|---|---|---|
| `tonesoul/yss_gates.py` | part of the dead "yss" chain | **runtime POAV gate** — but enforce is CONDITIONAL: it blocks only in lockdown / risk-danger zones; everyday traffic is record-only (`unified_pipeline.py:648` `enforce = high_risk_mode`, `:667`) | `unified_pipeline.py:638` `from tonesoul.yss_gates import poav_gate`; thresholds now live in `soul_config.py:139-140` (0.92 high-risk / 0.70 low-risk), not at the import site; extra importer `tools/eval/egress_gate_characterization.py:24` |
| `tonesoul/tsr_metrics.py` | yss helper | **council runtime + public demo** | `council/intent_reconstructor.py:8` (→ `council/runtime.py` main line); `examples/quickstart.py:81` |
| `tonesoul/action_set.py` | yss helper | **runtime policy** | `unified_pipeline.py:2615,3585` `from tonesoul.action_set import ACTION_POLICY` |
| `tonesoul/memory_manager.py` | yss helper | **live CLI** | `scripts/memory_compact.py` (has `main()`/`__main__`) |
| `tonesoul/skill_gate.py` | yss helper | **live CLI** | `scripts/skill_gate.py` (has `main()`/`__main__`) |
| `tonesoul/skill_promoter.py` | yss helper | **transitively live** | `skill_gate.py:57` imports it inside a function |
| `tonesoul/drift_monitor.py` | one of two drift impls | **canonical runtime drift** | wired into the dispatch trace; `drift_tracker.py` was the deletable duplicate (removed in PR5) |

**Lesson encoded:** the "yss subsystem" is NOT a clean dead island. The dead
*orchestrator* (`yss_pipeline`) pulled in modules that other live code also
imports independently. Always check importers from *outside* the suspected
closure.

---

## 2. Unwired-but-retained (the YSS governance subsystem)

These 9 modules are **built but imported by no live runtime path.** They are
**intentionally kept** (owner decision 2026-06-13), marked in-file with
`# YSS-STATUS: unwired`, as candidate substrate for the Responsibility
Manifold program's real-sensor / accountability layer. **Do not silently
delete them** — they are a parked design asset, not junk:

`yss_pipeline`, `yss_unified_adapter`, `audit_interface`, `evidence_collector`,
`generation_orch`, `intent_verification`, `mercy_objective`, `skill_apply`,
`constraint_stack`.

To find them at any time: `grep -rln "YSS-STATUS: unwired" tonesoul/`.
Canonical list + rationale: `task.md` › Reality Sync Patchset.
Why they matter: `docs/plans/responsibility_manifold_engineering_program_2026-06-12.md`.

---

## 3. Current repo state (post Reality Sync, 2026-06-13)

The Reality Sync Patchset (PRs #78–#81 merged, PR5 in progress) brought public
claims, packaging, sensors, and governance back to verifiable consistency:

- **master is green + branch-protected** (first time both hold). Required
  checks: `Test Python 3.12`, `Commit Attribution Check`. Direct push of a
  red commit is now blocked at the machine level.
- **Packaging works**: `pip install tonesoul52` + `ts council` no longer
  crash (PR1 relocated 4 repo-root `memory/` modules into the package; a CI
  guard `tests/test_packaging_repo_root_import_guard.py` stops the regression).
- **Public claims are evidence-bounded** (PR2): no "shipping in production",
  no "non-repudiable", "8 immutable laws" not 7, pip caveats honest.
- **Sensors are honestly labeled** (PR3): the vow/POAV/axiomatic evaluators
  are **lexical heuristics, English-centric, blind to zh-TW** — they do NOT
  measure truth/safety semantically. `AXIOMS.json` v1.2.0 records per-axiom
  enforcement status (0 fully enforced, 8 partial, 1 referenced, 0 aspirational
  as of 2026-06-15; the earlier "5 partial, 2 referenced, 2 aspirational" line was stale).
- **Governance is self-applied** (PR4): Aegis signing fails *visibly*
  (UNSIGNED marker) without PyNaCl instead of silently skipping; `audit()`
  detects chain-head/tail truncation.
- **Consolidation** (PR5): removed the `drift_tracker` duplicate + dead
  `tonesoul.pipeline` shim; flagged the unwired YSS subsystem; renamed
  `ALLOWED_DEPS` honestly (it is a dependency inventory with 8 accepted
  inversions, NOT strict-hierarchy enforcement — "0 layer violations" ≠ clean
  hierarchy).

**Since Reality Sync — two ADVISORY Tier-5 sensors** (2026-06-15/16, *not* part of
Reality Sync; advisory-only, default-OFF, record-only, measured before any wire-in):
the **embedding-based** `semantic_overclaim_sensor` (catches paraphrased `meta.not_for`
claims the lexical guardian misses — so "sensors are lexical heuristics" above is now
"lexical *plus* one embedding-based advisory sensor") and `intent_proportionality` (the
"小天使", flags a draft escalating beyond user intent). Both only record a signal on the
verdict; neither blocks or auto-edits. Evals in `docs/status/`; design rationale in
DESIGN.md "Tier-5 Advisory Sensors".

---

## 4. What "0 layer violations" and "100% annotated" actually mean

Treat the green badges as **inventory completeness, not architectural health**:

- `0 layer violations` = no edge stepped outside an allowlist that already
  permits ~52% of cross-layer pairs (incl. 8 bidirectional). See
  `ACCEPTED_INVERSIONS` in `scripts/analyze_codebase_graph.py`. Re-tightening
  to a real hierarchy (interface inversion) is deferred (PR5 option c).
- `100% __ts_layer__ annotated` = every module declares a layer; it does not
  mean the declaration matches behavior. (PR5b is cleaning ~35 files that
  carry contradictory double `__ts_purpose__` declarations from a stash-pop.)
- The truth sensors are keyword heuristics (§3). "AI that won't make things
  up" is a governance-structure claim, not a truth guarantee.

---

## 5. Where to look next (don't re-derive what's already written)

| You need | Go to |
|---|---|
| Per-module layer / coupling / imports | `docs/status/codebase_graph_latest.md` (auto-generated) |
| Import rules + accepted inversions | `docs/ARCHITECTURE_BOUNDARIES.md`, `ACCEPTED_INVERSIONS` |
| Current program + the active vow set | `task.md` › Reality Sync Patchset |
| Per-axiom enforcement reality | `AXIOMS.json` `meta.enforcement_reconciliation` |
| Why the system is shaped this way | `DESIGN.md` |
| The forward design thesis | `docs/plans/responsibility_manifold_engineering_program_2026-06-12.md` |

If you are about to "clean up," "consolidate," or "delete dead code": re-read
§0 and §1 first. The structure is here precisely so you do not have to trust
your memory — or a previous agent's.

---

## 6. Dormant subsystems map — built, ran, then went quiet (do NOT rebuild; do NOT blind-delete)

A 2026-06-13 fine-grained sweep (22 agents, adversarially verified — half the
"major" finds were overstated and downgraded) surfaced the repo's defining
pattern: **it is a graveyard of sophisticated, tested, then-forgotten work.**
Not rot — forgotten gems. This map exists so the next agent neither rebuilds
what's here nor deletes it thinking it's junk. Each is a pending owner decision
(revive / archive / mark-and-wait), not a fact about quality.

| Subsystem | What it is | Status (verified) | Entry / evidence | Decision pending |
|---|---|---|---|---|
| **Phase 7 Dream/Autonomous** | `autonomous_cycle`(367) + `dream_engine`(1001) + `wakeup_loop`(808) + `autonomous_schedule`(1659 LOC) = a full unprompted wake→perceive→dream→journal loop | Built + tested; **ran once 2026-03-08** (6 wakeup cycles, 2446 log entries, observability dashboard); **dormant since**; no production invocation; scattered across 4 top-level modules, no unified entry | `scripts/run_autonomous_dream_cycle.py`, `run_dream_engine.py`, `run_dream_wakeup_loop.py`; `docs/proposals/phase7_dream_engine.md`; `docs/status/dream_*` artifacts | **This is the marker-3 experiment machine** — revive with a serving model + extend to self-state-triggered + continuous, vs archive. Gated on a model. |
| **YUHUN Core v1.0** | `tonesoul/yuhun/` (7 modules) — semantic self-sensing: DriftMonitor=proprioception, JumpMonitor=vestibular, ObserverWindow=spatial; `sleep_bridge` feeds DreamEngine | Built + 30 tests pass (2026-04-13); **PARTIALLY WIRED** — called in `unified_pipeline` (this one is partly LIVE, not fully dormant) | `tonesoul/yuhun/{world_sense,dpr,sleep_bridge,...}.py` | Verify the live flow actually fires; add observability so you can see it run. |
| **GSE Strategy_Mirror** | `gse/strategy_mirror/` — 150-element rhetorical-move catalogue (57 green/73 yellow/20 red); names manipulation moves in ToneSoul's own output | **REVIVED 2026-06-14** — `scripts/run_strategy_mirror_shadow.py` verifies it discriminates (zh-TW rhetorical detection 1.0 / plain false-trip 0.0; catches urgency/scarcity as a red move). Production default still **OFF**, pending owner enable-decision. Phases 3-5 (~550 more moves) unbuilt | `scripts/run_strategy_mirror_shadow.py`; `tonesoul/council/pre_output_council.py:118-279` | Calibrate at scale (needs traffic) then decide on flipping the default ON. |
| **YSS governance** | 9 modules (3045 LOC): audit_interface, constraint_stack, evidence_collector, generation_orch, intent_verification, mercy_objective, skill_apply, yss_pipeline, yss_unified_adapter | Built; **unwired** (marked `# YSS-STATUS: unwired`); only importers are its own tests | grep `YSS-STATUS: unwired` | Responsibility-Manifold P1 candidate substrate (see §5 plan), or archive if P1 doesn't start. |
| **inter_soul** | 5 modules — multi-agent tension/sovereignty protocol (TensionPacket, RuptureNotice, SovereigntyBoundary) | Built; tests live in `.codex-temp/`; **ZERO production imports** | `tonesoul/inter_soul/` | For Phase 8 multi-agent; mark wire-in point or archive. |
| **market** |台股 analysis (analyzer/data_ingest/world_model, ~1338 LOC) | Half-dismantled (forecaster/gold_detector deleted; zombie .pyc cleaned 2026-06-14); no integration; off-thesis | `tonesoul/market/` | Off the accountability thesis — strongest archive candidate. |

**Forgotten ideas (docs, not code) — articulated, never operationalized:**
- `docs/philosophy/language_as_womb_2026.md` (289 lines: weak-model + strong-governance = subject posture) — cited by no axiom/council/eval.
- `docs/philosophy/complete_form_vision.md` (Vector-DB / async-dreaming / Git-personality-versioning vision) — current state ❌, no roadmap bridging the gap.
- `docs/philosophy/emergent_governance_vision.md` (single-user → multi-user → distributed governance) — zero multi-user code.
- `memory/crystals.jsonl` — 82 crystallized principles (2026-03, confidence 0.8-1.0), **`access_count` all 0**: read by DreamEngine, never consumed by runtime decisions.

Decision frame for all of the above: each is *revive*, *archive*, or *mark-and-wait* — not "is it good." Most are good and dormant. The honest risk is silent API drift (dormant code rotting against the live core) — so a dormant subsystem left in place should at least be on this map.

---

### 6a. Module-level dormancy markers (added 2026-06-15)

A 37-agent adversarial verification sweep (each module independently checked
unwired, then a second skeptic tried to *refute* dormancy — the exact discipline
§0 demands) confirmed **18 modules** carry zero non-test live importers, tagged
in-file with a uniform, greppable marker. **The grep below is the source of
truth, not this paragraph's count** — as of 2026-07-03 it returns **29 files**:
the original 18, minus `corpus/` 4 (archived, §6b), plus `market/` 4 and
`yuhun/context_assembler` (marked later, §6b), plus `loop/` 4 + `tech_trace/` 4 +
`axioms/` 2 (verified unwired and marked 2026-07-03 — they had been a coverage
hole in this convention):

```
# DORMANT (as of 2026-06-15): <reason>
```

Find them all at any time: `grep -rln "# DORMANT (as of" tonesoul/` (parallel to
the older `# YSS-STATUS: unwired` convention). Full reachability evidence per
module: `docs/architecture/architecture_legibility_2026-06-15.md`.

| Module(s) | What it is | Why dormant (verified) |
|---|---|---|
| `council/atomic_claims.py` | atomic-claim extraction with source spans | tested, never wired into the verdict pathway |
| `council/convergence.py` | deliberation-convergence scoring | tested; council `__init__`/runtime never call it |
| `memory/freshness.py` | zone freshness / staleness decay | unwired; only named in sibling docstrings |
| `memory/aaak.py` | AAAK compaction | never integrated into the session-end pipeline |
| `memory/hybrid_search.py` | RRF keyword+vector fusion + rerank | prod memory uses direct recall, not fusion |
| `memory/session_resonance.py` | cross-session tension-recurrence detector | parked staleness substrate |
| `gse/registry.py` | GSE element registry (loads JSON clusters) | re-exported by `gse.__init__` but no live importer |
| `observability/execution_honesty.py` | promise-validation framework | `observability` package never imported by live code |
| `observability/self_claim_audit.py` | first-person claim reducer | same — package facade unused at runtime |
| `inter_soul/{__init__,bridge,negotiation,sovereignty,types}.py` | cross-agent tension/sovereignty protocol | Phase-8 substrate; zero live importers (also the §6 row) |
| ~~`corpus/{__init__,consent,pipeline,storage}.py`~~ | privacy-first training-data corpus | **ARCHIVED 2026-06-15** (owner decision — parked duplicate of the live Supabase consent path). Removed from the tracked tree; recover via `git checkout b497c68 -- tonesoul/corpus`; local copy in `.archive/corpus_archived_2026-06-15/`. See §6b. |
| `loop/{__init__,config,engine,events}.py` | iterative execution engine + event streaming | only importers are tests/helpers.py + tests/test_loop_*.py (marked 2026-07-03) |
| `tech_trace/{__init__,capture,normalize,validate}.py` | Tech-Trace ingestion/normalize/validate helpers | only importers are tests/test_tech_trace_*.py (marked 2026-07-03) |
| `axioms/{__init__,living_insights}.py` | provisional philosophical observations store | zero live importers; the live axiom carrier is repo-root `AXIOMS.json`, not this package (marked 2026-07-03) |

**Caught as ACTUALLY LIVE — NOT marked dormant (the verification's safety win):**
`gse/element.py` — the `GSEElement` dataclass is imported by `gse/registry.py`
and `gse/__init__.py`. It is live *within* the (otherwise-parked) `gse` package,
so it carries a `# PACKAGE-STATUS` note, not a `# DORMANT` one. This is the §0
failure mode in miniature: "has importers" ≠ "live", but also ≠ "safe to call dead."

**YUHUN dead-hook — RESOLVED 2026-06-15 (owner decision: "wire if feasible").**
The old `_get_dpr()` / `_get_context_assembler()` dead hook is gone:
- **DPR is now wired** as an *advisory* signal — `unified_pipeline.py` records
  `dispatch_trace["dpr_advisory"]` (recommended FAST/COUNCIL path + complexity +
  triggers). It is advisory ONLY by design — a lexical router must not bypass the
  council. `_get_dpr()` is now live.
- **ContextAssembler stayed parked** — its `assemble()` would replace the
  pipeline's context-build (a behavior change), so it was not additively wireable.
  The dead `_get_context_assembler()` getter was **removed**; the module is kept as
  test substrate and marked "PARKED, not superseded."

---

### 6b. Tier 4 structural decisions — executed 2026-06-15 (owner: Fan-Wei)

Decision evidence + adversarial review: `docs/plans/01_active/tier4_structural_decisions_2026-06-15.md`.

| Item | Decision | What changed |
|---|---|---|
| `corpus/` | **Archive** | Removed from the tracked tree (parked duplicate of the live Supabase consent path). Recover: `git checkout b497c68 -- tonesoul/corpus`. The 3 corpus-dedicated tests were removed; the 2 consent cases in `test_security_memory_boundary.py` (duplicated in the archived `test_corpus_consent.py`) were dropped, leaving its 4 genuine memory-security tests. **Coverage note:** the live Supabase consent path's own test coverage is a separate, pre-existing question. |
| YUHUN hook | **Wire (advisory)** | DPR wired as `dispatch_trace["dpr_advisory"]`; ContextAssembler kept parked (see §6a). |
| `council/evolution.py` | **Rename** | → `council/voting_evolution.py` (resolves the live-vs-live grep collision with `tonesoul/evolution/`). Class names unchanged; 3 importers + 1 test updated. `yss`/`yuhun` were NOT renamed — they are not true namesakes. |
| `market/` | **Keep + mark** | The 4 modules now carry a `# DORMANT` marker with a **dated archive gate** ("archive at next consolidation unless a governance wire-in lands"). Not removed (tested + CLI-script-reachable). |
| dual `Hippocampus` | **Leave + mark** | No merge (M-effort/M-risk for zero gain). Root `memory/hippocampus.py` marked `# PARTIAL-LIVE` (only the static `compute_error_vector` is live; the default-ON corrective branch is a usually-zero near-no-op). |
