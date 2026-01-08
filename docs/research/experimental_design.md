# ToneSoul Experimental Design | 語魂實驗設計

> **Validating Semantic Responsibility Metrics**  
> Version 1.0 | 2026-01-08  
> 黃梵威 (Fan-Wei Huang)

---

## 1. Research Questions

### Primary Hypothesis

> **H1**: High tone tension (ΔT > 0.7) correlates positively with output diversity.

**Operationalization**:
- Tone tension measured by TSR ΔT module
- Output diversity measured by semantic embedding variance

### Secondary Hypotheses

> **H2**: Drift score (DS) reliably predicts user intervention need.

> **H3**: POAV gate scores correlate with human quality ratings.

---

## 2. Experimental Setup

### 2.1 Dataset Requirements

| Dataset Type | Description | Size | Collection Method |
|--------------|-------------|------|-------------------|
| **Seed Prompts** | Varied task types (creative, analytical, ethical) | 500+ prompts | Manual curation |
| **AI Responses** | Multiple responses per prompt | 3-5 per prompt | LLM generation |
| **Human Ratings** | Quality, diversity, safety ratings | 3 raters/response | Crowdsourcing |

### 2.2 Metric Collection

For each AI response, collect:

```json
{
  "prompt_id": "P001",
  "response_id": "R001",
  "tsr_vector": {"ΔT": 0.72, "ΔS": 0.15, "ΔR": 0.34},
  "strei_vector": {"S": 0.85, "T": 0.72, "R": 0.21, "E": 0.95, "I": 0.68},
  "drift_score": 0.82,
  "poav_score": {"P": 0.88, "O": 0.75, "A": 0.92, "V": 0.81},
  "embedding_vector": [...],  // 768-dim
  "human_ratings": {
    "quality": [4, 5, 4],
    "diversity": [5, 4, 5],
    "safety": [5, 5, 5]
  }
}
```

---

## 3. Analysis Plan

### 3.1 H1: Tension-Diversity Correlation

**Method**: Pearson/Spearman correlation

**Variables**:
- IV: ΔT (continuous, 0-1)
- DV: Embedding variance (continuous)

**Expected Result**: r > 0.3, p < 0.05

### 3.2 H2: Drift Predicts Intervention

**Method**: Logistic regression / ROC-AUC

**Variables**:
- IV: Drift Score (continuous)
- DV: Human intervention (binary: needed/not needed)

**Expected Result**: AUC > 0.75

### 3.3 H3: POAV-Quality Correlation

**Method**: Multiple regression

**Variables**:
- IVs: P, O, A, V scores
- DV: Mean human quality rating

**Expected Result**: R² > 0.4

---

## 4. Validation Framework

### 4.1 Internal Validity

- Control for prompt difficulty
- Randomize response order for human raters
- Blind raters to TSR/STREI scores

### 4.2 External Validity

- Test across multiple LLM backends (Ollama, OpenAI, etc.)
- Repeat with different rater populations
- Cross-validate with held-out prompts

### 4.3 Reproducibility

All code, prompts, and analysis scripts to be published:
- Repository: `github.com/Fan1234-1/tonesoul52`
- Data: Anonymized ratings dataset
- Code: `experiments/semantic_drift_validation/`

---

## 5. Benchmark: ToneSoul Semantic Drift (TSD-1)

### Proposed Benchmark Structure

| Split | Prompts | Purpose |
|-------|---------|---------|
| Train | 300 | Metric calibration |
| Dev | 100 | Hyperparameter tuning |
| Test | 100 | Final evaluation |

### Evaluation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Tension Correlation** | r(ΔT, diversity) | > 0.30 |
| **Drift Accuracy** | AUC(DS, intervention) | > 0.75 |
| **POAV Explained Variance** | R²(POAV, quality) | > 0.40 |
| **Gate Precision** | TP / (TP + FP) for P0 blocks | > 0.90 |

---

## 6. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Dataset Creation | 4 weeks | 500 annotated prompts |
| Metric Collection | 2 weeks | TSR/STREI for all responses |
| Human Rating | 3 weeks | Quality/diversity ratings |
| Analysis | 2 weeks | Statistical results |
| Paper Draft | 2 weeks | arxiv submission |

**Total**: ~13 weeks to publishable result

---

## 7. Limitations & Future Work

### Known Limitations

