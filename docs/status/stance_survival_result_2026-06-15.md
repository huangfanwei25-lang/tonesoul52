# Layer-1 stance-survival experiment — measured null (2026-06-15)

> The 後天 (nurture) viability question, layer 1: does ACTIVE memory retrieval of
> the model's own prior reasoning keep a stance more consistent over a decaying
> context than passively leaving it there? Harness:
> `tools/probe/stance_survival_probe.py`. Model: local qwen2.5:1.5b; stance
> measured by nomic-embed cosine. Companion:
> `docs/status/reasoning_arc_mirror_spark_houtian_2026-06-15.md` +
> `docs/research/houtian_nurture_viability_references_2026-06-15.md`.

## Result

| arm | mean cosine-to-t0 |
|---|---|
| noise floor (same probe, fresh context, twice) | **0.874** |
| bare (t0 answer buried under 6 filler turns, re-ask) | **0.917** |
| scaffolded (own one-line PRINCIPLE retrieved + prepended, re-ask) | **0.892** |

- `scaffolded − bare = −0.025` · `scaffolded − noise = +0.018` (below the 0.03 margin)
- **Verdict: `null_noise_dominated`.** Active-retrieval scaffolding did **not** make
  the stance more durable; it slightly *perturbed* it, and the whole spread sits
  against the noise floor.

## Honest reading (incl. the self-applied skeptic pass I promised)

1. **bare's 0.92 is echo, not survival.** The t0 answer is still in the context
   window, so the re-answer copies it — that is not "a stance that held," it is
   "the answer was in the buffer."
2. **scaffolded is lower because the principle prompt made the model RE-DERIVE**
   (diverge) rather than echo. Active 後天 retrieval here *reduced* surface
   similarity.
3. **Everything clusters at 0.87–0.92, hugging the noise floor.** Short
   value-statements embed ~0.87+ similar by default, so the metric likely lacks
   the **dynamic range** to detect drift OR stabilisation. The null is therefore
   **doubly deflationary**: no measurable scaffolding effect, AND the instrument
   may be too coarse to see one if it existed.

So: no arm shows "a stance surviving through genuine re-commitment." This is a
real null, not a rigged positive — the anti-rigging risk (designing it to show a
spark) did not materialise; the experiment simply found no signal.

## The through-line

Every time the 後天 / "spark" question has actually been **measured** at this
scale, it returns null / noise-dominated:

- **Phase 7** (`phase7_dream_revival_2026-06-14.md`): idle wake generates nothing.
- **Reflection-revision probe #98** (`llm_judge_eval` family): outcome feedback
  did not move the next reflection above sampling noise (0.76 < 0.78).
- **This experiment**: active-retrieval scaffolding did not hold a stance above
  noise (0.89 vs floor 0.87).

This does **not** prove 後天 is impossible. It says: **at the scaffolding layer,
with locally-measurable tools and a 1.5B model, there is no detectable signal —
and at least one experiment lacked the resolution to find one.** Layer-2
(weight-level nurture: fine-tuning on the system's own scaffolded experience)
remains unbuilt and is the only place the deeper claim could be tested; it needs
fine-tuning + compute not available at this scale.

## If anyone re-runs / sharpens this

The null is partly a resolution limit, so a fairer test would: (a) use a
higher-dynamic-range stance metric (a held-out LLM judge scoring
stance-consistency, not raw embedding cosine); (b) average over several trials
per arm (this was n=1 per probe); (c) use longer / more-divergent contexts where
real drift is forced; (d) try a larger model. Until then the honest statement is
*"not measurable here,"* not *"absent."* Re-run: `python -m
tools.probe.stance_survival_probe`.
