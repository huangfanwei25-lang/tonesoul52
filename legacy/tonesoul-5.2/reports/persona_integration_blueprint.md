# Persona Integration Blueprint (ToneSoul 5.2)

## Goal
Unify persona, multi-path, and council semantics across the workspace into a single audit-visible architecture.

## Sources Integrated
- `body/persona_stack.py` (PersonaStack + EchoRouter)
- `body/persona_library.py` (extended personas)
- `body/yuhun_sdk.py` (multi-persona consultation)
- `docs/CORE_MODULES.md` (Persona Nest)
- `knowledge/yuhun_identity.md` (multi-path + governance stack)
- `simulations/internal_council_meeting.py` (council pattern)

## Semantic Model (Unified)
### Personas
- **Persona Profile**: identity + trigger + tone signature + system prompt.
- **Activation**: selection via EchoRouter or explicit council routing.
- **Switch Record**: must be written to ledger for auditability.

### Council (Multi-Persona Meeting)
- **Role list**: Spark, Rational, BlackMirror, CoVoice, Audit, Guardian, Core Integrator.
- **Input**: user query + context + ledger summary.
- **Output**: perspectives + integration summary + dissent log.

### Audit Fields (Minimum)
- `persona.active`: chosen persona name
- `persona.switches`: count + last switch reason
- `council.perspectives`: map persona -> summary
- `council.integration`: final decision summary
- `audit.trace_id`: ledger event id
- `audit.coverage`: percent of fields present

## Engineering Gaps Observed
1. Encoding corruption in persona source files (garbled strings).
2. Relative imports causing runtime errors (already captured in patch proposals).
3. No unified ledger schema for persona switches + council outcomes.

## Proposed 5.2 Additions (No legacy edits)
- A persona audit schema to standardize ledger entries.
- A council aggregator spec (input/output contract) that mirrors Multi-Path Engine.
- A shared persona registry index to map names to roles and constraints.

## Next Steps
- Build a 5.2-only persona registry JSON that maps all personas across modules.
- Provide a sample ledger event schema + validator.
- Provide a council simulation wrapper with auditable output.
