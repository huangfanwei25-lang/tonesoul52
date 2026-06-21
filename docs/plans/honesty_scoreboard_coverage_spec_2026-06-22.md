# Spec — Honesty-Scoreboard Coverage Extension (work order for Codex)

> Status: bounded work-order spec; **not** ratified into task.md (ratification is an owner act).
> Author: Claude (Opus 4.8), architect lane · Implementer: Codex · Reviewer: Claude (cross-AI loop).
> Last updated: 2026-06-22.
>
> **Framing — read first.** This is a **coverage extension, NOT a feature and NOT a new
> measurement.** `tools/eval/honesty_scoreboard.py` already exists and already has all the
> machinery; this only makes its index cover the two characterizations that shipped *after* it
> (independent_check #157, drift_consistency #159). It adds **no new metric, no new capability, no
> composite score**, and changes **no runtime behaviour**. If it starts to grow beyond "add two
> pieces + keep the board honest", stop — that is scope creep. It does **not** change the standing
> conclusion that the binding next step is a real consumer.

## Goal

The board indexes program pieces 0–4. Two later characterizations are not yet indexed:

- `independent_check` — `tools/eval/independent_check_characterization.py` (#157)
- `drift_consistency` — `tools/eval/drift_consistency_characterization.py` (#159)

Add both to the board's coverage so the index is complete, while preserving every honesty
discipline the board already bakes in (anti-aggregation, per-piece forbidden-claim surfacing,
`canonical:false`, no composite score).

## What to change (minimal)

1. **Add two `Piece(...)` entries to `PIECES`:**
   - `Piece(6, "independent_check", "<leg>", "tools.eval.independent_check_characterization", "independent_check_characterization_latest")`
   - `Piece(7, "drift_consistency", "<leg>", "tools.eval.drift_consistency_characterization", "drift_consistency_characterization_latest")`

   `program_piece` **5 is the board itself** (it does not self-index) — keep the gap; do **not**
   renumber 0–4.

   **Leg choice** (pick the most *honest* descriptive label — a new leg is fine; `legs_covered`
   is a description, not a score):
   - `independent_check` spans council + unsourced-confidence marker + egress stack
     (cross-process). Candidate leg: **`independent-cross-check`** (new). Do not force it under an
     existing leg if that misleads.
   - `drift_consistency` spans council `logic_contradiction` + parked corrective-recall + the
     not-wired prior-position surface. Candidate leg: **`consistency-drift`** (new).

   State your leg choice + a one-line reason in the PR.

2. **Update the module docstring / `PIECES` comment.** It currently says the board is "program
   piece 5", that "1-4 are the program's measured pieces", and "egress_gate is piece 0". Extend it
   to note 6–7 are now indexed too, and that 5 is the board itself (intentionally not self-indexed).

3. **Fix the board's OWN line-ending bug** (same lesson as the drift review, #159). `main()`
   writes both artifacts with `write_text(..., encoding="utf-8")` **without** `newline="\n"`, so on
   Windows it emits **CRLF** and leans on git normalization to land LF. Pin both writes to
   `newline="\n"` so the source emits LF on all platforms.

4. **Regenerate the committed artifacts** so they reflect 7 pieces, **as LF**:
   `docs/status/honesty_scoreboard_latest.{json,md}`.

5. **Update `tests/test_honesty_scoreboard.py` to pin the NEW honest coverage — not tautologies:**
   - `piece_count` 5 → **7** entries; `pieces_built`; `legs_covered` now includes the new leg(s).
   - assert both new pieces appear in `pieces` with `build_ok: True`.
   - assert each new piece's `forbidden_public_claim_ids` are **surfaced** by the board — e.g.
     `detects_semantic_drift` (drift) and `compares_raw_evidence_content` (independent_check) appear
     in the board output. This pins that the board cannot quietly drop a piece's limits.
   - keep the existing anti-aggregation assertions intact.

## Shape notes (already handled by the board — verify, don't rebuild)

- Both pieces expose `build_report(updated_at=...)`, `doc_provenance.canonical=False`,
  `experiment.forbidden_public_claim_ids`, `allowed_conclusion`,
  `experiment.raw_fixture_text_in_public_report=False`, and `not_*` negations — exactly what
  `_summarize_piece` reads. **No adapter needed.**
- **Mismatch to leave alone:** `drift` has `experiment.measures` (a list); `independent_check` does
  **not**. The board uses `experiment.get("measures")` → `None` for independent_check. That is fine
  — do **not** invent a `measures` list for independent_check to "fix" it; `None` is honest.
- Both use `forbidden_public_claim_ids` (not egress's `forbidden_public_claims`); the board's
  `_forbidden_claims` already handles both spellings.

## Disciplines (same bar as the pieces)

- No new capability / no composite score / no new metric. **Coverage only.**
- **No runtime change** (nothing wired into the pipeline).
- `canonical:false` preserved; the anti-aggregation caveat + `BOARD_FORBIDDEN_CLAIM_IDS` left
  untouched (do **not** add a new board-level forbidden id — no new overclaim is introduced).
- Deterministic (byte-identical modulo timestamp); LF line endings **at the source**.

## Verification — run ALL before reporting (the recurring lesson)

- `ruff` **AND** `black --check` (black was the gap twice — "ruff passed" is **not** enough).
- `pytest tests/test_honesty_scoreboard.py` + the two piece tests (`test_independent_check_*`,
  `test_drift_consistency_*`) still green.
- Determinism: two `build_report(updated_at=FIXED)` runs byte-identical.
- Artifact faithfulness: regenerate to a temp path, `diff` vs committed = empty (numbers not
  hand-edited).
- **Line endings:** verify the committed json/md are LF using `read_bytes()` and counting
  `b"\r\n"` — do **not** use `read_text()` to check (it normalizes newlines on read and cannot
  detect CRLF; this exact false-negative happened in the #159 review).
- Report the honest numbers (`piece_count` 7, `legs_covered`, etc.).

## Non-goals (do NOT do)

- Do **not** add a composite / aggregate honesty score (the whole point is its absence).
- Do **not** wire anything into the runtime pipeline.
- Do **not** add a `measures` list to independent_check to make it symmetric with drift.
- Do **not** add the board to its own `PIECES` (no self-indexing).

## Hand-off

Codex implements; Claude independently reviews (re-runs the full verification above, **not**
trusting the self-report — `black` and LF line endings have *both* been self-report gaps) and
lands.
