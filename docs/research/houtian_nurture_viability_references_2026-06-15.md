# Reference Scaffolding — 後天可塑性與「火花」問題 (houtian / nurture viability)

> Companion to `docs/status/reasoning_arc_mirror_spark_houtian_2026-06-15.md`.
> Collected 2026-06-15 via a 5-way web-search sweep + adversarial verification
> pass (Claude Opus 4.8). Every entry was located via search and resolved to a
> real paper at the cited arXiv ID / DOI.

## E3 / Aggregation Caveat (read first)

**This is external reference scaffolding, not a validation of ToneSoul.** Every
entry below was located via web search and resolved to a real paper at the cited
arXiv ID / DOI; depth is **title/abstract only** — none were read in full, and
none should be upgraded to "read" or "verified-deep." These citations were
assembled to frame two sub-questions — (a) can a context-set or nurtured stance
stay *stable*? and (b) can nurture/scaffolding produce a *spark-like* new
direction? — and they deliberately pair optimistic existence-proofs with
deflationary counterweights. **Aggregation is not verification:** N
abstract-level reads do not compose into "the literature shows X." Several
entries are explicitly skeptical (persona/identity drift, Nature model-collapse,
Zador's innate-prior critique, the "Mirage" rebuttal). Peer-reviewed status is
noted per entry; the rest are preprints. Do **not** read this list as
"convergence toward ToneSoul" — it is an honest spread, and the spread is the
point.

## (1) Layer 1 — In-context / scaffolding 後天 (no weight change)

- **Measuring and Controlling Instruction (In)Stability in Language Model Dialogs** — Li et al., 2024, COLM 2024. https://arxiv.org/abs/2402.10962 — System-prompt stance drifts significantly within ~8 rounds of self-chat (attention decay), with a split-softmax mitigation. Pure-context conditioning is *fragile*. **direct** (peer-reviewed).
- **Examining Identity Drift in Conversations of LLM Agents** — Choi et al., 2024. https://arxiv.org/abs/2412.00804 — Across 9 LLMs: larger models drift *more*; assigning a persona may *not* help. Counterweight to "just scaffold a stance." **direct**.
- **In-Context Impersonation Reveals LLMs' Strengths and Biases** — Salewski et al., 2023, NeurIPS 2023 Spotlight. https://arxiv.org/abs/2305.14930 — A purely in-context persona systematically changes behavior/capability. Supports the *front* half (context shapes behavior); silent on long-horizon stability. **direct** (peer-reviewed).
- **Learning without training: the implicit dynamics of in-context learning** — Dherin et al., 2025 (preprint). https://arxiv.org/abs/2507.16003 — Argues a forward pass with context ≈ a forward pass with a low-rank context-induced weight edit — context acts *like* a transient weight edit. Mechanistic anchor for the 先天/後天 boundary. **direct**.
- **Generative Agents: Interactive Simulacra of Human Behavior** — Park et al., 2023, ACM UIST 2023. https://arxiv.org/abs/2304.03442 — Memory-stream + reflection + retrieval scaffold yields behavior raters find consistent over extended simulated time. Strongest optimistic existence-proof. Caveat: "believable to raters" ≠ verified-stable internal stance. **direct** (peer-reviewed).
- **Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering** — Bigelow et al., 2025. https://arxiv.org/abs/2511.00617 — ICL shifts belief in latent concepts by accumulating evidence (no weight updates), parallel to activation steering. Caveat: latent-concept belief is not a self-model. **direct**.
- **PICLe: Persona In-Context Learning** — Choi & Li, 2024, **ICML 2024** (PMLR v235). https://arxiv.org/abs/2405.02501 — Persona elicitation as Bayesian inference (88.1% vs 65.5% on Llama-2). Caveat: uses persona SFT to estimate the likelihood ratio → *not* pure no-fine-tuning. **direct**.
- **Looking Inward: LMs Can Learn About Themselves by Introspection** — Binder et al., 2025, ICLR 2025. https://arxiv.org/abs/2410.13787 — Privileged self-access (M1 predicts its own outputs better than M2). Honesty note: induced by *fine-tuning*, holds only on simple tasks (fails OOD). **direct**.
- **Language Models (Mostly) Know What They Know** — Kadavath et al. (Anthropic), 2022. https://arxiv.org/abs/2207.05221 — Large models are reasonably calibrated about their own answers (P(True)/P(IK)). But self-knowledge about correctness ≠ a stable identity. **direct**.
- **Does It Make Sense to Speak of Introspection in LLMs?** — Comsa & Shanahan, 2025. https://arxiv.org/abs/2506.05068 — A self-report is introspective only if it accurately describes an internal state via a causal link; fluent self-report is *not* evidence of a self-model. Counters over-reading. **direct**.
- **Self-Consistency Improves Chain of Thought Reasoning** — Wang et al., 2022, ICLR 2023. https://arxiv.org/abs/2203.11171 — Consistency of *answers* across sampled paths, NOT consistency of a *self*. Terminological-only bearing; must not be conflated. **tangential**.

## (2) Layer 2 — Weight-level / nature-vs-nurture

- **Constitutional AI: Harmlessness from AI Feedback** — Bai et al. (Anthropic), 2022. https://arxiv.org/abs/2212.08073 — Weight-level shaping using the model's own self-critiques + AI-feedback (RLAIF) from a short rule list. Existence proof for nurture-via-self-supervision — bounded by seed model + supplied principles. **direct**.
- **RLAIF vs. RLHF** — Lee et al. (Google), 2023, ICML 2024. https://arxiv.org/abs/2309.00267 — AI-generated feedback reaches parity with human feedback in RL alignment. Caveat: the AI labeler is itself a trained model (signal not ex nihilo). **direct**.
- **STaR: Bootstrapping Reasoning With Reasoning** — Zelikman et al., 2022, NeurIPS 2022. https://arxiv.org/abs/2203.14465 — Self-training loop on self-generated rationales; filter is an external correctness signal (bounds the "self-sourced" claim). **direct**.
- **Large Language Models Can Self-Improve** — Huang et al., 2022. https://arxiv.org/abs/2210.11610 — 540B fine-tunes on its own high-confidence CoT (no labels), GSM8K 74.4→82.1. Near-pure nurture-from-self-data — gains concentrate where self-consistency is a reliable proxy. **direct**.
- **AI models collapse when trained on recursively generated data** — Shumailov et al., 2024, *Nature* 631 (DOI 10.1038/s41586-024-07566-y). https://www.nature.com/articles/s41586-024-07566-y — The principal counterweight: recursive self-training causes irreversible **model collapse** (tails vanish). Self-data is not a free nurture source. **direct** (peer-reviewed).
- **Escaping Collapse: The Strength of Weak Data** — Amin et al., 2025. https://arxiv.org/abs/2502.08924 — Collapse is escapable *if* synthetic data is curated to inject exogenous signal (selection, human rewrites, separate verifier). Self-nurture viable but *conditional* on curation. The bridge between self-improve and collapse. **direct**.
- **Continual Learning of LLMs: A Comprehensive Survey** — Shi et al., 2024 (survey). https://arxiv.org/abs/2404.16789 — Maps the nurture channel + its central obstacle (catastrophic forgetting / general-to-specific trade-off). **direct** (survey).
- **Learning Not to Learn: Nature versus Nurture in Silico** — Lange & Sprekeler, 2020, AAAI 2022. https://arxiv.org/abs/2010.04466 — The most direct formal nature-vs-nurture treatment: derives *when* a learned/adaptive strategy beats a hard-coded one (ecological uncertainty, task complexity, lifetime). **direct** (peer-reviewed).
- **A critique of pure learning (what ANNs can learn from animal brains)** — Zador, 2019, *Nature Communications* 10:3770 (DOI 10.1038/s41467-019-11786-6). https://www.nature.com/articles/s41467-019-11786-6 — Innate genome-specified connectivity (the "nature" prior) enables rapid learning; without strong innate structure, experience alone does not yield competent directed behavior. **direct** (peer-reviewed).
- **Encoding innate ability through a genomic bottleneck** — Shuvaev et al., 2024, *PNAS* 121(38) (DOI 10.1073/pnas.2409160121). https://www.pnas.org/doi/10.1073/pnas.2409160121 — Heavily compressed innate weights still yield strong pre-experience performance — quantifies how much competence is innate prior vs experience. **direct** (peer-reviewed).
- **DREAM Architecture: a Developmental Approach to Open-Ended Learning in Robotics** — Doncieux et al., 2020. https://arxiv.org/abs/2005.06223 — Developmental-AI paradigm (minimal innate knowledge → incremental redescription/transfer). A single architecture proposal, not direct evidence. **tangential**.

## (3) Cross-cutting — intrinsic motivation / emergence / mirage

- **Emergent Abilities of Large Language Models** — Wei et al., 2022, TMLR. https://arxiv.org/abs/2206.07682 — The canonical pro-"spark": abilities absent in small models appear in large ones, unpredictable by extrapolation. Read against its critique. **direct** (peer-reviewed).
- **Are Emergent Abilities of LLMs a Mirage?** — Schaeffer et al., 2023, NeurIPS 2023. https://arxiv.org/abs/2304.15004 — Apparent emergence is an artifact of nonlinear metrics + small test sets; under continuous metrics, smooth improvement. A training-instilled "spark" may be a measurement choice, not a phase change. **direct** (peer-reviewed).
- **Curiosity-driven Exploration by Self-supervised Prediction** — Pathak et al., 2017, ICML 2017. https://arxiv.org/abs/1705.05363 — Self-initiated "direction" engineered as intrinsic reward (prediction error). Shows the spark can be *constructed*, not that it *arises* on its own. **direct** (peer-reviewed).
- **A survey on intrinsic motivation in reinforcement learning** — Aubret et al., 2019 (survey). https://arxiv.org/abs/1908.06976 — Taxonomy of intrinsic-motivation approaches + limits. Orientation, not proof that genuine intrinsic drive exists. **tangential** (survey).

## (4) Honest synthesis — what is and is NOT settled

The literature establishes that **context and self-generated supervision can
demonstrably shape behavior** (impersonation, PICLe, Constitutional AI, RLAIF,
STaR, self-improve) and that there are **mechanistic accounts** for why context
behaves like a transient weight edit (Dherin; Bigelow). It does **not** settle
that a nurtured stance is *durable*: the drift papers (Li; Choi) show
context-set personas decay within a handful of turns and that scale can make
this *worse*; the strongest stability demonstration (Generative Agents) verifies
only rater-perceived believability, not an internal stance; and Comsa & Shanahan
warn that fluent self-report is not evidence of a self at all. On the second
sub-question — whether nurture yields a *spark-like* new direction — the field is
openly split: emergence (Wei) vs. mirage (Schaeffer), self-improvement vs.
model-collapse (Nature) escapable only under curation (Amin), and the
innate-prior critiques (Zador; genomic bottleneck; Lange & Sprekeler) arguing
much directed competence is structural, not learned. Engineered intrinsic
motivation (Pathak) shows a drive can be *built*, not that it *arises*.

**Where ToneSoul's Layer-1 experiment sits:** context/scaffolding-only
conditioning (no weight change) sits squarely in the *contested,
fragility-leaning* region. It would be testing exactly the claim the drift
papers find weak — a durable stance from context alone — with the mechanistic
papers explaining *why* the effect exists but the stability papers explaining
*why it may not last*. So the load-bearing empirical question is **"does the
scaffolded stance survive over turns/sessions?"**, NOT "can context shape
behavior at all" (already established). This list is scaffolding for that
question, not evidence for any answer.

---

**Confabulation-risk note:** the known confabulation risk in this domain did
**not** materialize — all kept entries resolved to real papers at the claimed
arXiv ID / DOI with matching titles/authors (zero fabrications). 1 paper was
dropped (a self-duplicate, not a fake: Everitt et al., "Evaluating the
Goal-Directedness of LLMs," arXiv:2504.11844, listed twice). Two author gaps
were filled (Bigelow et al.; Amin et al.) and one venue corrected (PICLe → ICML
2024) during verification.
