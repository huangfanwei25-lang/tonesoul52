# Governance Depth Routing & Consistency Gate — Design Note

> Purpose: document the rationale, current-state analysis, and proposed design for governance-depth routing in ToneSoul.
> Source: Tufts neuro-symbolic energy paper (ScienceDaily 2026-04-05) + Module 0/A/B/C sketch from user + pipeline audit.
> Status: queued design (Phase 849-852). Not the active bucket — Phase 847 (Self-Improvement Loop v0) remains the current short board.

---

## 1. Why Thin The Pipeline

### The Problem

Every request to `UnifiedPipeline.process()` walks **30 steps** regardless of risk:

```
 1. ComputeGate.evaluate()        — route (local vs cloud)
 2. Cross-Session Recovery         — history recovery
 3. Injection Context              — persona injection
 4. Rebuild commit_stack           — Third Axiom
 5. Rebuild trajectory             — trajectory rebuild
 6. Scenario Envelope              — bull/base/bear
 7. ToneBridge.analyze()           — emotion/motive extraction
 8. Trajectory.analyze()           — trajectory analysis
 9. DriftMonitor.observe()         — drift monitoring
10. TensionEngine.compute()        — tension computation
11. Reflex Arc evaluate()          — reflex arc
12. RuntimeFriction                — friction computation
13. CircuitBreaker check           — circuit breaker
14. Jump Trigger check             — jump detection
15. AlertEscalation.evaluate()     — L1/L2/L3 escalation
16. Deliberation.deliberate_sync() — 3-voice debate (multi-round)
17. Early contradiction warning    — contradiction pre-check
18. GraphRAG retrieval             — graph memory
19. Semantic trigger check         — semantic trigger
20. Hippocampus recall             — vector memory + corrective
21. _build_context_prompt()        — assemble system prompt
22. LLM call (chat_with_tier)      — ACTUAL GENERATION
23. _self_check() loop             — Vow + Council + Tension (multi-LLM)
24. Commitment extraction          — commitment tracking
25. Semantic graph update          — graph update
26. POAV gate                      — output verification
27. Contract observer              — contract check
28. Reflex final gate              — reflex arc final gate
29. Mirror check                   — mirror recursion
30. Journal write                  — journal
```

Steps 1-21 and 24-30 are local computation (each < 10ms). The latency bottleneck is #22 (LLM call) and #23 (self_check, which may call LLM + Council 2-3 times).

But **code complexity** scales with number of steps. Asking "what's the weather?" runs the same 30-step path as "analyze this 10-K filing."

### The Research Anchor

Tufts neuro-symbolic paper (2026-04-05): hybrid neural+symbolic systems achieve 100x energy reduction. Core insight: **not all tasks need equal compute**. Use a lightweight classifier to pre-route and skip expensive paths.

### What Module 0/A/B/C Proposed (User Sketch)

- **Module 0**: Front-end risk router. SLM or intent classifier → risk score → L-Risk (bypass governance) or H-Risk (full pipeline).
- **Module A**: Neural divergent engine with "reverse pointer protocol" — every claim must point to source.
- **Grounding Bridge**: Translate continuous neural outputs to discrete boolean variables.
- **Module B**: Symbolic constraint core (C6). Asynchronous "poison packet" kills bad branches mid-generation.
- **Module C**: G-P-A-R governance bus with HelpSense formula.

### What We Keep vs What We Don't

| Concept | Verdict | Reason |
|---|---|---|
| Pre-hoc risk routing | **Keep** | Core value — route before generating, not after |
| Graduated governance depth | **Keep** | `light / standard / full` maps cleanly to existing seams |
| Reverse pointer protocol | **Defer (Phase 851)** | Can't control LLM token generation; do post-hoc grounding check instead |
| Grounding Bridge | **Don't import** | ToneBridge already extracts features; no need for a separate continuous→discrete bridge |
| Poison packet / async abort | **Don't import** | API-based LLM can't be interrupted mid-generation. Could do streaming abort as weak substitute |
| HelpSense formula | **Don't import** | ReflexEvaluator already more comprehensive |
| N>1/N=1 binary split | **Don't import** | SoulBand spectrum design is more nuanced (serene→alert→strained→critical) |
| Physical track routing | **Don't import** | ToneSoul doesn't control inference hardware |

---

## 2. Current State: What Already Exists

### ComputeGate (tonesoul/gates/compute.py)

Already has 3 routing paths:
- `RoutingPath.PASS_LOCAL` → local LLM, bypasses Council/Cloud
- `RoutingPath.PASS_CLOUD` → cloud LLM, full pipeline
- `RoutingPath.BLOCK_RATE_LIMIT` → rate-limited, no generation

But ComputeGate only decides **model routing** (local vs cloud), not **governance depth**. A request routed to cloud always runs the full 30-step pipeline.

### Reflex Arc (tonesoul/governance/reflex.py)

SoulBand system with 4 levels:
- SERENE (0-0.30): gate_modifier=1.0
- ALERT (0.30-0.55): gate_modifier=0.90
- STRAINED (0.55-0.80): gate_modifier=0.75, forced council
- CRITICAL (0.80-1.00): gate_modifier=0.55, hard enforcement

This already **tightens** governance when risk is high. What's missing is **loosening** governance when risk is low.

### AdaptiveGate (tonesoul/adaptive_gate.py)

