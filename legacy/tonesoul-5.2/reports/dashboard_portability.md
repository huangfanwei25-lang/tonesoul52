# Dashboard Portability Plan (ToneSoul 5.2)

## Issue
`body/dashboard/app.py` includes absolute `file:///c:/Users/...` links in the DNA tab.

## Impact
- Breaks on other machines.
- Leaks local filesystem paths.

## Suggested Fix (No edits applied)
- Replace with relative links to `docs/governance/...` and `docs/...`.
- Example (concept):
  - `docs/governance/STREI_OPERATIONAL_PROTOCOL.md`
  - `docs/governance/TEMPORAL_AUDIT_SPEC.md`
  - `docs/governance/COMMUNICATION_STANDARD.md`

## Optional Enhancement
- Provide a helper to resolve local file paths dynamically from repo root.
