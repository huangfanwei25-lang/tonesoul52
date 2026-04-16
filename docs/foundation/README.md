# ToneSoul Foundation Layer

> Purpose: give humans and AI one thin, decision-affecting project packet before deeper repo reading.
> Last Updated: 2026-04-14
> Status: foundation entry layer; subordinate to `AXIOMS.json`, executable code, tests, `task.md`, and canonical architecture contracts.
> Use When: first 3 minutes of a new conversation, or before re-entering the repo after a gap.

---

## What This Layer Is

- A compact startup pack for consistent project work.
- A routing layer to existing authority surfaces.
- A decision-oriented summary of what changes execution behavior.

## What This Layer Is Not

- Not a second architecture lane.
- Not a generated status dump.
- Not a replacement for runtime code, tests, or accepted contracts.
- Not private memory, hot memory, or historical residue.

## Entry Ownership

| Need | Owner Surface | Companion Surface | Avoid Treating As Owner |
|---|---|---|---|
| public repo introduction | [README.md](../../README.md) | [README.zh-TW.md](../../README.zh-TW.md) | `docs/INDEX.md` |
| AI operational start | [docs/AI_QUICKSTART.md](../AI_QUICKSTART.md) | `python scripts/start_agent_session.py --agent <your-id>` | `AI_ONBOARDING.md` |
| AI routing after session start | [AI_ONBOARDING.md](../../AI_ONBOARDING.md) | [docs/README.md](../README.md) | bulk-opening `docs/architecture/` |
| thin project packet | this Foundation Layer | [task.md](../../task.md) | the deep system guide |
| design rationale | [DESIGN.md](../../DESIGN.md) | [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](../architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | `docs/README.md` |
| docs browsing | [docs/README.md](../README.md) | [docs/INDEX.md](../INDEX.md) when exhaustive lookup is required | `README.md` |

## Fixed First-Hop Paths

- human/developer: `README.md` -> `docs/foundation/README.md` -> `docs/README.md` -> one chosen lane
- AI agent: `docs/AI_QUICKSTART.md` -> `python scripts/start_agent_session.py --agent <your-id>` -> `AI_ONBOARDING.md` -> `docs/foundation/README.md` -> `task.md`
- design / whole-system reasoning: `DESIGN.md` -> `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md` only after the bounded packet is clear

## First-Hop Guardrails

- Open one owner surface per question before widening into companions.
- Use `docs/README.md` for curated routing and `docs/INDEX.md` only for exhaustive browsing.
- If a document mostly routes to stronger surfaces, treat it as a router, not a second authority center.
- Formula-like notation in entry docs is orientation unless an executable owner is named; check `docs/GLOSSARY.md` and `docs/MATH_FOUNDATIONS.md` when formula posture matters.
- If Windows terminal output renders paths noisily, use [FILENAME_AND_ENTRY_INDEX.md](FILENAME_AND_ENTRY_INDEX.md) instead of trusting shell echoes.

## Reading Order

1. [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
2. [WORKFLOW.md](WORKFLOW.md)
3. [MODULE_ROLES.md](MODULE_ROLES.md)
4. [TASK_CARD.md](TASK_CARD.md)
5. [NAMING_AND_CLASSIFICATION.md](NAMING_AND_CLASSIFICATION.md)
6. [QA_AND_VALIDATION.md](QA_AND_VALIDATION.md)
7. [task.md](../../task.md)

## Authority Order

1. `AXIOMS.json`, executable code, tests
2. `task.md` and accepted architecture contracts
3. this Foundation Layer
4. `docs/plans/`, `docs/status/`, `docs/chronicles/`, historical reviews

## Keep This Layer Thin

- Summarize only content that affects decisions or execution.
- Link back to authority surfaces instead of duplicating them.
- Prefer one screen of guidance over a mini-whitepaper.
- If a section starts explaining history in detail, it belongs elsewhere.

## Source Anchors

- [README.md](../../README.md)
- [DESIGN.md](../../DESIGN.md)
- [docs/AI_QUICKSTART.md](../AI_QUICKSTART.md)
- [docs/README.md](../README.md)
- [docs/INDEX.md](../INDEX.md)
- [FILENAME_AND_ENTRY_INDEX.md](FILENAME_AND_ENTRY_INDEX.md)
- [docs/7D_AUDIT_FRAMEWORK.md](../7D_AUDIT_FRAMEWORK.md)
- [docs/FILE_PURPOSE_MAP.md](../FILE_PURPOSE_MAP.md)
- [docs/DOCS_INFORMATION_ARCHITECTURE_v1.md](../DOCS_INFORMATION_ARCHITECTURE_v1.md)
- [docs/GLOSSARY.md](../GLOSSARY.md)
- [docs/MATH_FOUNDATIONS.md](../MATH_FOUNDATIONS.md)
- [docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](../architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
- [docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md](../architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)

## Canonical Handoff Line

If a later agent only reads one folder before working, it should read this one.
