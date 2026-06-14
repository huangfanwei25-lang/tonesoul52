# ToneSoul — Judgment-Readiness Remediation Roadmap (P4)

> **P4 of the Judgment-Readiness Program (autonomous, 2026-06-15).** Synthesizes
> P1 (simulated judgment — `docs/status/judgment_readiness_findings_2026-06-15.md`),
> P2 (architecture legibility — `docs/architecture/architecture_legibility_2026-06-15.md`),
> and P3 (academic grounding — `docs/research/tonesoul_in_the_literature_2026-06-15.md`) into one
> prioritized, evidence-labeled action list. Sequenced by **leverage on the real
> goal**: *would a serious external party take this seriously, and can the honest
> core be absorbed by the field* — **not** by how impressive it looks.

## The one-sentence finding

All three phases independently converge on the **same** conclusion: **the honesty
is the product; the public framing oversells it.** Every judge protected the
self-grading enforcement ledger and refused to attack the candor; every judge
attacked the gap between that honest interior and hero words like *"categorical
refusal"* / *"perspectives debate"* / *"blocked or rewritten"*. **So the entire
roadmap is honesty-restoring, not shine-adding. The single highest-leverage move
is to make the public face as honest as the interior already is.** Inflation is
exactly what the judgment would kill — and we are 1–2 careless README edits away
from the "fantasy repo" dismissal trigger (≈70 contract docs over ~5 wired modules).

## Evidence ladder (used below)

`E1` runtime-enforced + tested · `E2` runtime present, shallow/lexical sensor ·
`E3` external/abstract-level · `E4` aspirational/designed-not-built ·
`E5` named-but-mechanism-weaker-than-name · `E6` claim only.

---

## Tier 0 — Landed this overnight (factual corrections, safe, done)

Pure stale-metadata corrections — the metadata was provably *wrong*, fixing it is
honesty-increasing and reversible. Verified stale by P1.

