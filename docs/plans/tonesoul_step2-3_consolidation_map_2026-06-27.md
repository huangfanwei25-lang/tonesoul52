# ToneSoul Step 2/3 — Consolidation Map (not a manifesto)

> **Last Updated:** 2026-06-27 · **Status:** inventory + honest gap map · **Author trail:** claude-opus-4-8

## §0 What this is (orientation, read first)

This is a **map**, not a manifesto. It exists because a recurring conversation produced
two appealing framings — "ToneSoul Step 2: Memory & Self-Knowledge" and "Step 3: Decision
Boundaries / DecisionOps" — and the honest job is to locate them against (a) what the repo
**already has**, (b) the **external reference architectures** that got there first, and
(c) the **genuine gaps**.

Three disciplines bind every line below:

1. **claim ≤ evidence.** Every claim about a ToneSoul piece is tagged with its real status:
   `wired` (live runtime path), `unwired` (present, tested, not on a runtime path), or
   `doc-only` (a prose convention the agent is trusted to follow, not machine-checked).
2. **Convergent, not novel.** Step 2 and Step 3 are *not* a ToneSoul invention. They are the
   well-trodden agent-memory + human-in-the-loop + provenance literature. The "第一步/第二步/
   第三步" ladder is a useful narrative, but the "same-source" feeling it produces is
   **vocabulary projection**, not external convergence. Do not let the ladder inflate into a
   claim that "ToneSoul has a coherent 7-layer responsibility theory."
3. **No manifesto.** The poetic/詩性 layer belongs in outward narrative. This document is the
   honest inventory the next agent reads before touching the memory or governance layers.

## §1 The honest headline

- **Structure: ~70% present and live.** Almost every named piece genuinely exists and most
  sit on a reachable runtime path (EpistemicLabeler → PreOutputCouncil → pipeline; decay →
  soul_db; Aegis chain → commit; reflex/vow/sovereignty/POAV egress gates). At "is the
  scaffolding really there and reachable," ~70% is fair.
- **Enforcement depth: closer to ~30–40% semantically real.** The load-bearing decision and
  honesty surfaces are **lexical English keyword heuristics**, not semantic judgment.
  `AXIOMS.json` records **0 of 8+1 axioms fully enforced (all partial)**; vow harm-detection
  is **3 literal English phrases**; POAV is keyword-counting; and the one embedding sensor
  that would close the paraphrase blind spot is **default-OFF, record-only**.
- **The memory loop is open.** The system *writes* traces, *decays* memory, and maintains
  `SUCCESSOR_MAP.md`, but **no runtime decision reads its own map or consumes crystallized
  memory** (`crystals.jsonl` access_count all 0). Store: yes. Self-consume: no.
- **The hardest boundaries are prose.** The governance-binding and autonomy "boundaries" are
  conventions in `CLAUDE.md` / handoff / user-memory; nothing in code verifies a decision
  record was written or that autonomy scope was respected.

So: the apparatus is real and reachable; the *semantic enforcement* is thinner than the
apparatus suggests; and the memory is a one-directional ledger, not yet a loop.

## §2 The three layers, mapped

Status legend: **[W]** wired (live) · **[U]** unwired (present, off the runtime path) ·
**[D]** doc-only (prose convention). Line numbers are as-found 2026-06-27 and will drift.

### 2.1 Honesty (claim ≤ evidence, refuse-both, cannot_verify)

| Piece | Pointer | Status |
|---|---|---|
| EpistemicLabeler (retrieved/distilled/generated/speculative + refusal_eligible) | `tonesoul/council/epistemic_labeler.py:276` | **[W]** |
| Labeler wired into PreOutputCouncil (`.label()` every verdict) | `tonesoul/council/pre_output_council.py:73` | **[W]** |
| Guardian OVERCLAIM (OBJECTs consciousness/safety-cert/legal-proof = `meta.not_for`) | `tonesoul/council/perspectives/guardian.py:63` | **[W]** |
| grounding_check (ungrounded-claim ratio → thin_support) | `tonesoul/grounding_check.py:97` | **[W]** |
| No-verdict / refuse-to-adjudicate stance (reviewer exits 0 even with findings) | `tonesoul/reviewer/__init__.py:3` | **[W]** |
| Claim-to-evidence reviewer (E0–E4 levels, cannot_verify, weaker-wording) | `tonesoul/reviewer/report.py:22` | **[U]** offline CLI only |
| semantic_overclaim_sensor (embedding paraphrase catch for `meta.not_for`) | `tonesoul/council/semantic_overclaim_sensor.py:1` | **[U]** advisory_only, default-OFF |

