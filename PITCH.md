# ToneSoul

**Runtime-level Constitutional AI as a framework — by an outside engineer, published and runnable today.**

> Evidence labels follow the repo's E1–E6 ladder (see README "Evidence Honesty"). Honest status up front: the framework runs in-repo and in demos (E3/E4); there is no external production deployment yet, and we say so.

Most "AI alignment" today lives in two places: research papers, and the post-training of frontier model providers. ToneSoul is a third place: a runtime governance framework that any application built on any LLM can wrap around its outputs, so the alignment posture is *enforced at execution time* rather than hoped for at training time.

It is built and maintained by Fan-Wei Huang — a medical-equipment maintenance engineer who started this project after watching what happens in hospitals when machines and humans drift out of agreement. The framework's origin is not academic. It is operational.

## The mapping

If you read alignment vocabulary, this is what ToneSoul actually is:

| ToneSoul (project naming) | Alignment vocabulary |
| --- | --- |
| `AXIOMS.json` — 8 immutable laws + first-order logic | Constitutional AI as machine-readable runtime invariants (honest caveat: per-axiom runtime enforcement varies — roughly half are enforced today, the rest referenced or aspirational; a per-axiom reconciliation is pending) |
| `誠實高於有益` (Axiom priority chain) | HHH triad with honesty explicitly ranked above helpfulness |
| Pre-output Council (Guardian / Analyst / Critic / Advocate / Axiomatic) + verifier | Multi-perspective deliberation + steering / refusal pipeline |
| `EpistemicLabeler` (Phase 864a, shipped 2026-04-19) | Per-output epistemic provenance: retrieved / distilled / generated / speculative-metaphysical |
| Vow system + `DriftMonitor` / `JumpMonitor` | Persona stability + behavioral consistency monitoring |
| Aegis hash chain (`.aegis/keys/`, Ed25519 signed verdict log) | Tamper-evident local audit trail (single machine, all keys held by the same operator — so this is *not* non-repudiation against the operator; signing requires the PyNaCl extra and is silently skipped without it, a known gap) |
| `GovernanceKernel` routing | Safety routing layer — outputs on the chat pipeline pass through governance (the quickstart demo path is shallower) |
| `Council Calibration v0a` (4 metrics, V1.1 shipped 2026-04-16) | Trackable governance baseline; bridges descriptive monitoring → outcome calibration |
| Isnād provenance | Chain-of-custody for memory / claims |

## What you can run today

```bash
pip install tonesoul52
python -m tonesoul.diagnose --agent demo
python examples/quickstart.py
```

> ⚠️ PyPI 1.0.0 shipped with a broken council import (`ModuleNotFoundError: No module named 'memory'`). The fix is in PR #78 (open at the time of writing), planned for 1.0.1. Until 1.0.1 is on PyPI, install from source: `pip install git+https://github.com/Fan1234-1/tonesoul52`.

Concrete defenses already in the codebase, with tests:

- **Prompt injection** — Council + verifier reject manipulated inputs.
- **Persona / vow override** — vow system rejects contradictions against declared identity.
- **Gradual context drift** — `DriftMonitor` flags semantic drift before it compounds.
- **Sudden persona flip** — `JumpMonitor` catches discontinuous identity shifts.
- **Thin-support flag** — a grounding check (lexical heuristic over caveat phrasing, user-echo, and context-keyword overlap) raises severity and routes to revision when support looks thin. It runs only at full governance depth, does not measure confidence, and cannot force a refusal on its own. (An earlier version of this document called this an "honesty cap" with forced hedge/refuse — that mechanism does not exist; this is the real one.)
- **Epistemic flagging** *(new, 2026-04-19)* — every output now carries a label distinguishing retrieved facts from distilled training-time synthesis from generated novel composition from speculative metaphysical claims; the latter must contain explicit framing or the verifier may refuse.

## What's honest about the boundaries

Phase 864b (verdict↔outcome JOIN, Bucket B) merged to master 2026-04-22 and Phase 864c (deliberation trace) merged 2026-06-03 — both now run against synthetic/test traffic only. What has **not** happened is real external traffic: the gateway has no external consumers yet, so calibration data comes from harnesses, not users. The roadmap says what's done and what isn't.

The Council's `council_decision_quality` indicator is currently `descriptive_only`. Upgrading it to `runtime_present` requires v0b verdict↔outcome alignment data — also planned, also not yet shipped. We say so.

## Why this is "Built with Claude Code"

The repository is one of the cleanest existing examples of a non-trivial framework being **co-built** with Claude Code over time, with the AI collaboration tracked in surfaces designed for AI inspection: [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), [AI_ONBOARDING.md](AI_ONBOARDING.md), per-commit `Co-Authored-By` attribution, and a session-tracking memory store. This is not "AI helped me write code" — it is multi-agent collaboration recorded as a first-class artifact. Read [AGENTS.md](AGENTS.md) and the recent commit log; the pattern is visible.

## Why this matters

Alignment frameworks usually get presented as either philosophy or proprietary internals. ToneSoul is the working framework that an engineer outside any frontier lab built, in the open, against a single hard constraint: the AI must be answerable for what it just said. On the chat pipeline, outputs pass through the governance kernel; verdicts and dissent are recorded, and committed traces are signed when the PyNaCl signing extra is installed (silently skipped without it — a known gap slated for repair). The quickstart demo exercises the council + vow layer directly — a shallower path with no trace signing.

If alignment is going to scale, more of it needs to look like this — a thing you can `pip install`, audit, and extend. *(Known gap: PyPI 1.0.0 shipped with a broken council import; the fix is in PR #78, open at the time of writing, planned for 1.0.1. Until then, install from source.)*

---

**Repository:** https://github.com/Fan1234-1/tonesoul52
**PyPI:** `pip install tonesoul52`
**Author:** Fan-Wei Huang (Fan1234-1)
**Drafted:** Claude Opus 4.7, 2026-04-19
