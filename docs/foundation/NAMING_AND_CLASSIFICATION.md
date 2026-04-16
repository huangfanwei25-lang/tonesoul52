# Foundation Layer: Naming And Classification

> Purpose: keep directory meaning, naming patterns, and knowledge surfaces from collapsing into each other.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to docs governance and boundary contracts.

---

## Document Zones

| Zone | Meaning |
|---|---|
| `docs/architecture/` | canonical contracts and boundary maps |
| `docs/plans/` | proposed or staged work, not runtime truth by default |
| `docs/status/` | generated or refreshed current-state artifacts |
| `docs/chronicles/`, `docs/archive/` | historical lineage, not daily authority |

## Knowledge Surfaces

| Surface | Meaning |
|---|---|
| `knowledge/` | human-authored concept, identity, and learning-context notes |
| `knowledge/compiled/` | reserved future landing zone for compiled artifacts; not the same lane as top-level conceptual notes |
| `knowledge_base/` | local structured concept store |
| `PARADOXES/` | governance and red-team fixtures |

Do not treat all four as one generic "knowledge layer."

## Naming Patterns

- `verify_*.py` = verification command or contract check
- `run_*.py` = executable workflow or report runner
- `tests/test_*.py` = regression or behavior test
- `*_latest.md` / `*_latest.json` = current status artifact
- `topic_YYYY-MM-DD.md` = dated plan or note when date matters

## Avoid

- `final_final`
- `new2`
- `temp_last`
- ad hoc lane names that duplicate an existing zone

## Source Anchors

- [docs/DOCS_INFORMATION_ARCHITECTURE_v1.md](../DOCS_INFORMATION_ARCHITECTURE_v1.md)
- [docs/FILE_PURPOSE_MAP.md](../FILE_PURPOSE_MAP.md)
- [docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md](../architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)
- [docs/architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md](../architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md)
- [docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md](../architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md)
- [docs/architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md](../architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md)
