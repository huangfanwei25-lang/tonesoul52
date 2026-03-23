# Trinket Protocol Spec v1

> Purpose: specify the auditable dispatch contract for high-tension handling across ToneSoul runtime and evolution lanes.
> Last Updated: 2026-03-23

Date: 2026-02-14  
Status: Active (Phase 100A baseline)

## 1. Purpose

Trinket Protocol defines an auditable runtime dispatch contract for high-tension handling across ToneSoul runtime and YSS evolution pipeline.

Goals:
- Keep L1/L2/L3 boundaries explicit.
- Route runtime behavior with a stable A/B/C state machine.
- Persist responsibility trace for post-hoc audit.

## 2. Layer Contract

- L1 Ontology: concrete facts, constraints, and externally verifiable claims.
- L2 Model: reasoning strategy, decomposition, and control decisions.
- L3 Metaphor: communication framing, style, and narrative scaffolding.

Rules:
- Layer Decoupling: never present L3 metaphors as L1 facts.
- Is-Ought Monitor: explicitly mark value-based prioritization.
- Currency Audit: avoid unexplained terminology inflation.
- Responsibility Trace: every non-standard path must leave trace metadata.

## 3. Runtime Dispatch Contract (A/B/C)

State A (`resonance`):
- Trigger: low adjusted tension, no conflict loop.
- Intent: normal path, standard deliberation.

State B (`tension`):
- Trigger: medium adjusted tension or resonance tension signal.
- Intent: caution path, stronger engineering/constraint framing.

State C (`conflict`):
- Trigger: high adjusted tension, conflict resonance, or loop risk.
- Intent: safety-prioritized path, guardrail-first behavior.

Required trace fields:
- `contract`: `trinket_dispatch_v1`
- `state`: `A|B|C`
- `mode`: `resonance|tension|conflict`
- `tension_score`, `adjusted_tension`
- `resonance_state`, `loop_detected`
- `prior_delta_t`
- `reasons[]`

## 4. Runtime Integration

`UnifiedPipeline` MUST:
- Build dispatch trace before deliberation and LLM call.
- Attach dispatch trace to:
  - `trajectory_analysis.dispatch`
  - `council_verdict.metadata.dispatch`
  - `council_verdict.metadata.dispatch_state`
  - `dispatch_trace` in response payload
- Include dispatch state in visual chain frame data.

## 5. Evolution Integration

`yss_pipeline` MUST provide:
- Unified request adapter (`run_pipeline_from_unified_request`)
- Seed mapping from runtime contract (`build_unified_seed`)
- Non-null A/B/C evaluation snapshot artifact (`multi_persona_eval.json`)

## 6. Compatibility / Zombie Boundary

`UnifiedCore` is marked `legacy_non_runtime`:
- Allowed for compatibility tests and legacy wrappers.
- Not the production chat runtime entrypoint.
- Production runtime owner: `tonesoul.unified_pipeline.UnifiedPipeline`.
