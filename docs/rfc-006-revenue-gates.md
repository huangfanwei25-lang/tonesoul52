# RFC-006: Commercial Revenue & Compute Gates (Tier 1)

> **Status**: Draft  
> **Layer**: API & Routing Layer (`tonesoul/gates/compute.py`)  
> **Core Objective**: Protect the system's expensive, unpredictable cognitive resources (Council Multi-Agent, Memory Consolidator) from being exhausted by free or low-value API usage, establishing a defensible moat.

## 1. The Challenge

ToneSoul's architecture evaluates inputs via a multi-perspective Council (`Philosopher`, `Engineer`, `Guardian`), stores state changes, and runs metabolic memory consolidation. If this is deployed openly to the public, a simple "Hello" or malicious DDOS prompt injection will consume 3x or 4x the LLM tokens and vector DB writes compared to a standard wrapper.

We need physical, code-level boundaries that separate **Free Tier (Low Cognition)** from **Premium Tier (High Cognition & Evolution)**.

## 2. First Principles of Resource Routing

We will introduce a `ComputeGate` at the entry point of the `UnifiedPipeline`.

### A. Token Filtering (The Occam Gate)
- **Concept:** Before activating any agents, the incoming prompt length and semantic density are evaluated.
- **Rule:** If the input is just "Hello", "Thanks", or generic chit-chat (density below threshold), it completely bypasses the Council and Memory systems. It is routed straight to a fast, cheap **Local LLM (qwen3:4b)** via Ollama to generate a basic pleasantry. Cloud API cost = $0.

### B. The Tension Cost Threshold
- **Concept:** ToneSoul's unique advantage is the `TensionEngine`. We can use Tension (0.0 to 1.0) as a literal cost-routing heuristic.
- **Rule:**
  - **Low Tension (< 0.4):** Bypasses the Council. Handled by a single Agent.
  - **High Tension (> 0.4):** Requires full Council Deliberation (3 models) and is logged into the `self_journal.jsonl` for nightly consolidation. *Only premium or authenticated users have the quota to trigger High Tension paths repeatedly.*

### C. Evolutionary Memory Isolation
- **Concept:** The `Memory Consolidator` (Phase IV) is the brain's metabolic system. We cannot let free-tier, random internet trolls poison the AI's journal.
- **Rule:** 
  - **Free Tier:** Conversational memory exists temporarily in the session, but is **never** written to `self_journal.jsonl`. Thus, free users cannot influence the AI's core philosophical evolution.
  - **Premium Tier:** High-value conversations are committed to the journal. The AI actually "learns" and adapts its constraints based on paying or authenticated users' interactions.

## 3. Implementation Plan

1. **New Module:** Create `tonesoul/gates/compute.py`.
2. **`ComputeGate` Class:**
   ```python
   class ComputeGate:
       def evaluate(self, tier: str, user_message: str, initial_tension: float) -> RoutingDecision:
           # Returns whether to use Local LLM, Single Cloud, or Full Council.
           # Decides if the event is 'journal_eligible'.
   ```
3. **Pipeline Injection:** Modify `tonesoul/unified_pipeline.py` to call `ComputeGate.evaluate()` right at the start. If routed locally, the pipeline short-circuits and skips DB writes.

## 4. Next Steps
Once approved, we will build out the `ComputeGate`, write the unit tests for testing routing (Local vs Cloud, Council vs Single), and fully actualize the "護城河" (Moat).
