# Evidence shadow integration — bounded, owner-authorized pilot

Use the existing `ts review` entry. Keep baseline wording findings unchanged; optional evidence
sidecar adds quotation integrity and declared argument review. Never change council verdicts,
trading authority, or forecast scoring. Source authenticity and semantic review remain explicit
human/assistant judgments, not automatic proof. No private finance records are included.

## Phase 1: Source and baseline
- [x] Match public master 2f4530c; isolate feature worktree.
- [x] Retrieve TSMC official release directly and verify short excerpts.
## Phase 2: Integration
- [x] Add optional `--evidence-case` with document hash binding.
- [x] Preserve existing findings and advisory exit behavior; invalid sidecar reports an error.
## Phase 3: Verification and delivery
- [x] Run focused tests, required full checks, and public-source replay.
- [ ] Record failures separately from functional results; publish only after required gates pass.

Success: stale source/document/review is surfaced, baseline is preserved, and sample results
cannot be presented as new independent forecasts or a general accuracy estimate.
