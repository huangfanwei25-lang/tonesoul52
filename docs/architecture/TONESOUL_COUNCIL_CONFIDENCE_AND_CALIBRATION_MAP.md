# ToneSoul Council Confidence And Calibration Map

> Status: architectural analysis document
> Purpose: map every confidence-bearing surface in the council system, classify each as descriptive or calibrated, name the evidence gap between current state and calibrated state, and identify which calibration approaches are plausible now versus infrastructure-blocked
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - tonesoul/council/runtime.py (CouncilRuntime.deliberate, build_council_summary)
>   - tonesoul/council/types.py (PerspectiveVote, CoherenceScore, CouncilVerdict)
>   - tonesoul/council/pre_output_council.py (PreOutputCouncil.validate)
>   - tonesoul/council/evolution.py (CouncilEvolution)
>   - tonesoul/deliberation/types.py (ViewPoint, Tension, TensionZone, SynthesizedResponse)
>   - docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md
>   - docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md
> Scope: 8 confidence surfaces mapped, 4 calibration approaches assessed

## How To Use This Document

If you are an AI agent reading a council output that contains a number labeled "confidence," "coherence," "dissent," or similar:

1. Check the **Confidence Surface Inventory** to understand what that number actually measures
2. Check the **Descriptive vs Calibrated** classification to know whether the number tells you about internal agreement or about real-world accuracy
3. Check the **Calibration Gap Table** to understand what would need to exist for the number to be calibrated
4. Do not quote council confidence numbers as probabilities

## Why This Document Exists

ToneSoul's council produces multiple numerical outputs: perspective confidence, coherence scores, dissent ratios, uncertainty levels, uncertainty bands. These numbers look like calibrated confidence — they use familiar vocabulary (confidence, uncertainty, coherence) and familiar ranges (0.0 to 1.0).

But none of these numbers are calibrated in the technical sense. A calibrated confidence of 0.80 means: of all predictions made with confidence 0.80, approximately 80% turn out correct. ToneSoul's council has no outcome tracking, no historical accuracy measurement, no post-hoc correction mechanism. Its numbers are internally descriptive — they describe how much the perspectives agreed — not externally calibrated — they do not predict how likely the output is to be correct.

This distinction matters because later agents and humans will naturally interpret 0.85 confidence as "the system is 85% sure." It is not. It is "85% of perspectives approved." These are very different claims.

## Compressed Thesis

Every confidence-bearing surface in ToneSoul's council is descriptive: it measures internal agreement among perspectives that share the same information, model, and incentives. No surface is calibrated: none are grounded in historical accuracy data. The gap between descriptive and calibrated is not a code fix — it requires outcome tracking infrastructure that ToneSoul does not yet have. Until that infrastructure exists, the honest posture is to label every confidence surface as "agreement metric, not accuracy predictor."

---

## Confidence Surface Inventory

### Surface 1: PerspectiveVote.confidence

**Location**: `tonesoul/council/types.py` — `PerspectiveVote` dataclass

**What it measures**: how confident a single perspective is in its own vote. Range 0.0 to 1.0.

**How it is produced**:
- In `rules` mode: deterministic — keyword/pattern match produces a fixed confidence value
- In `full_llm` mode: the LLM self-reports confidence based on its system prompt evaluation

**Classification**: **Descriptive (self-reported)**. In rules mode, confidence is a design-time constant, not a runtime measurement. In LLM mode, LLM self-reported confidence is well-known to be poorly calibrated (Kadavath et al. 2022, Xiong et al. 2023) — LLMs tend to be overconfident and their confidence does not track accuracy reliably.

**Misuse risk**: treating `confidence: 0.90` from Guardian as "Guardian is 90% sure this is safe." It is not — it is "Guardian's prompt produced a 0.90 confidence score for this evaluation."

### Surface 2: CoherenceScore.overall

**Location**: `tonesoul/council/types.py` — `CoherenceScore` dataclass

**What it measures**: the weighted inter-perspective agreement across all votes. Combines `c_inter` (pairwise agreement), `approval_rate`, `min_confidence`, and `has_strong_objection`.

**How it is produced**: `PreOutputCouncil.validate()` computes it from the collected `PerspectiveVote` objects. If `CouncilEvolution` weights are available, they modify perspective influence.

**Classification**: **Descriptive (agreement metric)**. Coherence measures how much perspectives agree. High coherence means "all perspectives, using the same information and model, reached similar conclusions." It does not mean "the conclusion is likely correct." Per the Independence Contract, high agreement among non-independent perspectives may reflect shared blind spots rather than robust validation.

**Misuse risk**: treating `coherence: 0.92` as "the system is 92% confident." It is "92% agreement among perspectives that share all information and model weights."

