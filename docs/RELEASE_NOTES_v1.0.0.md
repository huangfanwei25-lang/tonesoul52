# ToneSoul v1.0.0 Release Notes

> Purpose: release record for the first stable governance baseline and the gates used to declare ToneSoul v1.0.0 GA.
> Last Updated: 2026-03-23

Release date: 2026-02-24  
Status: GA (`v1.0.0`)

## Summary

ToneSoul v1.0.0 marks the first stable governance baseline with:

- same-origin web deployment path on Vercel,
- executable 7D audit workflow with SDH integration,
- council divergence quality observability,
- Elisa IDE integration contract (Phase 108 P0-P3),
- CI gates aligned to fail closed on contract regressions.

## Highlights

1. Deployment and runtime stability
- Hardened same-origin mode for web API routes.
- Added explicit backend governance signals (`backend_mode`, `governance_capability`).
- Added governance status surface: `GET /api/governance-status`.

2. Council quality and governance observability
- Added divergence quality metrics and role-tension visibility in deliberation payloads.
- Added governance status rendering support on chat-side message metadata.

3. Elisa integration completion (Phase 108)
- P0: Elisa payload profile + route contract tests + smoke scenario.
- P1: preflight Elisa checks + governance status probe.
- P2: CI blocking smoke includes Elisa scenario.
- P3: operational runbook + rollback + release checklist.

4. Security and integrity hardening
- Improved fallback observability and integrity-hash tracking in agent discussion workflows.
- Added stricter verification behavior for rollout-safe schema evolution.

## Verification Baseline

Core release gates used for v1.0.0:

```bash
python scripts/verify_7d.py --include-sdh --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --sync
python scripts/verify_web_api.py --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --same-origin --elisa-scenario
npm --prefix apps/web run test
npm --prefix apps/web run build
```

## Operational References

- Elisa integration plan: `docs/plans/elisa_tonesoul_governance_integration_2026-02-22.md`
- Elisa runbook: `docs/plans/elisa_tonesoul_operational_runbook_2026-02-24.md`
- v1.0 release gate decision: `docs/plans/release_v1.0_go_nogo_2026-02-24.md`

## Notes

- Current public production mode may run in `same_origin + mock_fallback` depending on deployment environment.  
  This is an accepted v1.0 operating mode when governance contracts and audit gates remain green.
