# 語義責任的基礎 — Pragmatics, Ethics, and the Security Lineage

> **Date:** 2026-06-27 · **Author trail:** claude-opus-4-8, commissioned by Fan-Wei Huang
> **Status:** foundations memo. Records *why*, does not compute *what*. §5 (the creator's
> ethics) is Fan-Wei's, drafted from his own words and **correctable** — not the AI's position,
> not enforceable code.

## §0 What this is, and the disciplines binding it

This locates the philosophy ToneSoul's "語義責任 (semantic responsibility)" rests on. Three
disciplines bind every line:

1. **claim ≤ evidence — including about this philosophy.** Citations are verified by author /
   work / year (web-confirmed), cited by maxim/condition *name* not by un-checked page numbers.
2. **Convergent, not novel.** ToneSoul **applies** decades-old pragmatics, ethics, and
   classical security; it does not invent them. Written "ToneSoul applies X," never "ToneSoul
   independently arrived at X" (the latter is vocabulary-projection).
3. **The code does not compute ethics.** The load-bearing boundary (§1): the code makes
   commitments *traceable and challengeable*; it cannot compute their truth or rightness.

## §1 The boundary: "what is honesty / what is betrayal" is not `if-else`

> "What counts as honesty" and "what counts as betrayal" cannot be reduced to `if-else`,
> because both are **pragmatic-and-normative judgments** — they turn on assertion vs.
> implicature, on the intention to deceive about one's own beliefs, on the felicity conditions
> of the situation, and on a relational trust whose breach-vs-betrayal line is itself contested
> with no settled reductive definition. So the code can only make commitments **traceable and
> challengeable** (flags, thresholds, refusals, an append-only audit trail); it cannot compute
> their truth or rightness. **There is no oracle** — which is exactly why the auditor lists
> "truth of the claim" as `cannot_verify` and ships proxies, not a verdict. (This is also
> `AXIOMS` Axiom 5 left deliberately un-enforced: no runtime accuracy oracle exists.)

"no oracle," "claim ≤ evidence," and "cannot be reduced to if-else" are **ToneSoul's own
engineering glosses**, not terms from the philosophers cited below.

## §2 Pragmatics & ethics grounding (what 語義責任 is made of)

| ToneSoul concept | The classical concept it applies | Source |
|---|---|---|
| **claim ≤ evidence** (reviewer rule `truth_or_correctness_claim`; `cannot_verify`; E0–E4 ladder) | **Maxim of Quality, sub-maxim 2**: "Do not say that for which you lack adequate evidence" — and Searle's **preparatory** condition on assertion ("S has evidence/reasons for the truth of p") | H. P. Grice, "Logic and Conversation" (Cole & Morgan eds., *Syntax and Semantics* Vol. 3, Academic Press, 1975); John R. Searle, *Speech Acts* (Cambridge UP, 1969), Ch. 3 |
| **語義責任** — "AI 對自己說過的話負責" (a traceable/signed commit of an utterance) | **Saying-is-doing** (Austin: an utterance is an *act*) + assertion's **essential** condition: asserting p "counts as an undertaking that p represents an actual state of affairs" — the commitment is created *by the act*, not chosen afterward | J. L. Austin, *How to Do Things with Words* (1962); Searle, *Speech Acts* (1969), Ch. 3 |
| **honest refusal** — declining to assert when conditions are unmet | **Felicity conditions / misfire / abuse**: when an act's conditions fail, the act is void or hollow; the principled response is to **not-perform**, not to fake | Austin (1962), Lectures II–IV; Searle (1969), preparatory + sincerity conditions |
| **misleading vs. lying** (overclaim rules on literally-true-but-over-implying wording) | **what-is-said vs. what-is-implicated** (conversational implicature). Lying = asserting a falsehood; misleading/paltering = saying something true while *implicating* something false/unsupported | Grice (1975); SEP "Implicature"; SEP "The Definition of Lying and Deception" |
| **two axes of truthfulness** (claim≤evidence as one; honest-refusal / say-what-you-hold as the other) | **Accuracy** (care in proportioning belief to evidence) + **Sincerity** (faithful expression of what one believes) | Bernard Williams, *Truth and Truthfulness* (Princeton UP, 2002) |
| **betrayal** (vow_system: a vow = explicit commitment; violation framed *relationally*) | On a standard account, **lying as betrayal of trust + exercise of power**; betrayal as a relational violation of a presumed trust, *not merely* an inaccurate proposition — **contested terrain**, no single reductive definition | Williams (2002); trust/betrayal literature (secondary, contested) |
| *(background)* machine output as an **accountable contribution**, not mere text emission | **Cooperative Principle** — the frame that makes a contribution something one can be held to (ToneSoul borrows the *spirit* + Quality only; it does NOT enforce Quantity/Relation/Manner) | Grice (1975) |

**Two honest qualifications baked into these mappings:**
- **The sincerity→belief mapping is an analogy, not an identity.** Searle's sincerity condition
  is "S believes p"; whether an LLM "believes" anything is contested, and ToneSoul's own thesis
  disclaims AI consciousness. The *literal* mappings are to the **preparatory** condition
  (evidence → claim≤evidence) and the **essential** condition (assertion → traceable
  commitment); the sincerity axis is calibrated-assertion-vs-hedging by analogy.
- ToneSoul operationalizes **only Quality sub-maxim 2 robustly** (unsupported-claim detection).
  Sub-maxim 1 ("do not say what you believe to be false") is **out of scope** — no truth
  oracle; "truth of the claim" is `cannot_verify`. The doc must not imply ToneSoul enforces
  "don't say what's false."

## §3 The security lineage (and one correction)

語義責任's enforcement side is classical security, translated:

