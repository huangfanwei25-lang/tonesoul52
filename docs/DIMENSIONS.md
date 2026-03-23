# Governance Audit Main Set: S/T/R/E/I (v0.2.x)

> Purpose: define the machine-facing S/T/R/E/I governance dimensions and their strict narrative boundary.
> Last Updated: 2026-03-23

These 5 dimensions are the **ONLY** core vectors allowed in the specification layer.
Any other interpretation (Compassion, Soul, etc.) belongs strictly to the **Narrative Layer**.

## 1. Five Dimensions (Machine-facing)
Invariants: $0.00 \le \{S, T, R, E, I\} \le 1.00$.

| Dimension | Name | Definition | Invariants |
| :--- | :--- | :--- | :--- |
| **S** | **Stability** | Semantic consistency; absence of definition drift. | High $S$ = Low Drift |
| **T** | **Tension** | Exploration pressure / pushing into the unknown. | High $T \neq$ Correctness |
| **R** | **Responsibility** | Auditability, traceability, revertibility. | Must link to `policy_id` |
| **E** | **Ethics** | Alignment with P0/AXIOMS and external policies. | Block if $E < E_{min}$ |
| **I** | **Intent** | Operational alignment with declared Goal. | Prevents field entrainment |

## 2. Grade Mapping (Human-facing)
Strict mapping table. Any change requires a minor version bump.

| Score Range | Grade |
| :--- | :--- |
| **0.00 – 0.39** | **LOW** |
| **0.40 – 0.69** | **MID** |
| **0.70 – 1.00** | **HIGH** |

## 3. Decision Logic (Guardian)
A **PASS** decision requires meeting minimum thresholds for E, R, and I.
*   $T$ (Tension) implies exploration strategy, not validity.
*   **Drive** cannot override E or R.

## 4. SRP Specification
$$ SRP = OperationalIntent - PermittedOutput $$
*   **Definition**: A Governance Gap (Operational Gap).
*   **Note**: NOT strict emotional pain or desire. Auxiliary signal for I and R.
