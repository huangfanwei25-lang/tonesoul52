# Council Structured / Runtime Boundary Addendum

Date: 2026-03-09
Scope: `governance_pipeline_and_llm`

## Problem

ToneSoul currently has two different council verdict contracts:

- an internal structured schema used to validate parsed LLM output
- an outward runtime/API payload used by `UnifiedPipeline`, the web/API layer, and observability surfaces

Both had been allowed to coexist under the same short label, `CouncilVerdict`, but they are not the same thing.

That naming overlap became dangerous because the structured schema in `tonesoul/schemas.py` silently ignored unknown fields. A runtime payload such as:

```python
{"verdict": "refine", "votes": [...]}
```

could be passed into the structured schema and would not fail. Instead it would quietly fall back to the structured defaults:

- `decision = defer`
- `confidence = 0.5`

This is worse than a loud validation error. It converts one contract into another while pretending the parse succeeded.

## Principle

The boundary is not only "public repo vs private repo". There is also a smaller but equally important boundary inside one runtime:

- structured schema = internal semantic contract
- runtime verdict payload = outward operational contract

These layers may share vocabulary, but they must not silently accept each other's shape.

## Correction

This phase applies three rules:

1. The structured schema is explicitly named `CouncilStructuredVerdict`.
2. The structured schema is `extra=\"forbid\"`, so runtime-only keys fail fast.
3. `CouncilVerdict` remains as a compatibility alias to avoid widening this phase into a public rename campaign.

This keeps the public/runtime payload stable while making the internal semantic validator strict again.

## Why This Is The Right Cut

This phase deliberately does **not** redesign the outward `council_verdict` payload.

That would be a wider public-contract phase affecting:

- `UnifiedPipeline`
- `apps/api`
- frontend deliberation payload consumers
- stored evolution / observability artifacts

The correct order is:

1. stop silent contract bleed at the validation seam
2. keep the outward runtime payload stable
3. only then decide whether a future outward rename or restructuring is worth the migration cost

## Secondary Finding

While validating this boundary, a dormant syntax blocker surfaced in `tonesoul/unified_pipeline.py`:

- `if semantic_graph_summary:` had a broken indentation block

This is a useful reminder that boundary work on shared seams should still end in broader regression, because the touched area may reveal unrelated but adjacent import/runtime failures.
