# Phase 866 - Public Surface Security Hardening (2026-04-23)

## Summary

This phase turns the highest-confidence public-surface findings from
`phase866_security_best_practices_report_2026-04-23.md` into small, reversible fixes.

Scope landed:

- fail-open auth / rate-limit posture on serverless + Flask API surfaces
- wildcard CORS on token-bearing serverless responses
- stored-XSS sinks in static observability surfaces
- token leakage via `?read_token=` URL ingestion in `apps/council-playground`

This phase does **not** claim that the whole repo is now "security complete".
It closes the most directly exploitable issues first and leaves larger design
tradeoffs explicitly visible.

## How The Findings Were Found

The audit started from the public ingress points and moved inward:

1. Read the HTTP entry surfaces under `api/` and `apps/api/server.py`
2. Trace how auth defaults are derived when env vars are absent
3. Inspect browser-facing observability pages for raw `innerHTML` sinks
4. Trace where browser-stored tokens or keys can be injected into requests

This surfaced four concrete risks:

1. `_is_production_env()` only recognized `TONESOUL_*` / `FLASK_ENV`, so
   hosted Vercel/Node deployments could miss the stricter auth posture.
2. `api/_shared/http_utils.py` replied with `Access-Control-Allow-Origin: *`
   even for endpoints that accept `Authorization` and ToneSoul token headers.
3. `apps/council-playground/app.js` and `apps/dashboard/world.html` rendered
   attacker-influenced strings into `innerHTML`.
4. `apps/council-playground/app.js` accepted `?read_token=` from the URL and
   persisted it in long-lived browser storage.

## What Changed And Why

### 1. Public-hosted envs now take the strict auth posture by default

Files:

- `api/_shared/core.py`
- `apps/api/server.py`

Change:

- `_is_production_env()` now treats `NODE_ENV=production`,
  `VERCEL_ENV=production|preview`, and `VERCEL=1` as production-grade surfaces
  for security posture purposes.

Why:

- The vulnerability was not "auth code missing"; it was "strict mode depends on
  too narrow an environment detector".
- This fix preserves the existing config model and closes the fail-open gap
  without forcing a larger auth redesign in one step.

### 2. Serverless CORS no longer defaults to wildcard for token-bearing APIs

File:

- `api/_shared/http_utils.py`

Change:

- CORS now reflects only:
  - same-origin requests
  - explicitly configured `TONESOUL_CORS_ORIGINS`
  - `*` only if a human explicitly configures `TONESOUL_CORS_ORIGINS=*`

Why:

- `Authorization` plus wildcard CORS is an unsafe default.
- The new behavior aligns the serverless helper with the repo's explicit-origin
  posture already used in the Flask surface.

### 3. Static observability pages now treat remote text as text

Files:

- `apps/council-playground/app.js`
- `apps/dashboard/world.html`

Change:

- `apps/council-playground` now builds audit-log DOM nodes with
  `textContent` instead of interpolating untrusted fields into `innerHTML`.
- `apps/dashboard/world.html` now escapes dynamic vow, tension, visitor, and
  Aegis label text before inserting HTML.

Why:

- These surfaces are operator-facing. A stored XSS here can become browser-side
  token theft or malicious action under an operator session.
- This was a direct sink fix, not a broad UI rewrite.

### 4. Playground token handling is now session-scoped and URL-free

File:

- `apps/council-playground/app.js`

Change:

- removed `?read_token=` URL ingestion
- moved token persistence from `localStorage` to `sessionStorage`

Why:

- Query-string tokens leak into browser history, copied URLs, screenshots, and
  logs.
- `sessionStorage` keeps convenience inside the tab while reducing persistence
  after the session ends.

## Why This Was Not Fixed Differently

Rejected in this phase:

- full auth architecture rewrite
- moving provider BYOK keys out of the browser
- full CSP / browser-hardening program
- replacing static dashboards with a new routed application

Reason:

- those are real follow-ups, but they are not small, reversible fixes
- the current phase goal was to close high-confidence exploit paths first
- patching the concrete sinks and defaults now gives immediate risk reduction
  without pretending the deeper architectural work is done

## Residual Risks Still Visible

Not fixed in Phase 866:

- `apps/web` still supports BYOK provider keys in browser storage; that remains
  a bounded but real exposure under XSS / extension compromise.
- Next/web browser-hardening headers (for example CSP) still need a separate
  rollout.
- `apps/dashboard/world.html` and `apps/council-playground/` remain static
  prototype/reference surfaces, not production-hardened applications.

## Verification

Re-verified during 2026-05-09 convergence extraction:

- `python -m pytest tests/test_api_phase_a_security.py tests/test_serverless_shared_core.py tests/test_static_surface_security.py -q`
- `python -m pytest tests/ -q --ignore=tests/test_demo_ui_modea_e2e.py -x --maxfail=1`
- `python -m ruff check tonesoul tests`
- `python -m black --check api/_shared/core.py api/_shared/http_utils.py apps/api/server.py tests/test_api_phase_a_security.py tests/test_serverless_shared_core.py tests/test_static_surface_security.py`
- `node --check apps/council-playground/app.js`
- `node -e "<parse inline scripts in apps/dashboard/world.html>"`

Not run in the extraction worktree:

- `npm --prefix apps/web run lint` / `build` — `apps/web/node_modules` was not
  present, and this phase does not touch `apps/web`.

New regression coverage added in:

- `tests/test_api_phase_a_security.py`
- `tests/test_serverless_shared_core.py`
- `tests/test_static_surface_security.py`
