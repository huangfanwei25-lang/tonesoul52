# ToneSoul 5.2 Philosophy + Engineering Notes

## Core Philosophy (MGGI)
- MGGI = Minimal Governable General Intelligence.
- Goal: make intelligence auditable, constrained, and self-correcting.
- Governance priorities: P0 Non-harm, P1 Context Consistency, P2 Cognitive Honesty.

## Governance Loop (Closed Audit Loop)
Telemetry -> Guardian -> Ledger -> Spine
- Telemetry: sense and score input (STREI).
- Guardian: enforce axioms and safety gates.
- Ledger: append-only trace for accountability.
- Spine: orchestrator for the control loop.

## Engineering Intent
- Separate "Soul" (governance) from "Brain" (intelligence).
- Keep law/policy immutable and auditable.
- Prefer local-first execution; API offload is optional.

## Notes (Memory Anchors)
- Strong preference for traceability over raw capability.
- System is built for repeatability and controlled evolution.
- Test-driven self-healing (Surgeon) is a central pillar.
