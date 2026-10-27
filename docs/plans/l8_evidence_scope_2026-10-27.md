# L8 gate evidence scope — 2026-10-27

Status: bounded report correction; not a training authorization or a new governance program.
Reviewed base: `2f4530ccb5ce913b1b636edda209f424f132e12d`.

## Finding and correction

`run_l8_adapter_dataset_gate.py` checks schema fields, declared review flags,
path policy and declared evaluation expectations. It does not read the referenced
source, authenticate a reviewer, or execute the named regression suite. Its old
primary status line says `l8_dataset_gate_ready` even when `ok` is false.
The stored July report covers one example, not a real training dataset audit.

This patch makes a failed/empty/partially malformed dataset say `blocked`, adds
SHA-256 fingerprints for the exact input and schema bytes parsed in that run,
and exposes the limited verification scope in JSON and Markdown. Each file is
read once for parsing and fingerprinting. This binds a report to checked bytes;
it does not bind human approval to those bytes or make the report tamper-proof.
The input and schema reads are sequential, not a filesystem-wide atomic snapshot.

Legacy `ok`, `approved_count`, and successful `ready` remain compatible and mean
only passing these local checks. Consumers must not treat them as authenticated
approval. v1 record policy and reviewer optionality are unchanged.

## Reproduction and verification plan

1. Reproduce rejected, empty and malformed-JSONL reports incorrectly saying ready.
2. Reproduce absent byte fingerprints and absent assurance labels.
3. Verify JSON/JSONL fingerprints match the bytes parsed, including CRLF, even if
   the files are replaced after their first read; retain existing policy tests.
4. Run repository checks before publishing; record actual results in the PR.

## Deferred approval binding

A future version should reference an immutable source revision plus source hash,
identify reviewer and review time, and bind a separate approval receipt to the
canonical training-example digest and policy version. Verification must compare
those values and check reviewer authority. Hashes alone do not establish authority.
Do not silently promote existing self-declared v1 rows into authenticated approvals.
Acceptance tests should cover source substitution, edited examples, missing or
unauthorized reviewers, and withdrawn approval. None of that is implemented here.

## Convergence decision

Prefer a small truthful report over a new memory subsystem. Current evidence
supports local declaration validation, not source authentication, semantic privacy
certification, training readiness, or model-level memory continuity. This work does
not reconstruct unpublished workstation edits and does not merge other draft PRs.

## Verified results

- Before patch: 5 new regression cases failed; 3 existing cases passed.
- After patch: all 8 focused cases passed.
- Full Python suite: 8,151 passed, 9 skipped (96.80 s); skipped is not passed.
- Python and web lint: passed (`npm run lint`, venv Python on PATH).
- Python compilation and Black checks for touched Python files: passed.
- Web build: first attempt failed on Google Fonts TLS verification. The second
  passed with `NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1`; TLS verification
  stayed enabled and no source/configuration changes or font mocks were used.
- Real example CLI `--strict`: passed; this remains an example-only check.
- `git diff --check`: passed.

The additional tests/documentation outweigh deletions because they establish the
previously missing failure-status and byte-identity guarantees. No new service,
dependency, private data, reviewer authority, or approval policy is introduced.
