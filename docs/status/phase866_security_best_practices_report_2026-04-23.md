# ToneSoul Security Review Report

> Scope: `apps/web`, `api/`, `apps/api/`, `apps/council-playground/`, `apps/dashboard/`
> Date: 2026-04-23
> Reviewer: Codex
> Remediation Update: Phase 866 landed follow-up fixes for `TS-AUTH-001`,
> `TS-XSS-001` (static observability sinks), `TS-TOKEN-001`, and `TS-CORS-001`.
> Treat this report as the discovery snapshot; see
> `docs/status/phase866_public_surface_security_hardening_2026-04-23.md`
> for the post-fix rationale and residual risk list.

## Executive Summary

No clear externally reachable shell-style RCE sink was found in the current public web/API surfaces.

The highest-risk issues are currently:

1. production protection defaults can fail open, leaving auth/rate limits dependent on extra env flags;
2. legacy/static dashboard surfaces contain stored-XSS sinks;
3. browser-held tokens/API keys are persisted in `localStorage` and, in one surface, also accepted from the URL query string.

These are more urgent than generic hardening work because they can directly expose operator tokens, provider API keys, or expensive write-capable endpoints.

## High Severity

### Finding 1

- Rule ID: `TS-AUTH-001`
- Severity: High
- Location:
  - `api/_shared/core.py:301`
  - `api/_shared/core.py:319`
  - `api/_shared/core.py:501`
  - `api/chat.py:56`
  - `api/chat.py:60`
  - `api/validate.py:42`
  - `api/validate.py:46`
  - `apps/api/server.py:101`
  - `apps/api/server.py:119`
  - `apps/api/server.py:334`
- Evidence:
  - `_is_production_env()` only treats `TONESOUL_PRODUCTION`, `TONESOUL_ENV`, or `FLASK_ENV` as production.
  - `_is_rate_limit_enabled()` falls back to `_is_production_env()`.
  - `_require_api_auth()` sets `fail_closed = _env_flag(_AUTH_FAIL_CLOSED_ENV, default=_is_production_env())`.
  - When no token is configured and `fail_closed` is false, `_require_api_auth()` returns success.
  - `api/chat.py` and `api/validate.py` both call `_require_write_api_auth()` and `_apply_rate_limit(...)` before processing requests.
- Impact:
  - If deployed without explicitly setting `TONESOUL_PRODUCTION=1` or `TONESOUL_AUTH_FAIL_CLOSED=1`, write-capable endpoints can become publicly callable and rate limiting can remain off.
  - This exposes `/api/chat` and `/api/validate` to abuse, cost amplification, prompt flooding, and persistence-side effects.
- Fix:
  - Treat Vercel/Next production signals as production too, for example `VERCEL_ENV=production`, `VERCEL=1`, or `NODE_ENV=production`.
  - Make write-path auth fail closed by default regardless of Flask-specific env names.
  - Make rate limiting opt-out, not opt-in, on internet-facing deployments.
- Mitigation:
  - Immediately set `TONESOUL_AUTH_FAIL_CLOSED=1`, `TONESOUL_PRODUCTION=1`, `TONESOUL_READ_API_TOKEN`, and `TONESOUL_WRITE_API_TOKEN` anywhere this code is public.
- False positive notes:
  - If your deployment already forces these env vars in infrastructure, severity drops.
  - The risk is still real at code level because production detection is incomplete.

### Finding 2

- Rule ID: `TS-XSS-001`
- Severity: High
- Location:
  - `apps/council-playground/app.js:161`
  - `apps/council-playground/app.js:174`
  - `tonesoul/supabase_persistence.py:445`
  - `tonesoul/supabase_persistence.py:461`
  - `apps/dashboard/world.html:633`
  - `apps/dashboard/world.html:650`
- Evidence:
  - `apps/council-playground/app.js` renders audit log HTML with `nodes.auditList.innerHTML = logs.map(...).join("")`.
  - It interpolates `${rationale}` directly into `<p class="list-item-body">${rationale}</p>`.
  - `record_chat_audit()` stores `rationale = _trim_text(summary or json.dumps(transcript or {}, ensure_ascii=False))`, so persisted audit text is at least partially attacker-influenced.
  - `apps/dashboard/world.html` also injects raw `${v.content || ''}` and `${t.topic || '—'}` into `innerHTML`.
- Impact:
  - A crafted prompt, transcript, or other persisted field can become stored XSS when an operator opens the dashboard/playground.
  - Because this repo also stores read tokens and API keys in browser storage, XSS can become token/key theft.
- Fix:
  - Stop rendering untrusted data with `innerHTML`.
  - Build DOM nodes with `textContent`, or escape every interpolated field before insertion.
  - Treat all audit/vow/tension text as untrusted, even if it comes from the model rather than directly from the user.
- Mitigation:
  - Disable or restrict legacy static dashboards until these sinks are fixed.
  - Clear any stored browser tokens on systems that have already opened these pages with untrusted data.
- False positive notes:
  - If these pages are never exposed and only used with fully trusted local data, exploitability drops.
  - The sink is still present in code and should be treated as real.

## Medium Severity

### Finding 3

