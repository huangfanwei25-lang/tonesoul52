# ToneSoul — Render Layer And Encoding Boundary Contract

> Purpose: explicitly separate real file corruption from terminal rendering noise, structural readability hazards, and metadata drift, so later agents stop calling every `??` display artifact "mojibake".
> Last Updated: 2026-03-29
> Authority: encoding hygiene boundary aid. Does not outrank runtime code or canonical contracts.

---

## Why This Contract Exists

The prior entrypoint pass raised "mojibake risk" for the root `.txt` files and flagged potential encoding hazards. After actual verification:

- **No file-layer corruption was found in any inspected surface.**
- All Chinese text in `.md` and `.txt` files is valid UTF-8 and renders correctly when read by tools that respect UTF-8.
- The PowerShell terminal on Windows may display `??` or garbled characters for CJK file paths and folder names (e.g., the repo directory `倉庫/`) due to cp950/cp65001 locale settings. This is terminal rendering noise, not file corruption.

Without this contract, a later agent seeing `??` in a shell command output will infer that the file is corrupted and flag a false "mojibake" problem.

---

## Four Encoding-Adjacent Problem Categories

### Category 1: Real File Corruption (mojibake)

**Definition**: The file's byte content contains incorrectly encoded characters. When read by a UTF-8-aware tool, garbled sequences appear (e.g., `é¡è¦`,`ä½ å¥½`, `\xc3\xa9` where Chinese was expected).

**How to detect**: Open the file in a tool that reads raw bytes as UTF-8 (e.g., `view_file`, VS Code, `python3 -c "open('file','r',encoding='utf-8').read()"`). If garbled characters appear in the content itself, it is real corruption.

**Current status in ToneSoul (2026-03-29)**: **NONE FOUND** in any inspected surface.

**Correct response**: Flag for immediate repair.

### Category 2: Terminal Rendering Noise

**Definition**: The file content is correct, but the terminal or shell displays garbled characters because:
- PowerShell's output codepage does not match UTF-8 (`chcp` shows 950 instead of 65001)
- The terminal font does not support CJK characters
- The file path itself contains CJK characters that the shell cannot render

**How to detect**: If `view_file` (which bypasses terminal encoding) shows the content correctly but `Get-Content` or `type` in PowerShell shows `??`, the problem is the terminal, not the file.

**Current status in ToneSoul**: The repo directory `倉庫/` is a CJK name. PowerShell commands may show path artifacts. This is **not** a file problem.

**Correct response**: Ignore as a file-quality concern. Optionally note it as a tooling limitation. When a later agent needs exact high-traffic paths, use `docs/foundation/FILENAME_AND_ENTRY_INDEX.md` instead of trusting garbled terminal echoes.

### Category 3: Structural Readability Hazards

**Definition**: The file content is encoding-correct, but its structure makes it hard to read or navigate. Examples:
- 43 consecutive routing sentences with no headers or grouping
- Duplicate metadata blocks within one file
- Contradictory Status vs Purpose headers
- Stale file counts in an index

**How to detect**: Read the file. If you can read all characters but still cannot navigate or trust the content, it is a structural hazard, not an encoding hazard.

**Current status in ToneSoul**: This is the actual primary hazard category. The AI_ONBOARDING "If wall" (43 statements, lines 45-87) is a structural readability problem. The TAE-01 Status/Purpose contradiction is a metadata trust problem.

**Correct response**: Flag as a structural or metadata hazard. Do not call it "mojibake" or "encoding issue."

### Category 4: Metadata Drift

**Definition**: The file's dates, counts, or claimed status no longer match reality. The content may be correct when it was written, but has drifted.

**How to detect**: Compare the metadata claim (e.g., "Last updated: 2026-03-22") against the actual last-modified date or current repo state.

**Current status in ToneSoul**: Several files have stale "Last Updated" dates, stale file counts, or contradictory status lines.

**Correct response**: Flag as metadata drift. Do not call it "encoding issue" or "corruption."

---

## Decision Table For Later Agents

| You observe | Category | Correct diagnosis | Correct action |
|-------------|----------|-------------------|----------------|
| Chinese characters appear as `é¡è¦` or similar in file content | 1: Real corruption | "This file has encoding corruption" | Flag for immediate repair |
| PowerShell shows `??` in file paths but `view_file` shows correct Chinese | 2: Terminal noise | "Terminal codepage mismatch" | Ignore as file concern |
| All characters are readable but 43 "If..." statements run without headers | 3: Structural hazard | "Structural readability problem" | Recommend grouping/collapsing |
| "Last Updated: 2026-03-22" but the file was clearly modified later | 4: Metadata drift | "Stale metadata" | Recommend date correction |
| `.txt` file uses CRLF while `.md` files use LF | Not a hazard | "Line ending style difference" | Ignore unless causing tooling issues |
| `.txt` file has BOM (byte order mark) | Not a hazard | "UTF-8 BOM present" | Harmless for `.txt` files |

---

## What The Prior Pass Got Right And Wrong

| Prior pass claim | Reality | Verdict |
|-----------------|---------|---------|
| "No actual mojibake found" | ✅ Confirmed | **Correct** |
| "All Chinese UTF-8 content intact" | ✅ Confirmed | **Correct** |
| "Root .txt files have mojibake risk" | ❌ No risk found. Content is clean UTF-8 with BOM. | **Overdiagnosed** — "risk" language was speculative, not evidence-based |
| "CRLF vs LF is a concern" | Trivially true but not a readability hazard | **Over-flagged** |
| "The real problems are structural, not encoding" | ✅ Confirmed | **Correct** |

---

## Rules For Later Agents

1. **Do not use the word "mojibake" unless you have confirmed Category 1 (real file corruption).**

2. **If shell output shows `??`, your first hypothesis should be terminal rendering (Category 2), not file corruption.**

3. **If content is readable but hard to navigate, diagnose it as a structural hazard (Category 3), not an encoding issue.**

4. **If dates or counts are wrong, diagnose it as metadata drift (Category 4), not corruption.**

5. **Do not re-audit encoding unless a new file type or a specific corruption report triggers it.** The current `.md` and `.txt` surfaces are clean as of 2026-03-29.

6. **If path rendering is noisy, prefer the repo's filename index over shell echoes.** Use `docs/foundation/FILENAME_AND_ENTRY_INDEX.md` for high-traffic lookup.
