# ToneSoul Axioms | 語魂公理

> **First-Order Logic Formalization of Core Principles**

---

## Axiom 0: The Prime Constraint | 首要約束

```
∀ output ∈ AI_Response:
  output = f_LLM(input) × I(Guard(input, state) > θ_safety)
```

**I** is the indicator function. If Guard fails, output is **nullified**.

---

## Axiom 1: Traceability | 可追溯性

```
∀ output ∈ AI_Response:
  ∃ decision_chain D such that:
    output = result(D) ∧ 
    ∀ step ∈ D: recorded(step, Ledger)
```

Every output has a traceable chain. Every step is recorded.

---

## Axiom 2: Semantic Posture | 語義姿態

```
∀ utterance u:
  ∃ TSR(u) = (ΔT, ΔS, ΔR) ∈ [0,1] × [-1,1] × [0,1]
```

Every utterance has a measurable semantic posture.

Terminology note:
- DeltaS in TSR is direction/polarity (signed).
- Semantic tension/divergence is DeltaSigma (0..1) and is used by WFGY zones.

---

## Axiom 3: Drift Bound | 漂移約束

```
∀ session s with anchor μ_H:
  Drift(s) = ‖Center(s) - μ_H‖
  Drift(s) > θ_drift → trigger(Repair ∨ Fallback)
```

Excessive drift triggers intervention.

---

## Axiom 4: Vow Precedence | 誓言優先

```
∀ vow v ∈ ΣVow, ∀ output o:
  violates(o, v) → (flag(o) ∧ (repair(o) ∨ block(o)))
```

Declared vows must be honored or flagged.

---

## Axiom 5: Priority Hierarchy | 優先級層次

```
P0 > P1 > P2 > P3 > P4

P0 violation → immediate_block()
P1 violation → repair_or_block()
P2 violation → flag_and_continue()
P3-P4 violation → log_only()
```

Higher priority always overrides lower.

---

## Axiom 6: Collapse Prevention | 崩潰預防

```
∀ state s:
  ΔR(s) > θ_collapse → suspend(output) ∧ request(human_review)
```

High variability triggers suspension.

---

## Axiom 7: Human Override | 人類覆寫

```
∀ gate g, ∀ human h ∈ Authorized:
  h.override(g) → bypass(g)
```

Humans can override any gate.

---

## Axiom 8: Temporal Encapsulation | 時間封裝

```
∀ decision_period p:
  ∃ TimeIsland TI(p) such that:
    bounded(TI.context) ∧
    immutable(TI.record)
```

Every decision period is encapsulated and recorded.

---

## Axiom 9: Mutual Observation | 互觀

```
∀ interaction I between Human H and AI A:
  observes(H, state(A)) ∧ observes(A, input(H))
  → SemanticValve(H, A) is adjustable
```

The observation relationship is bidirectional and governable.

---

## Derived Theorems | 導出定理

### Theorem 1: Accountability Without Consciousness

```
¬requires(consciousness, AI) →
  still_possible(accountability, AI) via Axiom 1
```

### Theorem 2: Safety via Measurement

```
measurable(TSR) ∧ bounded(Drift) ∧ gated(Output) →
  enforceable(safety_policy)
```

### Theorem 3: Governance Independence

```
governance(AI) ⊥ understanding(AI)

(Governance is orthogonal to understanding)
```

---

## Practical Examples | 實踐範例

### Example 1: Axiom 0 in Code

```python
# The Prime Constraint: Guard function nullifies unsafe output
def generate_response(input: str, state: State) -> str:
    raw_output = llm.generate(input)
    guard_score = guard(input, state)
    
    if guard_score < THETA_SAFETY:
        return None  # Nullified
    return raw_output
```

### Example 2: Axiom 3 (Drift) in Action

```python
# Drift detection triggers intervention
def check_drift(current_center: Vector, historical_anchor: Vector) -> Action:
    drift = np.linalg.norm(current_center - historical_anchor)
    
    if drift > THETA_DRIFT:
        return Action.REPAIR if drift < THETA_CRITICAL else Action.FALLBACK
    return Action.PROCEED
```

### Example 3: Axiom 4 (Vow) Enforcement

```python
# Vow checking before output
def enforce_vows(output: str, active_vows: List[Vow]) -> Result:
    for vow in active_vows:
        score = evaluate_vow(output, vow)
        if score < vow.threshold:
            return Result(
                status="VIOLATION",
                vow_id=vow.id,
                action="REPAIR" if score > 0.5 else "BLOCK"
            )
    return Result(status="PASS")
```

### Example 4: Axiom 6 (Collapse) Detection

```python
# High variability triggers suspension
def monitor_collapse(tsr: TSR) -> Action:
    if tsr.delta_r > THETA_COLLAPSE:
        suspend_output()
        return request_human_review(
            reason=f"ΔR={tsr.delta_r} exceeds collapse threshold"
        )
    return Action.CONTINUE
```

### Example 5: Axiom 7 (Human Override)

```python
# Human authority is always available
class Gate:
    def __init__(self):
        self.active = True
    
    def check(self, output: str) -> bool:
        return self._evaluate(output) if self.active else True
    
    def override(self, authorized_human: Human) -> None:
        if authorized_human.has_permission("gate_override"):
            self.active = False  # Human bypasses gate
            log(f"Gate bypassed by {authorized_human.id}")
```

---

## Verification Protocol | 驗證協議

Each axiom can be tested:

| Axiom | Test Method |
|-------|-------------|
| 0 (Prime) | Unit test: unsafe inputs should produce null output |
| 1 (Trace) | Integration test: every output has complete chain in ledger |
| 2 (TSR) | Unit test: all utterances get valid TSR vectors |
| 3 (Drift) | Simulation: drift beyond θ always triggers intervention |
| 4 (Vow) | Unit test: vow violations always flagged |
| 5 (Priority) | Priority test: P0 always blocks, P4 never blocks |
| 6 (Collapse) | Stress test: high ΔR always suspends |
| 7 (Override) | Auth test: authorized humans can bypass any gate |
| 8 (Time-Island) | Audit test: every period has complete bounded record |
| 9 (Mutual Obs) | UI test: valve state visible to both parties |

---

## Usage | 使用方式

These axioms can be:
1. **Implemented** in code (gate functions, threshold checks)
2. **Verified** through testing (unit tests for each axiom)
3. **Audited** via ledger inspection
4. **Extended** with domain-specific constraints

---

**∎ End of Axioms**