- Rule ID: `TS-TOKEN-001`
- Severity: Medium
- Location:
  - `apps/council-playground/app.js:64`
  - `apps/council-playground/app.js:73`
  - `apps/council-playground/app.js:90`
  - `apps/council-playground/app.js:109`
- Evidence:
  - The playground stores the read token in `localStorage`.
  - It also accepts `?read_token=` from the URL and persists it.
  - That token is then attached as `Authorization: Bearer ...` on subsequent API calls.
- Impact:
  - Query-string tokens leak into browser history, screenshots, logs, copied URLs, and potentially referrers.
  - Persisting the token in `localStorage` makes it recoverable by any XSS on the same origin.
- Fix:
  - Remove query-string token ingestion entirely.
  - Prefer short-lived tokens entered manually per session, or server-side auth not exposed to client JS.
  - If browser storage is unavoidable, prefer `sessionStorage` over `localStorage` and document the residual risk.
- Mitigation:
  - Treat any token that has appeared in a shared URL as compromised and rotate it.
- False positive notes:
  - If the token is only used in a fully local sandbox, impact drops, but URL leakage remains poor practice.

### Finding 4

- Rule ID: `TS-SECRETS-001`
- Severity: Medium
- Location:
  - `apps/web/src/components/SettingsModal.tsx:22`
  - `apps/web/src/components/SettingsModal.tsx:38`
  - `apps/web/src/components/SettingsModal.tsx:51`
  - `apps/web/src/components/ChatInterface.tsx:447`
  - `apps/web/src/components/ChatInterface.tsx:508`
  - `apps/web/src/components/ChatInterface.tsx:531`
  - `apps/web/src/components/ChatInterface.tsx:555`
  - `apps/web/src/components/SessionReport.tsx:124`
  - `apps/web/src/components/SessionReport.tsx:143`
- Evidence:
  - `SettingsModal` stores provider keys in `localStorage` under `tonesoul_api_settings`.
  - `ChatInterface` and `SessionReport` then call Gemini/OpenAI/Anthropic/xAI directly from browser code using those keys.
- Impact:
  - Any XSS, malicious extension, or local browser compromise on this origin can extract live provider credentials.
  - There is no server-side key scoping, rotation boundary, or request policy enforcement.
- Fix:
  - Move provider access behind a server-side BFF/proxy where the project owns the credential boundary.
  - If bring-your-own-key is required, store it in memory for the session only, or use encrypted browser storage plus a user passphrase and clear UX warnings.
- Mitigation:
  - Keep this flow behind explicit “local BYOK” labeling and do not present it as production-safe secret handling.
- False positive notes:
  - This is partly an intentional design choice, not a leaked server secret.
  - It is still a real security posture risk and should not be treated as harmless.

### Finding 5

- Rule ID: `TS-CORS-001`
- Severity: Medium
- Location:
  - `api/_shared/http_utils.py:30`
  - `api/_shared/http_utils.py:32`
  - `api/_shared/core.py:246`
  - `api/_shared/core.py:247`
  - `api/_shared/core.py:516`
- Evidence:
  - Serverless helpers send `Access-Control-Allow-Origin: *`.
  - They also allow `Authorization`, `X-ToneSoul-Read-Token`, and `X-ToneSoul-Write-Token`.
  - These same token headers are used for API protection.
- Impact:
  - Any origin can make browser-readable cross-origin requests to these endpoints if it has a token.
  - This weakens origin-based containment and increases blast radius when a token is exposed through XSS, copied URLs, or browser storage.
- Fix:
  - Restrict `Access-Control-Allow-Origin` to the actual frontend origins.
  - Avoid wildcard CORS on token-bearing endpoints.
- Mitigation:
  - If public CORS is temporarily required, split public unauthenticated endpoints from token-protected ones and apply different policies.
- False positive notes:
  - If these endpoints are never called cross-origin in production, this may not be currently exploited.
  - It is still an unsafe default for authenticated APIs.

## Low Severity

### Finding 6

- Rule ID: `TS-HEADERS-001`
- Severity: Low
- Location:
  - `apps/web/next.config.ts:3`
  - `apps/web/vercel.json:1`
- Evidence:
  - No CSP, `X-Content-Type-Options`, clickjacking, or referrer-policy headers are visible in app-level config.
  - `next.config.ts` only sets Turbopack root; `vercel.json` only defines build/runtime commands.
- Impact:
  - Missing browser hardening increases the blast radius of any future XSS or third-party content mistake.
  - This is especially relevant because the app currently stores tokens/API keys in browser storage.
- Fix:
  - Add a baseline CSP and standard security headers at the Next/Vercel layer.
  - At minimum consider `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and frame restrictions.
- Mitigation:
  - If headers are injected by a reverse proxy/CDN, document that clearly in repo docs so app-level review does not assume they are absent.
- False positive notes:
  - This finding is based on “not visible in app code”; infrastructure may already add these headers.

## RCE-Specific Note

I did not find a clear remotely reachable `eval`/`exec`/`shell=True`/unsafe-deserialization path in the current public web/API request surfaces.

There are local/desktop automation and CLI scripts that invoke subprocesses or GUI automation, but they appear to be operator-local tools rather than internet-facing handlers. They should still be reviewed separately if you plan to expose them beyond trusted local use.
