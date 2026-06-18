# Research Reading List — memory retrieval, AI accountability, MoE/multi-agent

> Purpose: the sourced coordinates behind this project's two active research threads (memory
> retrieval; AI accountability / guardrails) plus the MoE/multi-agent cluster (reference-only —
> the "neuralize ToneSoul into a MoE" direction is the one argued *against* in
> `docs/plans/honesty_auditor_program_2026-06-18.md`).
> Last Updated: 2026-06-18
> Status: pointer list, not a claim list. Provenance labels below; **verify against the source
> before relying.** Where a source and this repo's code disagree, the code wins.

**Provenance labels**
- `[R]` web-fetched + adversarially verified in this project's deep-research (2/3-to-kill).
- `[S]` coordinate confirmed via web search 2026-06-18 (existence/ID verified; not deep-read).
- `[K]` well-established reference, ID from knowledge — confirm if cited formally.
- `[P]` preprint / effectiveness author-reported — not independently verified.
- `[?]` named in discussion, could NOT be located — do not cite until confirmed.

---

## 1. Memory & retrieval (active thread — see `episodic_memory_provenance_2026-06-18.md`)

**Cognitive science**
- `[R]` Tulving & Thomson (1973), encoding-specificity — *Psychological Review* 80:352–373. (mechanism debated; descriptive finding stands)
- `[R]` Anderson (1983), spreading-activation (ACT-R) — *J. Verbal Learning & Verbal Behavior* 22:261–295.
- `[R]` Nader, Schafe & LeDoux (2000), reconsolidation — *Nature* 406:722–726 — https://www.nature.com/articles/35021052
- `[R]` Talarico & Rubin (2003), flashbulb = subjective-only, decays at everyday rate — *Psychological Science* 14(5):455–461 — https://journals.sagepub.com/doi/10.1111/1467-9280.02453

**Cultural memory** (filed by place/narrative/ritual, not similarity)
- `[R]` Aboriginal songlines / relational knowledge — PACJA art. 143975 — https://pacja.org.au/article/143975
- `[R]` Jack Goody, oral cultures — Princeton chapter PDF — http://assets.press.princeton.edu/chapters/s8150.pdf
- `[R]` Lynne Kelly, *The Memory Code* (use indexing structure, not the relational-ontology phrasing).

**AI memory systems** (convergent — this has been tried)
- `[R]` Generative Agents (Park et al., UIST 2023) — recency + importance/salience + relevance — arXiv:2304.03442
- `[R]` EM-LLM (Fountas et al., ICLR 2025) — Bayesian-surprise event segmentation + temporal-contiguity retrieval; beats InfLLM by only ~+0.2 avg (big wins vs generic embedder) — arXiv:2407.09450 / https://em-llm.github.io/
- `[R][P]` NEMORI (2025), surprise/prediction-error memory writing — arXiv:2508.03341
- `[R][P]` D-MEM (2026), error/RPE-gated memory — arXiv:2603.14597 (one novelty claim did NOT survive our adversarial check)

## 2. AI accountability / jailbreak / external gates (active thread — see `episodic` peer + `RELATED_WORK.md`)

**Intrinsic safety is shallow / removable**
- `[R]` Arditi et al. (NeurIPS 2024), refusal mediated by a low-dim linear direction; abliteration without retraining — https://proceedings.neurips.cc/paper_files/paper/2024/file/f545448535dfde4f9786555403ab7c49-Paper-Conference.pdf
- `[R]` Qi et al. (ICLR 2025), shallow safety alignment (first-few-tokens) — arXiv:2406.05946
- `[R]` TAR, tamper-resistant safeguards (durability claim contested) — arXiv:2408.00761
- `[R]` Extended-refusal fine-tuning (defense; self-reported) — arXiv:2505.19056

**External guardrails relocate, don't eliminate, jailbreaking**
- `[R]` STACK staged attack (71% ASR on a classifier pipeline) — arXiv:2506.24068
- `[R]` Guardrail generalization collapse on novel attacks (single-author preprint; indicative) — arXiv:2511.22047
- `[R]` Emoji-smuggling / character-injection (100% ASR; Azure Prompt Shield 60–72% evadable) — arXiv:2504.11168
- `[R]` Anthropic Constitutional Classifiers (86%→4.4%; but the public challenge was beaten in ~a week; frontier compute) — arXiv:2501.18837 / https://www.anthropic.com/research/next-generation-constitutional-classifiers

## 3. MoE / multi-agent / alignment data (REFERENCE ONLY — direction argued against)

> These are the academic anchors a second AI mapped ToneSoul's mechanisms onto. Included for
> reference. Note: "all of this exists in papers" = **convergent**, which means re-implementing
> labs' work with less compute, and neuralizing the mechanisms into weights would bury the
> auditability that is the project's only differentiator. See `honesty_auditor_program_2026-06-18.md`.

- `[S]` Mixture-of-Agents (MoA), Wang et al. 2024 / ICLR 2025 — layered multi-LLM debate (the council's academic cousin) — arXiv:2406.04692
- `[S]` Symbolic Mixture-of-Experts — gradient-free, skill-based text-level expert routing — arXiv:2503.05641
- `[S]` DeepSeekMoE — fine-grained expert segmentation + gating — arXiv:2401.06066
- `[K]` Anthropic HH-RLHF (Bai et al. 2022), helpful/harmless preference data — arXiv:2204.05862
- `[K]` TruthfulQA (Lin et al. 2021), truthfulness / "I don't know" calibration — arXiv:2109.07958
- `[?]` "Routing-Free MoE" — named in discussion; not located in search — confirm before citing.

---

## How to use this

The full verified findings (with vote counts and caveats) live in the deep-research outputs;
the load-bearing corrections are in `episodic_memory_provenance_2026-06-18.md`. This list is the
map, not the territory — open the sources. The honest direction these support is **measurement /
accountability** (`honesty_auditor_program_2026-06-18.md`), not capability-building.
