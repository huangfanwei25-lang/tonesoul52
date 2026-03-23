# Specification: Temporal Audit Constraints

> Purpose: define the temporal audit firewall that separates past facts, present operations, and future projections.
> Last Updated: 2026-03-23

## 1. The Three-Phase Firewall
To ensure the integrity of the **World Model**, all system reports and audits must strictly distinguish between temporal phases.

### Phase 1: Past (Definitions & Factum)
- **Scope**: Immutable axioms, legacy files in `archive/`, and committed ledger entries.
- **Role**: The "Ground Truth" foundation.
- **Rule**: Cannot be modified by current inferences.

### Phase 2: Present (Operations & Discussion)
- **Scope**: Active memory buffer, current STREI measurements, and ongoing file edits.
- **Role**: The "Active State".
- **Rule**: Must be mapped to specific physical files or sensor data.

### Phase 3: Future (Projections & Inference)
- **Scope**: Hypothesis generation, Dream Cycle insights, and projected decay.
- **Role**: The "Simulation Layer".
- **Rule**: **Back-flow Prohibition**. Projections cannot be stated as established facts in Phase 1 or 2.

## 2. Clause of Nullification
Any system output that merges Phase 3 (Inference) into Phase 1 (Fact) without explicit labeling is to be considered **Structurally Invalid** and rejected by the L1 Spine.
