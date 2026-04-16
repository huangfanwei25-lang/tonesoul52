# ToneSoul 2.0 Architecture Stack (2026-04-14)

> Purpose: define one pragmatic future-state architecture for a C# / .NET ToneSoul line without confusing orchestration logic, memory/governance rules, and local inference internals.
> Status: planning aid only. This is not the current repo runtime, not an accepted task-board program, and not a rewrite order by itself.
> Authority posture: `task.md`, current `docs/status/*`, code, and tests still outrank this note for present-tense claims.

---

## 1. Decision Summary

ToneSoul 2.0 should be treated as a **two-layer system**, not a single-framework bet:

1. `Semantic Kernel` as the **control plane**
2. `dotLLM` as the **inference engine**
3. one explicit **Inference Adapter Layer** between them

Pragmatic landing order:

1. stabilize ToneSoul logic in C# on top of `Semantic Kernel`
2. bring up the first local inference backend with `LLamaSharp`
3. keep the inference boundary swappable
4. replace or augment the backend with `dotLLM` only after the logic layer is already stable

This avoids two bad extremes:

- `dotLLM`-only: strong engine, weak system, too much infrastructure rebuilt from zero
- `Semantic Kernel` + opaque hosted API only: strong orchestration, weak traceability and weak inference control

---

## 2. Core Thesis

The future C# line should separate:

- **governance logic** from **token generation**
- **memory/rules/council behavior** from **numerical inference**
- **what ToneSoul believes is allowed** from **how a model produces the next token**

In ToneSoul terms:

- `L1 / L2 / L3` attribution rules
- council / dissent / vow / timestamp discipline
- honesty gates and evidence posture
- session memory and operator workflow

should live in the **logic layer**, not inside the inference engine.

By contrast:

- GGUF loading
- tensor execution
- logits inspection
- sampling control
- token-by-token veto or masking

should live in the **inference layer** or the adapter directly above it.

---

## 3. Stack Layout

```text
┌──────────────────────────────────────────────┐
│ ToneSoul Application Layer                  │
│ chat shell / operator UI / workflow entry   │
├──────────────────────────────────────────────┤
│ ToneSoul Logic Layer                        │
│ L1-L3 rules / council / vows / timestamps   │
│ memory policy / honesty gate / trace rules  │
├──────────────────────────────────────────────┤
│ Semantic Kernel                             │
│ agent orchestration / plugins / memory      │
│ tool routing / workflow composition         │
├──────────────────────────────────────────────┤
│ Inference Adapter Layer                     │
│ prompt packaging / trace bridge             │
│ token filter / logits policy / fail-stop    │
├──────────────────────────────────────────────┤
│ Inference Engine                            │
│ Phase 1: LLamaSharp                         │
│ Phase 2+: dotLLM                            │
└──────────────────────────────────────────────┘
```

---

## 4. Role Split

| Layer | Primary Role | ToneSoul-owned concern | Must not absorb |
|---|---|---|---|
| Application | entry surface | chat, operator shell, bounded workflows | inference internals |
| ToneSoul Logic | constitutional layer | L1/L2/L3, council, vow, memory, honesty | raw tensor execution |
| Semantic Kernel | orchestration layer | plugins, tools, workflow routing, session memory | model-specific math |
| Inference Adapter | translation layer | prompt packing, trace capture, token/logits policy hooks | business semantics |
| Inference Engine | compute layer | GGUF parse, inference, sampling, diagnostics | ToneSoul governance |

The key boundary is not "C# versus Python."

The key boundary is:

`governance/orchestration` versus `inference/compute`

---

## 5. Project Mapping

### Semantic Kernel

Use for:

- agent and workflow orchestration
- plugin / tool invocation
- memory plumbing
- prompt and function routing
- multi-step application logic

ToneSoul mapping:

- council orchestration
- rule-enforced session flows
- memory retrieval policy
- operator-facing bounded workflows
- honesty and trace posture at the application/control level

### dotLLM

Use for:

- local GGUF inference
- token generation
- logits-level introspection
- execution-time diagnostics

ToneSoul mapping:

- token-time veto hooks
- low-level fail-stop enforcement
- A/B/C verification at generation time
- inference trace capture for hallucination-control experiments

### LLamaSharp

Use first as:

- the shortest path to a working local C# inference backend
- a bootstrap backend while the logic layer is still being proven

It is a **bring-up accelerator**, not necessarily the final engine.

### llama.cpp / vLLM

Treat as:

- reference implementations and performance/architecture study targets
- not the primary control-plane choice for the first ToneSoul 2.0 landing

---

## 6. Why One Project Is Not Enough

### If ToneSoul 2.0 uses only dotLLM

You get:

- a powerful native engine
- low-level control

But you still need to build:

- memory/session management
- tool calling
- agent orchestration
- workflow composition
- policy routing

That means the team would spend early effort rebuilding infrastructure instead of validating ToneSoul logic.

### If ToneSoul 2.0 uses only Semantic Kernel plus hosted APIs

You get:

- fast orchestration
- plugins and memory scaffolding

But you lose:

