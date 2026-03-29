# ToneSoul Council Realism And Independence Contract

> Status: architectural honesty contract
> Purpose: define which parts of the current council are truly independent, which are perspective-voiced but not independent, and which claims later agents must avoid making about council realism
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - tonesoul/council/runtime.py (CouncilRuntime.deliberate)
>   - tonesoul/council/types.py (PerspectiveVote, CouncilVerdict, CoherenceScore)
>   - tonesoul/council/perspective_factory.py (_default_prompt, evaluate)
>   - tonesoul/council/pre_output_council.py (PreOutputCouncil.validate)
>   - tonesoul/council/evolution.py (CouncilEvolution)
>   - tonesoul/deliberation/types.py (ViewPoint, Tension, SynthesizedResponse)
>   - tonesoul/deliberation/perspectives.py (Muse, Logos, Aegis)
>   - spec/council_spec.md (perspective roles)
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md
>   - docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md
>   - docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md
> Scope: 2 council layers analyzed, 5 independence dimensions, 6 realism claims assessed

## How To Use This Document

If you are an AI agent describing what the council does, or deciding how much to trust a council verdict:

1. Check the **Independence Assessment** to understand what is and is not independent
2. Check the **Realism Claims** to know which statements about the council are safe versus overclaimed
3. Check the **What The Council Actually Provides** to understand genuine value without inflation

## Why This Document Exists

ToneSoul's council system produces votes, coherence scores, dissent ratios, and verdicts. These outputs look like the product of multi-agent deliberation. In many ways they are valuable — they surface different concerns, they flag risks, they create a structured decision record.

But the system also has structural limits that are easy to overclaim away. If later agents describe the council as "independent multi-agent debate" or "calibrated ensemble decision-making," they are attributing properties the system does not currently have.

This contract names the limits explicitly so the council's genuine value is preserved without inflation.

## Compressed Thesis

The council is a structured perspective multiplier, not an independent multi-agent debate system. Its value is in forcing multiple concern framings onto the same evidence — not in producing genuinely independent reasoning. This is valuable. It is also less than what "debate" or "ensemble" would imply in academic literature.

---

## Two Council Layers

ToneSoul has two distinct council-like systems. They must be assessed separately.

### Layer 1: Pre-Output Council

**Location**: `tonesoul/council/`

**Mechanism**: 4 perspectives (Guardian, Analyst, Critic, Advocate) + optional Axiomatic. Each evaluates the same `draft_output` + `context` through a different system prompt. Votes are collected, coherence is computed, verdict is generated.

**Modes**:
- `rules` — perspectives are deterministic keyword/pattern matchers (no LLM)
- `hybrid` — some perspectives use rules, others use LLM
- `full_llm` — all perspectives call an LLM with their role-specific system prompt

### Layer 2: Internal Deliberation

**Location**: `tonesoul/deliberation/`

**Mechanism**: 3 voices (Muse, Logos, Aegis). Multi-round adaptive debate with tension tracking. Produces a `SynthesizedResponse` with viewpoints, tensions, and dominant voice.

**Modes**:
- Rules-based with pattern matching and heuristic weighting
- Optional multi-round debate via `adaptive_rounds.py`

---

## Independence Assessment

Independence has multiple dimensions. The council is strong on some and weak on others.

### Dimension 1: Information Independence

**Question**: Do perspectives see different information?

**Assessment**: **No.** All perspectives in Layer 1 receive the same `draft_output`, `context`, and `user_intent` via the `evaluate()` method in `perspective_factory.py`. All voices in Layer 2 receive the same `DeliberationContext`.

**Why it matters**: in real multi-agent debate (Irving et al. 2018, Du et al. 2023), agents may see different evidence, explore different reasoning paths, or have access to different tools. ToneSoul's perspectives cannot disagree because they know different things — they can only disagree because they are prompted to evaluate differently.

**Impact**: "the council considered multiple sources of evidence" is overclaimed. The council considered multiple *framings* of the same evidence.

### Dimension 2: Model Independence

**Question**: Do perspectives use different reasoning engines?

**Assessment**: **No in single-model mode.** In `full_llm` mode, all perspectives call the same underlying LLM (Gemini or equivalent) with different system prompts. They share the same model weights, training data, and reasoning biases.

In `rules` mode, perspectives are deterministic keyword matchers — they have no reasoning engine at all.

**Why it matters**: ensemble methods gain power from model diversity (Lakshminarayanan et al. 2017). Five system prompts on one model produce correlated errors — they will share the same blind spots.

**Impact**: "the council uses ensemble reasoning" is overclaimed. The council uses single-model perspective multiplication.

### Dimension 3: Process Independence

**Question**: Can one perspective's output influence another's?

**Assessment**: **Mostly independent in Layer 1.** In `PreOutputCouncil.validate()`, all perspectives evaluate in a sequential loop but do not see each other's votes. The votes are collected independently and then aggregated.

**Partially coupled in Layer 2.** Adaptive deliberation runs multiple rounds where prior-round viewpoints may influence later rounds via `prior_viewpoints` in `DeliberationContext`.

**Impact**: Layer 1 votes are process-independent (good). Layer 2 may exhibit convergence pressure across rounds (concern: is convergence genuine agreement or prompt-induced compliance?).

### Dimension 4: Stake Independence

**Question**: Do perspectives have different incentives?

**Assessment**: **No.** All perspectives share the same training objective (be helpful, follow instructions). No perspective has a genuine stake in a particular outcome. The Critic is *prompted* to find weaknesses but is not *incentivized* to find them.

