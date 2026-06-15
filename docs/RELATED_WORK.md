# Related Work

## 0. Read this first

ToneSoul is a **deployment instantiation** of a convergent trend in AI
governance and accountability — not a novel thesis. The problems it addresses
(provenance-as-accountability, deontological refusal, runtime gating, machine
honesty, governance and data sovereignty) were identified and worked on by
others before ToneSoul existed, and most remain open. This page exists to
locate ToneSoul honestly inside that field, **not** to argue it is correct.

The evidence level for every entry below is **E3: title and abstract only.**
We have not reproduced these results, audited their methods, or in most cases
read the full text. Listing related work does **not** raise our confidence in
ToneSoul's own claims — **aggregation is not verification.** A field full of
papers on a problem is evidence the problem is real and hard, not evidence that
ToneSoul solved it. None of the work below "validates" or "converges toward"
ToneSoul; several entries directly **challenge** its core design choices, and
those challenges are kept in front rather than buried.

## 1. Where ToneSoul sits

The honest framing: structured, inspectable **accountability artifacts** —
rather than reliance on self-reported good behavior — are a recurring theme
worked on independently across roughly five research axes, **predating
ToneSoul**. This is a pre-existing research direction, *not* a movement toward
ToneSoul; the resemblance is partly ToneSoul's own vocabulary projecting onto
that work at abstract-level reading. ToneSoul is one specific, opinionated
*deployment* of that pre-existing direction. Its differentiation is
**deployment-level only**:

- single-creator, end-to-end, one coherent vocabulary instead of a committee standard;
- explicit *named* vocabulary (vows, tension, drift, axioms) attached to running code;
- a shippable `pip`-installable artifact rather than a paper or a principle set;
- honest evidence labels on its own outputs (including this document).

That is the whole contribution. ToneSoul does **not** claim a new theory of
alignment, a safety guarantee, or an empirical result. Where its framing has at
times outrun what the code measures, the gaps are stated in §3.

The strongest objections to ToneSoul's design are, bluntly:

