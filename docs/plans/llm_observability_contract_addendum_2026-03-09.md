# LLM Observability Contract Addendum (2026-03-09)

> Purpose: define the canonical observability contract for shared LLM payloads across runtime and dream surfaces.
> Last Updated: 2026-03-23

## Problem

`UnifiedPipeline` and `DreamEngine` were both emitting an `llm` observability payload, but each one was building the dict by hand.

That looked harmless because the shapes were currently similar:

- `backend`
- `model`
- `usage`

But the risk was structural:

- the same payload was now feeding more than one surface
- runtime trace tests depended on it
- dream / wake-up observability depended on it
- future budget and dashboard logic would keep depending on it

If two producers build the same shape manually, they do not really share a contract. They only share an accident.

## What Changed

This phase introduces a canonical schema-backed builder in `tonesoul/schemas.py`:

- `LLMUsageTrace`
- `LLMObservabilityTrace`

Both runtime producers now emit through the same builder:

- `UnifiedPipeline._attach_llm_observability()`
- `DreamEngine._build_llm_observability()`

## Why This Is the Right Scope

There is a larger nearby problem: the name `CouncilVerdict` already refers to one schema contract while the external runtime/API verdict payload still uses a different shape.

That issue is real, but it is not safe to "clean up" casually because it sits close to public contract behavior.

The LLM observability trace was the better next step because:

- it is already internal/runtime-facing
- it is duplicated in multiple producers
- it has existing tests on both call sites
- it can be canonicalized without changing the exposed shape

## Guardrail

When the same runtime payload shape appears in more than one producer and already feeds downstream observability, budget, or dashboard logic:

- do not wait for drift to become visible
- introduce one schema-backed builder before expanding the payload any further

The goal is not type purity. The goal is to stop parallel hand-built shapes from silently becoming different contracts.
