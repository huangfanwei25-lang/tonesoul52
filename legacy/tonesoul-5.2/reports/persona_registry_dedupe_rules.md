# Persona Registry Dedupe Rules (ToneSoul 5.2)

## Objectives
- Merge duplicate persona names across sources.
- Preserve source provenance for auditability.
- Flag encoding-corrupted entries rather than drop them.

## Rules
1. Normalize name for matching: `name.strip().lower()`.
2. Merge entries by normalized name.
3. Preserve all sources in a `sources[]` list.
4. Preserve all roles in a `roles[]` list.
5. Preserve notes/flags in `notes[]`.

## Outputs
- `persona_registry_cleaned.json`
- `persona_registry_cleaned.md`

## Non-Destructive
- No legacy files are modified.
- All changes remain inside `5.2`.
