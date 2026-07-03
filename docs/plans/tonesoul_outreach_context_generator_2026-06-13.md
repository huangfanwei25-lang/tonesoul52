# ToneSoul Outreach Context Generator Plan

This is a side-roadmap parked outside `task.md` because it is outreach infrastructure, not part of the active Reality Sync patchset.

## Phase 1: Context Profiles

- [x] Define platform profiles for audience, format, publish mode, automation boundary, policy sources, and things to avoid.
- [x] Define language profiles for zh-TW, zh-CN, en, ja, ko, es, fr, and de.
- [x] Mark strict platforms as manual-only or blocked instead of forcing publication.

**Success criteria**: the generator can explain why a draft is suitable, manual-only, review-required, or blocked.

## Phase 2: Draft Generation

- [x] Generate Markdown draft packets with frontmatter, warnings, blockers, and policy sources.
- [x] Generate a JSON manifest summarizing publish posture.
- [x] Preserve an evidence boundary and AI-use disclosure for longform/manual-review drafts.

**Success criteria**: `python -m tools.outreach.post_generator` creates platform-specific draft files without network access or publishing.

## Phase 3: Safety And Tests

- [x] Reject claims that imply guaranteed acceptance, proven safety, production readiness, sentience, or consciousness.
- [x] Keep the tool draft-only; no API posting, scraping, account rotation, or moderation evasion.
- [x] Add tests for strict platform blocking, disclosure, evidence boundary, and manual-only platform behavior.

**Success criteria**: focused pytest coverage passes for the outreach generator.

