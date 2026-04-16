# ToneSoul Encoding And Mojibake Hazard Register

> Purpose: register encoding hazards, garbled headers, broken section labels, and mixed-layer readability issues in high-traffic documentation so cleanup can follow a clear severity order.
> Last Updated: 2026-03-29
> Authority: documentation hygiene aid. Does not outrank runtime code, tests, or canonical architecture contracts.
> Status: historical 2026-03-29 hazard snapshot. Major AI entry cleanup landed on 2026-04-14; use current entry surfaces for live routing instead of treating this register as the latest policy.

---

## Overall Encoding Posture

After auditing the high-traffic surfaces:

- Markdown files in `docs/`, `docs/architecture/`, and root are UTF-8 and file-level content is intact.
- Chinese content in the audited files is present and readable at the file layer.
- The three root `.txt` files are UTF-8 with BOM and are structurally unusual, but not corrupted.

**There is no evidence of critical file-layer mojibake corruption in the current high-traffic surfaces.**

Most observed hazards are one of these instead:
- structural readability problems
- stale metadata
- render-layer terminal noise
- inconsistent routing signals

---

## Hazard Register

### Severity: High

| ID | Surface | Hazard | Why It Matters |
|----|---------|--------|----------------|
| H1 | historical entry cleanup notes | pre-2026-04-14 AI entry hazards | Keep only as lineage; do not treat as current state |

### Severity: Medium

| ID | Surface | Hazard | Why It Matters |
|----|---------|--------|----------------|
| M1 | historical cleanup notes | may still mention removed or rewritten entry hazards | Can mislead later readers if treated as current |
| M2 | `docs/README.md` and `docs/INDEX.md` | role split still needs to be respected by readers | Guided gateway and full registry serve different jobs |
| M3 | `docs/INDEX.md` | stale subdirectory counts | Later agents undercount the documentation surface area |
| M4 | root lineage `.txt` files | format mismatch | Not corruption, but unusual in a markdown-centric repo |
| M5 | root historical-spec references in older notes | absent-file references may survive in older reports | Readers may chase dead lineage paths |

### Severity: Low

| ID | Surface | Hazard | Why It Matters |
|----|---------|--------|----------------|
| L1 | `README.zh-TW.md` | content sync can drift again later | Chinese public entry should keep mirroring the live English entry posture |
| L2 | `SOUL.md` | version mismatch in identity text | Mostly cosmetic, but can confuse later readers |
| L3 | quickstart snapshots | test-count prose may drift over time | Snapshot drift is visible if counts are not refreshed |

---

## Render-Layer Boundary

The following must stay clearly separated:

- **File-layer corruption**: the bytes on disk are wrong
- **Render-layer noise**: terminal, shell, or locale shows replacement characters
- **Structural hazard**: the file is intact but badly organized
- **Metadata drift**: counts, dates, or routing claims are stale

`??` seen in a Windows terminal is **not** sufficient evidence of file corruption.
Treat display noise as a render-layer issue unless file inspection proves otherwise.

---

## Safest Cleanup Order

```text
Priority 1:
  - fix contradictory or duplicate metadata
  - remove stale footer dates
  - fix stale directory counts

Priority 2:
  - restructure the AI_ONBOARDING "If wall"
  - streamline the Chinese README routing surface

Priority 3:
  - decide long-term root lineage handling
  - decide docs/README versus docs/INDEX role split more sharply
```

---

## What Is Not A Hazard

- UTF-8 markdown files with intact Chinese text
- BOM in the root lineage `.txt` files by itself
- render-layer `??` that does not survive file-level inspection
- deep documents simply being long