**Gaps:** all live honesty sensors are lexical/English-centric (blind to zh-TW paraphrase per
`SUCCESSOR_MAP` §3/§4); the EpistemicLabel is honest *metadata* but **no runtime consumer
gates on `refusal_eligible`**; the richer E0–E4 auditor runs only offline; the one *semantic*
sensor that would close the lexical blind spot is built but **not wired to block**.

### 2.2 Memory & self-knowledge

| Piece | Pointer | Status |
|---|---|---|
| Event memory: session traces + governance store (FileStore/Redis) | `tonesoul/backends/file_store.py:92` | **[W]** |
| Memory decay (exponential forgetting + retrospective reinforcement) | `tonesoul/memory/decay.py:21` | **[W]** (≈0.995 lineage; see §3) |
| Aegis hash-chain + Ed25519 signing (UNSIGNED marker, not silent skip) | `tonesoul/aegis_shield.py:366` | **[W]** |
| Aegis chain wired into the commit path (every session-end trace chained) | `tonesoul/runtime_adapter.py:1953` | **[W]** |
| ProvenanceManager (second hash-chained ledger, isnād witnesses) | `tonesoul/memory/provenance_chain.py` | **[W]** |
| Footprints (recent visitor log, Redis-gated) | `tonesoul/runtime_adapter.py:392` | **[U]** Redis-only |
| Static self-knowledge: SUCCESSOR_MAP (deletion-hazard / dormancy map) | `docs/SUCCESSOR_MAP.md:1` | **[D]** |
| OpenClaw-Memory vector engine (submodule; real data gitignored) | `OpenClaw-Memory/` | **[U]** manual query |

**Gaps:** the system **does not read its own map** — `SUCCESSOR_MAP` and the philosophy
self-vision files are self-knowledge *for the next agent*, not consulted by any runtime
decision; decay runs but `crystals.jsonl` (82 principles) has **access_count all 0** — read
by DreamEngine, never consumed by a runtime decision, so "memory shaping behavior" is not
closed; several modules are DORMANT/unwired (`memory/freshness.py`, `session_resonance.py`,
`hybrid_search.py`, `aaak.py`); warm retrieval into live reasoning is still manual.

### 2.3 Decision-boundary (auto / report / confirm / forbidden / defer)

| Piece | Pointer | Status |
|---|---|---|
| AXIOMS claim-boundaries + `meta.not_for` + per-axiom enforcement ledger | `AXIOMS.json:276` | **[W]** (ledger: 0 enforced / 8 partial / 1 referenced) |
| Egress fail-closed reflex final gate (BLOCK replaces output) | `tonesoul/unified_pipeline.py:614` | **[W]** |
| Vow gates (VowEnforcer block/repair on draft) | `tonesoul/unified_pipeline.py:768` | **[W]** |
| Memory sovereignty egress gate (Axiom 8, fail-closed) | `tonesoul/memory/sovereignty_gate.py:63` | **[W]** narrow |
| POAV governance gate (≥0.92 high-risk path) | `tonesoul/yss_gates.py` | **[W]** record-only off high-risk |
| pr_preflight (PR-scope-truth guard, stacking + trailer check) | `scripts/pr_preflight.py:1` | **[U]** author-run CLI |
| Governance-binding convention (decision-record-before-major-change) | `CLAUDE.md` | **[D]** |
| autonomy_preference convention (autonomous-within-scope) | handoff + user-memory | **[D]** |

**Gaps:** the hardest boundaries are lexical (vow harm = 3 English phrases; POAV =
keyword-counting + path regex; paraphrase and zh-TW pass through); **0 of 8+1 axioms fully
enforced**; Axiom 5 (Mirror-Recursion accuracy gain) is **deliberately un-enforced — no
runtime accuracy oracle exists** (an honest boundary, not a TODO); the governance-binding +
autonomy conventions are **prose to the agent, not machine-checked**; POAV/de-escalation are
record-only off the high-risk path — observed-and-stamped far more often than they block.

## §3 The convergent reference architectures — wrap vs build

All external claims web-verified this session. Depth: **Graphiti E3, Ojewale E3** (primary
sources read); the rest **E2** (abstract/repo confirmed, not full-text). Per MEMORY Rule 4,
the E2 cross-domain mappings are synthesis-derived — deep-read before any public artifact
leans on them.

### 3.1 Memory / temporal — Zep/Graphiti (arXiv:2501.13956, E3)

