# Metrics Mapping (Migration Guide)

> Purpose: map legacy metric concepts onto the current S/T/R/E/I governance dimensions during migration.
> Last Updated: 2026-03-23

This document maps legacy metric concepts to the current **S/T/R/E/I** governance set.

---

## Mapping Table

| Legacy Concept | New Dimension | Notes |
| --- | --- | --- |
| **Load** | **S (Stability)** | Inverse mapping. High Load usually implies lower Stability. |
| **Drift / ΔΣ** | **S (Stability)** | Inverse mapping. High semantic tension lowers Stability. |
| **Risk** | **R (Responsibility)** | Direct mapping. Ethics is derived from axiom checks. |
| **ΔT (Triad)** | **T (Tension)** | Direct mapping. |
| **ΔS (Triad, Direction)** | **I (Intent)** | Polarity signal; not a stability score. |
| **ΔR (Triad)** | **R (Responsibility)** | Direct mapping. |
| **SRP** | **SRP (Gap)** | Derived metric: `Intent - Permitted`. |

---

## Migration Logic

- Convert **Load** → `S = 1.0 - Load`
- Convert **ΔΣ (semantic tension)** → `S = 1.0 - ΔΣ`
- Use **ΔT** and **ΔR** as direct inputs to T and R
- Use **ΔS (direction)** as intent polarity signal, not as stability
