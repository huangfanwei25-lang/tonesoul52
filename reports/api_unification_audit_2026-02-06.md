# API Unification Audit (2026-02-06)

## Scope
- Backend: `apps/api/server.py` (Flask, localhost:5000)
- Web routes: `apps/web/src/app/api/*/route.ts` (Next.js server routes)
- Goal: align on one backend contract and reduce mock drift.

## Findings
- Existing Flask endpoints:
  - `POST /api/chat`
  - `POST /api/validate`
  - `GET /api/memories`
  - `GET /api/consolidate`
  - `POST /api/session-report`
  - `GET /api/health`
- Web-side API routes were using mock-only behavior and defaulting to `http://localhost:8000`.
- Missing contract on Flask side for:
  - `POST /api/conversation`
  - `POST /api/consent`
  - `DELETE /api/consent/{session_id}`

## Changes Applied
- Added Flask endpoints:
  - `POST /api/conversation`
  - `POST /api/consent`
  - `DELETE /api/consent/<session_id>`
- Updated web route defaults:
  - `TONESOUL_BACKEND_URL` default changed to `http://localhost:5000`.
- Replaced web API route mocks with proxy-first behavior plus fallback:
  - `apps/web/src/app/api/chat/route.ts`
  - `apps/web/src/app/api/conversation/route.ts`
  - `apps/web/src/app/api/consent/route.ts`
- Added web proxy route for report generation:
  - `apps/web/src/app/api/session-report/route.ts`
- Updated frontend usage to backend-first:
  - `apps/web/src/components/ChatInterface.tsx` now calls `/api/chat` by default.
  - `apps/web/src/components/SessionReport.tsx` now calls `/api/session-report` first.
- Extended API smoke script:
  - `scripts/verify_api.py` now checks conversation/consent endpoints.
- Added web+backend smoke script:
  - `scripts/verify_web_api.py` verifies Next API routes plus backend health.

## Validation
- Added backend contract tests:
  - `tests/test_api_server_contract.py`
- Existing shared-channel hardening tests remain green:
  - `tests/test_agent_discussion.py`
- Web build passes with new dynamic routes:
  - `/api/chat`
  - `/api/conversation`
  - `/api/consent`
  - `/api/session-report`
- Live integrated smoke (web + backend) passes:
  - `python scripts/verify_web_api.py --web-base http://localhost:3000 --api-base http://localhost:5000 --require-backend`

## Hotfix
- Fixed backend session report import path to avoid package-level side effects:
  - `apps/api/server.py` now imports `SessionReporter` from `tonesoul.tonebridge.session_reporter`.

## Runtime Flags
- Chat execution:
  - `NEXT_PUBLIC_CHAT_EXECUTION_MODE=backend|legacy_provider` (default: backend)
  - Backward compatibility: `NEXT_PUBLIC_BACKEND_CHAT_FIRST=0` maps to legacy provider mode.
  - `NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK=1` enables provider fallback when backend chat fails.
- Session report execution:
  - `NEXT_PUBLIC_REPORT_EXECUTION_MODE=backend|provider` (default: backend)
  - `NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK=0|1` (default: 1)

## Residual Risk
- Direct provider paths still exist as fallback logic for development resilience.
- Backend `/api/chat` payload shape is not yet normalized to a strict shared schema with typed validation.

## Update: Runtime Drift Hardening (2026-02-06)

### Problem Observed
- Live smoke with `--require-backend` can still fail when:
  - Next.js route handlers silently fall back after backend returns non-JSON payload.
  - Runtime backend URL differs from build-time assumptions.
  - Chat route exceeds the default 10s smoke timeout.

### Fixes Applied
- Next route handlers now resolve backend URL dynamically per request via `process.env["TONESOUL_BACKEND_URL"]`, with fallback `http://127.0.0.1:5000`.
- Fallback behavior narrowed:
  - `mock_fallback` only on backend connection failures/timeouts.
  - Backend non-JSON responses now return explicit `502` with `backend_status`.
- Smoke tooling hardened:
  - `scripts/verify_web_api.py` now handles request exceptions without raw traceback.
  - CI `web_api_smoke` step now runs smoke with `--timeout 40`.

### Verification
- `pytest tests/ -q` -> `299 passed, 3 xfailed`.
- `npm --prefix apps/web run build` passed.
- Live strict smoke passed on isolated runtime:
  - `python scripts/verify_web_api.py --web-base http://127.0.0.1:3002 --api-base http://127.0.0.1:5001 --require-backend --timeout 40`

### Remaining Notes
- Local environment may still have an old backend process on `:5000`; this can cause false fallback signals during manual smoke checks.
- `jieba` absence produces a warning path in backend runtime; CI already installs `jieba`, but local setup docs should keep this explicit.
