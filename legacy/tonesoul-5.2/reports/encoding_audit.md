# Encoding / Mojibake Audit (ToneSoul 5.2)

## Findings
1. `yuhun_cli.py`
   - Contains garbled banner characters and non-ASCII sequences likely from encoding mismatch.
   - Risk: unreadable UI, potential terminal rendering issues, maintainability loss.

2. `ToneSoul-Repo/app.py`
   - Multiple garbled strings and broken text artifacts.
   - Risk: user-facing prompts unreadable; may hide syntax errors if quotes are corrupted.

3. `body/dashboard/app.py`
   - Contains mixed Unicode emoji and some corrupted glyphs in UI text.
   - Risk: mostly UX/visual; may be acceptable but should be normalized.

## Likely Cause
- Files saved in non-UTF-8 encoding and later read as UTF-8 (or vice versa).

## Suggested Fix Plan (No edits applied)
1. Identify original encoding (e.g., Big5/GBK/CP950) using a detector.
2. Re-save to UTF-8 with BOM disabled.
3. Verify string literals display correctly and run a quick syntax check.
4. If original text is unknown, replace with clean ASCII/UTF-8 equivalents.

## Notes
- Consider isolating banners and prompts into a `strings.py` module to keep encoding consistent.
