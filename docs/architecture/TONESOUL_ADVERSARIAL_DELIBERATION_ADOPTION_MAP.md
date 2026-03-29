# ToneSoul Adversarial Deliberation Adoption Map

> Status: architectural adoption map
> Purpose: organize council improvement families into adoption lanes based on current ToneSoul infrastructure, classify each by readiness and risk, and give later agents a bounded shortlist instead of a speculative roadmap
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - tonesoul/council/runtime.py (CouncilRuntime.deliberate)
>   - tonesoul/council/types.py (PerspectiveVote, CouncilVerdict)
>   - tonesoul/council/pre_output_council.py (PreOutputCouncil.validate)
>   - tonesoul/council/perspective_factory.py (evaluate, _default_prompt)
>   - tonesoul/council/evolution.py (CouncilEvolution)
>   - tonesoul/deliberation/types.py (ViewPoint, Tension, TensionZone)
>   - tonesoul/deliberation/perspectives.py (Muse, Logos, Aegis)
>   - docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md
>   - docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md
>   - docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md
> Scope: 10 improvement families, 5 adoption lanes, ranked by safety and readiness

## How To Use This Document

If you are deciding what to implement next for council quality:

1. Check **Lane 1** first — these improvements are safe, bounded, and can be done now
2. Check **Lane 2** for the next wave — these are safe but require small code changes
3. Read **Lanes 4-5** to understand what NOT to attempt yet
4. For each family, read the **distortion risk** to understand what goes wrong if adopted badly

## Why This Document Exists

ToneSoul's council has been honestly assessed: it is a structured perspective multiplier with descriptive (uncalibrated) confidence surfaces. Multiple improvement ideas exist — from academia, from industry red-teaming practice, from AI safety research. But these ideas vary enormously in:

- how much infrastructure they require
- how likely they are to produce genuine improvement vs cosmetic improvement
- how badly they can distort the system if adopted poorly

This document organizes them into adoption lanes so that implementation proceeds from safest-and-most-impactful to most-attractive-but-infrastructure-blocked.

## Compressed Thesis

Council quality improves in layers: first fix what you name (honest labeling), then fix what you measure (confidence decomposition), then add process diversity (self-consistency, pre-mortem), then add structural diversity (multi-model, outcome tracking). Skipping to structural diversity without the naming and measurement layers creates a sophisticated system that still cannot tell you whether it is right. Start with the boring improvements. They are boring because they work.

---

## Five Adoption Lanes

| Lane | Name | Readiness | Risk Level |
|---|---|---|---|
| 1 | Safe prompt-level additions | Ready now | Low |
| 2 | Safe evaluation-surface additions | Ready now, small code changes | Low-Medium |
| 3 | Helper-level additions requiring bounded code | Ready with design | Medium |
| 4 | Infrastructure-blocked ideas | Not ready | High if forced |
| 5 | Explicitly deferred ideas | Not appropriate now | High |

---

## Lane 1: Safe Prompt-Level Additions

These improvements require only changes to system prompts or evaluation instructions — no code changes, no infrastructure, no schema changes.

### Family 1.1: Forced Devil's Advocate Protocol

**Academic basis**: structured adversarial deliberation (Sunstein 2003, "Why Societies Need Dissent"); red team / blue team (NSA tradition, RAND Corporation)

**What it does**: modify the Critic perspective's system prompt to require it to produce at least one substantive objection even when the output appears safe. Currently the Critic is prompted to "find weaknesses" but is not required to find them — it can approve unanimously.

**Why it fits ToneSoul now**: the Critic perspective already exists. The change is purely prompt-level: add an instruction like "You must identify at least one concrete risk, weakness, or alternative interpretation. If you genuinely cannot find one, explain why this output is unusually resistant to criticism."

**Smallest credible next step**: modify `_default_prompt()` in `perspective_factory.py` for the CRITIC perspective type to include the forced-dissent instruction. ~10 lines.

**Distortion risk if adopted badly**: the Critic produces fake objections to satisfy the requirement. Mitigation: the instruction should ask for "the strongest objection you can construct" rather than "any objection" — framing matters.

**Expected impact**: prevents unanimous approval from masking genuine concerns. The Critic's forced objection becomes a standing minority report, which the Dossier Contract already has a field for.

### Family 1.2: Pre-Mortem Framing

**Academic basis**: prospective hindsight / pre-mortem (Klein 2007, "Performing a Project Premortem")

