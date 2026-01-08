# TODO (ToneSoul 5.2)

Scope: manage tasks and transcription fixes within `5.2/` only.

## Active Tasks


## Completed
- [x] Fix garbled transcription/encoding in `spec/tech_trace_integration.md` (saved with UTF-8 BOM) (2025-12-28 11:40:32).
- [x] Create TODO tracking framework (2025-12-27 17:23:51).
- [x] Scan for transcription/encoding issues across `5.2/**/*.md` and `5.2/**/*.txt` (2025-12-27 17:26:06).
- [x] Batch-fix transcription errors in `5.2/reports/WHITEPAPER_recovered_utf8.md` by syncing from `docs/WHITEPAPER.md` and saving the raw copy as `5.2/reports/WHITEPAPER_recovered_utf8_raw.md` (2025-12-27 17:26:06).
- [x] Refresh transcription scan report: `5.2/reports/transcription_fix_log.json` (2025-12-27 17:26:06).
- [x] Validate whitepaper sync: `docs/WHITEPAPER.md` matches `5.2/reports/WHITEPAPER_recovered_utf8.md` (2025-12-27 17:30:16).
- [x] Summarize system understanding (handoff, architecture tree, YSTM spec, execution architecture) (2025-12-27 17:30:16).
- [x] Expanded transcription scan to include `.json/.yaml/.yml/.toml` and refreshed `transcription_fix_log.json` (2025-12-27 17:51:21).
- [x] Added batch scan/fix script `5.2/scripts/transcription_fix.py` and ran it to refresh the report (2025-12-27 17:54:44).
- [x] Ignored raw corrupted backup in transcription scans and re-ran scan/apply (2025-12-27 18:08:08).
- [x] Implement TSR (Delta T/S/R) metrics + pipeline/audit/evidence wiring (2025-12-27 18:55:40).
- [x] Implement DCS gate + dcs_result artifact wiring (2025-12-27 18:55:40).
- [x] Deepen LTM provenance with artifact index/hashes + pointers (2025-12-27 18:55:40).
- [x] Refresh roadmap + whitepaper alignment + strategic positioning placeholder (2025-12-27 18:55:40).
- [x] Add TSR/DCS tests (2025-12-27 18:55:40).
- [x] Add TSR/DCS policy defaults and wire scoring/gates to spec config (2025-12-27 19:50:10).
- [x] Add TSR/DCS snapshot panel in audit dashboard (2025-12-27 21:42:30).
- [x] Reviewed staged/uncommitted changes; noted encoding issue in `spec/tech_trace_integration.md` (2025-12-28 00:50:37).

## Change Log
- 2025-12-28 11:40:32: Re-saved `spec/tech_trace_integration.md` with UTF-8 BOM to resolve garbled display in default Windows readers.
- 2025-12-27 17:23:51: Initialized TODO.md.
- 2025-12-27 17:26:06: Synced `WHITEPAPER_recovered_utf8.md` from `docs/WHITEPAPER.md`; archived raw copy; regenerated transcription scan report.
- 2025-12-27 17:30:16: Verified whitepaper sync matches source.
- 2025-12-27 17:30:16: Added system understanding summary draft.
- 2025-12-27 17:51:21: Expanded transcription scan suffixes and refreshed report.
- 2025-12-27 17:54:44: Added transcription_fix.py and refreshed scan report.
- 2025-12-27 18:08:08: Added ignore list for raw backup; re-ran scan with apply/heuristic (no changes).
- 2025-12-27 18:55:40: Added TSR metrics module + DCS gate + LTM provenance enhancements; updated docs and tests.
- 2025-12-27 19:50:10: Added TSR/DCS policy YAML defaults and loaded them in scoring/gates.
- 2025-12-27 21:42:30: Added TSR/DCS snapshot panel to audit dashboard.
- 2025-12-28 00:50:37: Reviewed staged/uncommitted deltas; added TODO for `spec/tech_trace_integration.md` encoding fix.

## Notes
- Memory entries are logged in `5.2/記憶.txt` for each adjustment.
- `5.2/reports/WHITEPAPER_recovered_utf8_raw.md` is intentionally preserved as a raw corrupted backup (contains replacement characters).

## System Understanding Summary (Draft)
- Philosophy kernel: define negative claims and vetoability; governance is audit-first rather than control-first.
- Time-Island protocol: chronos/kairos/trace bind artifacts to time, decision context, and residual risk.
- Governance core: value triplet + gate principles enforce non-bypassable safety and traceable decisions.
- Engineering core: tone schema/TSR, drift + POAV gating, DS/SR recovery, StepLedger, persona-as-function, and operating templates.
- Memory + trace: ETCL lifecycle, seed schema, EchoTrace responsibility chain, L2/L3 trace levels.
- YSTM spec: PoPE what/where decoupling, Node + UpdateRecord schema, energy totals, drift vectors, terrain outputs, semantic diff + patching.
- Execution architecture v0.4: YSS pipeline (M0-M5), YSTM record layer, gates, Skill Gravity Well integration, phase-2 governance expansion.