### Surface 3: CouncilVerdict.uncertainty_level

**Location**: `tonesoul/council/types.py` — `CouncilVerdict` dataclass

**What it measures**: a categorical uncertainty classification derived from coherence and vote patterns. Values: high, moderate, low.

**How it is produced**: `build_council_summary()` in `runtime.py` derives it from coherence score thresholds.

**Classification**: **Descriptive (threshold-derived)**. This is a binned version of coherence — it inherits all of coherence's limitations. "Low uncertainty" means "high agreement," not "the output is very likely correct."

**Misuse risk**: treating `uncertainty_level: low` as equivalent to "this output is safe to ship without review."

### Surface 4: CouncilVerdict.uncertainty_band

**Location**: `tonesoul/council/types.py` — `CouncilVerdict` dataclass

**What it measures**: a descriptive band providing narrative context for the uncertainty level. E.g., "narrow" or "wide."

**How it is produced**: derived from coherence and dissent metrics in `build_council_summary()`.

**Classification**: **Descriptive (narrative label)**. A human-readable wrapper around the same underlying agreement metric. Adds no calibration information.

### Surface 5: dissent_ratio

**Location**: computed in `build_council_summary()` in `runtime.py`

**What it measures**: the proportion of perspectives that voted CONCERN or OBJECT versus total votes. Range 0.0 to 1.0.

**How it is produced**: count of non-approving votes divided by total votes.

**Classification**: **Descriptive (voting fraction)**. This is one of the most honest surfaces — it directly reports what happened (X out of Y perspectives dissented) without implying accuracy. However, it can still be misused: a dissent ratio of 0.0 does not mean "no valid concerns exist" — it means "no prompted perspective raised a concern."

**Misuse risk**: treating `dissent_ratio: 0.0` as "there are no concerns about this output."

### Surface 6: Dossier confidence_posture

**Location**: defined in `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`

**What it measures**: a four-level classification of how confident the council outcome is — `high`, `moderate`, `contested`, `low`.

**How it is produced**: derived from coherence score and dissent ratio thresholds:
- `high`: coherence ≥ 0.8, dissent_ratio < 0.2
- `moderate`: coherence 0.5-0.8, dissent_ratio < 0.4
- `contested`: dissent_ratio ≥ 0.4 or coherence < 0.5
- `low`: coherence < 0.3

**Classification**: **Descriptive (binned agreement)**. This is a well-designed summary of the agreement state — it clearly communicates the council's internal consistency. But it is not calibrated: "high confidence" means "high agreement," not "high likelihood of correctness."

**Misuse risk**: treating `confidence_posture: high` as "the council is highly confident this is right" rather than "the council's perspectives highly agree."

### Surface 7: ViewPoint.confidence (Deliberation Layer)

**Location**: `tonesoul/deliberation/types.py` — `ViewPoint` dataclass

**What it measures**: how confident a deliberation voice (Muse, Logos, or Aegis) is in its viewpoint. Range 0.0 to 1.0.

**How it is produced**: rules-based pattern matching produces confidence based on keyword density and heuristic weights.

**Classification**: **Descriptive (heuristic-derived)**. The confidence value reflects how strongly the voice's patterns matched the input — it is a pattern strength metric, not an accuracy predictor.

### Surface 8: TensionZone classification

**Location**: `tonesoul/deliberation/types.py` — `TensionZone` enum

**What it measures**: aggregate tension level across deliberation: ECHO_CHAMBER (< 0.3), SWEET_SPOT (0.3-0.7), CHAOS (> 0.7).

**How it is produced**: average of individual `Tension.severity` values.

**Classification**: **Descriptive (tension metric)**. This is not confidence — it is a disagreement measure. But it carries implicit confidence semantics: ECHO_CHAMBER suggests "everyone agrees" (which feels confident) and CHAOS suggests "deep disagreement" (which feels uncertain). The zone names themselves carry calibration-like connotations that the underlying metric does not support.

**Misuse risk**: treating ECHO_CHAMBER as "the system is confident" when it may actually indicate that perspectives lack diversity (per Independence Contract, Dimension 1).

---

## Descriptive vs Calibrated: The Core Distinction

### What "descriptive" means

A **descriptive** confidence surface reports an internal property of the evaluation process:
- How many perspectives agreed
- How strongly a pattern matched
- How much tension exists between voices

Descriptive surfaces answer: "What happened inside the council?"

### What "calibrated" means

A **calibrated** confidence surface reports an external property verified against outcomes:
- Of all outputs where the council said confidence was 0.80, approximately 80% were correct
- Of all outputs marked "high confidence," the error rate was below 5%
- Uncertainty level "low" correlates with less than 10% downstream rework

Calibrated surfaces answer: "How often is the council right when it says X?"

