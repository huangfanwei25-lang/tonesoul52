# Vercel Deploy Guide (Navigator / apps/web)

Purpose: deployment guide for the Vercel-hosted web surface and its connection to the external ToneSoul backend.
Last updated: 2026-02-14

## Scope

This guide covers deployment settings for:
- Frontend/API routes on Vercel (`apps/web`)
- External backend (`apps/api/server.py`) reachable via public URL

---

## 1. Vercel Project Settings

Project root:
- `apps/web`

Build settings:
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: default (`.next`)

---

## 2. Required Vercel Environment Variables

Set in Vercel Project -> Settings -> Environment Variables.

| Variable | Recommended Value | Scope | Purpose |
|---|---|---|---|
| `TONESOUL_BACKEND_URL` | `https://<your-backend-domain>` or `same-origin` | Production + Preview | Next API route proxy target (external backend or same-origin backend alias) |
| `NEXT_PUBLIC_CHAT_EXECUTION_MODE` | `backend` | Production + Preview | Force chat to backend-first |
| `NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK` | `0` | Production | Disable provider fallback in production UI |
| `NEXT_PUBLIC_REPORT_EXECUTION_MODE` | `backend` | Production + Preview | Force session report to backend |
| `NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK` | `0` | Production | Disable provider fallback in production UI |
| `TONESOUL_ENABLE_CHAT_MOCK_FALLBACK` | `0` (or unset) | Production + Preview | Keep `/api/chat` transport fallback disabled unless explicitly needed |

Optional (legacy/provider mode only):
- `NEXT_PUBLIC_OLLAMA_URL`
- `NEXT_PUBLIC_OLLAMA_MODEL`

Backward compatibility variable (not preferred):
- `NEXT_PUBLIC_BACKEND_CHAT_FIRST=0` (maps to legacy provider mode)

---

## 3. Backend-Side Required Settings

Your backend host (not Vercel) should allow Vercel origins:

| Variable | Example |
|---|---|
| `TONESOUL_CORS_ORIGINS` | `https://tonesoul.example.com,https://tonesoul-git-main-xxx.vercel.app` |
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_KEY` | `<service_role_key>` |

Notes:
- Include both production domain and preview domain patterns you actually use.
- Avoid overly broad wildcard origins for production.
- `SUPABASE_KEY` should use service role key on backend only (never expose to frontend env).

---

## 4. Deployment Strategy

Recommended production policy:
1. Keep frontend on Vercel.
2. Choose backend mode:
   - External backend: keep backend on a stable host (VM/container/PaaS), set `TONESOUL_BACKEND_URL=https://<backend-domain>`.
   - Same-origin backend: set `TONESOUL_BACKEND_URL=same-origin` (or leave unset on Vercel) and use in-project Python aliases under `/api/_backend`.
3. Disable provider fallback in production (`NEXT_PUBLIC_*_FALLBACK=0`).
4. Keep chat mock fallback disabled in production (`TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=0`).

Why:
- Prevent "mock/provider fallback appears successful" in production.
- Keep contract behavior deterministic and auditable.

---

## 5. Post-Deploy Verification

From local or CI:

```powershell
python scripts/verify_web_api.py --web-base https://<your-vercel-domain> --api-base https://<your-backend-domain-or-same-vercel-domain> --require-backend --timeout 40
```

Success criteria:
- All web routes return non-fallback backend responses.
- No `backend_mode=mock_fallback` when `--require-backend` is used.

---

## 5.1 Pre-Deploy Guard (Recommended)

Run preflight before promoting production settings:

```powershell
python scripts/verify_vercel_preflight.py --strict --probe-health

# Same-origin backend mode
python scripts/verify_vercel_preflight.py --strict --same-origin
```

Preflight checks:
- external mode: `TONESOUL_BACKEND_URL` exists, is absolute HTTPS, and is not localhost
- same-origin mode: `TONESOUL_BACKEND_URL` may be unset / `self` / `same-origin`
- production policy keeps chat mock fallback disabled
- frontend execution/fallback flags match backend-first contract
- backend `/api/health` is reachable (when `--probe-health` is enabled and a probe URL is provided)

Manual GitHub Action entrypoint:
- `.github/workflows/vercel_preflight.yml`
- `workflow_dispatch` input: `backend_url`

---

## 6. Failure Patterns

If you see fallback behavior in production:
1. Check `TONESOUL_BACKEND_URL` value in Vercel env.
   - External mode: must be a reachable HTTPS backend, never `localhost`/`127.0.0.1`.
   - Same-origin mode: use `same-origin`/`self` or leave unset on Vercel.
   - Avoid invalid placeholders like `mock`.
2. Check backend CORS includes Vercel domain.
3. Confirm backend health endpoint is reachable over HTTPS.
4. Re-run `verify_web_api.py --require-backend`.

---

## 7. Decision Snapshot (Current)

- `SDH` gate: `SOFT_FAIL` (approved).
- `RDD` threshold: case-count first (`>=10`) (approved).
- `DDD` freshness SLA: 7 days (approved).
- `Systemic betrayal` operations require explicit user confirmation (approved).

---

## 8. Walkthrough Alignment (2026-02-14)

To keep deployment docs aligned with current runtime/governance:

- System walkthrough: `docs/system_walkthrough.md`
- Release staging checklist: `docs/plans/release_readiness_staging.md`
- Task board: `task.md`

Recommended minimum release gate before deployment:

```powershell
python -m pytest -v --tb=short --maxfail=5
python -m black --check --line-length 100 tonesoul tests
python -m ruff check tonesoul tests
python -m pytest tests/red_team -q
```
