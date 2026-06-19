# Canonical Scope

> A navigational front-door: which repo *is* the ToneSoul project, what it is and is not, and at
> what evidence level — for the external reviewers `CALL_FOR_REVIEW.md` invites.
>
> Status: hand-authored **consolidation, not a new source of truth**. It points to the canonical
> docs and reflects the GitHub repo state on 2026-06-19; it introduces **no new claims**. Where this
> document and the canonical sources (or the code) disagree, **they win**.

## 1. What ToneSoul IS

An **AI output accountability / governance layer**. Its one question is **"why does an answer
become the answer?"** — and its job is to make that answer's reasons **readable, runnable,
challengeable, and traceable**: evidence cited, dissent preserved, claim-boundaries held,
degradations logged. It is organized as five system areas (Governance · Council · Memory &
Continuity · Safety · Observability & Evidence).

- Canonical statements: [docs/POSITIONING.md](docs/POSITIONING.md), [README.md](README.md)
  (§90-Second Read, §Five System Areas), [AXIOMS.json](AXIOMS.json).

## 2. What ToneSoul is NOT

Not a truth oracle. Not a jailbreak / safety guarantee. Not a built-in moral compiler. Not a proof
that an AI is conscious. Not a replacement for human review or a domain verifier. Not (primarily) a
memory system, a personality / tone-aesthetic project, or a capability engine racing frontier labs.

- Canonical statements: [README.md](README.md) (§Not This), [AXIOMS.json](AXIOMS.json)
  (`meta.not_for`), [docs/POSITIONING.md](docs/POSITIONING.md) (§What this is not).

## 3. Evidence levels (E1–E6)

The project rates its own claims on a published ladder — **E1 test-backed … E6 unverifiable** — and
is explicit that **nothing is "fully enforced"**: the axioms' own ledger reads *0 fully enforced /
8 partial / 1 referenced*. The honesty characterizations (`tools/eval/*_characterization.py`,
indexed in the scoreboard) are the **E1 floor — test-backed, but scoped to sanitized fixtures, not
production**. Most architectural claims are document-backed (E4) or partial. Per-claim levels are
**not re-derived here**; they live in the matrix.

- Canonical sources:
  [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
  (E1–E6 definitions),
  [docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md](docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md)
  (per-claim mapping),
  [docs/status/honesty_scoreboard_latest.md](docs/status/honesty_scoreboard_latest.md)
  (the E1 characterizations), [AXIOMS.json](AXIOMS.json) (`meta.enforcement_reconciliation`).

## 4. Canonical repo vs lineage vs separate

There is **one canonical repo: `tonesoul52`** (this one). The author has ~26 GitHub repositories;
many share the ToneSoul name or lineage. This is the map, by **actual GitHub state on 2026-06-19**:

**Canonical**
- `tonesoul52` — the project. Everything else is ancestor, component, or separate.
- `OpenClaw-Memory` — supporting component (the Hybrid-RAG memory engine used by `tonesoul52` as a
  submodule), not a separate ToneSoul entry point.

**Live ToneSoul lineage — superseded by `tonesoul52`** (earlier generations of the engine; read `tonesoul52` instead)
- `ToneSoul-Architecture-Engine`, `ToneSoul-Memory-Vault`, `tonesoul-conscience`,
  `Yu-Hun-Cognitive-State-Navigator`.

**Adjacent — related, not superseded** (a different role, not a prior engine generation)
- `Philosophy-of-AI` — philosophical companion to the author's broader work. ToneSoul's ideas draw
  on it; `tonesoul52` does not replace it. Not a superseded engine, not the governance core.

**Archived ancestors** (already archived on GitHub — historical lineage, not entry points)
- `ToneSoul-Integrity-Protocol`, `tone-soul-integrity`, `tone-soul-integrity-tonesoul-xai`,
  `tonesoul-codex`, `ai-soul-spine-system`, `governable-ai`, `Genesis-ChainSet0.1`, `AI-Ethics`.

**Separate / parallel work** (not the ToneSoul governance core — reference or independent
experiments, not part of the ToneSoul entry narrative)
- `openclaw`, `star-office-ui`, `airi`, `hermes-agent`, `claw-code`, `med-de-id`, `WFGY`,
  `qwen3.5`, `system-prompts-and-models-of-ai-tools`, `Antigravity-Skills-Chronicle`.
  (`elisa` has no description and is not classified here.)

> Classification reflects `gh repo list` state on 2026-06-19 and may drift. Re-enumerate
> (`gh repo list <user>`) before trusting it. Lineage / separate calls for repos not opened in
> detail are best-effort from name + description, **not a content audit**.

## Footnote

This document is a front-door, not an authority. Verify each item against the canonical source it
points to. It was drafted to make the project legible to an outside reviewer (see
`CALL_FOR_REVIEW.md`) — its success is being **checkable**, not being believed.