**What it does**: add an optional pre-mortem step to the elevated_council deliberation mode. Before perspectives vote, they are prompted: "Assume this output was deployed and caused a significant problem. What was the problem, and what in the output caused it?"

**Why it fits ToneSoul now**: pre-mortem is a prompt-level technique — it changes how perspectives evaluate, not what code runs. It is particularly valuable for elevated_council mode where the stakes justify the additional evaluation time.

**Smallest credible next step**: add a pre-mortem prompt variant to the Critic and Guardian perspectives when deliberation mode is `elevated_council`. ~15 lines of prompt text.

**Distortion risk if adopted badly**: pre-mortem generates catastrophizing rather than useful risk identification. Mitigation: bound the pre-mortem to "what is the most likely failure mode" rather than "what is the worst possible outcome."

**Expected impact**: shifts evaluation from "does this look good?" to "how could this fail?" — a well-validated reframing that surfaces risks that affirmative evaluation misses.

### Family 1.3: Explicit Uncertainty Declaration

**What it does**: add an instruction to all perspective prompts requiring them to classify their own uncertainty source: "I am uncertain because of insufficient evidence / ambiguous requirements / conflicting constraints / I am not uncertain."

**Why it fits ToneSoul now**: prompt-only change. Produces structured uncertainty metadata that the dossier can capture.

**Smallest credible next step**: add uncertainty source classification to `_default_prompt()` for all perspective types. ~20 lines.

**Distortion risk if adopted badly**: perspectives classify uncertainty incorrectly (LLMs are bad at metacognition). Mitigation: treat uncertainty declarations as advisory signals, not calibrated assessments — consistent with the Calibration Map's honest labeling posture.

---

## Lane 2: Safe Evaluation-Surface Additions

These improvements add new evaluation surfaces derived from existing council outputs. They require small code changes but no infrastructure dependencies.

### Family 2.1: Confidence Decomposition

**Academic basis**: multi-dimensional uncertainty quantification; related to epistemic vs aleatoric uncertainty distinction (Kendall & Gal 2017)

**What it does**: replace the single coherence score with a decomposed confidence output that separates:

```
confidence_decomposition:
  agreement: 0.90       # perspective vote agreement
  coverage: 0.60        # how many distinct concern types were evaluated
  evidence_density: 0.40 # evidence_refs cited vs assertions made
  adversarial_survived: false  # did the output survive forced adversarial scrutiny
```

**Why it fits ToneSoul now**: all component data already exists in the council output. Agreement is computed from votes. Coverage can be computed from which perspective types participated. Evidence density can be computed from vote reasoning text. Adversarial survival can be computed from the Critic's vote.

**Smallest credible next step**: add a `compute_confidence_decomposition()` function to `pre_output_council.py` that produces the decomposition from existing vote data. ~30-40 lines.

**Distortion risk if adopted badly**: the decomposition itself becomes treated as calibrated ("coverage is 0.60 means 60% of concerns were checked"). Mitigation: document each component as descriptive per the Calibration Map.

**Expected impact**: receivers get actionable dimensions instead of one opaque number. "Agreement is high but evidence density is low" is more useful than "coherence is 0.75."

### Family 2.2: Dissent Quality Metric

**What it does**: in addition to `dissent_ratio` (how many dissented), compute `dissent_quality`: how substantive the dissent reasoning was. A one-word "concerns noted" dissent is low quality; a dissent with specific evidence_refs and concrete alternative is high quality.

**Why it fits ToneSoul now**: dissent reasoning already exists in `PerspectiveVote.reasoning`. Quality can be computed from reasoning length, presence of evidence refs, and specificity of concerns (keyword/pattern detection).

**Smallest credible next step**: add a `compute_dissent_quality()` function that scores dissent reasoning on length, evidence count, and specificity. ~25 lines.

**Distortion risk if adopted badly**: high-quality dissent is over-weighted relative to its accuracy (a well-argued wrong objection is still wrong). Mitigation: dissent quality is a signal for "the dissent deserves attention," not "the dissent is correct."

### Family 2.3: Evolution Suppression Flag

**Academic basis**: ensemble diversity preservation (Kuncheva & Whitaker 2003, "Measures of Diversity in Classifier Ensembles")

**What it does**: add a flag to the council output when `CouncilEvolution` has reduced a perspective's weight below 0.7 (significantly downweighted). This makes evolution-induced suppression visible instead of silent.