The bitemporal core: every edge carries **four timestamps** — `t_valid`/`t_invalid` (timeline
T = when the fact was true in the world) and `t_created`/`t_expired` (timeline T' = when it was
ingested). On contradiction, an LLM **closes the old edge's validity window** (`t_invalid` =
new edge's `t_valid`) rather than deleting — so historical state stays queryable
(`valid_at ≤ query_time < invalid_at`). LongMemEval: the real headline is **~90% latency cut**
(2.58s vs 28.9s) from shrinking the prompt; biggest gains are exactly temporal/relational
(temporal-reasoning +38%), but one category **regressed −17.7%** (stated, unsolved).

**Verdict — split:**
- **Event/temporal gap → WRAP, don't build.** The close-the-window edge model is genuinely
  hard (the upstream repo has open temporal-correctness bugs). Pin Graphiti behind a thin
  ToneSoul adapter at the R-Memory L3 slot, run it on a **local OpenAI-compatible LLM**
  (the qwen2.5 already used in Phase 7) against FalkorDB → **no per-ingest API cost**.
  ToneSoul already named this exact adoption: `TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
  (L3 Phase C) and `docs/plans/tonesoul_knowledge_graph_plan_2026-03-21.md`.
- **Relational/repo-topology gap → BUILD.** Graphiti's LLM entity-extraction is the *wrong
  tool* for static code-import topology (non-deterministic, a model call per ingest;
  `imports` is read from code, not inferred). Use a deterministic rg/AST walker for the
  4-node/5-edge repo graph ToneSoul already specced.

**Honest limit (load-bearing):** Graphiti is engineered for **retrieval quality, not
accountability**. Its "provenance" is data lineage for citation — **no hash-chain, no signing,
no fail-closed, no refusal**. It is **LLM-constructed** (inherits the extractor's
hallucinations); `t_valid` answers "what the graph *believes* was true when," not ground
truth. It is a good temporal substrate **under** ToneSoul governance, never a replacement —
the same conclusion the R-Memory doc already reached ("Redis/Graphiti are the nervous system,
governance stays sovereign").

### 3.2 Trace / provenance — Ojewale et al. "Audit Trails for Accountability in LLMs" (arXiv:2601.20727, E3)

The architecture: an append-only, tamper-evident, chronological ledger (`curr_hash =
SHA-256(payload + prev_hash)`, genesis `prev_hash="GENESIS"`, optional `sig?`) that records
lifecycle events **and** governance decisions in one stream. The decisive move:
**Approval / RiskWaiver / Attestation are first-class event types**, each carrying
`decision_owner`, rationale, the scoped IDs (`model_id`/`dataset_id`/`deployment_id`) they
apply to, constraints, and artifact references. `verify_log()` replays the chain to detect
modification/deletion/truncation.

**Verdict — keep ToneSoul's own mechanism, steal the schema.** ToneSoul already has the
mechanism and in places **exceeds** the paper: Aegis adds **mandatory Ed25519 signing** (vs
optional `sig?`), a head-anchor truncation check, and a content/injection filter before write;
`provenance_chain.py` is structurally near-identical to the paper's Store layer. Wrapping the
paper's library would not help — its emitters (HF TrainerCallback, FastAPI middleware) target
an ML-training/serving pipeline ToneSoul does not run.

**The single sharpest gap this surfaces:** ToneSoul **only hash-chains events; it does not
link approvals/attestations to artifacts.** There is no Approval/RiskWaiver/Attestation entity
naming a `decision_owner`, the scoped artifact it authorizes, and the constraints. Traces are
keyed by `session_id`/`agent`/`topics`, **not** scoped identifiers — so the paper's core
capability (filter+order to reconstruct an artifact's timeline) is not reconstructable today.
And ToneSoul has **≥3 non-unified provenance planes** (Aegis-chained `session_traces`, the
separate `provenance_chain.py` ledger, git commit trailers) where the paper deliberately puts
everything in one stream. **Cheap honest fix (~1 file, no dependency):** re-key traces to
stable scoped IDs + add explicit `Approval`/`RiskWaiver`/`Attestation` record types. W3C PROV
(Entity/Activity/Agent) is the serialization target if this is ever externalized.

### 3.3 Decision-boundary — the auto/report/confirm tiers, formalized (E2)

The "DecisionOps" 3-tier (auto-execute / do-but-report / must-confirm) is the lived-experience
form of: **OPA/Rego** (policy-as-code, decision/enforcement separation), **LangGraph HITL**
(`interrupt()` before irreversible actions, with the explicit "gate only the irreversible, or
humans rubber-stamp" rule), **AgentSpec** (arXiv:2503.18666, trigger/predicate/enforcement),
**capability-based security / POLA** (least authority = blast-radius minimization), and
**MCP Authorization** (OAuth scopes → tools). ToneSoul's vow/reflex/POAV gates are the same
shape; what they lack is the **human-decision-cost view** the article foregrounds (reducing
the *operator's* small judgments), which ToneSoul has under-emphasized because it optimizes
*the AI's accountability*, not *the human's cognitive load*. Same mechanism, different design
pressure; the ideal serves both.

## §4 Genuine gaps and the honest verdict on each

Ordered by honesty-of-payoff, with the discipline applied (measure before build; don't climb
a ladder of new subsystems).

1. **Lexical → semantic (biggest, and cheapest to start).** The semantic overclaim sensor
   already exists (§2.1) but is default-OFF/record-only. The honest move is **turn it ON in
   shadow mode and measure its catch-rate on new paraphrase/zh-TW attacks vs the lexical
   gate** — publish the number even if unflattering. This is *measure*, not build. It also
   closes the §1 "enforcement depth" gap where it most bites.
2. **Close the memory loop (or admit it's open).** No runtime decision consumes crystallized
   memory or the self-map (access_count all 0). Either wire **one** runtime consumer
   (corrective-recall / a crystal read on a real decision) and measure whether it changes an
   outcome, or state plainly in the docs that memory is store-only. The dormant
   `hippocampus.py` corrective-recall is the surprise/contradiction-cued instinct already
   built-but-never-lit — lighting it is the convergent direction (and aligns with Graphiti's
   contradiction-then-invalidate), but it is a no-op while RFC-012/no-rewrite is parked, so
   this is *measure the dark path*, not build a new one.
3. **Trace schema: scoped IDs + governance records (§3.2).** ~1 file, no dependency, directly
   from a deep-read source. The one place a new artifact is clearly justified.
4. **Temporal/relational memory: wrap Graphiti (§3.1).** Already planned; local LLM + FalkorDB
   keeps it free. Build only the deterministic repo-topology walker.
5. **The auditor ≠ auditee structural gap.** OPA's decision/enforcement separation,
   capability theory's unforgeable *external* tokens, and MCP's *external* authorization
   server all point at the same critique: ToneSoul **still largely gates and audits itself**.
   pr_preflight, the reviewer, and the council are author-run; by their own docstrings the
   same blind spot that produces an error can blind the self-check. The only real backstop
   stays the **external eye** (a separate model/human/session — the 語魂投資 #202 pattern).
   This is a known, documented boundary, not a quick fix.
6. **Decision-ergonomics (Step 3's real gift).** Adopt the auto/report/confirm tier as a
   *session-opening declarable convention* and carry the human-decision-cost view. This is a
   convention + maybe a small template, **not** a subsystem. `AGENTS.md`/`CLAUDE.md` are
   human-managed — propose, do not edit.

## §5 What this is NOT (the anti-manifesto)

- It is **not** a claim that ToneSoul independently reached SOTA. Every layer has an older,
  stronger, externally-validated reference (§3). ToneSoul's honest differentiation is
  **deployment-level**: single creator, one named vocabulary, pip-installable, honest
  evidence labels — exactly as `RELATED_WORK.md` §0 already states.
- The genuine contribution available here, if any, is **not the mechanism** (memory, hashing,
  tiered gates are all convergent) but the **binding**: memory + decision bound to
  provenance + permission + stop-conditions, where every read/write leaves an auditable trace
  gated by approval. Almost none of the referenced memory systems treat that as first-class
  (Graphiti's edge-provenance is the closest, and even that is for retrieval, not audit).
- It is **not** a 7-step responsibility theory. The "Step 1/2/3" ladder is a narrative over a
  convergent pattern; the value is accountability-alignment + discipline, **not novelty**.

## §N Coda (orientation, read last)

Where ToneSoul actually stands: the scaffolding is real and mostly live; the semantic
enforcement is thinner than the scaffolding implies; the memory is a ledger, not yet a loop;
the hardest boundaries are honest prose, not machine checks. That is not a failure — it is the
honest coordinate. The next cheap, honest moves are **measure** moves (turn the semantic
sensor on and publish its catch-rate; light or honestly retire the dark memory path) and
**one** clearly-justified build (the trace schema). What to refuse: building a bespoke memory
engine (wrap Graphiti), climbing a ladder of new subsystems, or letting the ladder narrative
inflate into a theory the evidence does not support. The external eye remains the only real
backstop — keep it external.
