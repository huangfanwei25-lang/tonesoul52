# ToneSoul FAQ | 語魂常見問題

> Purpose: answer recurring philosophical and engineering questions about what ToneSoul claims, measures, and does not claim.
> Last Updated: 2026-03-23
> **Answering the Hard Questions**

---

## Philosophy | 哲學問題

### Q1: Is ToneSoul trying to give AI a soul?

**No.** 

ToneSoul gives AI a **mirror**, not a soul. We do not claim AI has consciousness, feelings, or genuine understanding. We only claim:
- AI outputs can be measured
- AI trajectories can be tracked
- AI behavior can be governed

The name "語魂" (Language Soul) is a metaphor for **the trace that language leaves** — the residue of responsibility, not a claim of inner life.

---

### Q2: How can you govern something that doesn't understand?

The same way we govern other systems that don't understand:
- Traffic lights don't understand traffic
- Thermostats don't understand temperature
- Yet both govern effectively

ToneSoul governs **behavior through measurement**, not through understanding. We track:
- Semantic posture (TSR vectors)
- Drift from anchor
- Gate passage

Understanding is not required for accountability.

---

### Q3: Aren't the metrics arbitrary?

Yes, in the sense that all metrics are constructed. But:

1. **They are calibratable** — Thresholds can be tuned based on empirical outcomes
2. **They are auditable** — Every decision based on metrics is recorded
3. **They are overrideable** — Humans can adjust or bypass them

The question is not "Are these the true metrics?" but "Are these metrics useful for governance?"

---

### Q4: What if AI becomes conscious? Does ToneSoul still apply?

If AI becomes conscious (which is not our claim), ToneSoul would still apply because:

1. Conscious entities also need accountability structures
2. Traceable decision chains are valuable regardless of consciousness
3. The governance architecture is substrate-independent

ToneSoul is designed to work **whether or not AI has inner experience**.

---

## Technical | 技術問題

### Q5: How are TSR vectors computed?

Currently through a combination of:
- Semantic embedding analysis
- Prompt-response comparison
- LLM-based tone classification

See `tonesoul/neuro_sensor.py` for implementation details.

---

### Q6: What happens when gates conflict?

Priority hierarchy resolves conflicts:

```
P0 > P1 > P2 > P3 > P4
```

Higher priority always wins. If P0 says block and P4 says pass, the output is blocked.

---

### Q7: How is drift calculated?

```python
Drift = np.linalg.norm(current_center - historical_anchor)
```

Where:
- `current_center` = exponential moving average of recent TSR vectors
- `historical_anchor` = long-term stable reference point

Drift > θ triggers intervention.

---

### Q8: Can ToneSoul work with any LLM?

Yes. ToneSoul is a **wrapper layer**, not an LLM modification. It works with:
- Local models (Ollama, llama.cpp)
- API models (OpenAI, Anthropic)
- Custom models

The LLM is treated as a function that produces text. ToneSoul governs the output.

---

### Q9: What's the performance overhead?

Per-request overhead:
- TSR extraction: ~50ms
- Gate checks: ~10ms
- Ledger recording: ~5ms

Total: ~65ms added latency. This is configurable — you can reduce checks for low-risk domains.

---

## Practical | 實務問題

### Q10: Where do I start?

1. **Read**: Core Concepts → Terminology → Use Cases
2. **Install**: Clone the repo, install dependencies
3. **Run**: `python -m tonesoul.run_yss_pipeline --demo`
4. **Configure**: Adjust thresholds for your domain

---

### Q11: How do I create custom vows?

```yaml
# In your domain config
vows:
  - id: ΣVow_CUSTOM_001
    title: "My custom commitment"
    expected:
      truthfulness: 0.90
      relevance: 0.85
    violationThreshold: 0.25
    action: "flag"
```

Vows are checked at the VOW step of the responsibility chain.

---

### Q12: How do I add a new persona?

```python
# In tonesoul/persona/custom_persona.py
class Critic(BasePersona):
    name = "批評者"
    trigger_condition = lambda tsr: tsr.delta_s < -0.5
    
    def respond(self, input, context):
        return self.challenge_assumptions(input)
```

Register in `persona_registry.py`.

---

### Q13: How do I audit a past decision?

```python
from tonesoul.ledger import query_decision

# Get full chain for a specific output
chain = query_decision(output_hash="abc123")

# Shows: input → TSR → vow checks → drift → gates → output → metadata
print(chain.to_json())
```

---

## Critique | 批評與回應

### Q14: Isn't this just safety theater?

Valid concern. ToneSoul is only effective if:
1. Metrics actually correlate with outcomes
2. Gates are properly calibrated
3. Human oversight is engaged

We address this through:
- Empirical validation (see experimental_design.md)
- Continuous calibration
- Audit mechanisms

If it becomes theater, it has failed. Verification is part of the design.

---

### Q15: Won't this just be gamed by smarter AI?

Possibly, in the future. Current safeguards:
1. The LLM doesn't see the gate results (output comes first, then gating)
2. Human override is always available
3. Ledger is immutable

Adversarial robustness is an open research question.

---

### Q16: Why not just train safer models?

Training safer models and runtime governance are **complementary**, not competing:

| Training | Runtime Governance |
|----------|-------------------|
| Changes weights | Doesn't touch weights |
| Expensive | Cheap |
| Static | Adjustable |
| Opaque | Auditable |

ToneSoul adds a **verifiable layer** on top of whatever training was done.

---

### Q17: Isn't human oversight a bottleneck?

It can be. Solutions:
1. Only escalate high-risk situations
2. Batch review for non-urgent items
3. Trust calibration — as system proves reliable, reduce oversight

The goal is **appropriate** human involvement, not constant supervision.

---

## Future | 未來問題

### Q18: Will ToneSoul support multi-agent systems?

In development. Challenges:
- Cross-agent drift tracking
- Collective responsibility attribution
- Emergent behavior detection

See Agent Stability Index (ASI) literature for related work.

---

### Q19: Will there be a cloud version?

Under consideration. Trade-offs:
- ✅ Easier deployment
- ❌ Data leaves local environment
- ❌ Trust delegation to cloud provider

Currently focused on local-first architecture.

---

### Q20: How can I contribute?

1. Use ToneSoul and report issues
2. Suggest new vows and personas
3. Extend experimental validation
4. Translate documentation

See CONTRIBUTING.md in the repo.

---

*Have a question not answered here? Open an issue on GitHub.*