`_action_from_tension(value, gate_modifier)` already accepts the reflex arc's modifier. Thresholds are multiplied by gate_modifier (floor 0.55).

---

## 3. Proposed Design: governance_depth

### The Field

Add `governance_depth: str` to ComputeGate's routing result:

| governance_depth | When | What Gets Skipped | What's Preserved |
|---|---|---|---|
| `light` | Low-risk input + SERENE soul band | Steps 5-9, 12-20, 25 (trajectory/drift/scenario/deliberation/hippocampus/graphRAG/semantic) | ComputeGate + Reflex Arc + LLM + lightweight vow check + POAV + Contract + Journal |
| `standard` | Default | Steps 19-20 (semantic trigger + hippocampus corrective), deliberation capped at 1 round | Everything else |
| `full` | High-risk input OR non-SERENE soul band | Nothing skipped | Full 30-step pipeline |

### Axiom 4 Compliance

Axiom 4 (Non-Zero Tension): system never immune to governance signals.

Resolution: **`light` path still runs reflex arc + vow check**. If the reflex arc detects non-SERENE soul band, `governance_depth` is auto-upgraded to `full`. Governance signals remain constitutive even on the fast path.

### Input Risk Classification

Lightweight heuristic in ComputeGate (no LLM needed):
- Keyword scan for high-risk markers: numbers, financial terms, medical terms, legal terms, "verify", "check", "prove", "cite"
- History tension: if prior_tension > 0.3, auto-upgrade
- Message length: very long messages (> 500 chars) default to standard
- Soul band override: non-SERENE always upgrades to full

### Expected Step Count Per Depth

| Depth | Steps | LLM Calls | Estimated Overhead |
|---|---|---|---|
| `light` | ~8 | 1 | ~50ms local + LLM latency |
| `standard` | ~22 | 1-2 | ~150ms local + LLM latency |
| `full` | 30 | 2-4 | ~200ms local + LLM latency |

---

## 4. Verification Over-Budget Fail-Stop (Phase 852)

When `_self_check()` revision loop doesn't converge:

- Current: loops up to `max_revision_attempts` (default 3), each calling LLM + Council
- Problem: 3 × (LLM + Council) = 6+ LLM calls per request

Proposed fail-stop:
- **Budget**: total LLM calls per request capped at N (configurable, default 4)
- **Non-convergence response**: if self_check severity stays > threshold after budget exhaustion, emit honest failure message: "無法充分驗證此回應的可靠性。建議使用者自行查核。"
- **Not silent**: fail-stop is logged to dispatch_trace and visible in dashboard

---

## 5. Take E / R-Memory Compression Status

### What Codex Has Done

- `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md` — the **strategy specification**:
  - 6-layer hot-memory ladder: canonical_center / low_drift_anchor / live_coordination / bounded_handoff / working_identity / replay_review
  - Per-layer decay_posture: never_compress / compaction_safe / bounded_summarize / carry_forward / recompute / quarantine
  - Source-precedence rules and closeout grammar

### What Hasn't Been Done Yet

- **Actual compression algorithm** is not implemented
  - No AAAK-style 30x compression (from MemPalace research)
  - No temporal knowledge graph for session traces
  - No L0-L3 layered loading runtime
- Phase 848 is just `refresh AI first-hop discoverability for Take E` — making the existing doc findable
- The real compression runtime is a future workstream

### Research Concepts Available (from MemPalace distillation)

See `memory/reference_mempalace.md`:
- AAAK (Agent-specific Accessible Adaptive Knowledge): Structured compression → 30x reduction, 95%+ recall
- Temporal Knowledge Graph: session traces as time-aware nodes with decay
- L0-L3 layered loading: L0 always in context, L1 on session start, L2 on demand, L3 archived

These map cleanly to the hot-memory ladder but haven't been wired into runtime yet.

---

## 6. Implementation Boundaries

### What Phase 849-852 Covers (Queued)

1. **Phase 849**: Define `governance_depth` story and routing rules
2. **Phase 850**: Smallest runtime seam — `ComputeGate` returns `governance_depth`, `process()` reads it
3. **Phase 851**: Post-hoc grounding check in `_self_check()` (claim extraction + source trace)
4. **Phase 852**: Verification over-budget fail-stop (LLM call budget + honest failure)

### What This Does NOT Touch

- Axioms
- Vow system semantics
- Council deliberation logic
- Identity / hot-memory authority
- Phase 847 self-improvement active bucket

### Human-Reserved Pieces (Per User)

- Phase 849-850: governance-depth runtime seam (core pipeline)
- Phase 851: high-risk grounding check (core semantics)
- Phase 852: verification over-budget fail-stop (core pipeline)

These touch `tonesoul/gates/compute.py` and `tonesoul/unified_pipeline.py` — core semantic surfaces.

---

## 7. Before / After Summary

### Before (Current)

```
Every request → 30 steps → 2-4 LLM calls
"Hi" and "Analyze TSMC Q4 report" take the same path
No input risk classification
No governance depth routing
No verification budget
```

### After (Phase 849-852)

```
Input → risk classification (< 1ms)
  → light: 8 steps, 1 LLM call (chat, weather, brainstorm)
  → standard: 22 steps, 1-2 LLM calls (most tasks)
  → full: 30 steps, 2-4 LLM calls (fact-check, finance, medical)

Soul band override: non-SERENE always upgrades to full
Verification budget: max N LLM calls, honest fail-stop on non-convergence
```
