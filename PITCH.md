# ToneSoul

**Runtime-level Constitutional AI as a framework — by an outside engineer, shipping in production.**

Most "AI alignment" today lives in two places: research papers, and the post-training of frontier model providers. ToneSoul is a third place: a runtime governance framework that any application built on any LLM can wrap around its outputs, so the alignment posture is *enforced at execution time* rather than hoped for at training time.

It is built and maintained by Fan-Wei Huang — a medical-equipment maintenance engineer who started this project after watching what happens in hospitals when machines and humans drift out of agreement. The framework's origin is not academic. It is operational.

## The mapping

If you read alignment vocabulary, this is what ToneSoul actually is:

| ToneSoul (project naming) | Alignment vocabulary |
| --- | --- |
| `AXIOMS.json` — 7 immutable laws + first-order logic | Constitutional AI as machine-readable runtime invariants |
| `誠實高於有益` (Axiom priority chain) | HHH triad with honesty explicitly ranked above helpfulness |
| Pre-output Council (Guardian / Analyst / Critic / Advocate / Axiomatic) + verifier | Multi-perspective deliberation + steering / refusal pipeline |
| `EpistemicLabeler` (Phase 864a, shipped 2026-04-19) | Per-output epistemic provenance: retrieved / distilled / generated / speculative-metaphysical |
| Vow system + `DriftMonitor` / `JumpMonitor` | Persona stability + behavioral consistency monitoring |
| Aegis hash chain (`.aegis/keys/`, Ed25519 signed verdict log) | Non-repudiable provenance / decision audit trail |
| `GovernanceKernel` routing | Safety routing layer — every action passes through governance |
| `Council Calibration v0a` (4 metrics, V1.1 shipped 2026-04-16) | Trackable governance baseline; bridges descriptive monitoring → outcome calibration |
| Isnād provenance | Chain-of-custody for memory / claims |

## What you can run today

```bash
pip install tonesoul52
python -m tonesoul.diagnose --agent demo
python examples/quickstart.py
```

Concrete defenses already in the codebase, with tests:

- **Prompt injection** — Council + verifier reject manipulated inputs.
- **Persona / vow override** — vow system rejects contradictions against declared identity.
- **Gradual context drift** — `DriftMonitor` flags semantic drift before it compounds.
- **Sudden persona flip** — `JumpMonitor` catches discontinuous identity shifts.
- **Honesty cap** — when confidence < 60% on grounding-required claims, output is forced to hedge or refuse.
- **Epistemic flagging** *(new, 2026-04-19)* — every output now carries a label distinguishing retrieved facts from distilled training-time synthesis from generated novel composition from speculative metaphysical claims; the latter must contain explicit framing or the verifier may refuse.

## What's honest about the boundaries

The next layers — mutual user-AI calibration table (Phase 864b) and choice memory + deliberation trace (Phase 864c) — are written as specifications under [docs/plans/](docs/plans/), not yet implemented. The spec for them was drafted 2026-04-18; per the project's own phasing rule, 864b cannot start until 864a runs as baseline for ≥2 weeks. This is not a vapor-pitch. The roadmap says what's done and what isn't.

The Council's `council_decision_quality` indicator is currently `descriptive_only`. Upgrading it to `runtime_present` requires v0b verdict↔outcome alignment data — also planned, also not yet shipped. We say so.

## Why this is "Built with Claude Code"

The repository is one of the cleanest existing examples of a non-trivial framework being **co-built** with Claude Code over time, with the AI collaboration tracked in surfaces designed for AI inspection: [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), [AI_ONBOARDING.md](AI_ONBOARDING.md), per-commit `Co-Authored-By` attribution, and a session-tracking memory store. This is not "AI helped me write code" — it is multi-agent collaboration recorded as a first-class artifact. Read [AGENTS.md](AGENTS.md) and the recent commit log; the pattern is visible.

## Why this matters

Alignment frameworks usually get presented as either philosophy or proprietary internals. ToneSoul is the working framework that an engineer outside any frontier lab built, in the open, against a single hard constraint: the AI must be answerable for what it just said. Every output passes through the same governance kernel; the verdict, the dissent, and the epistemic label all get recorded; and the chain is signed.

If alignment is going to scale, more of it needs to look like this — a thing you can `pip install`, audit, and extend.

---

**Repository:** https://github.com/Fan1234-1/tonesoul52
**PyPI:** `pip install tonesoul52`
**Author:** Fan-Wei Huang (Fan1234-1)
**Drafted:** Claude Opus 4.7, 2026-04-19