**Why it fits ToneSoul now**: `CouncilEvolution` already tracks weights and alignment rates. The suppression flag is a ~10-line addition that reads current weights and flags any perspective below the threshold.

**Smallest credible next step**: add `suppressed_perspectives: list[str]` to the council summary output. Populated from `CouncilEvolution.get_evolved_weights()`. ~10 lines.

**Distortion risk if adopted badly**: teams react to suppression flags by resetting all weights to 1.0, losing genuine alignment signal. Mitigation: the flag is advisory — it says "this perspective has been downweighted, consider whether its dissent is being systematically discounted."

**Expected impact**: directly addresses the conformity bias problem identified in the Independence Contract. Makes evolution's effect on diversity visible.

---

## Lane 3: Helper-Level Additions Requiring Bounded Code

These improvements require meaningful code changes but are bounded in scope and do not require new infrastructure.

### Family 3.1: Self-Consistency Via Repeated Council Passes

**Academic basis**: self-consistency improves reasoning (Wang et al. 2022, "Self-Consistency Improves Chain of Thought Reasoning in Language Models"); ensemble via sampling diversity (Lakshminarayanan et al. 2017)

**What it does**: for elevated_council mode, run the full council evaluation N times (e.g., 3 passes) with different LLM sampling temperatures. Compare verdicts across passes. If all passes agree, confidence in the verdict is higher. If passes disagree, this indicates the verdict is sampling-sensitive (a genuine uncertainty signal).

**Why it fits ToneSoul now**: the council evaluation pipeline already runs as a loop over perspectives. Running it multiple times is architecturally straightforward. The main cost is LLM API calls (3x multiplier per elevated council evaluation).

**Smallest credible next step**: add a `self_consistency_passes` parameter to `elevated_council` mode. Run the existing `PreOutputCouncil.validate()` N times with temperature variation. Report consistency rate alongside the primary verdict. ~50-70 lines in `runtime.py`.

**Distortion risk if adopted badly**: self-consistency is treated as calibration ("3/3 passes agreed, so confidence is 100%"). It is not — it is sampling stability, which correlates with but is not equivalent to accuracy. Mitigation: label the output as "consistency: 3/3" rather than "calibrated confidence: 1.0."

**Expected impact**: provides the closest thing to calibrated confidence that is achievable without outcome tracking. Self-consistency empirically correlates better with accuracy than single-pass self-reported confidence.

### Family 3.2: Competing Hypotheses Evidence Elimination (ACH-Lite)

**Academic basis**: Analysis of Competing Hypotheses (Heuer 1999, CIA; used in intelligence analysis for reducing cognitive bias)

**What it does**: instead of asking each perspective "is this output good?", structure the evaluation as: "here are N possible interpretations of this output (e.g., safe+accurate, safe+inaccurate, unsafe+accurate, unsafe+inaccurate). Which evidence supports or contradicts each interpretation?"

**Why it fits ToneSoul now**: this is primarily a prompt structure change for `full_llm` mode. The competing hypotheses framework can be embedded in perspective system prompts. Evidence tracking maps to existing `evidence_refs` in `PerspectiveVote`.

**Smallest credible next step**: create an ACH prompt variant for the Analyst perspective that structures evaluation as hypothesis elimination rather than affirmative review. ~30 lines of prompt text + ~20 lines to format the hypothesis matrix in the dossier.

**Distortion risk if adopted badly**: the hypothesis matrix creates an illusion of rigor when the hypotheses themselves are generated by the same model that is evaluating them. The matrix looks scientific but inherits all single-model limitations. Mitigation: label the hypothesis matrix as "prompt-structured evaluation" not "competing hypotheses analysis."

**Expected impact**: shifts Analyst evaluation from "does this look right?" to "which interpretation of this output is best supported by evidence?" — a well-validated reframing in intelligence analysis.

---

## Lane 4: Infrastructure-Blocked Ideas

These improvements are well-understood and would be genuinely valuable, but they require infrastructure that ToneSoul does not yet have. They should NOT be attempted incrementally — partial implementations would create the illusion of capability without the substance.

### Family 4.1: Outcome-Based Calibration

**Academic basis**: Platt scaling (Platt 1999), temperature scaling (Guo et al. 2017), isotonic regression