- control over raw inference behavior
- token/logits-level inspection
- stronger traceability at the compute boundary
- a credible path to hard local fail-stop semantics

That conflicts with ToneSoul's stronger honesty and traceability goals.

---

## 7. Recommended Landing Path

## Phase 0: Preserve Behavioral Truth

Before any C# port becomes serious:

- treat the current Python ToneSoul repo as the behavioral reference
- decide which behaviors are essential enough to port
- write parity-oriented tests or scenario fixtures first

Do not begin by "rewriting everything in C#."

Begin by defining:

- what must remain equivalent
- what may simplify
- what is intentionally deferred

## Phase 1: Control Plane First

Target:

- `Semantic Kernel` + `LLamaSharp`

Goal:

- prove ToneSoul logic can run in a C# environment

Minimum deliverables:

- one C# solution skeleton
- one ToneSoul session flow
- one memory abstraction
- one council orchestration path
- one honesty/trace gate
- one local inference smoke path

Success looks like:

- memory works
- rule routing works
- local model responses are callable
- core session lifecycle is observable

## Phase 2: Freeze The Adapter Boundary

Before touching `dotLLM`, make the backend boundary explicit.

At minimum, define interfaces like:

```csharp
public interface IInferenceEngine
{
    Task<InferenceResult> GenerateAsync(InferenceRequest request, CancellationToken ct);
}

public interface IInferencePolicy
{
    TokenDecision Inspect(TokenStep step);
}

public interface IInferenceTraceSink
{
    Task WriteAsync(InferenceTrace trace, CancellationToken ct);
}
```

The exact names may change. The architectural point should not.

If `Semantic Kernel` or ToneSoul logic binds directly to one backend's concrete types, the swap to `dotLLM` will be expensive and noisy.

## Phase 3: Replace Or Extend The Engine

Target:

- `Semantic Kernel` + adapter + `dotLLM`

Goal:

- preserve the already-working logic layer
- gain deeper control over inference

This phase is where ToneSoul can start experimenting with:

- token veto
- logits masking
- generation-time contradiction checks
- inference trace capture
- stronger fail-stop rules before a sentence fully lands

## Phase 4: Calibrated Governance At Inference Time

Only after the above is stable:

- introduce harder L1-style checks at the inference boundary
- evaluate cost/latency impact
- prove that the extra controls reduce hallucination or drift rather than only making the system slower

---

## 8. ToneSoul-Specific Placement

### Put these in the logic/control layer

- L1 / L2 / L3 attribution rules
- council routing and dissent preservation
- vow handling
- timestamp discipline
- memory admission and promotion policy
- claim honesty posture
- session and operator workflow rules

### Put these in the adapter or inference layer

- prompt packaging for local inference
- token-by-token inspection
- logits-level blocking or reweighting
- low-level stop reasons
- inference trace capture
- runtime diagnostics about generation path

### Do not mix them

If council semantics become hard-coded inside the raw inference backend, the engine becomes ToneSoul-specific and harder to evolve.

If low-level generation controls are only expressed as high-level orchestration prose, the system stays too soft and too black-boxed.

---

## 9. Non-Goals

This document does **not** claim:

- that ToneSoul should abandon the current Python line now
- that `dotLLM` is already proven as the final production backend
- that pure native C# inference is automatically better than a binding-based path
- that ToneSoul 2.0 should become the active launch short board
- that current collaborator-beta work should pause for a full 2.0 rewrite

---

## 10. Main Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| dotLLM-first overreach | too many unknowns at once | start with LLamaSharp |
| layer leakage | governance bleeds into engine internals | keep adapter explicit |
| black-box drift | hosted API hides inference behavior | preserve local-engine path |
| parity loss | C# rewrite drifts from current ToneSoul semantics | define parity fixtures first |
| performance mythology | low-level control is assumed to help before evidence | measure before promoting claims |

---

## 11. Recommended Study Set

The following are the most relevant references for this 2.0 direction.

Treat this list as **planning input** and re-verify upstream APIs and repo state before implementation.

### Primary

- `dotLLM`
  - <https://github.com/kkokosa/dotLLM>
- `Semantic Kernel`
  - <https://github.com/microsoft/semantic-kernel>
- `LLamaSharp`
  - <https://github.com/SciSharp/LLamaSharp>

### Performance / Architecture Benchmarks

- `llama.cpp`
  - <https://github.com/ggerganov/llama.cpp>
- `vLLM`
  - <https://github.com/vllm-project/vllm>

---

## 12. Decision In One Sentence

ToneSoul 2.0 should use `Semantic Kernel` as the orchestration and governance host, keep ToneSoul semantics above a strict inference adapter, and adopt `dotLLM` only after the logic layer is already running and the backend boundary is swappable.

---

## 13. Repo-Native Interpretation

For the current repository, the honest reading is:

- this is a future architecture direction
- it belongs in `docs/plans/` until explicitly ratified
- it must not silently outrank the current Python implementation, tests, or launch-readiness short board

That keeps the 2.0 idea useful without letting it become a second fake present-tense roadmap.
