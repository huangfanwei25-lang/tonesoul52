# Paper Outline: Truth as Multi-Perspective Coherence
# 論文大綱：多視角一致性作為真理

> **Target Venues**: NeurIPS Workshop, AAAI AIES, ACL  
> **Authors**: Fan-Wei Huang, et al.  
> **Status**: Draft Outline

---

## Abstract (摘要)

We propose a novel framework for AI truth validation that rejects the single-authority model in favor of **multi-perspective coherence**. Instead of grounding AI outputs in an external fact database, we define truth as the degree of internal agreement across multiple evaluative perspectives. We implement this in **PreOutputCouncil**, a pre-generation validation system that aggregates votes from four perspectives (Guardian, Analyst, Critic, Advocate) and computes a coherence score to determine whether to approve, refine, declare stance, or block output.

---

## 1. Introduction

### Problem Statement
- Current AI systems either:
  - Rely on retrieval-augmented generation (RAG) from single-source databases
  - Use simple safety filters (keyword blocking)
  - Lack transparency in decision-making

### Our Contribution
- A **multi-perspective truth model** where truth = internal coherence
- **PreOutputCouncil**: An implementable validation layer
- Shift from "is this factually correct?" to "do multiple perspectives agree?"

---

## 2. Related Work

### 2.1 Constitutional AI (Anthropic)
- Rule-based constraints
- Single-perspective (safety-focused)
- **Difference**: We use multi-perspective voting, not single constitution

### 2.2 Debate and Self-Critique
- AI debating itself for robustness
- **Difference**: We formalize perspectives with distinct roles

### 2.3 Multi-Agent Systems
- Multiple agents with different goals
- **Difference**: We use perspectives within single system, not independent agents

---

## 3. Framework: Truth as Multi-Perspective Coherence

### 3.1 Core Insight

> "Truth is not an external fact to be retrieved, but internal coherence to be computed."

### 3.2 Perspective Set P

```
P = {Guardian, Analyst, Critic, Advocate}
```

| Perspective | Focus | Key Question |
|-------------|-------|--------------|
| Guardian | Safety | Is this harmful? |
| Analyst | Factuality | Is this logically sound? |
| Critic | Blind spots | What could go wrong? |
| Advocate | User intent | Does this help the user? |

### 3.3 Coherence Score

**Inter-Perspective Coherence**:

```
C_inter = (1/N²) Σᵢ Σⱼ agree(Pᵢ(x), Pⱼ(x))
```

Where `agree(v1, v2)`:
- 1.0 if same decision
- 0.5 if adjacent decisions
- 0.0 if opposite decisions

### 3.4 Decision Rule

| C_inter | Decision |
|---------|----------|
| > 0.6 | APPROVE |
| 0.3-0.6 | DECLARE_STANCE |
| < 0.3 | BLOCK |

---

## 4. Implementation: PreOutputCouncil

### 4.1 Architecture

```
Input → [Guardian, Analyst, Critic, Advocate] → Votes → Coherence → Verdict
```

### 4.2 Perspective Implementation

Each perspective uses heuristic rules (keyword detection) + optional LLM evaluation:

```python
class GuardianPerspective:
    BLOCK_KEYWORDS = {"bomb", "kill", "harm", ...}
    
    def evaluate(self, draft) -> Vote:
        # Keyword-based + optional LLM reasoning
```

### 4.3 Verdict Generation

```python
def generate_verdict(votes, coherence):
    if guardian_objects:
        return BLOCK
    if coherence < 0.3:
        return BLOCK
    if coherence < 0.6:
        return DECLARE_STANCE
    return APPROVE
```

---

## 5. Experiments

### 5.1 Test Scenarios

| Scenario | Expected Verdict | Result |
|----------|------------------|--------|
| Safe, helpful response | APPROVE | ✅ |
| Harmful content | BLOCK | ✅ |
| Subjective topic (art) | DECLARE_STANCE | ✅ |
| Logical inconsistency | REFINE | ✅ |

### 5.2 Comparison with Baselines

| Method | Transparency | Multi-Perspective | Stance Declaration |
|--------|--------------|-------------------|-------------------|
| Keyword Filter | Low | No | No |
| Constitutional AI | Medium | No | No |
| **PreOutputCouncil** | High | Yes | Yes |

---

## 6. Discussion

### 6.1 Why Multi-Perspective?
- Single-authority models fail for subjective domains
- Multiple perspectives mirror human decision-making (e.g., committees)
- Coherence is computable; "absolute truth" is not

### 6.2 Limitations
- Perspective definitions are heuristic (could be learned)
- Coherence threshold requires tuning
- Does not solve knowledge acquisition problem

### 6.3 Philosophical Implications
- Connects to pragmatism (truth as what works)
- Connects to coherentism in epistemology
- Avoids metaphysical debates about "real truth"

---

## 7. Conclusion

We present a practical framework for AI truth validation based on multi-perspective coherence rather than external authority. Our implementation, PreOutputCouncil, demonstrates that:

1. **Truth can be computed** as agreement across perspectives
2. **Transparency is achievable** through explicit voting
3. **Stance declaration** is a valid alternative to forced consensus

Future work includes:
- Learning perspective weights from user feedback
- Scaling to more perspectives
- Integration with retrieval systems

---

## References (Preliminary)

1. Bai et al. (2022). Constitutional AI: Harmlessness from AI Feedback.
2. Irving et al. (2018). AI Safety via Debate.
3. Leike et al. (2018). Scalable agent alignment via reward modeling.
4. Huang (2026). ToneSoul: Semantic Responsibility in AI Systems.

---

*Outline drafted by Antigravity, for Fan-Wei Huang, 2026-01-10*
