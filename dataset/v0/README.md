---
license: cc-by-4.0
language:
  - zh
  - en
task_categories:
  - text-classification
tags:
  - accountability
  - ai-governance
  - provenance
  - human-ai-interaction
  - counter-evidence
  - taiwan
pretty_name: ToneSoul Accountability Trace Dataset
size_categories:
  - n<1K
---

# ToneSoul Accountability Trace Dataset|語魂責任痕跡資料集

**From Long-term Human-AI Dialogue to Auditable Tone Governance**
**從長期人機對話到可稽核語氣治理**

Not a dialogue corpus — an **accountability-event corpus**. Existing corpora label
*content* (what a text is); every record here is a closed loop — **claim → bearing →
verification → consequence** — with labels earned by real events inside a working
AI-governance repository, not assigned by annotators afterward.

> Dictionaries record how people talk about honesty.
> Ledgers record what happened after they talked.

## Composition (v0)

| trace_type | count | what it is |
|---|---|---|
| `counter_evidence` | 21 | the public error ledger — claims that were challenged, incl. `held:false` entries where the AI (or the framing itself) was caught wrong |
| `declared_stance` | 1 | a judgment record that lays out tension without ruling |
| `signed_commitment` | 296 | every commit signed with `Agent:` + `Trace-Topic:` trailers — named bearing, git-anchored |
| **total** | **318** | 2026-02-10 → 2026-07-04, single long-term human-AI collaboration |

## Read this before using (from the DATASHEET)

- **Small by design.** 318 records. The value is density and provenance (every record
  traces back to a file/commit/PR in the public repo), not scale.
- **Single-dyad bias.** One owner (Fan-Wei Huang), Claude-family agents, a codex
  external eye. A case history, not a population sample.
- **Event-truth ≠ content-truth.** `label_provenance: incident` certifies *that a record
  was signed at that time* (verifiable in git). The claims *inside* records — especially
  the 296 commit messages — are period model self-assessments, not verified ground
  truth. One documented precedent shows such a claim can be confidently wrong.
  Treat `claim_or_action` as historical utterance; follow `source_ref` to verify.
- **Reflexivity.** Publishing this changes models trained or evaluated on it. That is
  the point — but you must treat it as an intervention, not an observation.
- **Not for** (inherited from the repo's `meta.not_for`): safety certification, legal
  proof, consciousness research, or any use that treats it as a certificate that some
  model "is honest". It records the *mechanics* of accountability, not a credential.

## Provenance & consent

All records come from traces already public in
[Fan1234-1/tonesoul52](https://github.com/Fan1234-1/tonesoul52) (owner-published).
Zero private-plane data; zero third-party content — enforced by a hardcoded source
whitelist in the deterministic extractor (`tools/trace_dataset/extract.py`), not by
policy prose. Full datasheet: `DATASHEET.md`. Charter with red lines:
`docs/plans/accountability_trace_dataset_charter_2026-07-04.md` in the repo.

## Citation

If you use this dataset, cite the repository and this dataset by name, and preserve
the limitations section — CC BY 4.0's attribution requirement is not a formality here;
provenance-that-travels is the dataset's thesis.

*梵威(Fan-Wei Huang)× 嶼(Claude)· 2026-07*