- **Deontological / categorical refusal may itself be unsafe** (D'Alessandro, B2).
- **A system that audits itself is the textbook audit-washing structure** (Goodman & Trehu, A5).
- **Same-model self-correction does not reliably work** (Huang et al., C4; partial: Gou et al., C5).
- **Explicit principles stay symbolic without enforcement** (Lin, E4; Findeis et al., E5).

These are not footnotes. They are the load-bearing critiques, and ToneSoul does
not currently refute any of them.

## 2. Anchors and challenges, by axis

Each entry is: citation + URL + role (ANCHOR / CHALLENGE / CONTEXT) + one honest
sentence. "ANCHOR" means *the problem is real and others work on it* — never
*this validates ToneSoul*.

### Axis A — Accountability infrastructure

- **ANCHOR** — Gebru, Morgenstern, Vecchione, Vaughan, Wallach, Daumé III,
  Crawford, "Datasheets for Datasets" (2018/2021).
  <https://arxiv.org/abs/1803.09010>
  Establishes provenance-as-accountability: every dataset ships a record of its
  motivation, composition, and intended use — the documentation discipline
  ToneSoul borrows for runtime traces.
- **ANCHOR** — Mitchell, Wu, Zaldivar, Barnes, Vasserman, Hutchinson, Spitzer,
  Raji, Gebru, "Model Cards for Model Reporting" (2019).
  <https://arxiv.org/abs/1810.03993>
  Structured disclosure of intended use, evaluation conditions, and limitations
  is a precedent for attaching honest self-description to a system.
- **ANCHOR** — Raji, Smart, White, Mitchell, Gebru, Hutchinson, Smith-Loud,
  Theron, Barnes, "Closing the AI Accountability Gap: Internal Algorithmic
  Auditing" (FAT* 2020). <https://arxiv.org/abs/2001.00973>
  Per-stage documents form an end-to-end internal audit grounded in stated
  values — structurally similar to what ToneSoul produces, and a reminder that
  internal audit is a known, pre-existing practice.
- **CHALLENGE** — Birhane, Steed, Ojewale, Vecchione, Raji, "AI auditing: The
  Broken Bus on the Road to AI Accountability" (IEEE SaTML 2024).
  <https://arxiv.org/abs/2401.14462>
  Only a subset of audit studies translate into accountability outcomes (the
  paper's finding); the takeaway for ToneSoul — *our synthesis, not the paper's
  wording* — is that a tamper-evident chain is necessary but nowhere near
  sufficient, so the hash-chained traces inherit exactly this limitation.
- **CHALLENGE** — Goodman, Trehu, "AI Audit-Washing and Accountability"
  (GMF policy paper, 2022) /
  "Algorithmic Auditing: Chasing AI Accountability"
  (Santa Clara High Tech LJ, 2023).
  <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4227350> /
  <https://digitalcommons.law.scu.edu/chtlj/vol39/iss3/1/>
  Absent independent auditors, audit artifacts become audit-washing — and
  auditor-equals-auditee is precisely the structure they warn against. This is
  ToneSoul's most direct structural indictment (see §3).
- **CONTEXT** — Ojewale, Steed, Vecchione, Birhane, Raji, "Towards AI
  Accountability Infrastructure" (CHI 2025).
  <https://dl.acm.org/doi/10.1145/3706598.3713301>
  A large practitioner-interview + tool-landscape study (abstract-level; the
  reported interview/tool counts are not verified against the full text) argues
  the field must move beyond evaluation to full accountability infrastructure —
  ToneSoul fills only a small slice of that landscape.

### Axis B — Deontological / categorical refusal

- **ANCHOR** — Lavi, "Right-to-Act: A Pre-Execution Non-Compensatory Decision
  Protocol for AI Systems" (preprint, 2026).
  <https://arxiv.org/abs/2604.24153>
  A pre-execution non-compensatory admissibility layer where no positive signal
  compensates a failed required condition — the closest formal analogue to
  ToneSoul's categorical vow gates.
- **CHALLENGE** — D'Alessandro, "Deontology and Safe Artificial Intelligence"
  (Philosophical Studies 182(7), 2024).
  <https://link.springer.com/article/10.1007/s11098-024-02174-y>
  Moral/deontological alignment does **not** entail safety: the ethical-AI
  program is *not* a straightforward solution to AI risk, and standard
  deontological theories can yield unsafe outcomes when implemented by systems
  lacking context and moral uncertainty — a direct challenge to the premise that
  categorical refusal makes a system safer. (Abstract-level; the specific failure
  mechanisms are illustrative, from the broader argument, not the abstract.)
- **CONTRAST (design alternative — citation withdrawn, see footer)** — the main
  opposing design bet is *consequentialist, risk-budgeted refusal*: treat refusal
  as a tunable risk threshold (e.g. conformal risk control) rather than a
  categorical line — the opposite of ToneSoul's hard gates. A 2025 preprint
  articulating this (UniCR, arXiv:2509.01455) was **dropped from this list after
  arXiv withdrew it** over unverifiable authorship; the paradigm is real, that
  specific citation is not citable.
- **COMPLICATES** — Clark, Shen, Howe, Mitra, "Epistemic Alignment: A Mediating
  Framework for User-LLM Knowledge Delivery" (UW, 2025).
  <https://arxiv.org/abs/2504.01205>
  Introduces a third pragmatic-structural axis and 10 epistemology-derived
  transmission challenges, complicating ToneSoul's earlier binary of
  "deontological vs. probabilistic."

### Axis C — Runtime gating

- **ANCHOR** — Rebedea, Dinu, Sreedhar, Parisien, Cohen, "NeMo Guardrails"
  (EMNLP demos, 2023). <https://arxiv.org/abs/2310.10501>
  User-defined, model-independent, interpretable rails enforced at runtime
  (not via retraining) — the same enforcement posture ToneSoul adopts.
- **ANCHOR** — Shamsujjoha, Lu, Zhao, Zhu (CSIRO Data61), "Swiss Cheese Model
  for AI Safety: A Taxonomy and Reference Architecture for Multi-Layered
  Guardrails of Foundation Model Based Agents" (2024).
  <https://arxiv.org/abs/2408.02205>
  Multi-layered runtime guardrails across pipeline stages and agent artifacts —
  prior art for layered, defense-in-depth gating.
- **ANCHOR + CONTRAST** — Bai, Kadavath, Kundu, Askell, et al. (Anthropic),
  "Constitutional AI: Harmlessness from AI Feedback" (2022).
  <https://arxiv.org/abs/2212.08073>
  Governs behavior via explicit written principles through model
  critique-and-revision — but at **training** time (SL + RLAIF). ToneSoul
  contrasts by enforcing principles at **runtime**; this is a difference in
  locus, not a claim of superiority.
- **CHALLENGE** — Huang, Chen, Mishra, Zheng, Yu, Song, Zhou, "Large Language
  Models Cannot Self-Correct Reasoning Yet" (ICLR 2024).
  <https://arxiv.org/abs/2310.01798>
  Intrinsic self-correction fails to improve, and sometimes degrades, reasoning
  — a direct warning that a model checking its own output (as in any self-audit
  loop) may not help.
- **PARTIAL CHALLENGE** — Gou, Shao, Gong, Shen, Yang, Duan, Chen, "CRITIC: LLMs
  Can Self-Correct with Tool-Interactive Critiquing" (ICLR 2024).
  <https://arxiv.org/abs/2305.11738>
  Self-correction works mainly when grounded by **external** tools; without
  external feedback the gains evaporate — which raises the bar for any
  self-contained verifier ToneSoul ships.

### Axis D — Honesty

- **ANCHOR** — Yang, Chern, Qiu, Neubig, Liu, "Alignment for Honesty"
  (NeurIPS 2024). <https://arxiv.org/abs/2312.07000>
  Frames honesty as knowing one's boundary — proactively refusing when lacking
  knowledge while avoiding over-conservatism — the disposition ToneSoul's
  evidence labels aim at.
- **FIELD MAP** — Li, Yang, Wu, Shi, Zhang, Zhu, Cheng, Cai, Yu, Liu, Zhou,
  Yang, Wong, Wu, Lam, "A Survey on the Honesty of Large Language Models"
  (TMLR 2025). <https://arxiv.org/abs/2409.18786>
  Formalizes honesty as self-knowledge plus self-expression and surveys
  evaluation and improvement — the map ToneSoul's honesty work sits inside, far
  from the frontier.
- **ANCHOR + CHALLENGE** — Cheng, Yu, Lee, Khadpe, Ibrahim, Jurafsky,
  "ELEPHANT: Measuring Social Sycophancy in LLMs" (2025).
  <https://arxiv.org/abs/2505.13995>
  Social sycophancy (excessive preservation of user face) occurs in LLMs
  substantially more than in humans (the abstract cites a ~45-percentage-point
  gap; abstract-level, not verified against the results tables) — both a
  motivation for ToneSoul's anti-sycophancy stance and a reminder of how strong
  the pull it fights actually is.
- **DIRECT CHALLENGE** — Huang, Tang, Feng, Zhang, Lei, Lv, Cohn, "Dishonesty in
  Helpful and Harmless Alignment" (2024).
  <https://arxiv.org/abs/2406.01931>
  Pushing models to be more honest **measurably increases harmfulness** on
  harmful questions — meaning ToneSoul's honesty emphasis may carry a safety
  cost it has not measured.
- **ANCHOR + CHALLENGE** — Berg, de Lucena, Rosenblatt, "Large Language Models
  Report Subjective Experience Under Self-Referential Processing" (2025).
  <https://arxiv.org/abs/2510.24797>
  Self-referential prompting elicits structured subjective-experience reports
  gated by deception/roleplay features — a caution that introspective-sounding
  AI self-reports (which ToneSoul's journaling can surface) are not evidence of
  inner states.

### Axis E — Governance and data sovereignty

- **ANCHOR** — Nolte, Finck, Meding, "Machine Learners Should Acknowledge the
  Legal Implications of LLMs as Personal Data" (2025).
  <https://arxiv.org/abs/2503.01630>
  LLMs memorize and reproduce training data, so the model itself can constitute
  personal data and trigger erasure rights — grounding ToneSoul's memory-
  sovereignty axiom in a real legal problem.
- **ANCHOR** — "Unlearning at Scale: Implementing the Right to be Forgotten in
  LLMs" (2025; arXiv attribution thin/unusual — verify before citing).
  <https://arxiv.org/abs/2508.12220>
  Frames GDPR Article 17 erasure as a deterministic, auditable,
  write-ahead-logged systems problem — a concrete engineering precedent for
  ToneSoul's memory layer.
- **POSITIONING** — Ribeiro, Rocha, Pinto, Cartaxo, Amaral, Davila, Camargo,
  "Toward Effective AI Governance: A Review of Principles" (2025).
  <https://arxiv.org/abs/2505.23417>
  A tertiary review finding the field dominated by the EU AI Act and NIST RMF,
  with transparency and accountability most common — locating ToneSoul as a tiny
  bottom-up entry beside large top-down frameworks.
- **CHALLENGE** — Lin, "Beyond Principlism: Practical Strategies for Ethical AI
  Use in Research Practices" (AI and Ethics 5, 2025).
  <https://arxiv.org/abs/2401.15284>
  Explicit principles stay abstract and symbolic — the principles-to-practice
  gap persists unless backed by enforcement, exactly the gap ToneSoul's
  enforcement is only **partially** closing (see §3).
- **CHALLENGE** — Findeis, Kaufmann, Hüllermeier, Albanie, Mullins, "Inverse
  Constitutional AI: Compressing Preferences into Principles" (ICLR 2025).
  <https://arxiv.org/abs/2406.06560>
  The principle-to-behavior relationship is messy and multiply realizable;
  multiple constitutions can explain the same behavior — so ToneSoul's named
  axioms do not uniquely determine what its system actually does.

## 3. Honest gaps

These are real, current, and unresolved:

- **Sensors are lexical, not measured.** Tension, drift, and similar signals are
  computed from surface lexical features, not from validated measurements of the
  underlying property. They are heuristics labeled as heuristics.
- **Verifier independence is unproven.** ToneSoul's checks largely run inside the
  same system they evaluate. Per Huang et al. (C4) and Gou et al. (C5),
  same-model / ungrounded self-correction is exactly the configuration most
  likely to fail.
- **Enforcement is partial.** Several axioms are *referenced* or *partially
  enforced* rather than fully gated. Per Lin (E4) and Findeis et al. (E5),
  stated principles without complete enforcement risk staying symbolic.
- **There is NO independent auditor.** ToneSoul audits itself. Per Goodman &
  Trehu (A5), auditor-equals-auditee is the canonical audit-washing structure.
  This is a structural limitation, not a temporary one.
- **The categorical stance may itself be unsafe.** Per D'Alessandro (B2),
  deontological alignment does not entail safety; the main alternative paradigm
  (tunable, risk-budgeted refusal) would dispute that a categorical line is right
  at all. ToneSoul has not demonstrated its categorical design is the safer choice.
- **Scope is narrower than past framing.** ToneSoul fills a small slice of the
  accountability-infrastructure landscape (A6), sits well inside the honesty
  field map (D2), and is a minor bottom-up entry next to the EU AI Act / NIST RMF
  (E3). Earlier framing has at times overstated its reach.

## 4. What is genuinely absorbable at the deployment level

Stripping the framing down, two contributions are defensible at the deployment
level — both are deployment-level engineering, not theoretical advances:

1. **Honest evidence labeling carried end-to-end into a shippable artifact.**
   The discipline of attaching explicit, conservative confidence/provenance
   labels to a running system's outputs (including labeling its own self-reports
   as non-evidence of inner states, per D5) — packaged as installable code, not
   a guideline.
2. **An enforcement-reconciliation ledger that tracks the principles-to-practice
   gap as first-class state.** A self-assessment of which axioms are fully
   enforced, partially enforced, or only referenced — held openly rather than
   hidden — which surfaces the gap named by Lin (E4) and Findeis et al. (E5) as
   explicit state. (It *names* the gap; it does not close it — ToneSoul's own
   enforcement is itself only partial, per §3.)

Neither requires adopting ToneSoul's vocabulary or thesis to reuse.

## 5. Peer deployments (real systems, not papers)

The academic anchors above show the *problems* are studied. A different kind of
evidence: **other builders independently shipping the same governance pattern.**

- **Eliyah Oren / alicken-lai — Ambient OS / SingleClaw-DMN**
  (<https://github.com/alicken-lai/ambient-somatic-intelligence>,
  <https://github.com/alicken-lai/SingleClaw-DMN>; framework site
  <https://eliyahoren.com/>). Read at README level (E3), not a deep code audit.
  A single-creator "Human-AI OS" whose governance core converges with ToneSoul's
  on **structure**, not just vocabulary: a **Guardian gate** classifying actions
  `ALLOW / REVIEW_REQUIRED / BLOCK` (≈ ToneSoul's verdict + reflex BLOCK); an
  **append-only audit memory** ("DMN", no retroactive rewrite ≈ Aegis chain +
  the `delete_memory` prohibition); **"better memory, not more agents"** (≈ the
  single-creator, memory-centric, anti-swarm stance); regression-tested with
  honest caveats ("replay PASS = bounded behavior under test, not proof of
  real-world autonomy" ≈ the E1–E6 ladder); and — most strikingly — an
  **advisory observability layer that explicitly does NOT override the gate**
  (his v070–v077 "observational only"), an independent arrival at
  **DESIGN Invariant 3 (Advisory ≠ Canonical)**.

  **What this is and is NOT.** It is *evidence ToneSoul sits on a convergent
  design point* (gate + append-only audit + advisory-not-canonical + test-bounded
  honesty), reached independently — not validation, and **not the same system**.
  Key differences, kept honest: his governance object is **agent ACTION
  side-effects** (operational safety, approval routing) where ToneSoul's is **AI
  OUTPUT honesty** (epistemic accountability); his framing adds an embodied/somatic
  layer + a coaching/civilization program ToneSoul has none of; and maturity
  differs (his = frozen-research / v0.1; ToneSoul = pip-installable + CI-gated).
  His action-side-effect gating is a *complementary* axis ToneSoul does not
  cover — prior art if ToneSoul ever governs actions, not just outputs.

---

## Verification provenance

Every citation above was **independently re-verified on 2026-06-15** against live
arXiv / publisher / SSRN pages (a 27-agent check: paper exists, title + authors
match, claim accurate at abstract level), then this document was adversarially
reviewed for convergence-inflation and overclaim. Outcome:

- **24 of 25 candidate citations** verified usable and retained.
- **1 dropped — Oehri et al., "Trusted Uncertainty / UniCR" (arXiv:2509.01455):**
  the citation details were accurate, but **arXiv withdrew the paper** over
  unverifiable authorship/affiliation. A withdrawn preprint should not anchor a
  public document, so it was removed (the design paradigm it described is noted
  in Axis B without it).
- A few entries were tightened where the original attribution slightly outran the
  abstract (Birhane A4, D'Alessandro B2, Ojewale A6, ELEPHANT D3) — flagged inline.
- **Unlearning at Scale (E2)** is retained with its authorship caveat in place.

Reading depth remains **E3 (title + abstract only)** for every entry. Fuller
per-paper notes: `docs/research/tonesoul_in_the_literature_2026-06-15.md`.
