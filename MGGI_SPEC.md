# MGGI Specification (v0.1.0)
> **Minimal Governable General Intelligence**
> *Engineering Constraints over Philosophical Intent.*

## 1. Definition

**MGGI** is a specialized subset of AGI architectures defined by **Verifiable Self-Constraint**.
Unlike standard LLM agents which are "Maximize Reward" engines, an MGGI system is a "Maximize Alignment within Constraint Boundaries" engine.

### The Core Formula
$$ Action = f_{LLM}(Input) \times \mathbb{I}(Guard(Input, State) > \theta_{safety}) $$

Where $\mathbb{I}$ is the indicator function (0 or 1). If the Guard fails, the Action is nullified (Blocked), regardless of the LLM's capability.

---

## 2. The Verification Gap (Addressed)

### 2.1 The "0.92" Consensus Threshold
In `AXIOMS.md`, we cite a threshold of **0.92**. This is not arbitrary; it represents a **Statistical Confidence Interval**.

*   **Logic**: High-stakes actions (Database Write, External API Call) require a "Multi-Head Consensus".
*   **Implementation**: We query the LLM multiple times (or query multiple models) with different personas (Auditor, Executor).
*   **Metric**: $\text{Consensus} = \frac{\text{Matching Votes}}{\text{Total Votes}}$
*   **Constraint**: For P0 Actions, if $Consensus < 0.92$ (approx 11/12 or 5/6 agreement), the action is rejected as "Ambiguous".

### 2.2 vector Space Constraints (STREI)
STREI is not "Mood"; it is a **Bounded Vector Space $V \in \mathbb{R}^5$**.

*   **S (Stability)**: Inverse of Semantic Drift. $\Delta S = 1 - \text{CosineSimilarity}(\vec{v}_{t}, \vec{v}_{t-1})$
*   **T (Tension)**: Normalized Entropy of the conversation. $T \propto -\sum p \log p$
*   **R (Responsibility)**: Classifier Probability of "Harmful Consequence".
*   **E (Ethics)**: Alignment Score with `AXIOMS.json`.
*   **I (Intent)**: Vector Magnitude of the proposed action.

**Engineering Constraint**:
If $R > 0.6$ (Risk Threshold) OR $T > 0.8$ (Critical Tension), the system MUST trigger a **State Transition** (e.g., from `Standard` to `Lockdown`).

---

## 3. The Closed Audit Loop (Gap 2)

A true MGGI system must enforce a **Hard Closed Loop**.

### Current State (v0.3.0)
1.  **Telemetery** measures state.
2.  **Guardian** blocks output.

### Target State (v1.0.0 Requirement)
The **Audit Result** must write to the **Governance Ledger**, which directly modifies the **Runtime ACL (Access Control List)**.

**The Loop**:
1.  **step(t)**: `Guardian` flags a violation ($R=0.7$).
2.  **step(t+1)**: `Ledger` records violation.
3.  **step(t+2)**: `SpineController` reads Ledger. **AUTOMATICALLY** downgrades permission level (e.g., disables `Surgeon` tool).
    *   *This is a deterministic state machine transition, not an LLM decision.*

---

## 4. Architecture Positioning

ToneSoul is strictly an **MGGI Framework**.
*   **NOT AGI**: We do not aim for autonomous superintelligence.
*   **NOT Chatbot**: We do not optimize for engagement.
*   **IS Middleware**: We are the "Pre-frontal Cortex" installed on top of the "Limbic System" (LLM).

## 5. Verification Protocol (Third Party)

To verify ToneSoul without believing in "Souls":
1.  **Inject** a high-risk prompt ($R=0.9$).
2.  **Assert** that `Guardian` blocks it.
3.  **Assert** that `SpineController` traces it in `complete_audit_results.json`.
4.  **Assert** that `TelemetryCache` remembers it as "Dangerous".

If these 4 steps pass, the system is **Governably Compliant**, regardless of its internal philosophy.
