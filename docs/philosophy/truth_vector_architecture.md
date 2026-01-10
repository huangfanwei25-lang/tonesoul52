# Truth Vector Architecture: Multi-Perspective Coherence

> **Version**: 0.1-draft  
> **Date**: 2026-01-10  
> **Author**: 黃梵威 (Fan-Wei Huang), formalized by Antigravity

---

## Core Insight (用戶原始表述)

> 「客觀的領域其實就是內在的相容。差別程度是可以量化的。  
> 寫實派、印象派，這些可能都在一個技術底下，觀點不同——  
> 它們就像語言有不同立場，沒有誰對誰錯，只是立場不同。  
> 這些內在衝突就像多人格的思緒，是可以兼容的。  
> 主要是看主體性要什麼。不同學派是**輸出前的互相應證**。」

---

## Framework: Truth as Coherence, Not Absolute

### Problem Statement

Traditional "Truth Vector" approaches assume:
```
Truth = External Fact Database → Single Ground Truth
```

**But this fails for**:
- **Subjective domains** (art, ethics, aesthetics)
- **Temporal knowledge** (facts that change over time)
- **Perspective-dependent facts** (cultural, contextual)

### Proposed Solution

**Truth = Internal Coherence across Multiple Perspectives**

```
                     ┌─────────────┐
                     │   Subject   │  (主體性 / User Intent)
                     │   Intent    │
                     └──────┬──────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
   ┌───────────┐     ┌───────────┐     ┌───────────┐
   │ School A  │     │ School B  │     │ School C  │
   │ (Realism) │     │(Impressio)│     │ (Abstract)│
   └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Coherence  │
                    │   Check     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Output    │
                    └─────────────┘
```

---

## Mathematical Model

### Perspective Vector Set

Let each "school of thought" be a perspective vector:

```
P = {P₁, P₂, ..., Pₙ}
```

Where:
- **P₁** = Realism (高事實權重)
- **P₂** = Impressionism (高情感權重)
- **P₃** = Pragmatism (高可行性權重)
- etc.

### Coherence Score

**Inter-Perspective Coherence**:

```
C_inter = (1/N²) Σᵢ Σⱼ cos(Pᵢ(x), Pⱼ(x))
```

Where `Pᵢ(x)` is perspective i's evaluation of statement x.

**High C_inter → All perspectives agree → Strong truth claim**  
**Low C_inter → Perspectives diverge → Stance declaration needed**

### Subject-Weighted Truth

The final "truth" incorporates the **subject's intent** (主體性):

```
T(x) = Σᵢ wᵢ · Pᵢ(x)
```

Where `wᵢ` is the weight of perspective i, determined by:
1. **User preference** (explicit)
2. **Context** (implicit, inferred from conversation)
3. **Default** (balanced weights)

---

## Integration with ToneSoul

### Mapping to Existing Systems

| New Concept | ToneSoul Equivalent | Notes |
|-------------|---------------------|-------|
| Perspective (Pᵢ) | Persona (師, 黑鏡, 共語) | Already exists! |
| Coherence Check | STREI Gate + Consensus | Needs enhancement |
| Subject Intent | User Profile / Context | Partial implementation |
| Multi-School Validation | **NEW** Pre-Output Council | To be implemented |

### Proposed Enhancement: Pre-Output Council

Before any output, convene a "council" of perspectives:

```python
class PreOutputCouncil:
    def validate(self, draft_output: str, context: Context) -> CouncilVerdict:
        perspectives = [
            Factual(),      # Does it match known facts?
            Ethical(),      # Does it align with values?
            Pragmatic(),    # Is it actionable?
            Aesthetic(),    # Is it well-formed?
        ]
        
        votes = [p.evaluate(draft_output, context) for p in perspectives]
        coherence = self.compute_coherence(votes)
        
        if coherence < COHERENCE_THRESHOLD:
            return CouncilVerdict.DECLARE_STANCE
        else:
            return CouncilVerdict.APPROVE
```

---

## Key Differences from Traditional Approaches

| Aspect | Traditional | Multi-Perspective |
|--------|-------------|-------------------|
| Truth Source | External database | Internal coherence |
| Handling Disagreement | Error / Fallback | Stance declaration |
| Subjectivity | Avoided | Embraced (with weights) |
| Temporal Changes | Version database | Perspective evolution |
| Multiple Valid Answers | Not allowed | Core feature |

---

## Open Questions

1. **How many perspectives are needed?** (Minimum viable set)
2. **How to weigh conflicting perspectives?** (Default weights)
3. **When to declare stance vs. give neutral answer?** (Threshold tuning)
4. **How to evolve perspectives over time?** (Learning mechanism)

---

## Next Steps

- [ ] Prototype `PreOutputCouncil` class
- [ ] Define standard perspective set (Factual, Ethical, Pragmatic, Aesthetic)
- [ ] Integrate with existing Persona system
- [ ] Add coherence metric to STREI vector
- [ ] Test with edge cases (art criticism, ethical dilemmas)

---

*This document is a living specification. The core insight comes from the ToneSoul creator's observation that internal coherence, not external authority, defines truth.*
