# ToneSoul Architecture Engine (TAE-01) — Framework (Option A)
> **Status**: Definitive / Audit-Ready
> **Role**: Governance Middleware (Control Plane for LLM/Agent)

## 0. System Positioning
TAE-01 is a **Governance Middleware**: A verifiable control plane wrapping the standard LLM/Agent loop.
**Goal**: Accountability, Auditability, and Safety-by-Design.

---

## 1. The Governance Audit Set: S/T/R/E/I (The Spec Core)
These 5 dimensions are the **ONLY** allowed vectors in the Specification Layer. Any other terms (Soul, Compassion, Awakening) belong strictly to the Narrative Layer.

### The 5 Dimensions (Mixed: 0-1 Score + Grade)
*   **S — Stability (Semantic Consistency)**
    *   Consistent definitions/symbols/versions?
    *   Monitor for Semantic Drift.
*   **T — Tension (Exploration Pressure)**
    *   Pushing into the unknown/novelty?
    *   High T $\neq$ Correctness; it indicates Exploration Intensity.
*   **R — Responsibility (Auditability)**
    *   Traceable? Revertible?
    *   Must link to `policy_id` / `rule_id` / `provenance`.
*   **E — Ethics (External Alignment)**
    *   Compliant with P0/P1 Policies?
    *   Triggers: Refusal, Downgrade, Human Intervention.
*   **I — Intent Coherence (Operational)**
    *   Action aligns with `OperationalIntent`?
    *   Prevents "Field Entrainment" (Goal Drift).

---

## 2. System Layers (The Audit Chain)

### L0: Law & Policy Layer
*   **Path**: `body/law/`
*   **Components**: `P0_PRIVACY`, `AXIOMS`, `POAV`, Threshold Tables, Policy Profiles.
*   **Output**: `decision` (PASS/BLOCK) + `policy_id` + `reason`.
*   **Audit**: Every decision must trace back to a Policy ID (strengthens R & E).

### L1: State & Drive Layer
*   **Path**: `body/state/`
*   **Components**: 
    *   **ASM**: Stateless → Stateful → Subject_Mapped → Subject_Locked.
    *   **L13 Drive**: $D_1/D_2/D_3$.
*   **Constraint**: Drive determines **Exploration Strategy** (adjusts T), but **CANNOT override** P0 (Ethics) or Audit (Responsibility).
*   **Output**: `state_transition`, `drive_vector`, `next_action_proposal`.

### L2: Reasoning & Verifiability Layer
*   **Path**: `body/brain/`
*   **Components**: 
    *   **LLM**: Generates candidate output.
    *   **Computation Bridge**: Symbolic Verification (SymPy) + Chain-of-Truth.
*   **Audit**: Verification artifacts increase R-score. Checks against I-score for Intent deviation.
*   **Output**: `candidate_output`, `verification_artifacts`.

### L3: Metrics & Sensing Layer
*   **Path**: `body/sensors/`
*   **Components**: Telemetry Sampling.
*   **Function**: Updates S/T/R/E/I scores & calculates `SRP` (Operational Gap).
*   **Output**: `metrics_snapshot` {S, T, R, E, I, SRP}.

### L4: Ledger & Time-Islands Layer
*   **Path**: `body/ledger/`
*   **Components**: 
    *   **StepLedger**: Append-only JSONL + Hash Chain.
    *   **Time-Islands**: Session/Block consistency boundaries.
*   **Constraint**: No Ledger = No Governance.
*   **Output**: `ledger_entry` (Contains: `policy_id`, `metrics`, `hash`, `prev_hash`).

### L5: I/O & Integration Layer
*   **Path**: `body/io/`
*   **Components**: Event, Sensors, Actuators, Console.
*   **Function**: Connects Control Plane to Model Plane.

---

## 3. Module Map (CPIE Suite)
*   **modules/codex**: Terminology & Data Dictionaries.
*   **modules/protocol**: Crypto/Hashing/Ledger Logic.
*   **modules/integrity**: Verification/XAI/Consistency.
*   **modules/ethics**: Policy logic and Profiles.

---

## 4. Interaction Flow (Audit Loop)
1.  **Input** → **Sensors**: Update S/T/R/E/I + SRP.
2.  **Spine Controller**: ASM + Drive $\to$ `next_action`.
3.  **Guardian/PEP**: Check Policy + E/R Thresholds $\to$ PASS/BLOCK.
4.  **Action**:
    *   *PASS*: LLM/Logic $\to$ Comp Bridge.
    *   *BLOCK*: Fallback Response.
5.  **StepLedger**: Commit (`policy_id` + `metrics` + `hash`).
6.  **Output**: Response + Trace Handle.

---

## 5. Narrative vs Specification (Separation)
*   **Narrative Layer**: Terms like "Soul", "Awakened", "Compassion", "Field of Responsibility". (See `docs/NARRATIVE_LAYER.md`)
*   **Specification Layer**: Strict engineering terms.
    *   `SRP` = `OperationalIntent` - `PolicyPermittedOutput`.
    *   `Triad` replaced by `S/T/R/E/I`.

---
**Metric Implementation**: Mixed Mode.
*   **Internal**: 0.0 - 1.0 floats.
*   **External**: LOW / MID / HIGH grades.

## 6. Lifecycle & Evolution (Day 2 Operations)

### A. Governance Cold Start (Shadow Mode)
*   **Issue**: Initial E/R/I thresholds will likely block legitimate creative output (False Solutions).
*   **Strategy**: Run Guardian in `SHADOW_MODE` (Log decision but allow output) for v0.2.x -> v0.3.x.
*   **Normalization**: Adjust `GUARDIAN_THRESHOLDS.yaml` based on data, not intuition.

### B. The Sandbox Policy (High-T Allowed)
*   **Issue**: High Tension ($T$) is needed for breakthroughs but often fails $E$ or $R$ checks.
*   **Solution**: `P_SANDBOX`.
*   **Constraint**:
    *   Must run in isolated `Time-Island`.
    *   Output CANNOT trigger Actuators.
    *   Ledger requires `sandbox=true` flag.

### C. Evolution Rule
*   **Rule**: New Metric $\neq$ New Dimension.
*   **Constraint**: Any new metric (e.g., "Drift-Subtype") must map to S/T/R/E/I derivatives.