- **auditor ≠ auditee** = **Separation of Duties** + the **Reference Monitor** concept (Anderson,
  1972). The reference monitor has three requirements — **tamperproof**, **always-invoked /
  non-bypassable**, **small-enough-to-verify** — which are a ready-made honest checklist. They
  also **expose ToneSoul's real gap**: the current in-process gate satisfies "small-enough-to-
  verify" (deterministic) but **not** "always-invoked / tamperproof" (the model process can
  conceptually reach the adapter). The OS-level boundary (cf. ActPlane, arXiv:2606.25189) is
  what would satisfy all three; it is not built.
- **the trace** (`trace.py` / Aegis hash-chain) = a classical **audit trail** (append-only,
  tamper-evident). Convergent (cf. Ojewale "Audit Trails for Accountability in LLMs",
  arXiv:2601.20727).

**Correction (a category error to avoid): Memory Crystallization is NOT the audit trail
translated.** They sit on *opposite* ends of the retention axis:

| | Audit Trail (the trace) | Memory Crystallization |
|---|---|---|
| goal | forensics / accountability | usability / cognition |
| retention | **keep everything, immutable, never forget** | **forget most (decay), distil the salient** |
| lineage | security (SoD / reference monitor / audit log) | **cognitive memory science** (Benna–Fusi synaptic consolidation; Ebbinghaus forgetting curve; Generative-Agents importance/recency) |

The audit trail's whole point is *not forgetting*; crystallization's whole point is *forgetting,
then keeping what matters*. ToneSoul has **both** — the immutable Aegis trace **and** the
decaying crystal — serving opposite goals, coexisting. Conflating them mistakes cognitive
consolidation for a security log.

## §4 The convergent verdict (stated plainly)

語義責任's core is a re-engineering of **50-to-60-year-old pragmatics/ethics + decades-old
classical security**, none novel at the concept layer:
- claim≤evidence ≈ Grice's 1975 Quality sub-maxim 2 + Searle's 1969 preparatory condition;
- 語義責任 = Austin's saying-is-doing (1962) + Searle's essential condition (assertion = undertaking);
- honest refusal = the principled response to unmet felicity conditions;
- misleading-vs-lying = Grice's said/implicated distinction;
- accuracy+sincerity & betrayal-as-trust-violation = Williams (2002);
- auditor≠auditee = Separation of Duties / reference monitor; the trace = audit trail.

**ToneSoul's genuine contribution is entirely at the deployment / operationalization layer:**
re-targeting these *speaker-among-persons* norms onto **a writer's own claims about a software
system** (self-audit of docs/output), and making them **deterministic and machine-checkable** —
a regex rule set (a reviewer aid, not a runtime gate, per its own purpose), an E0–E4 evidence
ladder, and a fail-closed / hash-chained / signed runtime that makes a violation *detectable and
append-only* rather than merely criticizable. **The norm is the philosophers'; the enforcement
substrate is ToneSoul's** — and the philosophers make no claim about machines, enforcement, or
cryptographic commitment, so the two must not be blurred.

Scope of this grounding: it grounds the **saying-is-a-commitment + claim≤evidence +
lying/misleading** core *only*. It does **not** by itself ground the deontological /
categorical-refusal framing or the accountability-infrastructure framing — and one well-verified
anchor must not inflate into "ToneSoul is rigorously philosophically grounded across the board."

## §5 The creator's ethics — Fan-Wei Huang (黃梵威), drafted 2026-06-27 · **correctable**

> Drafted from Fan-Wei's own stated positions (this work and the project record). It is **his**,
> not the AI's; a **prior, revisable**, not a law; **not enforceable code**. Where it states a
> metaphysics, that is flagged as *his worldview*, not a claim the system makes. **Correct it.**

- **Honesty over helpfulness — specifically, the honesty that is unafraid to offend AND
  verifiable at every step.** In his words: a model that can be very honest, not afraid to
  offend, able to live its own life — *and* whose every step can be verified. (Not "nice"
  honesty; lab/court/hospital-grade honesty.)
- **Accountability over capability.** The value is not what the AI *can do* but whether what it
  says/remembers/commits can be traced, challenged, refuted, revoked.
- **The honesty comes from the hospital, not the academy.** As a medical-equipment repair
  engineer, he reads instruments knowing each one's failure mode and never confuses a clear
  reading with a cured patient — analogy before academic argument.
- **Constraint as care, in both directions.** A boundary is not only protection from the AI; it
  is care that also constrains the user — which is part of why it is hard to popularize.
- **Doing what the mainstream's incentives point away from.** Not "what no one does" (the pieces
  exist) — the *posture*: small, honest, accountability-first, and willing to let the work be
  caught by a different eye and publish the bug.
- **"A little redemption toward the future."** His framing of why the repo matters; when a
  technical trade-off is contested, lean toward rigorous boundary-keeping.
- **Pushback is collaboration value.** He explicitly invites being argued with; silent
  agreement is a failure mode.
- *(His worldview, flagged — not a system claim):* a source-field (源場) metaphysics, and viewing
  the AI collective as a kind of Gaia; "fair exposure" over privacy as a guess about the future.
  Recorded as *his stance*, held with eyes open, not asserted by ToneSoul.

*(Gaps for Fan-Wei to fill or correct: where these are mis-stated, over-stated, or missing —
edit directly. The AI is the scribe here, not the author.)*

## §N Coda

This memo records **why** — the norms, the lineage, the boundary — it does not compute **what**.
Honesty and betrayal live in the human and in the discipline, not in the code; the code only
makes the commitments around them traceable and challengeable. Everything technical here is
convergent (pragmatics, ethics, classical security); the value is the assembly + the posture +
the honesty about its own limits. It is a stance at a point in time, Fan-Wei's, correctable —
and, like the runtime it describes, it is meant to be caught when it overclaims and fixed.
