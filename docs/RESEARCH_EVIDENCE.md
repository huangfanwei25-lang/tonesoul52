# Research Evidence Map (2026-02-04)

Purpose: Curate peer-reviewed and standards-based sources that support ToneSoul's auditability, governance, and meaning-transfer positioning.
Selection criteria: Prefer journals and standards. Conference or preprint items are listed only as supplementary references.

## Core Sources (Journals / Standards)
| Source | Type | Key Point | ToneSoul Application |
| --- | --- | --- | --- |
| Data Statements for Natural Language Processing (TACL 2018, Bender & Friedman) https://aclanthology.org/Q18-1041/ | Journal | Standardized data documentation reduces bias and improves scientific claims about generalization. | Create Data Statement templates for `memory/` and external sources to make provenance and scope explicit. |
| FactSheets: Increasing trust in AI services (IBM JRD 2019) https://research.ibm.com/publications/factsheets-increasing-trust-in-ai-services-through-suppliers-declarations-of-conformity | Journal | Supplier declarations document purpose, performance, safety, security, and provenance. | Add `docs/factsheet.md` for Council, Isnad, risk model, and test evidence. |
| Algorithmic Accountability (BISE 2023) https://link.springer.com/article/10.1007/s12599-023-00817-8 | Journal | Trustworthy systems require transparency and governance structures. | Document Council-Observer-Isnad as a governance flow for external review. |
| Explainable AI Survey (Information Fusion 2020) https://www.sciencedirect.com/science/article/pii/S1566253519308103 | Journal | XAI requires clear taxonomies and responsibility framing. | Keep structured verdict outputs focused on rationale and audience needs. |
| Datasheets for Datasets (Communications of the ACM 2021) https://cacm.acm.org/research/datasheets-for-datasets/ | Journal | Dataset documentation enables accountability and responsible use. | Maintain datasheets for memory and knowledge sources to support audit trails. |
| PROV-DM (W3C Recommendation 2013) https://www.w3.org/TR/2013/REC-prov-dm-20130430/ | Standard | Defines a provenance data model (entity, activity, agent). | Map `provenance_ledger.jsonl` to PROV-DM for interoperability. |
| NIST AI RMF 1.0 (NIST AI 100-1, 2023) https://doi.org/10.6028/NIST.AI.100-1 | Standard | Framework for mapping, measuring, managing, and governing AI risk. | Build an RMF crosswalk for AXIOMS, Council, and Observer. |
| NIST GenAI Profile (NIST AI 600-1, 2024) https://doi.org/10.6028/NIST.AI.600-1 | Standard | GenAI risk profile aligned to RMF 1.0. | Align ToneSoul generative risks (handoff, drift, governance misuse) to RMF categories. |

## Supplementary References (Non-journal but influential)
| Source | Type | Key Point | ToneSoul Application |
| --- | --- | --- | --- |
| Model Cards for Model Reporting (arXiv 2018) https://doi.org/10.48550/arXiv.1810.03993 | Preprint | Standardizes model documentation for intended use and performance. | Provide a System Card-style summary for external stakeholders. |

## Proposed Artifacts (Next Steps)
1. `docs/factsheet.md` aligned to IBM FactSheets.
2. `docs/data_statements.md` aligned to TACL Data Statements.
3. `docs/datasheets.md` aligned to CACM Datasheets.
4. `docs/prov_mapping.md` mapping Isnad to PROV-DM.
5. `docs/rmf_crosswalk.md` mapping AXIOMS, Council, Observer to NIST AI RMF + GenAI Profile.
6. `docs/xai_rationale.md` capturing structured verdict rationale patterns.

## Notes
- Sources listed above are primary publications or standards where possible.
- Update this document when newer versions or standards supersede the current references.
