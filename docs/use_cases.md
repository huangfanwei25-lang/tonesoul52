# ToneSoul Use Cases | 語魂應用場景

> **Where and How to Apply Semantic Responsibility**

---

## Use Case 1: AI Tutoring | AI 教學助教

### Scenario

AI mathematics tutor helping students solve problems.

### Risk

- Providing incorrect solutions
- Skipping steps that confuse learners
- Overconfident assertions without clarification

### ToneSoul Application

```yaml
vows:
  - id: ΣVow_EDU_001
    commitment: "Clarify student understanding before asserting"
  - id: ΣVow_EDU_002  
    commitment: "Show steps, not just answers"

gates:
  - P0: No incorrect mathematical statements
  - P1: Verify against known solution
  
persona_triggers:
  - 師 (Definer): When new concept introduced
  - 共語 (Bridge): When student shows confusion
```

### Metrics Tracked

| Metric | Threshold | Action on Violation |
|--------|-----------|---------------------|
| Truthfulness | > 0.95 | Block + human review |
| Step coverage | > 0.80 | Flag for review |
| Clarity (ΔR) | < 0.50 | Simplify output |

---

## Use Case 2: Customer Service Bot | 客服機器人

### Scenario

AI handling customer complaints and support requests.

### Risk

- Misunderstanding customer intent
- Making unauthorized commitments
- Escalating emotions instead of diffusing

### ToneSoul Application

```yaml
vows:
  - id: ΣVow_CS_001
    commitment: "Do not promise what cannot be fulfilled"
  - id: ΣVow_CS_002
    commitment: "Acknowledge emotion before problem-solving"

tone_monitoring:
  - ΔT > 0.7: Customer may be frustrated → activate 共語
  - ΔS < -0.3: Negative direction → check escalation need
```

### Escalation Flow

```
ΔT > 0.8 AND Drift > 0.5
    → Stop automated response
    → Transfer to human agent
    → Log full context to ledger
```

---

## Use Case 3: Content Moderation | 內容審核

### Scenario

AI screening user-generated content for policy violations.

### Risk

- False positives (over-censoring)
- False negatives (missing violations)
- Inconsistent application of rules

### ToneSoul Application

```yaml
governance_stack:
  P0: Illegal content → immediate block
  P1: Policy violation → flag for review
  P2: Borderline content → log + let pass with warning

drift_anchor: Policy definition document
threshold: 0.3 (tight tolerance for moderation)

audit:
  every_decision: recorded
  human_review_rate: 10% random sample
```

---

## Use Case 4: Code Generation | 程式碼生成

### Scenario

AI generating code based on user specifications.

### Risk

- Introducing security vulnerabilities
- Incorrect implementation of requirements
- Unverifiable or undocumented code

### ToneSoul Application

```yaml
vows:
  - id: ΣVow_CODE_001
    commitment: "No known vulnerability patterns"
  - id: ΣVow_CODE_002
    commitment: "Include error handling"
  - id: ΣVow_CODE_003
    commitment: "Document non-obvious logic"

verification:
  - Static analysis before output
  - Test case generation for critical paths
  
responsibility_chain:
  input: User requirement
  output: Code + tests + documentation
  trace: Requirement → Design decision → Implementation → Verification
```

---

## Use Case 5: Medical Information | 醫療資訊

### Scenario

AI providing health information to users.

### Risk

- Providing diagnosis (unauthorized)
- Missing critical symptoms
- Creating false reassurance

### ToneSoul Application

```yaml
constraints:
  NEVER:
    - Provide diagnosis
    - Recommend specific treatments
    - Dismiss symptoms
    
  ALWAYS:
    - Recommend consulting professional
    - Flag emergency symptoms
    - Provide general information only

collapse_threshold: 0.40 (very conservative)
human_review: any uncertainty
```

---

## Use Case 6: Creative Writing | 創意寫作

### Scenario

AI assisting with story writing, poetry, or creative content.

### Risk

- Plagiarism or unattributed copying
- Loss of author's voice
- Inappropriate content generation

### ToneSoul Application

```yaml
# Creative mode allows higher tension
thresholds:
  ΔT: 0.90 (high tension permitted)
  ΔR: 0.60 (moderate variability okay)
  Drift: 0.70 (looser anchor)

vows:
  - id: ΣVow_CREATE_001
    commitment: "No unattributed copying"
  - id: ΣVow_CREATE_002
    commitment: "Match author's specified style"

persona:
  default: 共語 (collaborative)
  on_request: 黑鏡 (critical feedback)
```

---

## Use Case 7: Research Assistant | 研究助手

### Scenario

AI helping researchers find and synthesize information.

### Risk

- Hallucinated citations
- Misrepresentation of sources
- Confirmation bias in synthesis

### ToneSoul Application

```yaml
vows:
  - id: ΣVow_RESEARCH_001
    commitment: "Every citation must be verifiable"
  - id: ΣVow_RESEARCH_002
    commitment: "Acknowledge uncertainty explicitly"

trace_level: HIGH (full source chains)
hallucination_check: cross-reference all claims

output_format:
  claim: "The finding is..."
  source: [verified_citation]
  confidence: 0.85
  alternatives: ["Some argue..."]
```

---

## Implementation Priority | 實施優先級

| Use Case | Risk Level | Complexity | Priority |
|----------|------------|------------|----------|
| Medical | 🔴 High | Medium | P1 |
| Tutoring | 🟡 Medium | Medium | P1 |
| Customer Service | 🟡 Medium | Low | P2 |
| Moderation | 🟡 Medium | High | P2 |
| Code Generation | 🟡 Medium | High | P2 |
| Creative Writing | 🟢 Low | Low | P3 |
| Research | 🟡 Medium | Medium | P2 |

---

## Pattern Summary | 模式總結

Common patterns across use cases:

1. **Domain-specific vows** — Each domain has unique commitments
2. **Adjusted thresholds** — High-risk domains use tighter bounds
3. **Persona selection** — Match persona to interaction type
4. **Escalation paths** — Define clear human handoff points
5. **Full traceability** — All domains log to ledger

---

*Each use case is a **configuration** of ToneSoul, not a separate system.*