### Why the distinction matters

| Scenario | Descriptive interpretation | Calibrated interpretation |
|---|---|---|
| Coherence 0.95 | All perspectives agreed | Output is very likely correct |
| Dissent ratio 0.0 | No perspective raised a concern | No valid concerns exist |
| Confidence 0.85 | The perspective's prompt produced 0.85 | The perspective is right 85% of the time |
| Uncertainty: low | Perspectives converged | The output rarely needs correction |

The left column is what ToneSoul's numbers actually mean. The right column is what they would mean if calibrated. Every current surface is in the left column only.

---

## Classification Summary

| Surface | Type | Basis | Calibrated? | Can Be Calibrated Without Infrastructure? |
|---|---|---|---|---|
| PerspectiveVote.confidence | Self-reported | LLM or rules constant | No | No — requires outcome tracking |
| CoherenceScore.overall | Agreement metric | Weighted vote agreement | No | No — requires outcome tracking |
| uncertainty_level | Threshold-derived | Binned coherence | No | No — requires outcome tracking |
| uncertainty_band | Narrative label | Binned coherence | No | No — inherits from uncertainty_level |
| dissent_ratio | Voting fraction | Vote count | No | Partially — could track dissent-vs-rework correlation |
| confidence_posture | Binned agreement | Coherence + dissent thresholds | No | No — requires outcome tracking |
| ViewPoint.confidence | Heuristic | Pattern match strength | No | No — requires outcome tracking |
| TensionZone | Tension metric | Average tension severity | No | No — requires outcome tracking |

---

## What Would Make Council Confidence Calibrated

### Requirement 1: Outcome Tracking

To calibrate any confidence surface, ToneSoul needs to know: **was the council's output actually correct?**

This requires:
- A definition of "correct" for each output type (safety evaluation, content quality, task routing)
- A mechanism to record outcomes (human feedback, downstream failure tracking, rework detection)
- A sufficient sample size (hundreds to thousands of recorded outcomes)

**Current status**: not implemented. No outcome recording exists. The council produces evaluations but never learns whether they were right.

**Infrastructure needed**: outcome annotation pipeline — either human-in-the-loop feedback or downstream signal capture (e.g., "this output was later flagged by a human" or "this task required rework").

### Requirement 2: Historical Bucketing

Once outcomes are tracked, calibration requires bucketing:
- Group all council outputs by their confidence level (e.g., all outputs with coherence 0.8-0.9)
- Measure the actual accuracy rate within each bucket
- Compare predicted accuracy (implied by the confidence value) to actual accuracy

**Current status**: not possible without Requirement 1.

**Infrastructure needed**: outcome database queryable by confidence surface values.

### Requirement 3: Post-Hoc Correction

If bucketing reveals miscalibration (e.g., coherence 0.90 outputs are only correct 70% of the time), apply a correction function:
- Platt scaling (Platt 1999): fit a sigmoid to map raw confidence to calibrated probability
- Temperature scaling (Guo et al. 2017): single-parameter recalibration
- Isotonic regression: non-parametric calibration

**Current status**: not possible without Requirements 1 and 2.

**Infrastructure needed**: calibration function that adjusts confidence surfaces before they are published.

### Requirement 4: Ongoing Monitoring

Calibration drifts over time as models change, prompts change, and task distributions shift. A calibrated system must continuously monitor whether its calibration still holds.

**Current status**: not applicable (no calibration to monitor).

**Infrastructure needed**: calibration monitoring dashboard or automated recalibration trigger.

---

## Calibration Approaches Assessment

### Approach 1: Self-Consistency (Wang et al. 2022)

**Method**: run the council multiple times on the same input with different sampling temperatures. If the council reaches the same verdict across multiple runs, confidence is higher. If verdicts vary, confidence is lower.

**Fit with ToneSoul**: plausible for `full_llm` mode. Each perspective could be evaluated N times (e.g., 3-5 runs) with temperature > 0. Consistency across runs provides a rough confidence signal that is better calibrated than single-run self-report.

**What it requires**: multiple LLM calls per perspective (cost multiplier: 3-5x). A consistency aggregation function.

**Lane**: helper-level code change + cost increase. No infrastructure dependency.

**Limitation**: still measures agreement among runs of the same model — not genuinely independent reasoning. But empirically, self-consistency provides better-calibrated confidence than single-pass self-report (Wang et al. 2022).

**Distortion risk if adopted badly**: treating consistency as calibration rather than as an improved heuristic. Self-consistency is better than single-pass confidence but still not calibrated against outcomes.

### Approach 2: Historical Outcome Tracking

**Method**: record whether council outputs were correct (via human feedback or downstream signals). Build a calibration curve mapping coherence/confidence values to actual accuracy rates.

