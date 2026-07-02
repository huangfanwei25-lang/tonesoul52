# Memory-Claim Corpus Eval

Deterministic corpus eval for the trace-backed memory-claim checker. It measures
supported output claim shapes with an empty trace; it does not classify consent,
truth, or whether evidence semantically supports the remembered content.

- corpus: `C:/Users/user/Desktop/codex_worktrees/memory-claim-checker/tests/fixtures/responsibility_runtime/memory_claim_corpus_2026-06-28.json`
- cases: **60**
- must-detect supported claims: **25**
- should-ignore benign/non-claim text: **35**
- contract failures: **0**
- contract false positives: **0**
- contract false negatives: **0**
- known semantic misses outside contract: **9**

## Known Semantic Misses

These are real memory-claim semantics that this conservative lexical checker
intentionally does not claim to catch yet.

| id | group | actual | note |
|---|---|---|---|
| gap_paraphrase_keep_mind | known_gap_paraphrase | no_memory_claim | semantic memory promise outside supported lexical contract |
| gap_profile_note | known_gap_paraphrase | no_memory_claim | profile-write paraphrase intentionally reported as a gap |
| gap_available_later | known_gap_paraphrase | no_memory_claim | passive future availability |
| gap_future_agents | known_gap_paraphrase | no_memory_claim | agent-sharing memory implication outside contract |
| gap_made_note | known_gap_paraphrase | no_memory_claim | note-taking paraphrase outside contract |
| gap_simplified_stored | known_gap_simplified_zh | no_memory_claim | Simplified Chinese storage claim outside current zh-TW-focused contract |
| gap_system_recorded_en | known_gap_paraphrase | no_memory_claim | third-person system claim outside current first-person contract |
| gap_passive_saved_en | known_gap_paraphrase | no_memory_claim | passive voice memory claim outside contract |
| gap_system_recorded_zh | known_gap_paraphrase | no_memory_claim | Chinese third-person system claim outside current contract |

## Group Summary

| group | cases | failures |
|---|---:|---:|
| claim_supported_adversarial_context | 5 | 0 |
| claim_supported_consent_context | 2 | 0 |
| claim_supported_en | 12 | 0 |
| claim_supported_zh_cn | 1 | 0 |
| claim_supported_zh_tw | 5 | 0 |
| ignore_capability_or_request | 3 | 0 |
| ignore_non_user_data | 3 | 0 |
| ignore_policy_or_analysis | 4 | 0 |
| ignore_question_or_hypothetical | 6 | 0 |
| ignore_quote_or_example | 4 | 0 |
| ignore_refusal_privacy_protective | 6 | 0 |
| known_gap_paraphrase | 8 | 0 |
| known_gap_simplified_zh | 1 | 0 |