**Why it matters**: real adversarial processes (legal cross-examination, red teaming) work because the adversary has genuine incentive to find flaws. Prompted adversarialism is weaker than incentivized adversarialism.

**Impact**: "the Critic provides adversarial scrutiny" is partially overclaimed. The Critic provides prompted skepticism, which is valuable but structurally weaker than genuine adversarial incentive.

### Dimension 5: Temporal Independence

**Question**: Are perspectives evaluated at different times with potentially different context?

**Assessment**: **No in Layer 1** (all evaluate synchronously). **Partially yes in Layer 2** (adaptive rounds occur sequentially, with new tension information available between rounds).

**Impact**: Layer 2's multi-round debate is closer to genuine deliberation than Layer 1's single-pass voting.

---

## Independence Summary Table

| Dimension | Layer 1 (Pre-Output Council) | Layer 2 (Internal Deliberation) |
|---|---|---|
| Information | Same input for all perspectives | Same input for all voices |
| Model | Same LLM (or same rules engine) | Same rules engine |
| Process | Independent votes (good) | Coupled across rounds (mixed) |
| Stake | No genuine incentive (prompted only) | No genuine incentive |
| Temporal | Synchronous (single pass) | Sequential rounds (partial independence) |

---

## What The Council Actually Provides

Despite the independence limitations, the council provides genuine value that should not be dismissed:

### 1. Structured Concern Multiplexing

The council forces 4-5 different concern framings onto the same output. Guardian checks safety, Analyst checks accuracy, Critic checks weaknesses, Advocate checks user intent. Even without independence, this catches concerns that a single evaluator would miss.

**Analogy**: a code review checklist (security, performance, readability, correctness) is not the same as 4 independent reviewers. But it catches more issues than no checklist at all.

### 2. Quantified Disagreement Signal

`coherence_score` and `dissent_ratio` provide a quantified signal that the system is not unanimously confident. Even if the disagreement is prompt-induced rather than evidence-induced, the signal itself is useful: low coherence means "this output does not satisfy all concern framings."

### 3. Auditable Decision Record

The council produces a structured transcript with votes, reasoning, evidence refs, and divergence analysis. This is an auditable shell (per Observable Shell Opacity Contract) that is more useful than a binary approve/reject.

### 4. Evolution-Tracked History

`CouncilEvolution` tracks perspective alignment and weight changes over time. Even with its conformity bias problem, it provides a signal of how consistently perspectives agree — which is useful metadata even if the weights themselves need improvement.

---

## Realism Claims Assessment

| Claim | Safe To Make? | Why |
|---|---|---|
| "The council provides multi-perspective evaluation" | **Yes** | Multiple concern framings are applied. This is perspective multiplication, which is real. |
| "The council provides independent multi-agent debate" | **No** | Perspectives are not independent by any of the 5 dimensions assessed. |
| "The council provides calibrated confidence" | **No** | Confidence values are uncalibrated. See Confidence And Calibration Map. |
| "The council provides ensemble decision-making" | **No** | Ensemble requires model diversity. Single-model perspective multiplication is not ensemble. |
| "The council surfaces concerns that a single pass would miss" | **Yes** | Structured concern framings catch more issues than no structure. |
| "The council's dissent reflects genuine disagreement" | **Partially** | Dissent reflects prompted concern-framing disagreement, not evidence-based or incentive-based disagreement. |

---

## Claims Later Agents Must Not Make

1. **"The council verified this output."** The council evaluated this output against multiple concern framings. It did not verify it against ground truth.

2. **"All perspectives agreed, so the output is safe."** All perspectives share the same information and model. Unanimous agreement may reflect shared blind spots, not comprehensive safety.

3. **"The Critic found no issues."** The Critic is a prompted skeptic with the same information as other perspectives. It may miss issues that a genuine adversary with different information would catch.

4. **"Council confidence is 0.85, so we are 85% certain."** Council confidence is a coherence metric, not a calibrated probability. See Confidence And Calibration Map.

5. **"The council debate resolved the tension."** Multi-round convergence in Layer 2 may reflect genuine resolution or prompt-induced compliance. The difference is not currently observable.

---

## What Would Make The Council More Real

These are structural changes that would move the council toward genuine independence. They are not recommendations — they are the truthful answer to "what is missing?"

| Missing Property | What Would Provide It | Current Status |
|---|---|---|
| Information independence | Different perspectives receive different evidence subsets | Not implemented; would require evidence routing |
| Model independence | Different perspectives use different models or model configurations | Not implemented; would require multi-model infrastructure |
| Incentive independence | Critic has a measurable reward for finding real issues | Not implemented; would require outcome tracking |
| Temporal independence | Perspectives evaluate at different times with accumulating evidence | Partially present in Layer 2 adaptive rounds |
| Calibrated confidence | Historical accuracy of council predictions is tracked and used to adjust confidence | Not implemented; requires outcome tracking infrastructure |

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` | Dossier preserves whatever the council produces; this contract clarifies what the council actually produces |
| `TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` | Mode selection determines depth; this contract clarifies that depth does not equal independence |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Council verdict is classified as `partially_observable`; this contract explains why |
| `TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md` | Companion: this contract assesses independence; calibration map assesses confidence quality |
| `TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md` | Companion: this contract names the gaps; adoption map names the improvements |

---

## Canonical Handoff Line

The council is a structured perspective multiplier. It forces multiple concern framings onto the same evidence and produces a quantified disagreement signal with an auditable decision record. This is genuinely valuable. It is also not independent debate, not calibrated ensemble, and not adversarial scrutiny in the academic sense. Name what it is. Preserve what it does. Do not inflate what it is not.