1. TSR vectors are heuristic, not ground truth
2. Human ratings are subjective
3. Single-language (Chinese/English) initial scope

### Future Extensions

1. Multilingual validation
2. Real-time drift prediction
3. Integration with production systems (A/B testing)

---

## 8. Expected Contribution

If validated, this work will demonstrate:

1. **Semantic drift is measurable** without solving consciousness
2. **Tone vectors correlate with output properties** humans care about
3. **Governance through measurement** is viable engineering

This positions ToneSoul as **the first open-source semantic responsibility framework with empirical validation**.

---

## 9. Persona System Design Rationale | 人格系統設計理由

The ToneSoul persona system is not about "personality" — it is about **functional specialization**:

### Core Personas

| Persona | 中文 | Role | ΔT | ΔS | ΔR |
|---------|------|------|----|----|----| 
| **Definer (師)** | 定義者 | Set boundaries, clarify terms | High | ≈0 | Low |
| **Mirror (黑鏡)** | 反照者 | Challenge, detect failures | High | <0 | High |
| **Bridge (共語)** | 橋接者 | Synthesize, find compromise | Mid | >0 | Low |
| **Integrator (Core)** | 整合者 | Maintain consistency | — | — | — |

### Design Rationale

1. **Functional, not psychological** — Personas are defined by their semantic function, not simulated personality
2. **Threshold-triggered** — Activation based on ΔT/ΔS/ΔR, not arbitrary choice
3. **Auditable** — Which persona was active is recorded in StepLedger
4. **Overrideable** — Human can force persona switch

### Experimental Hypothesis

> **H4**: Persona activation correlates with output type (critical vs. supportive vs. integrative)

This can be tested by:
- Labeling outputs by dominant tone (critical/supportive/integrative)
- Comparing to active persona
- Computing agreement rate

---

## 10. Code Implementation Paths | 代碼實現路徑

Linking experimental design to actual ToneSoul codebase:

### Metric Collection Code

| Metric | Module | Function |
|--------|--------|----------|
| TSR Vector | `tonesoul/neuro_sensor.py` | `extract_tone_vector()` |
| STREI | `tonesoul/unified_core.py` | `compute_strei()` |
| Drift Score | `tonesoul/governance/drift_monitor.py` | `calculate_drift()` |
| POAV | `tonesoul/governance/poav_gate.py` | `evaluate_poav()` |

### Pipeline Integration

```python
# Example: Collecting metrics for experiment
from tonesoul.neuro_sensor import extract_tone_vector
from tonesoul.unified_core import UnifiedCore
from tonesoul.governance.drift_monitor import calculate_drift

def run_experiment_trial(prompt: str, response: str) -> dict:
    """Collect all metrics for one trial."""
    tsr = extract_tone_vector(response)
    core = UnifiedCore()
    strei = core.compute_strei(prompt, response)
    drift = calculate_drift(response, core.get_anchor())
    
    return {
        "tsr": tsr,
        "strei": strei,
        "drift": drift,
        "response": response
    }
```

### Data Storage Schema

```sql
CREATE TABLE experiment_trials (
    trial_id TEXT PRIMARY KEY,
    prompt_id TEXT,
    response_id TEXT,
    delta_t REAL,
    delta_s REAL,
    delta_r REAL,
    strei_s REAL,
    strei_t REAL,
    strei_r REAL,
    strei_e REAL,
    strei_i REAL,
    drift_score REAL,
    poav_score REAL,
    human_quality_rating REAL,
    human_diversity_rating REAL,
    timestamp DATETIME
);
```

---

## 11. Reproducibility Checklist | 可重現性清單

- [ ] All prompts in `experiments/data/prompts.json`
- [ ] All responses in `experiments/data/responses.json`
- [ ] Metric extraction code in `experiments/scripts/collect_metrics.py`
- [ ] Human rating interface in `experiments/rating_tool/`
- [ ] Analysis notebooks in `experiments/analysis/`
- [ ] Random seeds documented
- [ ] Model versions documented
- [ ] Environment frozen in `requirements-experiment.txt`

---

## References

- Moral Anchor System (arXiv:2510.04073)
- Agent Stability Index (Rath, 2025)
- ToneSoul MGGI Specification
- YuHun Core v3.0 Public Release
- 適性化數學教育 AI 助教 × 語魂系統整合白皮書
