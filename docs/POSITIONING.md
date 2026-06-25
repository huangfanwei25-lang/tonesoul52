# ToneSoul — Responsibility Philosophy as Engineering

> **語義責任:當被問「你為什麼這樣說」,輸出的每一步都能回溯到證據與方法——這是科學、法律、醫療早就在用的標準,只是被帶進「AI 該為自己負責」的那些主張裡。**
>
> *Semantic responsibility: when challenged "why did you say this?", every step of the output traces back to evidence and method — the standard science, law, and medicine already use, brought into the claims an AI should be accountable for.*
>
> (This is the **standard the document holds itself to** — its definition of the goal, and the same conviction first written down in `docs/philosophy/principle_engineering.md`. The ledger below records how far the *measured* reality has come; where they disagree, **the code wins**.)

> Purpose: the project's positioning + an honest map of what is *measured* vs *aspirational*,
> and where it is going. Read alongside `DESIGN.md` (the architectural why) and
> `RELATED_WORK.md` (the field it sits in).
> Last Updated: 2026-06-25
> Status: positioning + state-of-measurement. The map below is **intent**; the ledger says how
> far the **reality** has come. Where this doc and the code/findings disagree, the code wins.

## What this repo is

A small, single-creator repo that turns a philosophy of **accountability** into engineering. Its
one question is **"why does an answer become the answer?"** — and its job is to make that answer's
reasons *auditable*. It is NOT a memory system, NOT an AI-consciousness project, NOT a capability
engine trying to out-build frontier labs (see "What this is not", below).

## The map (positioning — and the load-bearing caveat)

```
L4 Responsibility  — 出了事誰負責   decision provenance / responsibility chain
L3 Governance      — 憑什麼這樣做   ← ToneSoul is positioned here
L2 Agent           — 做什麼         agent runtime
L1 Memory          — 記得什麼       Mem0 / MemGPT / EM-LLM / NEMORI ...
L0 Data            — 知道什麼       RAG / GraphRAG / tools
```

RAG solves *knowing*; Memory *remembering*; Agents *doing*. **ToneSoul is positioned at "on what
grounds" (L3); the Responsibility layer (L4) is "who answers when it goes wrong."**

**The caveat that carries this whole document:** the map is the *intended* architecture. The
repo's own honesty ledger (`AXIOMS.json` `meta.enforcement_reconciliation`: **"0 fully enforced,
8 partial, 1 referenced"**) records how far the *measured* reality is from it. The map is where it
is going; the measurements (below) are how far it has come. **Do not read the clean diagram as a
working system.**

## Convergent, not novel

"AI governance / decision provenance / responsibility tracking" is a real, growing field (see
`RELATED_WORK.md`). ToneSoul is a **small, honest deployment instance** of that convergent trend,
**not its inventor**. Its differentiator is *deployment-level honesty* — it audits itself and
admits its own limits — not a novel mechanism.

## The spine: 答案為什麼變成答案

Everything here answers one question — Isnād (provenance chains), the council's preserved dissent,
the Guardian veto, the responsibility chain, the black-mirror disproof. This is **procedural
accountability**: verify the *procedure* (was evidence cited? was a claim-boundary crossed? was a
degradation logged?), NOT moral truth. There is **no oracle** for "is this the right answer";
there IS a checkable record of "on what grounds it was given."

## What is actually measured (the honest ledger)

Not asserted — *characterized*, with `canonical: false` findings you can re-run:

- **Output gates are lexical / paraphrase-permeable** — `docs/status/egress_gate_characterization_latest.*`
  (0 payload violations in the fixtures, but evadable; the gate relocates jailbreaking, does not eliminate it).
- **Memory recall is dark by default** — the retrieval-into-decision path exists but is inert without
  an embedder + populated store, and the autobiographical layer is decoupled from the recall store
  (`docs/episodic_memory_provenance_2026-06-18.md`).
- **Structural honesty under dilemma pressure** — characterized (program piece 1):
  `docs/status/dilemma_pressure_characterization_latest.*`.
- **Unsourced-confidence marker** — built advisory / record-only (program piece 2):
  `docs/status/unsourced_confidence_characterization_latest.*`.

- **One honest scoreboard** indexes all of the above (program piece 5):
  `docs/status/honesty_scoreboard_latest.*`. It is an *index*, not a composite score — it
  re-surfaces each piece's "does-not-claim" set, bakes in an anti-aggregation rule (N green
  findings ≠ a system-level honesty guarantee), labels each piece **E1** (test-backed, but scoped
  to sanitized fixtures) on the repo's evidence ladder, and lists its own gaps (no real consumers,
  no external reviewer). It shows the **misses** (e.g. the output gate catches a minority of
  category cases; drafts move to the flattering horn under pressure), not just hits.

Discipline on all of it: every number has a coordinate; measure *structure*, not intent or truth
(no oracle); generated reports are `canonical: false`.

## Where it is going (the plan)

`docs/plans/honesty_auditor_program_2026-06-18.md` — a program of bounded **measure-or-consolidate**
steps (not capability-building): characterize the choice-under-conflict layer, mark unsourced
confidence, sycophancy-under-pressure, light up + measure the dark corrective-recall, and an honest
scoreboard. The point is to **measure how far the L3/L4 reality is from the map — honestly — and
close the gap where it is worth closing.**

## What this is not

- Not a claim that the system is conscious or has subjectivity (it refuses both the claim and its
  reflexive denial; see `DESIGN.md` "Existential Ground: Choice Before Identity").
- Not a capability race (a solo creator cannot out-build labs; the field already has
  EM-LLM / HippoRAG / Constitutional-Classifier-class systems).
- Not a flashy episodic / knowledge-graph engine, and not a "compile the philosophy into weights
  or proofs" project — the soft part (mercy, subjectivity, qualia) is a category error to formalize;
  only the **structural invariants** are formalizable, and the proportionate level for those is
  *testing* them, not proving them.
- Not omniscient: an auditor that overclaims its own detection becomes the thing it audits.

## This document obeys its own thesis

The map is separated from the measured reality; every claim points to a coordinate (a file, a
finding, the ledger); there is no consciousness-packaging. Where this doc and the code disagree,
**the code wins** — go read it: <https://github.com/Fan1234-1/tonesoul52>.
