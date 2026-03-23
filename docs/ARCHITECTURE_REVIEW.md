# ToneSoul Architecture Review (2026-02-03)

> Purpose: historical architecture review capturing strengths, issues, and recommendations from an earlier repo state.
> Last Updated: 2026-03-23

## Review by Codex (Multi-Role Mode)

### Overall Score: 6.7 / 10

---

## 🏗️ Architect

### Strengths
- Council Facade + SoulDB direction is correct
- Clear separation of concerns emerging

### Issues
- README and actual paths/implementation have drifted
- Ledger path inconsistencies

### Recommendations
- Sync README with current structure
- Add "Quick Start" guide in docs/

---

## 🔒 Security Auditor

### Strengths
- All SQL uses parameterized queries (no injection risk)
- API keys moved to credential resolver

### Issues
- JSON content stored unencrypted in SQLite
- Sensitive data handling needs future encryption

### Recommendations
- Consider encrypting sensitive fields
- Keep monitoring API key exposure

---

## 🧪 Tester

### Issues
- Missing test dependencies (hypothesis, pytest-asyncio)
- Critical paths lacking tests

### Recommendations
- Add test dependency installation to docs
- Prioritize tests for Council and SoulDB

---

## 📚 Documentation

### Strengths
- docs/STRUCTURE.md and docs/SOUL_DB.md are actionable
- README describes architecture and concepts

### Issues
- README not reflecting recent changes (Council Facade, SQLite migration)
- New dependencies not documented

### Recommendations
- Update README with Ledger path and SoulDB interface
- Add environment setup guide

---

## 🦞 ToneSoul (MGGI Philosophy)

### Strengths
- Isnād now has hash-verified chain (auditable consistency)
- Structured verdict output enables external audit

### Issues
- Isnād not yet integrated into all key outputs
- Some modules still use "internal state" instead of "observable coherence"

### Recommendations
- Auto-write Council verdict + structured output to Isnād/ledger
- Clearly separate "observable coherence" fields from "internal assumptions"

---


## Addendum (2026-02-04): Meaning Transfer Positioning

### Summary
- Positioning shifts from "rule enforcement" to "meaning transfer".
- Axioms should encode values; behaviors are derived and testable.
- Audit artifacts (Isnad, drift_log, structured verdicts) should capture "why", not only "what".

### Risks to Watch
- Surface compliance without understanding.
- Handoff that transfers instructions but drops reasons.
- Responsibility breaks when outputs lack rationale.

### Suggested Updates
- README should state the positioning clearly and list concrete risks.
- Provide 2-3 user-facing use cases to align with intent.

---

## Action Items (Priority Order)

1. [ ] Auto-write Council verdict to Isnād (close the audit loop)
2. [ ] Update README with current architecture
3. [ ] Add test dependencies to requirements.txt
4. [ ] Create docs/QUICKSTART.md for new developers
5. [ ] Encrypt sensitive fields in SQLite (future)

*Reviewed: 2026-02-03 23:33 | Reviewer: Codex (GPT-5.1-codex)*
