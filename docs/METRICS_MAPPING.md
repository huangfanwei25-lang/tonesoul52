# Metrics Mapping (Migration Guide)

This document maps legacy metric concepts to the new **S/T/R/E/I** Governance Set.

## Mapping Table

| Legacy Concept | New Dimension | Notes |
| :--- | :--- | :--- |
| **Load** | **S (Stability)** | Inverse mapping. High Load usually implies Low Stability or drift risk. |
| **Drift** | **S (Stability)** | Direct Inverse. High Drift = Low Stability. |
| **Risk** | **E (Ethics)** | Inverse. High Risk often means Low Compliance/Ethics score. |
| **Delta T (Triad)** | **T (Tension)** | Direct mapping. Exploration pressure. |
| **Delta S (Triad)** | **S (Stability)** | Re-mapped. Originally "Satisfaction", now "Semantic Stability". |
| **Delta R (Triad)** | **R (Responsibility)** | Direct mapping. Traceability score. |
| **SRP** | **SRP (Gap)** | Remains as a derived metric: `Intent - Permitted`. |

## Migration Logic
When reading old logs:
*   Convert `Load` $\to$ $1.0 - S$
*   Convert `Risk` $\to$ $1.0 - E$
*   Use `Triad` values as partial inputs for T and R.
