# Episodic-Memory Claims — Provenance (Isnād)

> Purpose: the verifiable coordinates behind ToneSoul's "memory is not a similarity cloud"
> claims, and the companion appendix for the public article on the same theme. This file
> exists because the project demands that every AI claim expose its time-space coordinates;
> so the project's own claims expose theirs here.
> Last Updated: 2026-06-18
> Status: hand-authored evidence appendix (reference). Not architecture canon. Verify against
> the cited sources and against this repo's actual files — do not take this page on trust.

## The one-line position

Non-semantic-similarity memory retrieval (episodic / temporal / affective-salience /
surprise-or-error-cued / event-segmented) is **convergent, not novel** — a real, named,
actively-growing research direction with built systems and benchmark results. ToneSoul is a
small, honest instance of that wave, not its inventor. Its differentiator is deployment-level
**accountability**, not a new retrieval mechanism.

## Verified claims and their coordinates

Sources below were web-fetched and adversarially verified (2026-06-18 deep-research,
2/3-to-kill); confidence/caveats are stated, not hidden.

**Cognitive science**
- Retrieval is cue/context-triggered, not a similarity scan over all items — Tulving &
  Thomson (1973) *Psychological Review* 80:352–373; Anderson (1983) spreading-activation
  (ACT-R). Caveat: encoding-specificity's *mechanism* is debated (cue-distinctiveness vs
  cue-overlap); the descriptive finding stands.
- Recall is reconstructive and re-writes the memory (reconsolidation) — Nader, Schafe &
  LeDoux (2000) *Nature* 406:722–726. Caveat: destabilization often requires a
  prediction-error/mismatch; boundary-condition/replication literature exists.
- Flashbulb/emotional memory is special only **subjectively** (vividness, confidence), NOT
  in objective accuracy — it decays at the same rate as everyday memory — Talarico & Rubin
  (2003) *Psychological Science* 14(5):455–461; (2007) *Applied Cognitive Psychology*. (This
  is the strongest-verified, 3-0.)

**Cultural memory** (filed by place / narrative / ritual / significance, not similarity)
- Aboriginal songlines & relational knowledge systems — PACJA art. 143975. Jack Goody (oral
  cultures) — Princeton chapter PDF. Lynne Kelly, *The Memory Code*. Use the *indexing
  structure* only; do not import the sources' relational-ontology/mystical phrasing as a
  mechanism.

**AI — this has already been tried (convergent, not novel)**
- Generative Agents: memory stream = recency + LLM-scored importance/salience + relevance —
  Park et al., UIST 2023, arXiv:2304.03442. (Its recency factor is 0.995 — see correction below.)
- EM-LLM: Bayesian-surprise event segmentation + two-stage (similarity + temporal-contiguity)
  retrieval — Fountas et al., ICLR 2025, arXiv:2407.09450 / em-llm.github.io. Honest magnitude:
  beats the strong InfLLM baseline by only ~**+0.2 average**; its large wins are against a
  generic RAG embedder, so name the baseline when citing a number.
- Surprise/prediction-error-cued memory writing ("discrepancy mobilizes memory") — NEMORI,
  arXiv:2508.03341; D-MEM, arXiv:2603.14597. Caveat: **preprints, effectiveness
  author-reported**; one D-MEM novelty claim did **not** survive our adversarial check
  (internal, not peer review). Cite as "direction exists", not as settled result.

**ToneSoul itself** (verify line-by-line in this repo)
- Memory decay: `tonesoul/memory/decay.py` — `HALF_LIFE_DAYS = 7.0`, `DECAY_CONSTANT =
  ln(2)/7`, applied as `exp(-DECAY_CONSTANT * elapsed)`. A 7-day half-life, exponential.
- The "surprise/error-cued recall" exists **but is dark**: `tonesoul/memory/hippocampus.py`
  header records, verbatim, that `recall` / `recall_corrective` are *tested-but-NO-live-caller
  (parked RFC-012); the class is never instantiated at runtime*, and the default-ON corrective
  branch computes a ~zero error vector in the no-rewrite case (silent near-no-op). I.e.: the
  instinct is built, not lit, and never honestly measured.

## Correction (the point of this page)

An earlier framing claimed ToneSoul's `decay.py` uses **0.995, "the same number" as Generative
Agents, an "independent convergence."** That is **wrong** and is corrected here:
- `decay.py` does **not** use 0.995 — it uses a 7-day half-life (constant ≈ 0.099), a different
  parameterization and a different form.
- The 0.995 in this repo lives in `tonesoul/tension_engine.py` (`persistence_decay = 0.995`) —
  a *tension*-persistence mechanism, **not** memory recency.
- "0.995" was a concept that floated in from earlier informal writing, not a repo fact. The
  real, checkable shared idea is narrower and honest: both Park's system and ToneSoul choose
  **decay-over-time** rather than **pure similarity** — not the same constant.

This correction is the method working on its own author: a claim, when forced to its
coordinates, was found unsupported and fixed. That demand applies to the project's own claims
and its collaborating AI's claims, not only to others'.

## How to verify

Do not take this page on trust. The repo is the Isnād anchor:
<https://github.com/Fan1234-1/tonesoul52> — read `tonesoul/memory/decay.py`,
`tonesoul/memory/hippocampus.py`, `tonesoul/tension_engine.py`, `tonesoul/council/`, and
`provenance_chain` directly. Where this page and the code disagree, the code wins.
