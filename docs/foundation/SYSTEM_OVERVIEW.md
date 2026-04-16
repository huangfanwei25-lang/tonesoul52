# Foundation Layer: System Overview

> Purpose: define what ToneSoul is, what it is not, and what the current honest center of the project is.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to `README.md`, `DESIGN.md`, and canonical architecture contracts.

---

## One-Sentence Description

ToneSoul is a verifier-first AI governance architecture that tries to keep outputs challengeable, traceable, and bounded by visible contracts rather than smooth over uncertainty.

## What The Project Is Doing

- Building a governance stack, not only a chat wrapper.
- Preserving dissent before output finalization.
- Keeping continuity bounded instead of treating all memory as identity.
- Distinguishing tested behavior from documented intention.

## What It Is Not

- Not a single master prompt.
- Not "memory plus vibe" dressed up as architecture.
- Not a claim that council agreement equals correctness.
- Not a claim that all documented ideas are already runtime truth.
- Not yet a broadly proven public-maturity platform.

## Current Honest Center

- Guided collaborator-beta is the honest operating posture.
- File-backed, testable, evidence-bounded flows outrank mythology-heavy system stories.
- The repo should prefer one durable design center over overlapping overview files.

## Current Minimal Runnable Core

The clearest runnable core today is the governance demo:

```bash
python examples/quickstart.py
```

That flow demonstrates:

- posture load via `runtime_adapter`
- tension scoring
- POAV quality scoring
- vow checks
- council validation

## If You Need One Mental Model

Read ToneSoul as:

- governance before persuasion
- disagreement before finalization
- bounded continuity before identity inflation
- evidence before overclaim

## Source Anchors

- [README.md](../../README.md)
- [DESIGN.md](../../DESIGN.md)
- [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](../architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md)
- [docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](../architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
