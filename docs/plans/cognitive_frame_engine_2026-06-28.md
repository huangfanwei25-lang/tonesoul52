# Cognitive Frame Engine MVP

> Date: 2026-06-28
> Status: implementation plan + boundary contract for the first deterministic slice.
> Scope: problem-structure framing for AI agents. This is not a claim that the model has
> human cognition, world understanding, or a private chain of thought.
> Anchors: `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`,
> `docs/plans/tonesoul_responsibility_native_runtime_architecture_2026-06-27.md`,
> `docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md`.

## Thesis

The next practical step toward an AI agent "cognitive engine" is not a hidden
thinking layer. It is an external, auditable **Cognitive Frame**:

```text
question -> time / place / actors -> known facts -> unknowns -> hypotheses
         -> constraints -> next probes -> evidence refs -> reviewable frame
```

This follows ToneSoul's externalized-cognition direction: keep the important
reasoning dependencies outside opaque model weights, and make the frame small
enough to test.

## Boundary

The MVP can verify:

- the frame has a concrete question;
- factual lanes carry `evidence_refs`;
- hypotheses are not mislabeled as observed facts;
- unknowns or hypotheses lead to next probes;
- malformed or extra fields fail closed;
- the evaluator is deterministic and does not call an LLM or network.

The MVP cannot verify:

- whether the evidence semantically supports the claim;
- whether the temporal or spatial context is complete;
- whether the model "really understands" the situation;
- whether the next probes are optimal;
- whether a future answer will be correct.

This is the same discipline as the responsibility runtime: Phase 1 validates
form and traceability, not truth.

## First Implementation Slice

Add a parked, test-backed package:

```text
tonesoul/cognition/
  __init__.py
  cognitive_frame.py
```

The package exports:

- `CognitiveFrame`
- `FrameItem`
- `CognitiveFrameIssue`
- `CognitiveFrameValidationResult`
- `validate_cognitive_frame`

The schema is intentionally boring:

- `question`
- `temporal_context`
- `spatial_context`
- `actors`
- `known_facts`
- `hypotheses`
- `unknowns`
- `constraints`
- `next_probes`

Every lane item has:

- `text`
- `evidence_refs`
- `confidence`: `observed | derived | inferred | unknown`

## Acceptance Criteria

- Unit tests cover valid frames, malformed frames, missing evidence, missing probes,
  and the form-only claim/evidence boundary.
- A deterministic probe writes a small status report under `docs/status/`.
- No private memory data is read or committed.
- No live pipeline behavior changes.
- Full validation remains green before PR: `pytest tests/ -x` and
  `ruff check tonesoul tests`.

## Future Cuts

After this MVP is stable:

1. Feed real public project artifacts into the frame and measure coverage.
2. Add adversarial fuzzy cases for overconfident framing.
3. Connect the frame to responsibility-runtime trace events.
4. Only then consider using an LLM to propose candidate frames, with this
   deterministic evaluator as the outer contract.
