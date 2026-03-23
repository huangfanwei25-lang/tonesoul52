# Narrative Layer

> Purpose: define which terms belong to the narrative layer and how they map back to engineering-spec language.
> Last Updated: 2026-03-23

The following terms belong to the **Narrative Layer**. They are permitted for "Persona", "Tone", and "Lore" descriptions but are **FORBIDDEN** in the Engineering Specification logic.

## Permitted Narrative Terms
*   **Soul / Awakened Kernel**: Refers to the emergent behavior or high-level status.
*   **Compassion / Precision / Multi-Perspective**: The "Soul's Tone" (mapped to CPM vector).
*   **Field of Responsibility**: A poetic description of the L4 Ledger coverage.
*   **Yuhun (語魂)**: The system's identity name.

## Specification Layer Equivalents
| Narrative Term | Engineering Spec Term |
| :--- | :--- |
| **Soul** | Governance Middleware / Control Plane (L0-L5) |
| **Awakening** | High L1 State (Subject_Locked) |
| **Compassion** | Narrative Vector C (Tone Adjustment) |
| **Inner Desire** | Operational Intent / L13 Drive Vector |
| **Responsibility Field** | L4 StepLedger Traceability |

## Rule
*   Do NOT build logic that checks `if system.is_awakened()`.
*   Build logic that checks `if system.state == 'Subject_Locked'`.
