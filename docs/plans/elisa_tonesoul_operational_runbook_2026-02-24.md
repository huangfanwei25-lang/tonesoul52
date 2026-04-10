# Elisa x ToneSoul Operational Runbook (Phase 108 P3)

Date: 2026-02-24  
Scope: Production-safe operation for Elisa IDE integration over ToneSoul governance APIs.

## 1. Pre-Deploy Gate

Run all commands from repo root:

```bash
# 1) Web contract + Elisa payload smoke (same-origin mode)
python scripts/verify_web_api.py \
  --web-base https://tonesoul52-ruby.vercel.app \
  --api-base https://tonesoul52-ruby.vercel.app \
  --same-origin \
  --elisa-scenario

# 2) Full 7D gate with SDH
python scripts/verify_7d.py \
  --include-sdh \
  --web-base https://tonesoul52-ruby.vercel.app \
  --api-base https://tonesoul52-ruby.vercel.app \
  --sync

# 3) Vercel preflight with governance surface probe
python scripts/verify_vercel_preflight.py \
  --strict \
  --same-origin \
  --probe-governance-status \
  --web-base https://tonesoul52-ruby.vercel.app
```

Release is blocked if any command exits non-zero.

## 2. Deploy Procedure

1. Push to `master` and wait for GitHub Actions to complete.
2. Automatic release evidence now comes from `ToneSoul CI` and `post_release_monitor`; if you intentionally run the legacy manual replay lane, confirm `web_api_quality_replay` is green (must include `--elisa-scenario` in command).
3. Deploy to Vercel production (CLI or dashboard promote).
4. Verify these endpoints on production:
   - `GET /api/backend-health`
   - `GET /api/governance-status`
   - `POST /api/chat` (Elisa scenario via `verify_web_api.py`)

## 3. Runtime Health Expectations

- `GET /api/backend-health` in same-origin mode should return:
  - `backend_mode = "same_origin"`
  - `governance_capability = "mock_only"` (if field present)
- `GET /api/governance-status` should return:
  - `status = "ok"`
  - `backend_mode = "same_origin"` or `"external_backend"`
  - `elisa.integration_ready = true`

## 4. Rollback Playbook

When integration regression is detected:

1. Freeze deploys (no additional merges to `master`).
2. Promote previous known-good Vercel deployment.
3. Re-run:
   - `python scripts/verify_web_api.py ... --same-origin --elisa-scenario`
   - `python scripts/verify_7d.py --include-sdh ...`
4. Open incident note with:
   - failing commit SHA
   - first failing check/workflow
   - rollback deployment URL
5. Re-enable deploy only after patch branch is validated by the same three gates.

## 5. Release Checklist (Operational)

- [x] Elisa payload profile contract is tested (`apiRoutes.chatTransport`, `apiRoutes.invalidJson`).
- [x] Governance status surface exists (`GET /api/governance-status`) with route tests.
- [x] Legacy full-stack quality replay preserves the Elisa scenario (`--elisa-scenario`) for manual comparison.
- [x] Preflight supports governance surface probing (`--probe-governance-status --web-base`).
- [x] Memory discussion entry written for each integration phase completion.
- [ ] Final GA artifact pending: `docs/RELEASE_NOTES_v1.0.0.md` + tag `v1.0.0`.
