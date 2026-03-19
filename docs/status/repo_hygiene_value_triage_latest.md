# Repo Hygiene Value Triage (Latest)

Generated: 2026-03-17

## Scope

- Goal: classify suspicious or orphan/local files by value before deletion.
- Method: tracked-reference check + quick content inspection.

## High Value (Keep)

- `temp/test_lore.md`
  - Value: architecture lore describing why ToneSoul favors fast, fluid design over heavy over-analysis.
  - Reason to keep: explains foundational design intent.
- `docs/nlnet_grant_proposal_draft.md`
  - Value: strategic grant proposal draft.
  - Reason to keep: planning artifact with external-facing relevance.
- `reports/git_phase2_commit_batch_draft_2026-02-20.md`
  - Value: historical coordination and commit-batching context.
  - Reason to keep: process memory for future large merges.
- `memory/resonance_drafts.md`
  - Value: resonance and memory governance notes.
  - Reason to keep: connected to ongoing memory/governance evolution.

## Medium Value (Archive/Review)

- `law/README_old.md`
  - Value: minimal legacy documentation value.
  - Suggested handling: archive path or replacement README with redirect note.
- `temp/consolidator_worktree_backup.py`
  - Value: backup snapshot of consolidator logic.
  - Suggested handling: keep only if used as historical recovery reference; otherwise archive or remove.

## Low Value (Delete)

- `tmp/add_llm_endpoints.py`
- `tmp/fix_arch.py`
- `tmp/fix_arch2.py`
- `tmp/fix_arch3.py`
- `tmp/fix_chat_corruption.py`
- `tmp/fix_llm_backend.py`
- `tmp/fix_persona.py`
- `tmp/fix_persona_backend.py`
- `tmp/fix_server_persona.py`
- `tmp/fix_settings.py`
- `tmp/fix_sv2.py`
- `tmp/fix_try_block.py`
- `tmp/upgrade_chat_switcher.py`
- `temp_diff.txt`
- `.codex_tmp/` (empty)
- `temp_ci_lint_62894064342/` (empty)

## Actions Applied In This Pass

- Deleted all listed low-value orphan scripts/files.
- Deleted empty local artifacts: `.codex_tmp/`, `temp_ci_lint_62894064342/`.
- Kept high/medium value candidates for explicit follow-up decisions.

## Boundary Rule Reinforced

- Public review surfaces stay in `docs/status/` and `docs/chronicles/`.
- Local runtime/cache state stays under `memory/autonomous/` and should not appear in repo root.