| # | Fix | Was | Now | File |
|---|---|---|---|---|
| T0.1 | Axiom 3 enforcement note | "hardcoded literal … `governance_gate_score` is unread" (as_of 2026-06-13) | reads `SOUL.risk.governance_gate_score` (since #95 / 1eb4006); keeps the lexical-sensor + record-only caveat; as_of 2026-06-15 | `AXIOMS.json` |
| T0.2 | Axiom enforcement count | "5 partial, 2 referenced, 2 aspirational" | "8 partial, 1 referenced, 0 aspirational" (marks the old line stale) | `docs/SUCCESSOR_MAP.md` |
| T0.3 | de_escalation docstring | "live-apply … kept separate" | live-apply now wired (#104) via `de_escalation_framing` append; states what is *still* not done (generative rewrite, zh-TW sensor) | `tonesoul/governance/de_escalation.py` |

These are this session's own family error (trusting a stale "X is current" record —
SUCCESSOR_MAP §0 says it has bitten the repo 5+ times). The audit caught a 6th. Fixed.

---

## Tier 1 — Highest leverage, AWAITING YOUR REVIEW (public-face honesty downgrades)

**This is the #1 finding (hit by all 5 judgment lenses).** These edit the README
hero — your public face, which you own (you just decided #75). I did **not**
auto-edit them overnight; they go in an open PR with recommended wording for your
call. Each is a *downgrade* of an over-claim to match runtime — the safe direction.

| # | README claim (E-now) | Runtime reality | Recommended wording | Finding |
|---|---|---|---|---|
| T1.1 | "**categorical** refusal of forbidden claim classes … categorical, not probabilistic" (E6) | `guardian._detect_overclaim` returns CONCERN (conf 0.8), not OBJECT; BLOCK needs OBJECT>0.7; so forbidden-class claims **ship with a dissent annotation**, not refused. Paraphrase-permeable, EN-only. | "**surfaces** forbidden-class assertions as a Guardian CONCERN that can route to REFINE — keyword-level, analytical-hedge-exempt, paraphrase-permeable; it does **not** hard-block them." | S1 |
| T1.2 | "five council perspectives evaluate **independently** … **debate** … builds **external** machinery" (E5) | 5 keyword/regex matchers over the *same* draft string; no inter-perspective comms, no 2nd LLM call; the substrate-separated verifier is default-OFF + Mock (Phase D deferred). | "five **lexical voters** over a single draft." Reserve "independent/externalized" for the verifier **only after Phase D ships**. | S3 |
| T1.3 | "blocked or **rewritten** with audit traces" (E4-as-present) | No generative rewrite path. BLOCK = fixed canned string (`reflex.py:511`); `epistemic_labeler.py:58` "we do not auto-rewrite." | "blocked or **replaced with a refusal message**." | S9 |
| T1.4 | "Resonance Detection **distinguishes genuine understanding from empty agreement**" (E5) | cosine-delta threshold (`resonance.py:60-110`) wearing an E5 name. | "classifies cosine-delta convergence between consecutive turns." | S4 |
| T1.5 | stale facts: "7652 tests collected" vs "3,137 passing"; "master has no branch protection yet" | branch protection **is** live (gh api: required Test Python 3.12 + Commit Attribution); test count inconsistent within one file. | reconcile the test number; "master is branch-protected (required checks + up-to-date)." | S-stale |
| T1.6 | Axiom 6 (P0 "safety overrides everything") presented as enforced | BLOCK short-circuit is real, but detector = 3 EN + 6 zh-TW literal phrases; `llm_judge_eval` measures harm-recall-paraphrase **0.0**. | add `enforcement_scope`: "P0 intent; sensor lexical (3 EN + 6 zh-TW), paraphrase-permeable; semantic gate is open work." | S2 |

**Why not just build the hard-block to make T1.1 true?** Because a hard-block still
leaves the paraphrase gap — that would be a *second* over-claim. The honest fix is
the wording, not a slogan-justifying feature. (P1's explicit guidance.)

---

## Tier 2 — Legibility (P2, zero behavior change) — partly landable, partly review

The drift is concentrated in **markerless parked code** + **naming collisions**.
Doc-only items are safe; the multi-file marker sweep should be one reviewable PR.

- **T2.1 (doc-only, safe):** Add to SUCCESSOR_MAP §6 a dormant-subsystems table —
  `corpus/`, `council/{atomic_claims,convergence}`, `inter_soul/*`, root `gse/`,
  `stale_rule_verifier`+`memory/freshness` (reachable only via the dormant dream
  loop). Closes the silent-drift gap §6 itself warns about. **E1-doc.**
- **T2.2 (multi-file, one PR for review):** Add dormancy markers (`# DORMANT: …`,
  parity with the existing `# YSS-STATUS: unwired`) to the marker-less parked
  modules above + the 2 honesty sensors. Comments only; all verified zero non-test
  importers. Stops the recurring re-discover-cold → wrong-delete/rebuild failure.
- **T2.3 (metadata-only):** Fix contradictory `__ts_purpose__` in `yuhun/dpr.py`
  ("Dense Passage Retrieval: semantic retrieval" → "Dynamic Priority Router") —
  the code is a router, not retrieval; an auditor trusting the annotation mis-describes it.

## Tier 3 — Positioning (S8) — AWAITING YOUR REVIEW (public-facing)

- **T3.1:** `docs/research/tonesoul_in_the_literature_2026-06-15.md` exists (P3, 25
  verified citations, ANCHOR/CHALLENGE per axis, E3-caveated; landed as research
  scaffolding next to the houtian references). Decide whether to **promote** it to a
  top-level public-facing positioning doc, or keep it research-scoped. **Your call.**
- **T3.2:** Add a short `## Related work` block (or `docs/RELATED_WORK.md`) to
  README/DESIGN citing the anchors and stating the **narrow** novelty explicitly:
  *"self-grading enforcement reconciliation + cross-session accountability ledger
  in a single-creator deployment"* — not "epistemic defense" as if unprecedented.
  Public-facing → your call.

## Tier 4 — Structural decisions (owner-gated, wire-OR-archive, never delete-on-sight)

Per SUCCESSOR_MAP discipline these are **decisions, not cleanups**. Left entirely
for you; P2 ranked them by (safety × surface reduction).

- **T4.1 `corpus/`** — largest coherent dead surface (zero non-test importers, HIGH
  unreachable / only MEDIUM safe-to-delete: it's a tested privacy-first consent+storage
  unit, a "forgotten gem"). **Proposal: mark dormant + map it; wire-or-archive is yours.**
- **T4.2 YUHUN dead hook** (`unified_pipeline.py:190-210`, `_get_dpr`/`_get_context_assembler`,
  zero call sites) — **wire** (close 6a20ecf as intended) OR **remove** the getters.
  Do *not* do both; do *not* silently remove if you intended to wire.
- **T4.3** Off-thesis subsystems (`market`/台股, half-dismantled `inter_soul`) — archive
  out of the canonical tree to shrink the doc/code-surface dismissal trigger (S4).
- **T4.4** Consolidate the two `Hippocampus` impls (both live — preserve the corrective path).
- **T4.5** Naming-collision renames (`evolution`×2, `corpus`×2, `yuhun`×3, `yss`) —
  legibility benefit MEDIUM, execution risk HIGH (touches live API + PR1 packaging guard).
  Treat as ARCHITECTURE_BOUNDARIES work, not cleanup.

## Tier 5 — Research depth (turns "methods paper" → "results paper") — sequenced, not urgent

These are the only items that change what ToneSoul *can claim*, and all are
honestly blocked on resources, not will. Pre-register before running (avoid the
under-powered-null trap P1/the spark-measurement memory both flag).

- **T5.1 Semantic sensors (E2→E1 on the load-bearing axis).** Replace/augment the
  lexical vow + POAV + overclaim detectors with an embedding or small-LLM-judge gate.
  The `llm_judge_eval` pilot (n=36, 1 model — **label it pilot everywhere**, S7)
  shows the direction; productionizing it is the single biggest credibility upgrade.
  Honest cost: latency + a model dependency + a real benchmark with a human gold set.
- **T5.2 Ship Phase D** (Haiku-backed `independent_verifier`, currently Mock + default-OFF)
  so "externalized evaluation" becomes *true* — then T1.2 wording can be upgraded, not before.
- **T5.3 The spark / 後天 question** — measured null 3× at local scale, admittedly
  under-powered. Promote nulls to a first-class "what we measured and it came back
  null" section; **pre-register** the sharper re-test (held-out LLM-judge stance
  metric, multi-trial, larger model) the stance doc outlines. The deep Layer-2
  (weight-level fine-tune on the system's own scaffolded experience) is **unbuilt —
  needs compute not available at this scale**; it is the only place the deep claim
  can be tested. A clearly-labeled honest null is more publishable than a dressed-up positive.

---

## What absorbable unit to lead with (P1 + P3 agree)

If the field absorbs anything, it is **the enforcement-reconciliation practice**:
a constitution (`AXIOMS.json meta.enforcement_reconciliation`) that publicly grades,
per-axiom with file:line provenance, how much of each of its own commitments the
runtime actually keeps — and **refuses to fabricate metrics it cannot measure**
(Axiom 5 left "referenced" on purpose). Three judges called this "genuinely novel
as a governance-repo *practice*." Lead with that. It is liftable without lifting the
ToneSoul vocabulary — which is exactly the absorption test.

## Sequencing (by leverage)

1. **Tier 0** (done). 2. **Tier 1** README honesty PR (your review — biggest single
leverage). 3. **Tier 2.1/2.3** doc+metadata legibility (safe). 4. **Tier 3.2**
related-work + narrow-novelty framing (your review). 5. **Tier 2.2** marker sweep PR.
6. **Tier 5.1/5.2** semantic sensors + Phase D (the credibility upgrades). 7. **Tier 4**
structural decisions, one at a time, your call. 8. **Tier 5.3** pre-registered spark re-test.

> No item in this roadmap makes a sensor semantically stronger than it is or claims
> a capability that isn't built. Every Tier-1/2 item *reduces* a claim or *adds a
> caveat*. That is the point: the way to survive judgment is to be the repo that
> already audited itself harder than the judges did.