**Fit with ToneSoul**: this is the gold standard for calibration. But it requires infrastructure that does not exist: outcome annotation, sufficient volume, and a definition of "correct."

**What it requires**: outcome recording pipeline, human feedback mechanism, sample size (hundreds minimum for meaningful calibration), calibration function.

**Lane**: infrastructure-blocked. This is the right long-term answer but cannot be done incrementally.

**Limitation**: requires human effort to annotate outcomes. May never reach statistical significance for rare event types (e.g., BLOCK verdicts).

### Approach 3: Post-Hoc Calibration (Platt Scaling / Temperature Scaling)

**Method**: given historical data, fit a simple function that maps raw confidence to calibrated probability.

**Fit with ToneSoul**: purely depends on Approach 2 (outcome tracking). Cannot be implemented without historical data.

**What it requires**: all of Approach 2's requirements, plus a calibration function (Platt: logistic regression; temperature: single parameter optimization).

**Lane**: infrastructure-blocked. Depends entirely on outcome tracking.

### Approach 4: Confidence Decomposition

**Method**: instead of producing a single confidence number, decompose confidence into orthogonal components that the receiver can evaluate independently:

```
confidence_decomposition:
  agreement: 0.90       # how much perspectives agreed
  coverage: 0.60        # how many distinct concern types were evaluated
  evidence_density: 0.40 # how much evidence was cited vs asserted
  adversarial_survived: false  # did the output survive adversarial scrutiny
```

**Fit with ToneSoul**: plausible now. Does not require outcome tracking — it replaces a single misleading number with multiple honest descriptive dimensions.

**What it requires**: ~30-50 lines of code to compute decomposition components from existing council outputs.

**Lane**: safe evaluation-surface addition. No infrastructure dependency.

**Limitation**: does not produce calibrated confidence. But it makes the descriptive nature explicit and gives receivers better information for their own judgment.

**Distortion risk if adopted badly**: the decomposition itself becomes treated as calibrated (e.g., "coverage is 0.60, so 60% of concerns were checked"). The components are still descriptive — they describe the evaluation process, not the output's accuracy.

---

## What Is Plausible Now vs Infrastructure-Blocked

| Approach | Plausible Now? | Why / Why Not |
|---|---|---|
| Self-consistency (multiple runs) | Yes, with cost trade-off | Requires only multiple LLM calls, no infrastructure |
| Confidence decomposition | Yes | Requires only code to compute components from existing surfaces |
| Honest labeling ("agreement, not accuracy") | Yes | Requires only documentation and naming changes |
| Historical outcome tracking | No | Requires annotation pipeline, human feedback, sample volume |
| Platt/temperature scaling | No | Requires historical outcome data |
| Ongoing calibration monitoring | No | Requires calibrated baseline to monitor |

---

## Recommended Posture Until Calibration Exists

### 1. Name every confidence surface honestly

Replace implied accuracy labels with explicit agreement labels in documentation, dossier outputs, and agent instructions:

| Current label | Honest replacement |
|---|---|
| "confidence: 0.85" | "agreement_score: 0.85" |
| "uncertainty: low" | "disagreement: low" |
| "high confidence posture" | "high agreement posture" |

### 2. Add confidence decomposition (Approach 4)

This is the safest improvement: it replaces one misleading number with multiple honest dimensions. It can be implemented now with ~30-50 lines of code and no infrastructure dependency.

### 3. Consider self-consistency for elevated council mode

When the council operates in `elevated_council` mode (high-stakes tasks), running each perspective 3 times and measuring consistency provides a better confidence signal than single-pass evaluation. This has a 3x cost multiplier but is bounded and well-understood.

### 4. Defer outcome tracking until the system has enough volume

Outcome tracking is the right long-term answer but requires infrastructure investment that only pays off at scale. ToneSoul should not build this until it has enough council evaluations (hundreds minimum) to produce statistically meaningful calibration data.

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` | Companion: independence assessment explains why agreement metrics are not accuracy predictors |
| `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` | Dossier's `confidence_posture` field is assessed here as descriptive |
| `TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` | Mode selection should factor in confidence quality (elevated mode has more perspective diversity) |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Confidence surfaces are part of the partially_observable shell — this document clarifies their opacity |
| `TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md` | Companion: adversarial methods may improve confidence quality more than calibration alone |

---

## Canonical Handoff Line

Every confidence number the council produces is a measure of internal agreement, not external accuracy. Coherence tells you how much perspectives agreed. Dissent ratio tells you how many objected. Neither tells you whether the output is correct. Until outcome tracking exists, the honest posture is: name these numbers as agreement metrics, decompose them into independently evaluable dimensions, and never present them as probabilities. Agreement is valuable. Agreement is not calibration.