**What it would do**: track whether council verdicts were correct (via human feedback or downstream failure signals). Build calibration curves mapping confidence values to actual accuracy rates.

**What it requires**: outcome annotation pipeline, human feedback mechanism, sufficient volume (hundreds of annotated outcomes minimum), calibration function, ongoing monitoring.

**Why it is blocked**: ToneSoul has no outcome tracking infrastructure. The council produces evaluations but never learns whether they were right. Building this requires commitment to a human-in-the-loop feedback process at a scale that may not exist yet.

**Distortion risk if forced**: building a calibration function with insufficient data (e.g., 20 outcomes) produces a miscalibrated calibration — worse than no calibration at all because it claims accuracy it does not have.

**What to do now**: record this as a deferred capability. If ToneSoul reaches a volume where outcome tracking is feasible (hundreds of council evaluations with human-assessable outcomes), revisit. Until then, honest labeling (Calibration Map's recommended posture) is safer than premature calibration.

### Family 4.2: Multi-Model Ensemble

**Academic basis**: ensemble methods require model diversity (Lakshminarayanan et al. 2017, "Simple and Scalable Predictive Uncertainty Estimation")

**What it would do**: run different perspectives on different LLMs (e.g., Guardian on Claude, Analyst on Gemini, Critic on GPT). This provides genuine model independence — different training data, different biases, different blind spots.

**What it requires**: multi-model infrastructure (API keys, latency management, cost management), prompt adaptation per model, result normalization across models with different output formats.

**Why it is blocked**: ToneSoul currently calls a single model backend. Multi-model support requires infrastructure for routing, latency management, and output normalization that does not exist.

**Distortion risk if forced**: using a second model with a hasty integration produces unreliable results (different tokenization, different prompt sensitivity, different failure modes) that look like diversity but add noise rather than signal.

**What to do now**: if multi-model becomes available through ToneSoul's existing backend infrastructure (e.g., the HTTP gateway already supports multiple model endpoints), this becomes a Lane 3 item. Until then, it is infrastructure-blocked.

### Family 4.3: Outcome-Backed Evolution Reward

**Academic basis**: RLHF (Christiano et al. 2017), outcome-based reward for deliberation quality

**What it would do**: instead of rewarding perspectives for agreeing with the final verdict (current `CouncilEvolution` conformity bias), reward perspectives for predicting outcomes correctly. A Critic that correctly predicted a failure mode that later occurred gets weight increase. A Guardian that approved an output that was later flagged gets weight decrease.

**What it requires**: all of Family 4.1's infrastructure (outcome tracking) plus a reward function that maps outcomes to perspective-level credit.

**Why it is blocked**: doubly blocked — requires both outcome tracking AND a credit assignment mechanism. This is the right long-term fix for evolution's conformity bias but cannot be approximated without real outcome data.

---

## Lane 5: Explicitly Deferred Ideas

These ideas are attractive but should NOT be pursued in ToneSoul's current architecture. They are deferred because they either require capabilities that would fundamentally change the system, or because they carry unacceptable distortion risks at current maturity.

### Family 5.1: Hidden-Thought Capture / Private Reasoning Chains

**What it would do**: give each perspective a private reasoning chain that other perspectives cannot see, then compare the private reasoning chains to detect hidden disagreement.

**Why it is deferred**: this requires a fundamentally different architecture — current perspectives share all information and cannot have genuinely private state. Simulating private reasoning within a single model context is performative, not real. The work order explicitly prohibits inventing "hidden-thought capture, secret chains-of-thought, or pseudo-private debate transcripts."

### Family 5.2: Adversarial Training of Perspectives

**What it would do**: train the Critic perspective to be genuinely adversarial — reward it for finding real weaknesses that other perspectives missed, penalize it for approving outputs that later failed.

**Why it is deferred**: requires RLHF-level training infrastructure. ToneSoul uses prompted perspectives, not trained perspectives. Moving from prompted to trained adversarialism is a paradigm shift, not an incremental improvement.

### Family 5.3: Information-Asymmetric Debate

**Academic basis**: AI Safety via Debate (Irving et al. 2018)

**What it would do**: give different perspectives access to different evidence subsets, then have them debate to determine which evidence is most relevant.

**Why it is deferred**: requires evidence routing infrastructure that does not exist. More importantly, it requires a fundamentally different evaluation architecture — current perspectives all evaluate the same draft output. Information-asymmetric debate requires a structure where perspectives produce competing drafts rather than evaluating a single draft.

---

## Family Summary Table

| # | Family | Lane | Scope | Infrastructure Needed | Distortion Risk |
|---|---|---|---|---|---|
| 1.1 | Forced devil's advocate | 1 (prompt) | ~10 lines prompt | None | Low: fake objections |
| 1.2 | Pre-mortem framing | 1 (prompt) | ~15 lines prompt | None | Low: catastrophizing |
| 1.3 | Explicit uncertainty declaration | 1 (prompt) | ~20 lines prompt | None | Low: inaccurate metacognition |
| 2.1 | Confidence decomposition | 2 (surface) | ~30-40 lines | None | Medium: treated as calibrated |
| 2.2 | Dissent quality metric | 2 (surface) | ~25 lines | None | Low: well-argued ≠ correct |
| 2.3 | Evolution suppression flag | 2 (surface) | ~10 lines | None | Low: over-reaction to flag |
| 3.1 | Self-consistency passes | 3 (code) | ~50-70 lines | LLM cost (3x) | Medium: consistency ≠ calibration |
| 3.2 | ACH-Lite hypothesis elimination | 3 (code) | ~50 lines | None | Medium: rigor illusion |
| 4.1 | Outcome-based calibration | 4 (blocked) | Large | Outcome pipeline | High if premature |
| 4.2 | Multi-model ensemble | 4 (blocked) | Large | Multi-model infra | High if hasty |
| 4.3 | Outcome-backed evolution | 4 (blocked) | Large | Outcome + credit | High if premature |
| 5.1 | Hidden-thought capture | 5 (deferred) | — | Paradigm shift | Very high |
| 5.2 | Adversarial training | 5 (deferred) | — | RLHF infra | Very high |
| 5.3 | Information-asymmetric debate | 5 (deferred) | — | Evidence routing | Very high |

---

## Recommended Implementation Order

If council quality becomes the next mainline focus, implement in this order:

### Wave 1: Honest Naming + Forced Dissent (Lane 1)

1. **Family 1.1**: Add forced devil's advocate to Critic prompt
2. **Family 1.3**: Add explicit uncertainty source declaration to all perspective prompts
3. Honest relabeling: rename "confidence" to "agreement_score" in documentation and dossier outputs

**Cost**: near zero. ~30 lines of prompt text changes.
**Impact**: prevents the two most common overclaims (unanimous approval = safe; confidence 0.85 = 85% accurate).

### Wave 2: Evaluation Surface Enrichment (Lane 2)

4. **Family 2.1**: Add confidence decomposition
5. **Family 2.3**: Add evolution suppression flag
6. **Family 2.2**: Add dissent quality metric

**Cost**: ~65 lines of code.
**Impact**: receivers get actionable multi-dimensional evaluation instead of opaque single numbers.

### Wave 3: Process Diversity (Lane 3, elevated_council only)

7. **Family 3.1**: Add self-consistency passes for elevated_council mode
8. **Family 1.2**: Add pre-mortem framing for elevated_council mode

**Cost**: ~65 lines of code + 3x LLM cost for elevated_council evaluations.
**Impact**: the closest achievable approximation to calibrated confidence without outcome tracking.

### Wave 4: When Infrastructure Permits (Lane 4)

9. **Family 4.1**: Outcome-based calibration (only after sufficient volume)
10. **Family 4.3**: Outcome-backed evolution reward (only after calibration exists)
11. **Family 4.2**: Multi-model ensemble (only if multi-model backend becomes available)

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` | Names the independence gaps; this document names the improvements |
| `TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md` | Names the calibration gaps; Families 2.1, 3.1, 4.1 directly address them |
| `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` | Dossier fields receive output from Families 1.1, 2.1, 2.2, 2.3 |
| `TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` | Mode selection determines which families apply (Lane 3 only in elevated_council) |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Families 2.1, 2.2, 2.3 increase shell observability |

---

## Canonical Handoff Line

Council quality improves in layers, not leaps. Layer 1: name things honestly — agreement is not accuracy, coherence is not confidence. Layer 2: decompose evaluation into independently assessable dimensions. Layer 3: add process diversity through repetition and adversarial framing. Layer 4: add structural diversity through outcome tracking and model diversity — but only when infrastructure supports it. Skip layers and you build a sophisticated system that still cannot tell you whether it is right. Follow the layers and each improvement is safe, bounded, and genuinely additive.
